#!/usr/bin/env bash
# Renderiza a animacao quadro a quadro em 4 processos e junta com o audio.
# Uso: bash render.sh pasta_da_animacao mix.wav saida.mp4 [FPS=24]
# Quadros que ja existem sao pulados: se parar no meio, rode de novo.
export NODE_PATH=${NODE_PATH:-$(npm root -g)}
set -e; A=$(cd "$1" && pwd); MIX=$2; OUT=$3; FPS=${FPS:-24}; H=$(cd "$(dirname "$0")" && pwd)
DUR=$(cd "$A" && node -e "const{chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://'+process.cwd()+'/anim.html');console.log(await p.evaluate(()=>DUR));await b.close()})()")
N=$(python3 -c "import math;print(math.ceil($DUR*$FPS))"); Q=$(( (N+3)/4 )); echo "duracao $DUR s, $N quadros"
cd "$A"; for k in 0 1 2 3; do FPS=$FPS node "$H/render_all.js" anim.html quadros $((k*Q)) $(( (k+1)*Q < N ? (k+1)*Q : N )) & done; wait
ffmpeg -v error -y -framerate $FPS -i quadros/f_%05d.jpg -i "$MIX" -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -c:a aac -b:a 320k -shortest -movflags +faststart "$OUT"
echo "pronto: $OUT"
