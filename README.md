# Higgsfield Motion

Skill do Claude Code para criar vídeos de motion no estilo do vídeo **Higgsfield + Claude** do Victor Dias ([@diasl_uisvictor](https://instagram.com/diasl_uisvictor)), feito em parceria com a [Higgsfield](https://higgsfield.ai).

![Quadros do vídeo de referência](assets/exemplo_quadros.jpg)

Você grava a narração, gera as cenas no Higgsfield (Seedance), e o Claude monta o resto: texto cinético com a sua fala palavra por palavra, interface em vidro, as cenas entrando em tela cheia e virando card de vidro, laser cortando a tela, logo com corte de lâmina, trilha 3D, um efeito sonoro para cada coisa que acontece na tela, digitação em cada palavra, capa e legenda para o Instagram.

## O que vem junto

- **Modelo da animação** (`assets/modelo/`): o motor do vídeo de referência, pronto para trocar texto, cenas e marca.
- **Som**: trilha limpa girando em 3D, mapa visual do vídeo, efeitos automáticos (cortes, cenas, laser, logo e um toque de digitação por palavra) e mix final em -14 LUFS.
- **Sons CC0** (`assets/sons_cc0/`): whooshes, risers, impactos suaves, teclas, cliques e sons de cena (vento, rugido, asas, fogo, passos), todos de uso livre. Licenças em `LICENSES_katana.txt` e, para as gravações do Freesound, CC0.
- **Capa e legenda** para Reels (`assets/capa/`).
- **Tudo o que foi aprovado e reprovado** no vídeo de referência (`references/`).

## O que você precisa

- Claude Code no computador (o chat comum não renderiza vídeo).
- Narração em áudio e o texto dela, os clipes gerados no Higgsfield e a sua música.
- Python 3, FFmpeg, Node e Playwright. A skill confere e pede um "sim" para instalar o que faltar.

## Como instalar

Abra o Claude Code e cole:

```
Instala esta skill para mim: https://github.com/jislan1220-ux/higgsfield-motion.git na pasta ~/.claude/skills/higgsfield-motion
```

Depois é só pedir: *"faz um vídeo no estilo Higgsfield Motion com esta narração e estes clipes"*.

## Aviso

Skill independente, feita pelo Victor Dias. Não é um produto oficial da Higgsfield. Os sons de pacotes pagos usados no vídeo original não estão aqui; use os sons CC0 que vêm junto ou os seus.
