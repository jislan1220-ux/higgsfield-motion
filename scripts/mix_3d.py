"""Mix 3D imersivo (para fone): musica girando em volta da cabeca e subindo/descendo,
SFX que voam pelo espaco seguindo a animacao, reverb de cinema e camadas de trailer.

Uso: mix_3d.py voz.wav trilha.wav pasta_sfx eventos.json saida/ [--dur 25.5]
- voz.wav: voz ja tratada (stems/voz.wav do mixar.py)
- trilha.wav: trilha ja cortada no tempo do video (trilha_cinematica.py)
eventos.json: lista de {"nome", "t", "db", "alinhar": "pico"|"inicio",
                         "az": [graus_ini, graus_fim], "el": [ini, fim], "rev": 0..1}
az: 0 frente, 90 direita, -90 esquerda, 180 atras. el: -1 baixo, 1 cima.
"""
import argparse, json, pathlib, re, subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve
import librosa

ap = argparse.ArgumentParser()
ap.add_argument('voz'); ap.add_argument('trilha'); ap.add_argument('sfx'); ap.add_argument('eventos'); ap.add_argument('saida')
ap.add_argument('--dur', type=float, default=25.5)
ap.add_argument('--drop', type=float, default=0.88)
ap.add_argument('--fim', type=float, default=23.25)
ap.add_argument('--mus_lufs', type=float, default=-27.5)  # nivel da trilha antes do master
ap.add_argument('--sfx_lufs', type=float, default=-22.5)  # nivel dos efeitos antes do master
ap.add_argument('--limpa', action='store_true')  # v24: musica limpa (sem pad, pouco reverb, giro lento e suave)
a = ap.parse_args()
SR = 48000; N = int(a.dur * SR); OUT = pathlib.Path(a.saida); (OUT / 'stems').mkdir(parents=True, exist_ok=True)
t = np.arange(N) / SR
rng = np.random.RandomState(11)

def filt(x, kind, f, o=2): return sosfilt(butter(o, f, kind, fs=SR, output='sos'), x, axis=0)
def load(p, mono=False):
    x, _ = librosa.load(str(p), sr=SR, mono=False); x = np.atleast_2d(x)
    if x.shape[0] == 1: x = np.vstack([x, x])
    x = x[:2].T
    return x.mean(1) if mono else x
def fit(x):
    y = np.zeros((N,) + x.shape[1:]); n = min(N, len(x)); y[:n] = x[:n]; return y

def binaural(x, az, el):
    """x mono, az em graus por amostra, el -1..1 por amostra -> estereo."""
    n = len(x); az = np.radians(az); s = np.sin(az); c = np.cos(az)
    lp = filt(x, 'low', 2200); dark = filt(x, 'low', 5000); hp = filt(x, 'high', 6000)
    # elevacao: em cima mais brilho, embaixo mais escuro; atras um pouco abafado
    base = x + np.clip(el, 0, 1) * 0.9 * hp - np.clip(-el, 0, 1) * 0.85 * (x - dark)
    base = base - 0.35 * np.clip(-c, 0, 1) * (x - dark)
    base = base * (1 + 0.12 * el)
    lpb = lp * (1 + 0.12 * el)
    ear = []
    for lado in (-1, 1):  # esquerda, direita
        longe = np.clip(-lado * s, 0, 1)            # quanto a fonte esta do outro lado
        sig = base * (1 - 0.75 * longe) + lpb * 0.75 * longe
        g = 1 - 0.62 * longe
        d = 0.00066 * longe * SR                    # atraso entre os ouvidos
        idx = np.arange(n) - d; i0 = np.floor(idx).astype(int); fr = idx - i0
        i0 = np.clip(i0, 0, n - 1); i1 = np.clip(i0 + 1, 0, n - 1)
        ear.append((sig[i0] * (1 - fr) + sig[i1] * fr) * g)
    return np.stack(ear, 1)

def ir(dur, decay, cor=6000, pre=0.025):
    m = int(dur * SR); tt = np.arange(m) / SR
    h = np.stack([rng.randn(m), rng.randn(m)], 1) * np.exp(-tt / decay)[:, None]
    h = filt(h, 'low', cor); h[:int(pre * SR)] = 0
    return h / np.sqrt((h ** 2).sum())
SALA = ir(3.2, 0.9)          # sala de cinema grande
def reverb(x, h=SALA):
    return np.stack([fftconvolve(x[:, 0], h[:, 0])[:len(x)], fftconvolve(x[:, 1], h[:, 1])[:len(x)]], 1)

def lufs(p):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(p), '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True)
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1])
def wav(p, x): wavfile.write(str(p), SR, x.astype(np.float32))
def norm(x, nome, alvo):
    p = OUT / 'stems' / f'{nome}.wav'; wav(p, x); x = x * 10 ** ((alvo - lufs(p)) / 20); wav(p, x); return x

