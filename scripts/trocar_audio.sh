#!/usr/bin/env bash
# Troca so o som do video, sem renderizar a imagem de novo (mudancas de efeito, volume, trilha).
# Uso: bash trocar_audio.sh video.mp4 mix.wav saida.mp4
set -e; ffmpeg -v error -y -i "$1" -i "$2" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart "$3"; echo "pronto: $3"
