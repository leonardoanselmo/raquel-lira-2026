"""Resultado oficial de governador em PE: todos os candidatos, comparecimento e a margem sobre os 50%.

Para vencer no 1º turno, a candidata precisa de mais da metade dos votos válidos. O script calcula
quantos votos ela teve acima desse limite.

Entrada: dados/resultado_estado.json (passo 1). Saída: dados/resultado_oficial.json
"""
from comum import CANDIDATO, candidatos, ler_json, salvar_json

estado = ler_json('resultado_estado.json')
ints = lambda s: int(s)
lista = []
for k, p, a in candidatos(estado):
    lista.append(dict(n=k['n'], nm=k['nmu'], sg=p['sg'], colig=a['nm'], v=int(k['vap']), pct=float(k['pvap'].replace(',', '.')),
                      e=k['e'] == 's', st=k['st'], vice=', '.join(v['nmu'] for v in k.get('vs', []))))
lista.sort(key=lambda x: -x['v'])
ela = next(x for x in lista if x['n'] == CANDIDATO)
v, e = estado['v'], estado['e']
validos = ints(v['vv'])
limite = validos // 2 + 1                     # maioria absoluta dos válidos
resumo = dict(aptos=ints(e['te']), comparecimento=ints(e['c']), abstencao=ints(e['a']), validos=validos,
              brancos=ints(v['vb']), nulos=ints(v['tvn']), limite=limite, acima=ela['v'] - limite + 1,
              turno_decidido=any(x['e'] for x in lista))
print(f"{ela['nm']}: {ela['v']} votos ({ela['pct']}%), {ela['st']}; votos acima da maioria absoluta: {resumo['acima']}")
print(f"comparecimento {resumo['comparecimento']} de {resumo['aptos']}; válidos {validos}, brancos {resumo['brancos']}, nulos {resumo['nulos']}")
salvar_json(dict(lista=lista, ela=ela, resumo=resumo), 'resultado_oficial.json')
