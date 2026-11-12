# O modelo da animação (`assets/modelo/anim.html`)

Uma página HTML que desenha cada quadro com `window.__setTime(t)`. O render tira um print por quadro (`scripts/render_all.js`). Tempos dentro do arquivo estão em **tempo da narração**; as inserções das cenas geradas empurram o resto (`toReal`).

## O que trocar para um vídeo novo

| Constante | O que é |
|---|---|
| `WT` | cada palavra da narração e o segundo em que ela é falada (da transcrição) |
| `FR` | frases: início, texto, altura na tela e palavras de destaque |
| `SC` | as cenas de motion: início, fim e o desenho de cada uma (texto, chips, caixas, menu, telas de cor) |
| `INSL` | em que segundo da narração entra cada cena gerada, e qual clipe (`c1`, `c2`) |
| `INSB` | duração de cada inserção em batidas: total e quanto fica em tela cheia (`BPS` = 60/BPM da música) |
| `CLIPS` | texto da frase em cima da cena gerada e os clipes do card, com o ponto de cada corte |
| `CLIPBG` | clipes que passam escurecidos no fundo das cenas de motion |
| `HITS`, `FLASH`, `SLASH` | batidas fortes, clarões e lasers |
| `FOC` | onde a luz fica em cada cena |
| Logo e crédito | procure `KATANA` e `um vídeo de` na cena final |
| Selos | procure `COMENTA` e `patrocinado` |

Depois de trocar, rode `node scripts/tempos.js times.json` dentro da pasta: ele gera os cortes, as palavras de destaque, as batidas, as inserções e o fim da logo em tempo do vídeo final, que o som usa.

## Clipes

`clips/<id>/f_0001.jpg`... a 30 fps, 1440x810, gerados por `scripts/preparar_clipes.sh`. Os ids `c*` são as cenas principais (até 6 s) e `o*` são extras (até 5 s).

## Fontes

Inter Display, Inter e JetBrains Mono precisam estar instaladas no sistema. League Gothic vem em `fonts/`.
