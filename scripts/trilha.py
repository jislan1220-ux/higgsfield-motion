"""Monta a trilha cinematografica: intro abafada que abre no drop, corte seco no fim
e camadas sinteticas (braam, sub drop, boom) na pasta de SFX.
Uso: trilha_cinematica.py musica.mp3 inicio drop_video fim_video saida.wav pasta_sfx"""
import sys, os, subprocess, pathlib, numpy as np  # intro limpa, sem eco (aprovado); LIMPA=0 liga o eco
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

mus, ini, drop, fim, out, pasta = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5], pathlib.Path(sys.argv[6])
SR = 48000

# intro: passa-baixa que abre de 350 Hz ate 2,5 kHz, volume subindo; depois do drop, musica cheia
fc = (f"[0:a]atrim=0:{drop},asetpts=PTS-STARTPTS,lowpass=f=350,lowpass=f=900,volume='0.55+0.45*t/{drop}':eval=frame,"
      f"afade=t=in:st=0:d=0.6{'' if os.environ.get('LIMPA', '1') != '0' else ',aecho=0.8:0.6:120|260:0.25|0.15'}[a];"
      f"[0:a]atrim={drop}:{fim},asetpts=PTS-STARTPTS,afade=t=out:st={fim - drop - 0.03}:d=0.03[b];"
      f"[a][b]concat=n=2:v=0:a=1,aresample={SR}[o]")
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(ini), '-t', str(fim), '-i', mus, '-filter_complex', fc,
                '-map', '[o]', '-ac', '2', '-c:a', 'pcm_f32le', out], check=True)

def lp(x, f, o=4): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def salvar(nome, x):
    x = np.asarray(x, float)
    if x.ndim == 1: x = np.stack([x, x], 1)
    x = x / (np.abs(x).max() + 1e-9) * 0.89
    wavfile.write(str(pasta / f'{nome}.wav'), SR, (x * 32767).astype(np.int16))

r = np.random.RandomState(3)
# braam: acorde grave de serras desafinadas, filtro abrindo e fechando, cauda longa
d = 3.2; t = np.arange(int(d * SR)) / SR
env = np.minimum(1, t / 0.03) * np.exp(-t / 1.1)
L = np.zeros_like(t); R = np.zeros_like(t)
for f in (41.2, 55.0, 61.7, 82.4, 110.0):
    for k, det in enumerate((-0.35, 0, 0.35)):
        ph = r.rand() * 2 * np.pi
        saw = 2 * ((f * (1 + det / 100) * t + ph / (2 * np.pi)) % 1) - 1
        (L if k % 2 == 0 else R)[:] += saw
        (R if k % 2 == 0 else L)[:] += saw * 0.6
cut = 180 + 1400 * np.exp(-t / 0.35)
blocos = [(i, min(i + 2400, len(t))) for i in range(0, len(t), 2400)]
outL = np.zeros_like(t); outR = np.zeros_like(t)
for a, b in blocos:
    outL[a:b] = lp(L[max(0, a - 4800):b], cut[a])[-(b - a):]
    outR[a:b] = lp(R[max(0, a - 4800):b], cut[a])[-(b - a):]
sub = np.sin(2 * np.pi * np.cumsum(30 + 30 * np.exp(-t / 0.25)) / SR) * np.exp(-t / 0.9)
salvar('braam', np.stack([np.tanh(1.6 * outL * env) + 0.9 * sub, np.tanh(1.6 * outR * env) + 0.9 * sub], 1))

# sub drop: seno caindo de 90 para 28 Hz
d = 2.2; t = np.arange(int(d * SR)) / SR
f = 28 + 62 * np.exp(-t / 0.4)
salvar('sub_drop', np.tanh(1.4 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.minimum(1, t / 0.005) * np.exp(-t / 0.7))

# boom com cauda de sala
d = 4.0; t = np.arange(int(d * SR)) / SR
corpo = np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-t / 0.06)) / SR) * np.exp(-t / 0.5)
ruido = lp(r.randn(len(t)), 900) * np.exp(-t / 0.08) * 0.5
cauda = np.stack([lp(r.randn(len(t)), 2500) * np.exp(-t / 1.2), lp(r.randn(len(t)), 2500) * np.exp(-t / 1.25)], 1) * 0.08
salvar('boom_cauda', np.stack([corpo + ruido, corpo + ruido], 1) + cauda)
print('ok', out)
