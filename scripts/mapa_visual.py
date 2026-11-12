"""Mapa visual do video pronto: o que acontece na tela e quando. Base para por um efeito em cada evento.
Uso: python mapa_visual.py video.mp4 pasta_saida
Gera grades de quadros a 2 fps com o tempo escrito (grade_0.jpg, grade_1.jpg...) e eventos.txt com os
picos de diferenca entre quadros (cortes, flashes, lasers, entradas), com o brilho antes e depois."""
import os, subprocess, sys
import numpy as np
from scipy.signal import find_peaks
v, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', v], capture_output=True, text=True).stdout)
for i in range(int(dur // 15) + 1):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(i * 15), '-t', '15', '-i', v, '-vf',
        f"fps=2,scale=320:-1,drawtext=text='%{{pts\\:flt\\:{i * 15}}}':x=4:y=4:fontsize=20:fontcolor=yellow:box=1:boxcolor=black,tile=6x5",
        '-frames:v', '1', f'{out}/grade_{i}.jpg'], check=True)
fps = 24
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vf', f'fps={fps},scale=160:90,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
x = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160).astype(float)
b = x.mean((1, 2)); d = np.r_[0, np.abs(np.diff(x, axis=0)).mean((1, 2))]
p, _ = find_peaks(d, height=6, distance=5)
with open(f'{out}/eventos.txt', 'w') as f:
    for i in p:
        tipo = 'CLARAO' if b[i] - b[max(0, i - 3)] > 40 else ('CORTE' if d[i] > 30 else 'movimento')
        f.write(f'{i / fps:7.2f}s  {tipo:9s} diferenca {d[i]:5.1f}  brilho {b[max(0, i - 3)]:4.0f} -> {b[i]:4.0f}\n')
print(open(f'{out}/eventos.txt').read())
