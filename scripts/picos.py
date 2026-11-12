"""Picos da musica para o fundo reagir a trilha (graves, agudos e fluxo da luz).
Uso: python picos.py trilha.wav DURACAO_DO_VIDEO pasta_da_animacao/peaks.js
O anim.html le PK_L (graves), PK_H (agudos) e PK_F (fluxo acumulado), 30 valores por segundo."""
import json, sys
import librosa, numpy as np
trilha, dur, saida = sys.argv[1], float(sys.argv[2]), sys.argv[3]
y, sr = librosa.load(trilha, sr=48000, mono=True); n = int(dur * 30)
S = np.abs(librosa.stft(y, n_fft=4096, hop_length=1600)); f = librosa.fft_frequencies(sr=sr, n_fft=4096)
def nz(a):
    a = a[:n]; a = np.pad(a, (0, max(0, n - len(a)))); a = a / (np.percentile(a, 98) + 1e-9); a = np.clip(a, 0, 1.2)
    o = np.zeros_like(a); v = 0
    for i, x in enumerate(a): v = x if x > v else v * 0.86 + x * 0.14; o[i] = v
    return o
L = nz(S[f < 150].mean(0)); H = nz(S[f > 2000].mean(0)); F = np.cumsum(0.4 + 1.6 * L) / 30
open(saida, 'w').write('const PK_L=%s,PK_H=%s,PK_F=%s;' % tuple(json.dumps([round(float(x), 3) for x in a]) for a in (L, H, F)))
print('ok', saida, n, 'quadros')
