"""Trajetória eleitoral de Raquel Lyra, de 2010 a 2026.

Ela disputou deputada estadual (2010 e 2014, PSB 40789), prefeita de Caruaru (2016 e 2020, PSDB 45) e
governadora (2022, PSDB 45; 2026, PSD 55). Os cargos são diferentes, então a trajetória mostra votos e
o percentual dos votos nominais válidos na disputa de cada ano (no estado, ou em Caruaru para prefeita).

As candidaturas são achadas pelo começo do nome (RAQUEL TEIXEIRA LYRA; a partir de 2020 o nome
termina com LUCENA). Para 2010 a 2020, lê só o arquivo de Pernambuco de dentro do zip nacional do TSE
(votacao_candidato_munzona_AAAA.zip), por leitura parcial via HTTP, e guarda em brutos/hist/. 2022 vem
do passo 4 e 2026 do passo 2.

Saída: dados/trajetoria.json
"""
import collections as C
import csv

from comum import BRUTOS, CDN, NOME_PREFIXO, ler_json, salvar_json
from remotezip import extrair

ANOS = [2010, 2014, 2016, 2020, 2022]


def arquivo(ano):
    if ano == 2022:
        return BRUTOS / 'votacao_candidato_munzona_2022_PE.csv'
    destino = BRUTOS / 'hist' / f'munzona_{ano}_PE.csv'
    if not destino.exists():
        destino.parent.mkdir(exist_ok=True)
        print(f'lendo o trecho de PE do arquivo de {ano}')
        extrair(f'{CDN}/votacao_candidato_munzona/votacao_candidato_munzona_{ano}.zip',
                lambda n: n.upper().endswith('_PE.CSV'), destino)
    return destino


eleicoes = []
for ano in ANOS:
    dela, total, info = C.Counter(), C.Counter(), {}
    with open(arquivo(ano), encoding='latin-1') as f:
        for r in csv.DictReader(f, delimiter=';'):
            if r['NM_CANDIDATO'].startswith(NOME_PREFIXO):
                chave = (r['NR_TURNO'], r['CD_CARGO'], r['SG_UE'] if r['TP_ABRANGENCIA'] == 'M' else 'PE')  # eleição estadual vem separada por município em 2010
                dela[chave] += int(r['QT_VOTOS_NOMINAIS'] or 0)
                info[chave] = dict(ano=ano, turno=int(r['NR_TURNO']), cargo=r['DS_CARGO'], numero=r['NR_CANDIDATO'],
                                   partido=r['SG_PARTIDO'], situacao=r['DS_SIT_TOT_TURNO'],
                                   onde='Pernambuco' if r['TP_ABRANGENCIA'] != 'M' else r['NM_UE'].title())
    if not dela:
        print(ano, 'sem candidatura')
        continue
    with open(arquivo(ano), encoding='latin-1') as f:
        for r in csv.DictReader(f, delimiter=';'):
            chave = (r['NR_TURNO'], r['CD_CARGO'], r['SG_UE'] if r['TP_ABRANGENCIA'] == 'M' else 'PE')  # eleição estadual vem separada por município em 2010
            if chave in dela:
                total[chave] += int(r.get('QT_VOTOS_NOMINAIS_VALIDOS') or r['QT_VOTOS_NOMINAIS'] or 0)
    for chave in sorted(dela):
        e = info[chave]
        e.update(votos=dela[chave], pct=round(100 * dela[chave] / total[chave], 2) if total[chave] else None)
        eleicoes.append(e)
        print(e)

of = ler_json('resultado_oficial.json')['ela']
eleicoes.append(dict(ano=2026, turno=1, cargo='Governador', numero=of['n'], partido=of['sg'], situacao=of['st'].upper(),
                     onde='Pernambuco', votos=of['v'], pct=of['pct']))
salvar_json(dict(eleicoes=eleicoes), 'trajetoria.json')