# ---------- voz ----------
voz = fit(load(a.voz))
env = np.sqrt(np.convolve(voz.mean(1) ** 2, np.ones(2400) / 2400, 'same'))
env = env / (np.percentile(env[env > 1e-4], 90) + 1e-9)
# envelope da voz em blocos de 1 ms: ataque de 12 ms, soltura de 350 ms
e = np.clip(env, 0, 1)
blk = e[: N // 48 * 48].reshape(-1, 48).max(1); dk = np.zeros_like(blk); v = 0.0
a1 = 1 - np.exp(-1 / 12); r1 = 1 - np.exp(-1 / 350)
for i, x in enumerate(blk):
    v += (x - v) * (a1 if x > v else r1); dk[i] = v
duck = np.interp(t, (np.arange(len(dk)) + .5) * 48 / SR, dk)
g_mus = 1 - 0.55 * np.clip(duck, 0, 1)          # ate ~ -7 dB sob a voz

# ---------- musica em 3D ----------
mus = fit(load(a.trilha))
grave = filt(mus.mean(1), 'low', 140, 4)          # grave parado no centro
alto = mus - filt(mus, 'low', 140, 4)
mid = alto.mean(1); side = (alto[:, 0] - alto[:, 1]) / 2
# velocidade da volta: lenta antes do drop, rapida depois, acelera no fim
vel = np.where(t < a.drop, 360 / 9.0, 360 / 4.6) if not a.limpa else np.full(N, 360 / 14.0)
vel = vel * (1 + (0.6 if not a.limpa else 0) * np.clip((t - (a.fim - 4)) / 4, 0, 1))
az = np.cumsum(vel) / SR - 30
el = 0.85 * np.sin(2 * np.pi * t / 3.1) if not a.limpa else 0.35 * np.sin(2 * np.pi * t / 9.0)  # sobe e desce
rot = binaural(mid, az, el)
if a.limpa:  # metade fica parada e aberta (estereo original), metade gira em volta: 3D sem embolar
    mus3 = rot * 0.7 + mid[:, None] * 0.25 + np.stack([side, -side], 1) * 1.1 + grave[:, None] * 0.95
    mus3 = mus3 + reverb(mus3) * 0.08
else:
    mus3 = rot * 0.9 + np.stack([side, -side], 1) * 0.3 + grave[:, None] * 0.95
    mus3 = mus3 + reverb(mus3) * np.where(t < a.drop, 0.7, 0.28)[:, None]

# camada de trailer: pad grave na tonica da musica, girando no sentido contrario
y_k, _ = librosa.load(a.trilha, sr=22050, duration=20)
chroma = librosa.feature.chroma_cqt(y=y_k, sr=22050).mean(1); raiz = int(chroma.argmax())
f0 = librosa.midi_to_hz(36 + raiz)
pad = sum(np.sin(2 * np.pi * f * (1 + d) * t + rng.rand() * 6) for f in (f0, f0 * 1.5, f0 * 2) for d in (-0.003, 0, 0.003))
pad = filt(pad, 'low', 900) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 7)) * np.clip(t / 1.5, 0, 1)
pad = pad * np.clip((a.fim + 0.6 - t) / 0.6, 0, 1)
pad3 = binaural(pad, -az * 0.7 + 180, -el * 0.6)
pad3 = pad3 + reverb(pad3) * 0.6
mus_total = (mus3 + (0 if a.limpa else 1) * pad3 * 0.12 * np.sqrt((mus3 ** 2).mean() / ((pad3 ** 2).mean() + 1e-12))) * g_mus[:, None]

# ---------- SFX em 3D ----------
pasta = pathlib.Path(a.sfx); cache = {}
def som(nome):
    if nome not in cache:
        x = load(pasta / f'{nome}.wav', mono=True); x = x / (np.abs(x).max() + 1e-9)
        pk = int(np.convolve(x ** 2, np.ones(960) / 960, 'same').argmax()); cache[nome] = (x, pk)
    return cache[nome]
seco = np.zeros((N, 2)); envio = np.zeros((N, 2))
for ev in json.load(open(a.eventos, encoding='utf8')):
    x, pk = som(ev['nome']); i = int(ev['t'] * SR) - (pk if ev.get('alinhar', 'pico') == 'pico' else 0)
    c = max(0, -i); i = max(0, i); n = min(len(x) - c, N - i)
    if n <= 0: continue
    seg = x[c:c + n] * 10 ** (ev.get('db', -10) / 20)
    u = np.linspace(0, 1, n); az0, az1 = ev.get('az', [0, 0]); e0, e1 = ev.get('el', [0, 0])
    s3 = binaural(seg, az0 + (az1 - az0) * u, e0 + (e1 - e0) * u)
    seco[i:i + n] += s3; envio[i:i + n] += s3 * ev.get('rev', 0.4)
sfx = seco + reverb(envio, ir(2.4, 0.7, 7000) if not a.limpa else ir(1.2, 0.35, 6000))
sfx = sfx * (1 - 0.2 * np.clip(duck, 0, 1))[:, None]

# ---------- niveis e master ----------
voz = norm(voz, 'voz', -19.5)
mus_total = norm(mus_total, 'trilha_3d', a.mus_lufs)   # 8 dB abaixo da voz (antes eram 12)
sfx = norm(sfx, 'sfx_3d', a.sfx_lufs)
mix = voz + mus_total + sfx
pre = OUT / 'pre.wav'; wav(pre, mix)
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(pre), '-af', 'loudnorm=I=-14:TP=-1:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
j = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
ln = f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(pre), '-af', f'{ln},aresample={SR}', '-c:a', 'pcm_s24le', str(OUT / 'mix.wav')], check=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(OUT / 'mix.wav'), '-c:a', 'libmp3lame', '-b:a', '320k', str(OUT / 'audio_para_aprovar.mp3')], check=True)
pre.unlink()
print('tonica do pad:', librosa.midi_to_note(36 + raiz), 'mix integrado:', lufs(OUT / 'mix.wav'), 'LUFS')
