"""Gera o relatório em PDF (relatorio/Raquel_Lyra_55_2026.pdf) com dicas ao passar o mouse.

As dicas são campos de formulário invisíveis com texto de ajuda (/TU). Aparecem no Adobe Acrobat
Reader e no Firefox; o leitor de PDF do Chrome e do Edge não as mostra.
Requer: pip install -r requirements.txt. Entradas: dados/relatorio.json e dados/pe_municipios.geojson (passos 5 e 6).
"""
import json, math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
from PIL import Image, ImageDraw

from comum import DADOS, RAIZ

pdfmetrics.registerFont(TTFont('R', 'C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont('B', 'C:/Windows/Fonts/segoeuib.ttf'))
pdfmetrics.registerFont(TTFont('SB', 'C:/Windows/Fonts/seguisb.ttf'))

D = json.load(open(DADOS / 'relatorio.json', encoding='utf-8'))
GEO = json.load(open(DADOS / 'pe_municipios.geojson', encoding='utf-8'))

INK = HexColor('#16202a'); INK2 = HexColor('#4a5561'); MUTED = HexColor('#7a848e'); LINE = HexColor('#dfe3e0')
ACC = HexColor('#1f56c4'); ACCS = HexColor('#e3ebfa'); GRAY = HexColor('#b7bec4'); TRACK = HexColor('#eceeea')
UP = HexColor('#2a78d6'); DOWN = HexColor('#d6553f'); WARNBG = HexColor('#fdf3dc'); WARNINK = HexColor('#7a5208')
BINS = [HexColor(h) for h in ['#eceeea', '#d4e2f6', '#9fc0ec', '#5f95db', '#2c66c4', '#143f8a']]
W, H = A4; M = 40; CW = W - 2 * M

def fmt(n): return f'{int(round(n)):,}'.replace(',', '.')
def pct(p): return f'{p:.2f}'.replace('.', ',') + '%'
def sgn(d): return ('+' if d > 0 else '-' if d < 0 else '') + fmt(abs(d))
SMALL = {'da', 'de', 'do', 'dos', 'das', 'e'}
def title(s):
    return ' '.join(w if (i and w in SMALL) else w[:1].upper() + w[1:] for i, w in enumerate(s.lower().split()))
def binof(p): return 1 if p < 40 else 2 if p < 50 else 3 if p < 60 else 4 if p < 70 else 5  # % dos válidos

(RAIZ / 'relatorio').mkdir(exist_ok=True)
c = canvas.Canvas(str(RAIZ / 'relatorio' / 'Raquel_Lyra_55_2026.pdf'), pagesize=A4)
c.setTitle('Raquel Lyra 55 em 2026'); c.setAuthor('Dados: TSE'); c.setSubject('Votação para governadora em Pernambuco, 1º turno de 2026')
NT = [0]
def tip(x, y, w, h, text):
    NT[0] += 1
    c.acroForm.textfield(name=f't{NT[0]}', tooltip=text, x=x, y=y, width=max(w, 1), height=max(h, 1),
                         borderWidth=0, borderColor=None, fillColor=None, textColor=None, value='',
                         fieldFlags='readOnly', forceBorder=False, relative=False)

PAGE = [0]
def footer():
    PAGE[0] += 1
    c.setFont('R', 7.5); c.setFillColor(MUTED)
    c.drawString(M, 24, f"Fonte: TSE (resultados.tse.jus.br e dadosabertos.tse.jus.br), dados de {D['meta']['dg']} às {D['meta']['hg']}." + (' Sujeitos a reprocessamento.' if D['meta']['aviso'] else ''))
    c.drawRightString(W - M, 24, f'{PAGE[0]}')

def text(x, y, s, font='R', size=10, color=INK, width=None, lead=None):
    c.setFont(font, size); c.setFillColor(color)
    lines = simpleSplit(s, font, size, width) if width else [s]
    lead = lead or size * 1.4
    for i, l in enumerate(lines): c.drawString(x, y - i * lead, l)
    return y - len(lines) * lead

def head(y, eyebrow, h, body=None):
    c.setStrokeColor(INK); c.setLineWidth(1.5); c.line(M, y, W - M, y)
    y -= 14; text(M, y, eyebrow.upper(), 'SB', 7.5, ACC)
    y -= 20; y = text(M, y, h, 'B', 16, INK, CW, 19)
    if body: y = text(M, y - 2, body, 'R', 9.5, INK2, CW, 13.5)
    return y - 8

def hint(y, s='Passe o mouse sobre os elementos para ver os detalhes.'):
    return text(M, y, s, 'R', 8, MUTED) - 4

# ---------- mapa ----------
def draw_map(x0, y0, w, h, bbox, feats, label_ids=(), cell=2.0):
    lon0, lat0, lon1, lat1 = bbox
    k = min(w / (lon1 - lon0), h / (lat1 - lat0))
    mw, mh = (lon1 - lon0) * k, (lat1 - lat0) * k
    ox, oy = x0 + (w - mw) / 2, y0 + (h - mh) / 2
    P = lambda lo, la: (ox + (lo - lon0) * k, oy + (la - lat0) * k)
    def polys(f):
        g = f['geometry']; return [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
    c.saveState(); p = c.beginPath(); p.rect(x0, y0, w, h); c.clipPath(p, stroke=0, fill=0)
    c.setStrokeColor(HexColor('#ffffff')); c.setLineWidth(0.4)
    for f in feats:
        m = D['mapa'].get(f['properties']['id'])
        c.setFillColor(BINS[binof(m[2]) if m else 0])
        pth = c.beginPath()
        for poly in polys(f):
            for ring in poly:
                pts = [P(*pt) for pt in ring]
                pth.moveTo(*pts[0])
                for q in pts[1:]: pth.lineTo(*q)
                pth.close()
        c.drawPath(pth, fill=1, stroke=1, fillMode=0)
    c.restoreState()
    # rótulos
    for f in feats:
        if f['properties']['id'] in label_ids:
            pts = [P(*pt) for poly in polys(f) for pt in poly[0]]
            cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
            m = D['mapa'][f['properties']['id']]
            s = f"{f['properties']['name']} {p1(m[2])}"
            c.setFont('SB', 6.5); tw = c.stringWidth(s, 'SB', 6.5)
            c.setFillColor(Color(1, 1, 1, alpha=0.85)); c.roundRect(cx - tw / 2 - 2, cy - 3, tw + 4, 9, 2, fill=1, stroke=0)
            c.setFillColor(INK); c.drawCentredString(cx, cy - 0.5, s)
    # áreas de dica: rasteriza e junta células por linha
    gw, gh = int(w / cell) + 1, int(h / cell) + 1
    img = Image.new('I', (gw, gh), 0); dr = ImageDraw.Draw(img)
    for i, f in enumerate(feats):
        for poly in polys(f):
            pts = [((P(*pt)[0] - x0) / cell, (y0 + h - P(*pt)[1]) / cell) for pt in poly[0]]
            if len(pts) > 2: dr.polygon(pts, fill=i + 1)
    px = img.load()
    for r in range(gh):
        cstart, cur = 0, 0
        for col in range(gw + 1):
            v = px[col, r] if col < gw else 0
            if v != cur:
                if cur:
                    f = feats[cur - 1]; m = D['mapa'].get(f['properties']['id'])
                    nm = f['properties']['name']; v26 = m[1] if m else 0
                    t = f"{nm}: {fmt(v26)} voto{'s' if v26 != 1 else ''}" + (f" ({pct(m[2])} dos válidos, {m[3]}º lugar na cidade)" if v26 else '')
                    tip(x0 + cstart * cell, y0 + h - (r + 1) * cell, (col - cstart) * cell, cell, t)
                cur, cstart = v, col

def legend(y):
    x = M
    for i, t in enumerate(['sem dados', 'menos de 40%', '40 a 50%', '50 a 60%', '60 a 70%', '70% ou mais']):
        c.setFillColor(BINS[i]); c.rect(x, y, 12, 8, fill=1, stroke=0)
        c.setFillColor(INK2); c.setFont('R', 8); c.drawString(x + 16, y + 1, t); x += 22 + c.stringWidth(t, 'R', 8) + 10
    c.drawString(x + 4, y + 1, 'dos votos válidos')

# ---------- barras ----------
def bars(x, y, w, items, row=12, lw=110, vmax=None, log=False, vw=70, fs=8):
    vmax = vmax or max(i['v'] for i in items)
    bw = w - lw - vw - 6
    def L(v):
        if log: return max(2, math.log10(v / 0.7) / math.log10(vmax * 1.05 / 0.7) * bw)
        return max(2, v / vmax * bw)
    for it in items:
        if it.get('cut'):
            c.setStrokeColor(DOWN); c.setDash(3, 2); c.setLineWidth(0.8); c.line(x, y + 2, x + w, y + 2); c.setDash()
            c.setFont('R', 7); c.setFillColor(DOWN); c.drawRightString(x + w, y + 4, it['cut']); y -= 10
        hl = it.get('hl')
        c.setFont('B' if hl else 'R', fs); c.setFillColor(INK if hl else INK2)
        lb = it['lb']
        while c.stringWidth(lb, 'B' if hl else 'R', fs) > lw - 4: lb = lb[:-2] + '…' if not lb.endswith('…') else lb[:-2] + '…'
        c.drawString(x, y, lb)
        c.setFillColor(GRAY if it.get('dim') else ACC)
        bl = L(it['v']); c.rect(x + lw, y - 1.5, bl, row * 0.62, fill=1, stroke=0)
        c.setFont('SB', fs - 0.5); c.setFillColor(INK); c.drawString(x + lw + bl + 4, y, fmt(it['v']) + ('  ' if it.get('x') else ''))
        if it.get('x'):
            off = c.stringWidth(fmt(it['v']) + '  ', 'SB', fs - 0.5)
            c.setFont('R', fs - 1); c.setFillColor(MUTED); c.drawString(x + lw + bl + 4 + off, y, it['x'])
        tip(x, y - row * 0.3, w, row, it['tip'])
        y -= row
    return y

# ---------- rodapé do autor ----------
FOTO = RAIZ / 'img' / 'leo.jpg'
def autor(y):
    """Cartão "Quem desenvolveu?" com foto redonda; abre página nova se não couber."""
    larg = CW - 132
    cargo = simpleSplit('Bacharelado em Administração e Desenvolvimento de Sistemas, com mais de 20 anos de experiência na área.', 'SB', 8.8, larg)
    p1 = simpleSplit('Procurei desenvolver um relatório baseado nos dados do TSE, mostrando o panorama político do candidato para o mesmo entender os dados consolidados e gerar conhecimento agregado da campanha atual.', 'R', 8.8, larg)
    p2 = simpleSplit('Com ajuda da inteligência artificial (AI) nos mapas e gráficos, obtendo uma compreensão visual mais detalhada.', 'R', 8.8, larg)
    alt = 34 + 22 + len(cargo) * 12 + 6 + (len(p1) + len(p2)) * 12.5 + 6 + 8 + 26
    if y - alt < 50:
        footer(); c.showPage(); y = H - 50
        y = head(y, 'Sobre o relatório', 'Quem desenvolveu este relatório') - 6
    topo = y; base = y - alt
    c.setStrokeColor(LINE); c.setFillColor(HexColor('#ffffff')); c.setLineWidth(0.8); c.roundRect(M, base, CW, alt, 10, fill=1, stroke=1)
    cx, cy, r = M + 62, topo - 64, 44
    c.setFillColor(ACCS); c.circle(cx, cy, r + 4, fill=1, stroke=0)
    c.saveState(); p = c.beginPath(); p.circle(cx, cy, r); c.clipPath(p, stroke=0, fill=0)
    c.drawImage(str(FOTO), cx - r, cy - r, 2 * r, 2 * r); c.restoreState()
    x = M + 124; yy = topo - 24
    text(x, yy, 'QUEM DESENVOLVEU?', 'SB', 7.5, ACC); yy -= 22
    text(x, yy, 'Léo Ansélmo', 'B', 16, INK); yy -= 16
    for l in cargo: text(x, yy, l, 'SB', 8.8, ACC); yy -= 12
    yy -= 6
    for l in p1: text(x, yy, l, 'R', 8.8, INK2); yy -= 12.5
    yy -= 6
    for l in p2: text(x, yy, l, 'R', 8.8, INK2); yy -= 12.5
    yy -= 8
    s = 'Instagram: @leonardoanselmo79'; c.setFont('SB', 8.8); tw = c.stringWidth(s, 'SB', 8.8)
    c.setStrokeColor(LINE); c.setFillColor(HexColor('#f5f6f3')); c.roundRect(x, yy - 6, tw + 20, 18, 9, fill=1, stroke=1)
    c.setFillColor(ACC); c.drawString(x + 10, yy, s)
    c.linkURL('https://www.instagram.com/leonardoanselmo79/', (x, yy - 6, x + tw + 20, yy + 12), relative=0)
    tip(x, yy - 6, tw + 20, 18, 'Abrir o Instagram de Léo Ansélmo: https://www.instagram.com/leonardoanselmo79/')
    return base - 10

# ================= PÁGINA 1 =================
EU = '55'; BASE = 'CARUARU'
O = D['oficial']; R = O['resumo']; ELA = O['ela']; TOT = ELA['v']; SEG = next(x for x in O['lista'] if x['n'] != EU)
B = D['base']; X = D['perda']; T = X['tot']; CP = D['comp']; C2 = CP['comp']
VENCEU = sum(1 for m in D['mun'] if m[3] == 1)
p1 = lambda v: f'{v:.1f}'.replace('.', ',') + '%'
def pp(v): return ('+' if v > 0 else '-' if v < 0 else '') + f'{abs(v):.1f}'.replace('.', ',') + ' p.p.'
y = H - 50
text(M, y, 'ELEIÇÕES 2026 · PERNAMBUCO · GOVERNADORA · 1º TURNO, 04/10/2026', 'SB', 7.5, MUTED)
y -= 34; c.setFont('B', 30); c.setFillColor(INK); c.drawString(M, y, 'Raquel Lyra'); c.setFillColor(ACC); c.drawString(M + c.stringWidth('Raquel Lyra ', 'B', 30), y, '55')
y -= 20; y = text(M, y, f"Reeleita governadora no 1º turno com {fmt(TOT)} votos ({pct(ELA['pct'])} dos válidos). Para onde foram os votos: o mapa por município, a trajetória desde 2010, o que mudou em relação a 2022, Caruaru, a capital Recife e cada seção eleitoral.", 'R', 11, INK2, CW, 15)
y -= 14
K = [('Votos em Pernambuco', fmt(TOT), f"{pct(ELA['pct'])} dos válidos · 1º turno", f"Raquel Lyra (PSD, 55) teve {fmt(TOT)} votos, {pct(ELA['pct'])} dos válidos, e foi reeleita no 1º turno."),
     ('Municípios em que venceu', f"{VENCEU} de {len(D['mun'])}", f"nos outros {len(D['mun']) - VENCEU}, {title(SEG['nm'])} à frente", f"Ela foi a mais votada em {VENCEU} dos {len(D['mun'])} municípios de Pernambuco."),
     ('Vantagem sobre João Campos', fmt(TOT - SEG['v']), f"votos · {p1(ELA['pct'] - SEG['pct']).replace('%', ' pontos')} à frente", f"{title(SEG['nm'])} ({SEG['sg']}) teve {fmt(SEG['v'])} votos ({pct(SEG['pct'])})."),
     ('Acima da maioria absoluta', fmt(R['acima']), 'votos além do necessário', f"Para vencer no 1º turno eram necessários {fmt(R['limite'])} votos (mais da metade dos {fmt(R['validos'])} válidos).")]
kw = (CW - 3 * 8) / 4
for i, (a, b, s, t) in enumerate(K):
    x = M + i * (kw + 8)
    c.setStrokeColor(LINE); c.setFillColor(HexColor('#ffffff')); c.setLineWidth(0.8); c.roundRect(x, y - 58, kw, 58, 5, fill=1, stroke=1)
    text(x + 9, y - 14, a, 'R', 8, INK2); text(x + 9, y - 36, b, 'B', 17, INK); text(x + 9, y - 50, s, 'R', 6.6, MUTED)
    tip(x, y - 58, kw, 58, t)
y -= 80
y = head(y, '1 · Mapa', f"Venceu em {VENCEU} dos {len(D['mun'])} municípios", 'Cor pelo percentual dos votos válidos que ela teve em cada município. Fernando de Noronha não aparece no mapa.')
y = hint(y)
legend(y - 8); y -= 18
feats = [f for f in GEO['features'] if f['properties']['id'] != '2605459']
mh = 215
draw_map(M, y - mh, CW, mh, (-41.40, -9.50, -34.80, -7.25), feats, cell=2.0)
y -= mh + 14
text(M, y, 'A Região Metropolitana e o Agreste, ampliados, estão na página seguinte.', 'R', 8.5, INK2)
footer(); c.showPage()

# ================= PÁGINA 2: zoom =================
y = H - 50
y = head(y, '1 · Mapa ampliado', 'Região Metropolitana do Recife, Zona da Mata e Agreste', 'Os rótulos mostram os municípios com mais de 40 mil votos para ela; os demais aparecem ao passar o mouse.')
y = hint(y); legend(y - 8); y -= 20
BB = (-36.45, -8.95, -34.80, -7.45)
lab = {k for k, v in D['mapa'].items() if v[1] >= 40000}
mh = 480
draw_map(M, y - mh, CW, mh, BB, feats, label_ids=lab, cell=2.5)
footer(); c.showPage()

# ================= PÁGINAS 3 e 4: municípios =================
items = [dict(lb=title(nm), v=v, x=f"{pct(p)} · {pos}º", hl=nm == BASE, dim=pos != 1,
              tip=f"{title(nm)}: {fmt(v)} votos, {pct(p)} dos válidos, {pos}º lugar · {'2º colocado' if pos == 1 else 'mais votado'}: {title(o)} ({osg}, {pct(op)})")
         for nm, v, p, pos, o, osg, op in D['mun']]
vmax = D['mun'][0][1]
for n, parte in enumerate([items[:106], items[106:]]):
    y = H - 50
    if n == 0:
        y = head(y, '2 · Por município', f"Votos nos {len(items)} municípios: venceu em {VENCEU}", 'Escala logarítmica: cada marca vale 10 vezes a anterior. Ao lado de cada barra: votos, % dos válidos e a posição dela na cidade. Barras cinzas: municípios em que ela ficou em 2º.')
    else:
        y = head(y, '2 · Por município (continuação)', f"Do 107º ao {len(items)}º município")
    y = hint(y) - 6
    half = (len(parte) + 1) // 2; colw = (CW - 16) / 2
    bars(M, y, colw, parte[:half], row=11.6, lw=92, vmax=vmax, log=True, vw=80, fs=7.1)
    bars(M + colw + 16, y, colw, parte[half:], row=11.6, lw=92, vmax=vmax, log=True, vw=80, fs=7.1)
    footer(); c.showPage()

# ================= PÁGINA 5: trajetória e 2022 x 2026 =================
EL = D['traj']['eleicoes']
cargo = lambda e: 'Prefeita' if e['cargo'] == 'Prefeito' else 'Governadora' if e['cargo'] == 'Governador' else 'Deputada estadual'
res = lambda e: 'foi ao 2º turno' if '2º TURNO' in e['situacao'] else 'eleita' if 'ELEIT' in e['situacao'] else e['situacao'].lower()
y = H - 50
y = head(y, '3 · Trajetória', 'Seis eleições vencidas desde 2010: deputada, prefeita e governadora',
         'Raquel Lyra foi eleita deputada estadual em 2010 e 2014 (PSB), prefeita de Caruaru em 2016 e 2020 (PSDB) e governadora em 2022 (PSDB). Em 2026, já pelo PSD, foi reeleita no 1º turno. Percentual dos votos nominais válidos da disputa de cada ano (no estado; em Caruaru para prefeita).')
y = hint(y) - 4
cols = [('Ano', 0, 34), ('Cargo', 34, 150), ('Onde', 184, 80), ('Partido e número', 264, 90), ('Votos', 354, 70), ('% válidos', 424, 50), ('Resultado', 484, CW - 484)]
c.setFont('SB', 7.8); c.setFillColor(INK2)
for nm, x, w in cols: (c.drawRightString if nm in ('Votos', '% válidos') else c.drawString)(M + x + (w if nm in ('Votos', '% válidos') else 0), y, nm)
y -= 5; c.setStrokeColor(INK); c.setLineWidth(0.8); c.line(M, y, W - M, y); y -= 12
for i, e in enumerate(EL):
    if i % 2 == 0: c.setFillColor(HexColor('#f5f6f3')); c.rect(M, y - 3.5, CW, 13.6, fill=1, stroke=0)
    vals = [str(e['ano']), cargo(e) + (' · 2º turno' if e['turno'] == 2 else ''), e['onde'], f"{e['partido']} {e['numero']}", fmt(e['votos']), pct(e['pct']) if e['pct'] is not None else '', res(e)]
    for (nm, x, w), v in zip(cols, vals):
        c.setFont('SB' if e['ano'] == 2026 else 'R', 7.8); c.setFillColor(INK)
        (c.drawRightString if nm in ('Votos', '% válidos') else c.drawString)(M + x + (w if nm in ('Votos', '% válidos') else 0), y, v)
    tip(M, y - 3.5, CW, 13.6, f"{e['ano']}: {cargo(e)}{' (2º turno)' if e['turno'] == 2 else ''} em {e['onde']}, {e['partido']} {e['numero']}, {fmt(e['votos'])} votos, {res(e)}")
    y -= 13.6
y -= 22
T22 = CP['tot22']; subiu = sum(1 for r in C2 if r[6] > r[4])
y = head(y, '4 · 2022 × 2026', f"Do 2º turno de 2022 para 2026: subiu em {subiu} municípios e caiu em {len(C2) - subiu}",
         f"Em 2022 ela teve {pct(T22['1']['pct'])} dos válidos no 1º turno e {pct(T22['2']['pct'])} no 2º turno. Em 2026 venceu já no 1º turno, com {pct(ELA['pct'])}. Comparação com o 2º turno de 2022, a votação que a elegeu. Escala de 0% a 100% dos válidos.")
c.setFillColor(GRAY); c.circle(M + 4, y + 3, 3.2, fill=1, stroke=0); text(M + 11, y, '2022, 2º turno', 'R', 8, INK2)
c.setFillColor(ACC); c.circle(M + 88, y + 3, 3.2, fill=1, stroke=0); text(M + 95, y, '2026', 'R', 8, INK2)
text(M + 135, y, 'Coluna da direita: variação em pontos percentuais', 'R', 8, INK2); y -= 18
lw = 140; tw = CW - lw - 60
for r in C2[:22]:
    nm, a, b_ = r[0], r[4], r[6]; d = b_ - a
    c.setFont('R', 8.1); c.setFillColor(INK2); c.drawString(M, y, title(nm))
    x1 = M + lw + a / 100 * tw; x2 = M + lw + b_ / 100 * tw
    c.setStrokeColor(LINE); c.setLineWidth(1.6); c.line(M + lw, y + 2.5, M + lw + tw, y + 2.5)
    c.setStrokeColor(HexColor('#c9ced2')); c.setLineWidth(2.2); c.line(min(x1, x2), y + 2.5, max(x1, x2), y + 2.5)
    c.setFillColor(GRAY); c.circle(x1, y + 2.5, 3.2, fill=1, stroke=0)
    c.setFillColor(ACC); c.circle(x2, y + 2.5, 3.2, fill=1, stroke=0)
    c.setFont('SB', 7.8); c.setFillColor(UP if d > 0 else DOWN); c.drawRightString(W - M, y, pp(d))
    tip(M, y - 4, CW, 14, f"{title(nm)}: {pct(a)} no 2º turno de 2022 ({fmt(r[3])} votos) · {pct(b_)} em 2026 ({fmt(r[5])} votos)")
    y -= 14.5
footer(); c.showPage()

# ================= PÁGINA 6: maiores variações =================
ordv = sorted(C2, key=lambda r: (r[6] - r[4]))
y = H - 50
y = head(y, '4 · 2022 × 2026 (continuação)', 'Onde ela mais cresceu e onde mais caiu', 'Variação do percentual dos válidos, do 2º turno de 2022 para o 1º turno de 2026. A tabela completa, com o 1º turno de 2022, está no site.')
y = hint(y) - 4
colw = (CW - 20) / 2
for j, (ttl, lst, cor) in enumerate([('Onde mais cresceu', ordv[::-1][:20], UP), ('Onde mais caiu', ordv[:20], DOWN)]):
    x = M + j * (colw + 20); yy = y
    text(x, yy, ttl, 'B', 10); yy -= 15
    for r in lst:
        c.setFont('R', 8.1); c.setFillColor(INK2); c.drawString(x, yy, title(r[0]))
        c.setFont('SB', 8.1); c.setFillColor(cor); c.drawRightString(x + colw, yy, f"{p1(r[4])} → {p1(r[6])}")
        tip(x, yy - 3, colw, 12, f"{title(r[0])}: {pct(r[4])} no 2º turno de 2022 → {pct(r[6])} em 2026 ({pp(r[6] - r[4])})")
        yy -= 13
footer(); c.showPage()

# ================= PÁGINA 7: Caruaru =================
def short(n):
    p = n.split(); suf = p[-1] in ('NETO', 'FILHO', 'JUNIOR', 'JÚNIOR')
    return title(' '.join([p[0]] + p[-2:] if suf else [p[0], p[-1]]))
car = next(m for m in D['mun'] if m[0] == BASE); c22 = next(r for r in C2 if r[0] == BASE)
y = H - 50
y = head(y, '5 · Caruaru', f"Em Caruaru, onde foi prefeita, {pct(car[2])} dos votos",
         f"Raquel Lyra governou Caruaru de 2017 a 2022. Em 2026 teve {fmt(B['top'][0]['v'])} votos na cidade ({pct(B['top'][0]['p'])} dos válidos), contra {pct(B['top'][1]['p'])} de {short(B['top'][1]['nm'])}. No 2º turno de 2022 ela tinha {pct(c22[4])}. Dados por seção do TSE ({sum(l['secoes'] for l in B['locais'])} seções, {len(B['locais'])} locais de votação).")
y = hint(y) - 4
text(M, y, 'Votos para governador em Caruaru', 'B', 10); y -= 16
it = [dict(lb=f"{short(t['nm'])} {t['n']}", v=t['v'], x=pct(t['p']), hl=t['n'] == EU, dim=t['n'] != EU,
           tip=f"{title(t['nm'])} ({t['n']}): {fmt(t['v'])} votos em Caruaru, {pct(t['p'])} dos válidos") for t in B['top'][:7]]
y = bars(M, y, CW, it, row=14, lw=170, vmax=B['top'][0]['v'], fs=8.5)
text(M, y - 2, f"Válidos para governador na cidade: {fmt(B['validos'])}. Brancos: {fmt(B['brancos'])}. Nulos: {fmt(B['nulos'])}.", 'R', 7.5, MUTED); y -= 24
text(M, y, 'Votos de Raquel por bairro do local de votação (15 com mais votos)', 'B', 10); y -= 16
it = [dict(lb=title(b[0]), v=b[1], x=pct(b[3]) + ' dos válidos', tip=f"{title(b[0])}: {fmt(b[1])} votos de Raquel, {pct(b[3])} dos {fmt(b[2])} válidos") for b in B['bairros'][:15]]
y = bars(M, y, CW, it, row=13, lw=170, fs=8.2) - 14
text(M, y, 'Os 15 locais de votação com mais votos', 'B', 10); y -= 14
cols = [('Local de votação', 0, 220), ('Bairro', 220, 120), ('Seções', 340, 40), ('Votos', 380, 50), ('Válidos', 430, 50), ('% válidos', 480, CW - 480)]
c.setFont('SB', 8); c.setFillColor(INK2)
for nm, x, w in cols: (c.drawString if x < 340 else c.drawRightString)(M + x + (0 if x < 340 else w), y, nm)
y -= 5; c.setStrokeColor(INK); c.setLineWidth(0.8); c.line(M, y, W - M, y); y -= 11
for i, l in enumerate(B['locais'][:15]):
    if i % 2 == 0: c.setFillColor(HexColor('#f5f6f3')); c.rect(M, y - 3.5, CW, 12.6, fill=1, stroke=0)
    vals = [title(l['local']), title(l['bairro']), str(l['secoes']), fmt(l['votos']), fmt(l['validos']), pct(l['pct'])]
    for (nm, x, w), v in zip(cols, vals):
        if x < 340:
            c.setFont('R', 7.3); c.setFillColor(INK)
            while c.stringWidth(v, 'R', 7.3) > w - 6: v = v[:-2] + '…'
            c.drawString(M + x, y, v)
        else:
            c.setFont('SB' if nm == 'Votos' else 'R', 7.5); c.setFillColor(INK); c.drawRightString(M + x + w, y, v)
    tip(M, y - 3.5, CW, 12.6, f"{title(l['local'])} ({title(l['bairro'])}): {fmt(l['votos'])} votos de Raquel em {l['secoes']} seções, {pct(l['pct'])} dos {fmt(l['validos'])} válidos")
    y -= 12.6
footer(); c.showPage()

# ================= PÁGINA 8: Recife 2022 x 2026 =================
CA = HexColor('#d9622b')
r22 = 100 * T['2022']['iz'] / T['2022']['val_iz']; r26 = 100 * T['2026']['iz'] / T['2026']['val_iz']
a22 = 100 * T['2022']['ca'] / T['2022']['val_fed']; a26 = 100 * T['2026']['ca'] / T['2026']['val_fed']
virou = sum(1 for r in X['locais'] if r[9] > r[11] and r[10] < r[12])
y = H - 50
y = head(y, '6 · Recife, 2022 × 2026', 'Na capital, a vantagem de 2022 virou derrota',
         f"No 2º turno de 2022, Raquel teve {fmt(T['2022']['iz'])} votos em Recife ({pct(r22)} dos válidos) contra {fmt(T['2022']['ca'])} de Marília Arraes ({pct(a22)}). Em 2026 teve {fmt(T['2026']['iz'])} ({pct(r26)}), e João Campos, prefeito da cidade, teve {fmt(T['2026']['ca'])} ({pct(a26)}). Dos {len(X['locais'])} locais de votação que existiam nas duas eleições, ela venceu em 2022 e perdeu em 2026 em {virou}. Adversário: Marília Arraes em 2022, João Campos em 2026.")
y = hint(y) - 4
c.setFillColor(GRAY); c.circle(M + 4, y + 3, 3.2, fill=1, stroke=0); text(M + 11, y, '2022', 'R', 8, INK2)
c.setFillColor(ACC); c.circle(M + 48, y + 3, 3.2, fill=1, stroke=0); text(M + 55, y, 'Raquel 2026', 'R', 8, INK2)
c.setFillColor(CA); c.circle(M + 118, y + 3, 3.2, fill=1, stroke=0); text(M + 125, y, 'Adversário 2026', 'R', 8, INK2)
text(M + 210, y, 'Números: % dos válidos em 2022 → em 2026 · 20 bairros com mais votos', 'R', 8, INK2); y -= 20
Bs = sorted([b for b in X['bairros'] if b[1] + b[5] > 0 and b[2] + b[6] > 0], key=lambda b: -(b[2] + b[6]))[:20]  # bairros com votos nos dois anos
lw = 128; colw = (CW - lw - 16) / 2
text(M + lw, y, 'Raquel', 'B', 9.5); text(M + lw + colw + 16, y, 'Adversário', 'B', 9.5); y -= 15
for b in Bs:
    c.setFont('R', 8); c.setFillColor(INK2); c.drawString(M, y, title(b[0])[:26])
    for j, (a, z, cor, nm) in enumerate([(b[3], b[4], ACC, 'Raquel'), (b[7], b[8], CA, 'Adversário')]):
        x0 = M + lw + j * (colw + 16); X1 = x0 + a / 100 * colw * 0.72; X2 = x0 + z / 100 * colw * 0.72
        c.setStrokeColor(LINE); c.setLineWidth(1.4); c.line(x0, y + 2.5, x0 + colw * 0.72, y + 2.5)
        c.setStrokeColor(HexColor('#c9ced2')); c.setLineWidth(2.2); c.line(min(X1, X2), y + 2.5, max(X1, X2), y + 2.5)
        c.setFillColor(GRAY); c.circle(X1, y + 2.5, 3, fill=1, stroke=0)
        c.setFillColor(cor); c.circle(X2, y + 2.5, 3, fill=1, stroke=0)
        c.setFont('R', 6.8); c.setFillColor(INK2); c.drawString(max(X1, X2) + 6, y, p1(a) + ' → ' + p1(z))
        tip(x0, y - 4, colw, 14, f"{nm} em {title(b[0])}: {pct(a)} dos válidos em 2022, {pct(z)} em 2026")
    y -= 14.5
y -= 12
text(M, y, 'Os 15 locais de votação com mais eleitores', 'B', 10); y -= 13
cols = [('Local de votação', 0, 175), ('Raquel: votos', 175, 72), ('Raquel: % dos válidos', 247, 96), ('Adversário: votos', 343, 72), ('Adversário: %', 415, CW - 415)]
c.setFont('SB', 7.4); c.setFillColor(INK2)
for nm, x, w in cols: (c.drawString if x == 0 else c.drawRightString)(M + x + (0 if x == 0 else w), y, nm)
c.setFont('R', 6.8); c.setFillColor(MUTED)
for nm, x, w in cols[1:]: c.drawRightString(M + x + w, y - 9, '2022 → 2026')
y -= 14; c.setStrokeColor(INK); c.setLineWidth(0.8); c.line(M, y, W - M, y); y -= 11
for i, r in enumerate(sorted(X['locais'], key=lambda r: -(r[3] + r[5]))[:15]):
    if i % 2 == 0: c.setFillColor(HexColor('#f5f6f3')); c.rect(M, y - 3.5, CW, 12.4, fill=1, stroke=0)
    vals = [title(r[0]), f'{fmt(r[2])} → {fmt(r[3])}', f'{p1(r[9])} → {p1(r[10])}', f'{fmt(r[4])} → {fmt(r[5])}', f'{p1(r[11])} → {p1(r[12])}']
    for (nm, x, w), v in zip(cols, vals):
        c.setFont('SB' if '%' in nm else 'R', 7.1); c.setFillColor(DOWN if nm == 'Raquel: % dos válidos' else UP if nm == 'Adversário: %' else INK)
        if x == 0:
            while c.stringWidth(v, 'R', 7.1) > w - 6: v = v[:-2] + '…'
            c.drawString(M, y, v)
        else:
            c.drawRightString(M + x + w, y, v)
    tip(M, y - 3.5, CW, 12.4, f"{title(r[0])} ({title(r[1])}): Raquel {fmt(r[2])} → {fmt(r[3])} votos ({pct(r[9])} → {pct(r[10])}); adversário {fmt(r[4])} → {fmt(r[5])} ({pct(r[11])} → {pct(r[12])})")
    y -= 12.4
footer(); c.showPage()

# ================= PÁGINA 9: seções =================
S = D['secoes']
y = H - 50
y = head(y, '7 · Por seção eleitoral', f"{fmt(len(S))} seções; as 45 com mais votos para ela",
         f"Algumas seções pequenas não têm urna própria: os eleitores delas votam na urna de outra seção do mesmo local. O resultado sai só na seção que tem a urna (consolidada), com os eleitores das duas somados. Exemplo: em Brejão, a seção 452 (63 eleitores) votou na urna da 181 (272), que aparece com 335 aptos. {sum(1 for s in S if s[9])} seções são consolidadas. A lista completa está no site e em dados/raquel_lyra_55_por_secao.csv.")
y = hint(y) - 6
cols = [('Município', 0, 100), ('Zona', 100, 26), ('Seção', 126, 32), ('Local de votação', 168, 196), ('Aptos', 364, 40), ('Votos', 404, 40), ('Válidos', 444, 40), ('% válidos', 484, CW - 484)]
NUM = {'Zona', 'Seção', 'Aptos', 'Votos', 'Válidos', '% válidos'}
c.setFont('SB', 7.6); c.setFillColor(INK2)
for nm, x, w in cols: (c.drawRightString if nm in NUM else c.drawString)(M + x + (w if nm in NUM else 0), y, nm)
y -= 5; c.setStrokeColor(INK); c.setLineWidth(0.8); c.line(M, y, W - M, y); y -= 11
for i, s in enumerate(S[:45]):
    if i % 2 == 0: c.setFillColor(HexColor('#f5f6f3')); c.rect(M, y - 3.5, CW, 12.6, fill=1, stroke=0)
    vals = [title(s[0]), str(s[1]), str(s[2]), title(s[3]), fmt(s[5]), fmt(s[6]), fmt(s[7]), pct(s[8])]
    for (nm, x, w), v in zip(cols, vals):
        c.setFont('SB' if nm == 'Votos' else 'R', 7.2); c.setFillColor(INK)
        if nm in NUM: c.drawRightString(M + x + w, y, v)
        else:
            while c.stringWidth(v, 'R', 7.2) > w - 6: v = v[:-2] + '…'
            c.drawString(M + x, y, v)
    ag = f" · consolidada com as seções agregadas {s[9].replace(' ', ', ')}" if s[9] else ''
    tip(M, y - 3.5, CW, 12.6, f"{title(s[0])}, zona {s[1]}, seção {s[2]} ({title(s[3])}, {title(s[4])}): {fmt(s[6])} votos de Raquel, {pct(s[8])} dos {fmt(s[7])} válidos, {fmt(s[5])} eleitores aptos{ag}")
    y -= 12.6
footer(); c.showPage()

# ================= PÁGINA 10: resultado oficial =================
y = H - 50
y = head(y, '8 · Resultado oficial', f"Reeleita no 1º turno, com {fmt(R['acima'])} votos acima da maioria absoluta",
         f"Para vencer no 1º turno, era preciso ter mais da metade dos {fmt(R['validos'])} votos válidos, ou seja, pelo menos {fmt(R['limite'])}. Raquel Lyra teve {fmt(TOT)}. {title(SEG['nm'])} ({SEG['sg']}) ficou em 2º, com {fmt(SEG['v'])} votos ({pct(SEG['pct'])}). A vice na chapa de Raquel é {title(ELA['vice'])}.")
y = hint(y) - 4
text(M, y, 'Candidatos a governador', 'B', 10); y -= 16
it = [dict(lb=f"{title(k['nm'])} ({k['sg']})", v=k['v'], x=pct(k['pct']), hl=k['n'] == EU, dim=k['n'] != EU,
           tip=f"{title(k['nm'])} ({k['sg']}, {k['n']}), vice {title(k['vice'])}: {fmt(k['v'])} votos, {pct(k['pct'])} · {k['st']}") for k in O['lista']]
y = bars(M, y, CW, it, row=14, lw=190, fs=8.5) - 16
text(M, y, 'Eleitorado e votos', 'B', 10); y -= 16
ap = R['aptos']
it = [dict(lb=l, v=v, x=pct(100 * v / (ap if i < 3 else R['comparecimento'])) + (' do eleitorado' if i < 3 else ' do comparecimento'), dim=i != 3, tip=f"{l}: {fmt(v)}")
      for i, (l, v) in enumerate([('Eleitores aptos', ap), ('Compareceram', R['comparecimento']), ('Não compareceram', R['abstencao']), ('Votos válidos', R['validos']), ('Brancos', R['brancos']), ('Nulos', R['nulos'])])]
y = bars(M, y, CW, it, row=14, lw=190, fs=8.5, vw=130) - 10
y = text(M, y, 'Resultado proclamado pelo TSE.', 'R', 8, MUTED) - 14
text(M, y, 'Fontes', 'B', 10); y -= 14
y = text(M, y, 'API de resultados do TSE (votos por município e resultado oficial, 2026): resultados.tse.jus.br/oficial/ele2026/6259/dados/pe/. Portal de Dados Abertos do TSE (dadosabertos.tse.jus.br): votação por município de 2010 a 2022; votação por seção e locais de votação de 2022 e 2026. Contornos dos municípios: geodata-br, a partir de malhas do IBGE.', 'R', 8.5, INK2, CW, 12)
y = autor(y - 14)
footer(); c.showPage()
c.save()
print('páginas:', PAGE[0], '· campos de dica:', NT[0])
