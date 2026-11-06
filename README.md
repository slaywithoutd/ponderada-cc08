# Ponderada CC08: do pipeline ao deadlock

**Maria Clara Oliveira Santos**

Análise de arquitetura, pipeline, processos, semáforos e deadlock da pulseira sensorial Tato, com a decisão de CTO e o código produtor/consumidor da questão A4.

## O que está neste repositório

| Entrega | Arquivo |
|---|---|
| Ponderada CC08: Parte A (problema técnico) e Parte B (decisão do CTO) | [ponderada/ponderada-tato.md](ponderada/ponderada-tato.md) |
| Código da questão A4 | [ponderada/codigo/](ponderada/codigo/) |
| **Atividade da aula S2: ARQUITETURA DE COMPUTADORES: PIPELINES E PARALELISMO** | [ponderada/atividade-s2/aula02_cc08_colab_atividade.ipynb](ponderada/atividade-s2/aula02_cc08_colab_atividade.ipynb) |

### Atividade da aula S2: ARQUITETURA DE COMPUTADORES: PIPELINES E PARALELISMO

Notebook da aula 02 do CC08 (Prof. João Luisi), rodado no Google Colab e salvo com todas as saídas e a célula de respostas preenchida (palpites, partes 1 a 3 e a questão 4). O GitHub mostra o notebook direto no navegador, com os gráficos e os números medidos, sem precisar rodar nada.

- **Parte 1, previsão de desvio:** o mesmo laço com vetor embaralhado e ordenado; quanto custa um erro de previsão.
- **Parte 2, latência e vazão:** soma com K acumuladores independentes; onde a curva para de melhorar.
- **Parte 3, SMT:** duas threads no mesmo núcleo, com somas dependentes e independentes.
- **Questão 4:** manter ou tirar um `if` de um interpretador, usando os números medidos.

Para rodar de novo: abra o arquivo no Colab (`Arquivo > Fazer upload de notebook`) e use `Ambiente de execução > Executar tudo`. O enunciado original está [no Colab da aula](https://colab.research.google.com/drive/1IjO_NK50cqxP2EBGn0TH6179lw4SM42Y).

## Estrutura

```
README.md
.gitignore
ponderada/
├── ponderada-tato.md      # Parte A (problema técnico) e Parte B (decisão do CTO)
├── codigo/                # Questão A4 (Python 3, sem dependências externas)
│   ├── comum.py
│   ├── versao1.py
│   ├── versao2.py
│   └── versao3.py
├── img/                   # Prints (caches da máquina e execuções da A4)
└── atividade-s2/          # Atividade da aula S2 (notebook do Colab, com saídas e respostas)
    └── aula02_cc08_colab_atividade.ipynb
```

## Como rodar a A4

Precisa de Python 3.8 ou mais novo; não há bibliotecas para instalar. Entre na pasta do código:

```bash
cd ponderada/codigo
```

Cada versão roda as 3 execuções com 20.000 amostras e N = 7 com um único comando (no Windows use `python`, no Linux/macOS `python3`):

| Versão | Comando | O que mostra |
|---|---|---|
| 1, sem sincronização | `python versao1.py` | condição de corrida: amostras perdidas, duplicadas e travamentos |
| 2, com semáforos | `python versao2.py` | 20.000 consumidas, 0 perdidas, 0 duplicadas |
| 3, ordem trocada | `python versao3.py` | deadlock: o consumidor fica 1 s sem receber nada e a execução é registrada como travada |

Parâmetros opcionais (os padrões são os do enunciado):

```bash
python versao1.py --amostras 20000 --n 7 --execucoes 3
```
