"""Compara 2026 com 2022, município a município, na disputa para governador.

Em 2022 Raquel Lyra (PSDB, 45) ficou em 2º no 1º turno e venceu o 2º turno contra Marília Arraes.
Em 2026 (PSD, 55) venceu no 1º turno. Como a quantidade de eleitores muda entre as cidades e os anos,
a comparação principal é pelo percentual dos votos válidos em cada município. Para governador, todo
voto válido é nominal, então os válidos do município são a soma dos votos de todos os candidatos.

Baixa votacao_candidato_munzona_2022.zip (~640 MB, todos os estados) para brutos/ e extrai só PE.
Entradas: dados/municipios.json (passo 1). Saída: dados/comparacao_2022.json
"""
import collections as C
import csv
import zipfile

from comum import BRUTOS, CDN, baixar, ler_json, salvar_json

csv22 = BRUTOS / 'votacao_candidato_munzona_2022_PE.csv'
if not csv22.exists():
    z = baixar(f'{CDN}/votacao_candidato_munzona/votacao_candidato_munzona_2022.zip', BRUTOS / 'votacao_candidato_munzona_2022.zip')
    with zipfile.ZipFile(z) as zf:
        zf.extract(csv22.name, BRUTOS)

ela = {t: C.Counter() for t in ('1', '2')}
validos = {t: C.Counter() for t in ('1', '2')}
todos = {t: C.defaultdict(C.Counter) for t in ('1', '2')}   # votos de cada candidato por município
nomes = {}
with open(csv22, encoding='latin-1') as f:
    for r in csv.DictReader(f, delimiter=';'):
        if r['CD_CARGO'] != '3':
            continue
        t, m, q = r['NR_TURNO'], r['NM_MUNICIPIO'], int(r['QT_VOTOS_NOMINAIS_VALIDOS'] or 0)
        validos[t][m] += q
        todos[t][m][r['NR_CANDIDATO']] += q
        nomes[r['NR_CANDIDATO']] = r['NM_URNA_CANDIDATO']
        if r['NR_CANDIDATO'] == '45':
            ela[t][m] += q


def pct(v, t):
    return round(100 * v / t, 2) if t else 0.0


def vencedor(t, m):
    n, v = todos[t][m].most_common(1)[0]
    return nomes[n], pct(v, validos[t][m])


comp = []
for m26 in ler_json('municipios.json'):
    m = m26['nome']
    pos1 = 1 + sum(1 for n, v in todos['1'][m].items() if v > ela['1'][m])
    v2, p2v = vencedor('2', m)
    # [município, votos e % no 1º turno de 2022, votos e % no 2º turno de 2022, votos e % em 2026,
    #  posição no 1º turno de 2022, vencedor do 2º turno de 2022, posição em 2026, adversário em 2026 (líder ou 2º)]
    comp.append([m, ela['1'][m], pct(ela['1'][m], validos['1'][m]), ela['2'][m], pct(ela['2'][m], validos['2'][m]),
                 m26['votos'], m26['pct'], pos1, v2, m26['pos'], m26['outro']])
comp.sort(key=lambda r: -r[5])
tot = {t: dict(votos=sum(ela[t].values()), validos=sum(validos[t].values())) for t in ('1', '2')}
for t in tot:
    tot[t]['pct'] = pct(tot[t]['votos'], tot[t]['validos'])
print('2022:', tot)
print('municípios onde a % subiu em relação ao 2º turno de 2022:', sum(1 for r in comp if r[6] > r[4]), 'de', len(comp))
v22 = {r[0] for r in comp if r[4] > 50}; v26 = {r[0] for r in comp if r[9] == 1}; v1 = {r[0] for r in comp if r[7] == 1}
print(f'venceu: 1º turno 2022 {len(v1)}, 2º turno 2022 {len(v22)}, 2026 {len(v26)}; nas duas {len(v22 & v26)},',
      f'passou a vencer {len(v26 - v22)}, deixou de vencer {len(v22 - v26)}, perdeu nas duas {len(comp) - len(v22 | v26)}')
salvar_json(dict(tot22=tot, comp=comp), 'comparacao_2022.json')
