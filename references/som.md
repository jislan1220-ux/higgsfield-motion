# Som: a receita aprovada

Aprendida no vídeo Higgsfield + Claude, da v21 à v32, com tudo o que o Victor aprovou e reprovou.

## Trilha

- Limpa e leve: sem pad grave, quase sem reverb, girando devagar em volta da cabeça (uma volta a cada 14 s). Os graves ficam parados no centro. Isso é o `--limpa` do `mix_3d.py`.
- A intro entra abafada e abre na primeira batida forte; corte seco no fim, na logo.
- Master em -14 LUFS, pico em -1 dB.

## Efeitos

**Um efeito para cada coisa que acontece na tela, e só ali.** Antes de montar os eventos, faça o mapa visual (`scripts/mapa_visual.py`) e ligue cada evento a um som:

| Na tela | Som |
|---|---|
| Corte | whoosh atravessando de um lado para o outro |
| Laser ou lâmina cortando a tela | blade whoosh |
| Chip, botão, item de menu aparecendo | tique ou pop seco de interface, um por item |
| Caixa de texto ou de comentário abrindo | som curto de abrir de interface |
| Palavra do texto cinético aparecendo | toque de digitação de interface |
| Clarão ou tela de cor | riser curto (no máximo 1,5 s) chegando na batida |
| Entrada de cena gerada | riser curto + impacto suave |
| Cena gerada | o som da própria cena (vento, rugido, fogo, passos, gritos) |
| "Grátis", recompensa | brilho ou "twinkle" de sucesso |
| Logo final | blade whoosh + boom suave + sinos |

**Digitação em cada palavra.** Foi o detalhe que o Victor mais gostou ("fica foda"). Um toque curto de interface com uma caudinha, em 3 ou 4 tons levemente diferentes, alternando um pouco de lado. Fica baixinho (-26 dB, -22 nas palavras de destaque) e com um pouco de sala (reverb 0,22), para soar cinematográfico, não clique seco. Não toque duas vezes no mesmo instante nem em cima de outro som de interface. O `eventos_sfx.py` faz isso sozinho a partir do `WT`.

**Cenas geradas bem presentes.** Os sons das cenas ficam 4 dB acima do resto dos efeitos (`--cena_db 4`). O momento forte da cena (no modelo, a rosnada do dragão) fica uns 8 dB acima dos outros sons da cena, com um grave embaixo, para sentir o impacto.

**Peso vem do grave, não do volume.** Whooshes finos, só de ar, parecem baixos mesmo com +3 dB. Prefira whooshes com corpo abaixo de 120 Hz. Se a pessoa disser que o efeito está baixo, troque por sons mais graves antes de só subir o volume.

## Reprovado

- Impacto pesado de trailer em tela de cor (soou "uma bosta").
- Riser de sci-fi com sub na logo final.
- Impacto no começo sem nada forte na imagem e riser longo crescendo por baixo da voz na abertura (soou "estranho").
- Tique de interface em todo corte, inclusive nos cortes de cena.
- Muitas camadas empilhadas, braams, trilha com eco ("poluída").

## Níveis de partida

`mix_3d.py --limpa --sfx_lufs -24.3 --mus_lufs -25.2`, com a voz em -19,5 LUFS. Ajuste só o que a pessoa pedir.

## Pacote de efeitos da pessoa

Se a pessoa mandar um pacote como referência, meça cada pasta com `scripts/analisar_pacote.py pasta saida.json` (volume, grave abaixo de 120 Hz, brilho, largura estéreo) e compare com os sons em uso. Converta os escolhidos para wav 48 kHz numa pasta de sons e aponte os papéis em `sons.json`, por exemplo `{"corte": ["slide_whoosh", "whoosh_grave"], "laser": "blade_whoosh", "letra": ["tecla0", "tecla1", "tecla2", "tecla3"]}`. Para tirar 4 tons de um som de digitação: `ffmpeg -i som.mp3 -af "atrim=0.05:0.5,asetrate=48000*0.94,aresample=48000,afade=t=out:st=0.25:d=0.15" tecla1.wav` (use 0,89, 0,94, 1 e 1,06).

Sons de pacotes pagos (Epidemic Sound e afins) não vão para o repositório: ficam só na máquina da pessoa.
