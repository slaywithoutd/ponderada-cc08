"""
comum.py - Funções compartilhadas pelas três versões da questão A4.

Ponderada CC08 (pulseira Tato) - Maria Clara Oliveira Santos
Parâmetros: D1 = 5, D2 = 4, N = 3 + (D2 mod 5) = 7.

O módulo concentra o que não muda entre as versões:
  - os parâmetros padrão (N, número de amostras, tempo de travamento);
  - a leitura dos argumentos de linha de comando;
  - a análise do que o consumidor recebeu (consumidas, perdidas, duplicadas);
  - a impressão das execuções e da tabela final.

Cada versão (versao1.py, versao2.py, versao3.py) só implementa a função
que roda UMA execução do produtor/consumidor e chama `rodar_experimento`.
"""

import argparse
import sys
import time

# Tamanho do buffer circular: N = 3 + (D2 mod 5) = 3 + (4 mod 5) = 7.
N_PADRAO = 7
# Quantidade de amostras geradas pelo sensor em cada execução.
AMOSTRAS_PADRAO = 20_000
# Quantas vezes cada versão é executada.
EXECUCOES_PADRAO = 3
# Se o consumidor ficar este tempo (s) sem receber nada, registra travamento.
TIMEOUT_TRAVAMENTO = 1.0


def ler_argumentos(descricao):
    """Lê os argumentos opcionais de linha de comando.

    Parâmetros:
        descricao (str): texto mostrado em --help.

    Retorno:
        argparse.Namespace com os campos `amostras`, `n` e `execucoes`.
        Sem argumentos, valem os padrões do enunciado (20.000 amostras,
        N = 7, 3 execuções).
    """
    parser = argparse.ArgumentParser(description=descricao)
    parser.add_argument("--amostras", type=int, default=AMOSTRAS_PADRAO,
                        help="amostras por execução (padrão: 20000)")
    parser.add_argument("--n", type=int, default=N_PADRAO,
                        help="posições do buffer circular (padrão: 7)")
    parser.add_argument("--execucoes", type=int, default=EXECUCOES_PADRAO,
                        help="quantas execuções rodar (padrão: 3)")
    return parser.parse_args()


def analisar(recebidas, total):
    """Compara o que o consumidor recebeu com o que o produtor gerou.

    O produtor gera as amostras 0, 1, ..., total-1, cada uma uma única vez.

    Parâmetros:
        recebidas (list[int]): amostras na ordem em que o consumidor as tirou
            do buffer. O valor -1 indica uma posição que nunca foi escrita.
        total (int): quantas amostras o produtor deveria entregar.

    Retorno:
        dict com:
          consumidas - quantas leituras o consumidor fez do buffer;
          perdidas   - amostras de 0..total-1 que nunca chegaram ao consumidor;
          duplicadas - leituras a mais: a mesma amostra lida de novo ou uma
                       posição vazia (-1) lida como se fosse amostra;
          vazias     - quantas dessas leituras a mais eram posição vazia (-1).
    """
    unicas = {x for x in recebidas if 0 <= x < total}
    vazias = sum(1 for x in recebidas if x == -1)
    return {
        "consumidas": len(recebidas),
        "perdidas": total - len(unicas),
        "duplicadas": len(recebidas) - len(unicas),
        "vazias": vazias,
    }


def rodar_experimento(titulo, executar_uma_vez, descricao):
    """Roda uma versão várias vezes e imprime cada execução e a tabela final.

    Parâmetros:
        titulo (str): nome da versão, impresso no cabeçalho.
        executar_uma_vez (callable): função `f(total, n)` que roda uma
            execução e devolve uma tupla `(recebidas, travou, detalhe)`:
            recebidas (list[int]), travou (bool) e detalhe (str, texto livre
            sobre o estado das threads no fim).
        descricao (str): texto do --help.

    Retorno:
        list[dict]: um dicionário por execução, com os campos de `analisar`
        mais `travou` e `segundos`.
    """
    sys.stdout.reconfigure(encoding="utf-8")
    args = ler_argumentos(descricao)
    print(f"== {titulo} ==")
    print(f"amostras por execucao = {args.amostras} | N = {args.n} | "
          f"travamento = {TIMEOUT_TRAVAMENTO:.0f} s sem receber nada")
    print()

    resultados = []
    for numero in range(1, args.execucoes + 1):
        inicio = time.perf_counter()
        recebidas, travou, detalhe = executar_uma_vez(args.amostras, args.n)
        segundos = time.perf_counter() - inicio
        r = analisar(recebidas, args.amostras)
        r["travou"] = travou
        r["segundos"] = segundos
        resultados.append(r)
        print(f"execucao {numero}: consumidas={r['consumidas']} "
              f"perdidas={r['perdidas']} duplicadas={r['duplicadas']} "
              f"(vazias={r['vazias']}) travou={'SIM' if travou else 'nao'} "
              f"tempo={segundos:.2f}s")
        if detalhe:
            print(f"    {detalhe}")

    print()
    print("| Execucao | Consumidas | Perdidas | Duplicadas | Travou? |")
    print("|---|---|---|---|---|")
    for numero, r in enumerate(resultados, start=1):
        print(f"| {numero} | {r['consumidas']} | {r['perdidas']} | "
              f"{r['duplicadas']} | {'Sim' if r['travou'] else 'Nao'} |")
    return resultados
