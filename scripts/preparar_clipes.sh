#!/usr/bin/env bash
# Extrai os quadros de cada clipe gerado no Higgsfield (Seedance) para a animacao: clips/<id>/f_0001.jpg ... a 30 fps.
# Uso: bash preparar_clipes.sh pasta_da_animacao c1=clipe1.mp4 c2=clipe2.mp4 o1=extra1.mp4 ...
# Se o clipe tiver vinheta preta nas bordas, use CORTE=0.8 antes do comando para recortar 80% do centro.
set -e; A=$1; shift
for par in "$@"; do id=${par%%=*}; f=${par#*=}; mkdir -p "$A/clips/$id"; pre=""
  [ -n "$CORTE" ] && pre="crop=iw*$CORTE:ih*$CORTE,"
  ffmpeg -v error -y -i "$f" -vf "${pre}fps=30,scale=1440:810:force_original_aspect_ratio=increase,crop=1440:810" -q:v 3 "$A/clips/$id/f_%04d.jpg"
  echo "$id: $(ls "$A/clips/$id" | wc -l) quadros"; done
