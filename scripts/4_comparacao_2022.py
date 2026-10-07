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
with open(csv22, encoding='latin-1') as f:
    for r in csv.DictReader(f, delimiter=';'):
        if r['CD_CARGO'] != '3':
            continue
        t, m, q = r['NR_TURNO'], r['NM_MUNICIPIO'], int(r['QT_VOTOS_NOMINAIS_VALIDOS'] or 0)
        validos[t][m] += q
        if r['NR_CANDIDATO'] == '45':
            ela[t][m] += q


def pct(v, t):
    return round(100 * v / t, 2) if t else 0.0


comp = []
for m26 in ler_json('municipios.json'):
    m = m26['nome']
    comp.append([m, ela['1'][m], pct(ela['1'][m], validos['1'][m]), ela['2'][m], pct(ela['2'][m], validos['2'][m]),
                 m26['votos'], m26['pct']])
comp.sort(key=lambda r: -r[5])
tot = {t: dict(votos=sum(ela[t].values()), validos=sum(validos[t].values())) for t in ('1', '2')}
for t in tot:
    tot[t]['pct'] = pct(tot[t]['votos'], tot[t]['validos'])
print('2022:', tot)
print('municípios onde a % subiu em relação ao 2º turno de 2022:', sum(1 for r in comp if r[6] > r[4]), 'de', len(comp))
salvar_json(dict(tot22=tot, comp=comp), 'comparacao_2022.json')
