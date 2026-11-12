"""Monta os eventos de SFX do motion com a receita aprovada no video Higgsfield + Claude.

Automatico (a partir de times.json e do anim.html):
  - corte                  -> whoosh atravessando de um lado para o outro
  - entrada de cada cena   -> riser curto chegando na batida + impacto suave
  - troca da cena p/ card  -> laser (blade whoosh) + glitch baixinho
  - corte dentro do card   -> whoosh
  - cada palavra na tela   -> toque de digitacao de interface (baixinho, com sala, 4 tons, alternando lado)
  - logo final             -> blade whoosh + boom suave + sinos
Manual (extra.json, a partir do mapa visual): chips, menus, caixas de texto, telas de cor, sons das cenas.
  Formato de cada item: {"som": "tique", "t": 2.0, "db": -20}  (som = papel em sons.json ou nome do arquivo)
  Sons de cena (vento, rugido, fogo...): {"som": "real_rugido", "t": 4.29, "db": -5, "cena": true}

Uso: python eventos_sfx.py times.json anim.html eventos.json [--sons sons.json] [--extra extra.json]
Depois: python mix_3d.py voz.wav trilha.wav PASTA_SONS eventos.json saida --limpa --sfx_lufs -24.3 --mus_lufs -25.2
"""
import argparse, json, re

ap = argparse.ArgumentParser()
ap.add_argument('tempos'); ap.add_argument('anim'); ap.add_argument('saida')
ap.add_argument('--sons', default=None); ap.add_argument('--extra', default=None)
ap.add_argument('--cena_db', type=float, default=4, help='quanto os sons das cenas sobem (aprovado: +4)')
a = ap.parse_args()

# papeis -> arquivos (sem .wav). Os padroes sao da pasta assets/sons_cc0 (CC0). Troque pelos seus em sons.json.
SONS = {
    'corte': ['m_wh_grave', 'm_wh1', 'm_wh2', 'm_wh4'],
    'laser': 'm_wh3', 'riser': 'm_riser', 'impacto': 'm_boom', 'glitch': 'kt_glitch',
    'tique': 'kt_blip', 'pop': 'kt_sel', 'abrir': 'kt_data', 'sucesso': 'm_chimes', 'brilho': 'm_glitter',
    'letra': ['kt_key1', 'kt_key2', 'kt_key3', 'kt_key4'], 'sinos': 'm_chimes', 'boom': 'm_boom',
}
if a.sons: SONS.update(json.load(open(a.sons)))
def som(papel, i=0):
    s = SONS.get(papel, papel); return s[i % len(s)] if isinstance(s, list) else s

J = json.load(open(a.tempos)); INS = J['ins']; E = []
def ev(nome, t, db, az=(0, 0), el=(0, 0), rev=.08, al='pico'):
    if t >= 0: E.append({"nome": nome, "t": round(t, 3), "db": round(db, 1), "az": list(az), "el": list(el), "rev": rev, "alinhar": al})
def ui(nome, t, db, az=(0, 0)): ev(nome, t, db, az, (.1, .1), .05, 'inicio')

# cortes
for i, c in enumerate(J['cuts'][:-1]):
    s = -1 if i % 2 == 0 else 1
    ev(som('corte', i), c, -14, (s * 100, -s * 100), (.2, -.1))
# cenas geradas (insercoes)
for k, I in enumerate(INS):
    t = I['t']; s = -1 if k % 2 == 0 else 1
    ev(som('riser'), t, -17, (0, 0), (.2, .3))
    ev(som('impacto'), t, -14, rev=.1, al='inicio')
    ev(som('laser'), t + I['half'], -15, (s * 90, -s * 90)); ui(som('glitch'), t + I['half'], -25)
    ev(som('corte', 2), t + I['q'], -17, (-s * 100, s * 100))
# logo final
e = J['end']
ev(som('laser'), e + .05, -12, (-90, 90), (.2, 0)); ev(som('boom'), e + .05, -17, al='inicio', rev=.15)
ev(som('sinos'), e + .45, -18, (60, -60), (.4, .4), rev=.2, al='inicio')

# manuais (mapa visual)
if a.extra:
    for x in json.load(open(a.extra)):
        nome = som(x['som']); db = x.get('db', -20) + (a.cena_db if x.get('cena') else 0)
        if x.get('cena'): ev(nome, x['t'], db, tuple(x.get('az', (0, 0))), tuple(x.get('el', (0, 0))), x.get('rev', .1), 'inicio')
        elif x['som'] in ('tique', 'pop', 'abrir', 'sucesso', 'glitch'): ui(nome, x['t'], db, tuple(x.get('az', (0, 0))))
        else: ev(nome, x['t'], db, tuple(x.get('az', (0, 0))), tuple(x.get('el', (0, 0))), x.get('rev', .08), x.get('alinhar', 'pico'))

# letras: um toque por palavra (tempos de WT no anim.html, em tempo da narracao)
HT = open(a.anim, encoding='utf-8').read()
WT = json.loads(re.search(r'const WT=(\[\[.*?\]\]);', HT).group(1))
INSN = [(float(m), I['len']) for (m, _), I in zip(json.loads(re.search(r"get\('ins'\)\|\|'(\[.*?\])'", HT).group(1)), INS)]
def real(m): return m + sum(L for m0, L in INSN if m >= m0)
DEST = set(w.lower() for w in J.get('destaques', [])) | {k[1].lower().strip('“”.,:!') for k in J['kw']}
ocupado = [x['t'] for x in E if x['alinhar'] == 'inicio' and x['rev'] <= .05]
k = 0; ult = -1
for w, m in WT:
    t = real(m)
    if any(abs(t - o) < .1 for o in ocupado) or (k and t - ult < .06): continue
    ult = t; forte = w.lower().strip('“”.,:!') in DEST
    ev(som('letra', k), t, (-22 if forte else -26) + (k % 3) * -.7, ((-1) ** k * 25, 0), (.2, .2), .22, 'inicio')
    k += 1

E.sort(key=lambda x: x['t'])
json.dump(E, open(a.saida, 'w'), indent=0, ensure_ascii=False)
print(len(E), 'eventos,', k, 'toques de letra')
