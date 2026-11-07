# Ponderada CC08: do pipeline ao deadlock

Maria Clara Oliveira Santos

Análise de arquitetura, pipeline, processos, semáforos e deadlock da pulseira sensorial Tato, com a decisão de CTO e o código produtor/consumidor da questão A4.

## Conteúdo

| Entrega | Arquivo |
|---|---|
| Ponderada CC08, com a Parte A (problema técnico) e a Parte B (decisão do CTO) | [ponderada/ponderada-tato.md](ponderada/ponderada-tato.md) |
| Código da questão A4 | [ponderada/codigo/](ponderada/codigo/) |
| Atividade da aula S2: ARQUITETURA DE COMPUTADORES: PIPELINES E PARALELISMO | [ponderada/atividade-s2/aula02_cc08_colab_atividade.ipynb](ponderada/atividade-s2/aula02_cc08_colab_atividade.ipynb) |

### Atividade da aula S2: ARQUITETURA DE COMPUTADORES: PIPELINES E PARALELISMO

O notebook foi executado no Google Colab e está salvo com todas as saídas e com a célula de respostas preenchida (palpites, partes 1 a 3 e questão 4). O GitHub exibe o arquivo no navegador, com os gráficos e os números medidos, sem precisar executar nada. As partes medem:

- previsão de desvio, com o mesmo laço sobre um vetor embaralhado e um ordenado, para estimar o custo de um erro de previsão;
- latência e vazão da soma em ponto flutuante, com K acumuladores independentes;
- SMT, com duas threads somando em modo dependente e independente.

A questão 4 usa esses números para decidir se um `if` deve continuar no laço de um interpretador. Para executar de novo, basta abrir o arquivo no Colab (`Arquivo > Fazer upload de notebook`) e usar `Ambiente de execução > Executar tudo`.

## Estrutura

```
README.md
.gitignore
ponderada/
├── ponderada-tato.md      # Parte A e Parte B
├── codigo/                # Questão A4 (Python 3, sem dependências externas)
│   ├── comum.py
│   ├── versao1.py
│   ├── versao2.py
│   └── versao3.py
├── img/                   # Prints das caches e das execuções da A4
└── atividade-s2/          # Notebook da atividade S2, com saídas e respostas
    └── aula02_cc08_colab_atividade.ipynb
```

## Como rodar a A4

É preciso ter Python 3.8 ou mais novo; não há bibliotecas para instalar. Entre na pasta do código:

```bash
cd ponderada/codigo
```

Cada versão roda as 3 execuções com 20.000 amostras e N = 7 com um único comando (no Windows, `python`; no Linux e no macOS, `python3`):

| Versão | Comando | O que mostra |
|---|---|---|
| 1, sem sincronização | `python versao1.py` | condição de corrida: amostras perdidas, duplicadas e travamentos |
| 2, com semáforos | `python versao2.py` | 20.000 consumidas, 0 perdidas e 0 duplicadas |
| 3, ordem trocada | `python versao3.py` | deadlock: o consumidor fica 1 s sem receber nada, e a execução é registrada como travada |

Os parâmetros são opcionais, e os valores padrão são os do enunciado:

```bash
python versao1.py --amostras 20000 --n 7 --execucoes 3
```
