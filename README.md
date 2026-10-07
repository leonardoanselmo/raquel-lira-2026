# Raquel Lyra 55 em 2026

Para onde foram os votos de Raquel Lyra (Raquel Teixeira Lyra Lucena, PSD, número 55) para governadora de Pernambuco, no 1º turno de 04/10/2026.

**Site:** https://leonardoanselmo.github.io/raquel-lira-2026/
**PDF:** [relatorio/Raquel_Lyra_55_2026.pdf](relatorio/Raquel_Lyra_55_2026.pdf)

Resultado proclamado pelo TSE: **reeleita no 1º turno** com 2.805.438 votos (53,27% dos válidos), 172.012 votos acima da maioria absoluta. João Campos (PSB, 40) ficou em 2º, com 44,82%.

O relatório tem:
- mapa de Pernambuco com o percentual dela em cada município;
- os 185 municípios, com a posição dela e quem disputou a ponta;
- trajetória de 2010 a 2026: deputada estadual, prefeita de Caruaru e governadora;
- 2022 × 2026 por município (1º e 2º turno de 2022 contra 2026);
- Caruaru, onde ela foi prefeita, por bairro e por local de votação;
- Recife 2022 × 2026: a capital, onde a vantagem de 2022 virou derrota, com mapa dos locais de votação;
- votos em cada seção eleitoral de PE, sem misturar as seções agregadas;
- resultado oficial, comparecimento e votos válidos.

## Estrutura

| Pasta / arquivo | Conteúdo |
|---|---|
| `index.html` | O site publicado no GitHub Pages (gerado pelo passo 6) |
| `scripts/` | Coleta e análise, numeradas na ordem em que rodam |
| `scripts/comum.py` | Parâmetros (número, cargo, Caruaru, Recife, adversário) e funções compartilhadas |
| `scripts/template.html` | Modelo da página. Os dados são inseridos no passo 6 |
| `dados/` | Resultados que alimentam o site e o PDF |
| `relatorio/` | Versão em PDF (gerada pelo passo 7) |
| `brutos/` | Downloads grandes do TSE (fora do Git, criados pelos scripts) |

## Como atualizar

Requer Python 3.10 ou mais novo. Os passos 1 a 6 usam só a biblioteca padrão.

```bash
cd scripts
python 1_coleta_municipios.py   # API do TSE: votos, % e posição da 55 nos 185 municípios
python 2_resultado_oficial.py   # todos os candidatos, comparecimento e margem sobre os 50%
python 3_base_secoes.py         # Caruaru por local de votação e bairro (~280 MB na 1ª vez)
python 3b_votos_por_secao.py    # votos da 55 em cada seção de PE (mesmos downloads do passo 3)
python 3c_perdas_2022.py        # Recife: 2º turno de 2022 x 1º turno de 2026 (~150 MB de 2022)
python 4_comparacao_2022.py     # 2022 x 2026 por município (~640 MB na 1ª vez)
python 4b_trajetoria.py         # trajetória 2010-2026 (lê só o trecho de PE dos arquivos antigos)
python 5_mapa.py                # contornos dos municípios e votos por código IBGE
python 6_monta_site.py          # gera dados/relatorio.json e index.html
```

Para gerar o PDF:

```bash
pip install -r requirements.txt
python scripts/7_gera_pdf.py
```

## Escolhas da análise

- **Comparação com 2022:** em 2022 ela ficou em 2º no 1º turno (20,58%) e venceu o 2º turno (58,70%). A comparação principal usa o 2º turno de 2022, a votação que a elegeu; a tabela completa traz os dois turnos.
- **Recife:** compara as votações decisivas de cada ano, o 2º turno de 2022 (contra Marília Arraes, 77) e o 1º turno de 2026 (contra João Campos, 40). Na comparação por bairro entram só bairros que aparecem no cadastro de locais nos dois anos, porque alguns locais mudaram de bairro no cadastro do TSE.
- **Seções:** a mesma numeração de seção se repete em zonas eleitorais diferentes (Caruaru tem 3 zonas e Recife 11), então as seções são contadas por zona e número.

## Seções agregadas e consolidadas

Quando uma seção é agregada a outra, os eleitores dela votam na urna da seção principal, e o TSE publica o resultado só na principal. O arquivo de votos por seção não tem linhas para as agregadas: em PE são 673 agregadas, somadas em 626 seções principais. O passo 3b não cria linha para seção agregada, marca a principal como consolidada e soma o eleitorado das duas.

## Fontes

- [API de resultados do TSE](https://resultados.tse.jus.br/oficial/ele2026/6259/dados/pe/pe-c0003-e006259-u.json): votos por município e resultado oficial (eleição 6259, cargo 3).
- [Portal de Dados Abertos do TSE](https://dadosabertos.tse.jus.br/): `votacao_candidato_munzona` de 2010 a 2022, `votacao_secao_2022_PE`, `votacao_secao_2026_PE`, `eleitorado_local_votacao_2022` e `eleitorado_local_votacao_2026`.
- Contornos dos municípios: [geodata-br](https://github.com/tbrugz/geodata-br), a partir da malha do IBGE.

## Sobre o PDF

As dicas ao passar o mouse no PDF aparecem no Adobe Acrobat Reader e no Firefox. O leitor de PDF do Chrome e do Edge não as mostra. Para a versão interativa em qualquer navegador, use o site.

---

## Quem desenvolveu?

<img src="img/leo.jpg" alt="Foto de Léo Ansélmo" width="96" align="left">

**Léo Ansélmo** — Bacharelado em Administração e Desenvolvimento de Sistemas, com mais de 20 anos de experiência na área.

Procurei desenvolver um relatório baseado nos dados do TSE, mostrando o panorama político do candidato para o mesmo entender os dados consolidados e gerar conhecimento agregado da campanha atual.

Com ajuda da inteligência artificial (AI) nos mapas e gráficos, obtendo uma compreensão visual mais detalhada.

Instagram: [@leonardoanselmo79](https://www.instagram.com/leonardoanselmo79/)
