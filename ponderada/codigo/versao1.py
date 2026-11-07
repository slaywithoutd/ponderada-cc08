"""
versao1.py - A4, Versão 1: buffer circular SEM sincronização.

Ponderada CC08 (pulseira Tato) - Maria Clara Oliveira Santos (N = 7)

A thread do sensor (produtora) gera as amostras 0, 1, 2, ... e a thread do
motor (consumidora) as retira de um buffer circular de N posições. As duas
usam um contador compartilhado `ocupadas` e espera ocupada (busy waiting).

Para a condição de corrida aparecer, cada thread lê o contador, chama
time.sleep(0) (simula ser interrompida no pior momento) e só então escreve
o valor novo. Assim uma atualização pode apagar a outra (lost update):
  - se o contador fica MAIOR que o real, o consumidor lê posições já
    consumidas ou vazias -> amostras duplicadas;
  - se fica MENOR que o real, o produtor sobrescreve posições ainda não
    lidas -> amostras perdidas.
Se o consumidor ficar 1 s sem receber nada, a execução é registrada como
travamento.

Nota sobre a espera ocupada: em Python só uma thread roda bytecode por vez
(GIL). Um laço `while` vazio seguraria a CPU por até 5 ms a cada volta e
20.000 amostras levariam minutos. Por isso o laço de espera chama
time.sleep(0) a cada volta: a thread continua girando e testando o contador
(espera ocupada, sem dormir à espera de um evento), mas cede a vez para a
outra thread a cada teste.

Uso: python versao1.py            (3 execuções, 20.000 amostras, N = 7)
     python versao1.py --help     (parâmetros opcionais)
"""

import threading
import time

from comum import TIMEOUT_TRAVAMENTO, rodar_experimento


class EstadoCompartilhado:
    """Memória compartilhada entre produtor e consumidor, sem proteção.

    Atributos:
        buffer (list[int]): N posições; -1 marca posição nunca escrita.
        ocupadas (int): contador de posições ocupadas (a variável disputada).
        parar (threading.Event): avisa o produtor para desistir quando o
            consumidor já terminou ou travou.
    """

    def __init__(self, n):
        """Cria o buffer vazio.

        Parâmetros:
            n (int): número de posições do buffer circular.

        Retorno:
            None.
        """
        self.n = n
        self.buffer = [-1] * n
        self.ocupadas = 0
        self.parar = threading.Event()


def produtor(estado, total):
    """Thread do sensor: escreve as amostras 0..total-1 no buffer.

    Parâmetros:
        estado (EstadoCompartilhado): buffer e contador compartilhados.
        total (int): quantas amostras gerar.

    Retorno:
        None. Termina ao gerar todas as amostras ou quando `estado.parar`
        é sinalizado.
    """
    entrada = 0
    for amostra in range(total):
        # Espera ocupada: gira enquanto o contador diz que o buffer está cheio.
        while estado.ocupadas >= estado.n:
            if estado.parar.is_set():
                return
            time.sleep(0)           # cede a vez (ver nota no topo)
        estado.buffer[entrada] = amostra
        entrada = (entrada + 1) % estado.n
        # ---- região crítica (sem proteção) ----
        lido = estado.ocupadas
        time.sleep(0)               # interrupção no pior momento
        estado.ocupadas = lido + 1
        # ---------------------------------------


def consumidor(estado, total, saida):
    """Thread do motor: retira amostras do buffer até receber `total` leituras.

    Parâmetros:
        estado (EstadoCompartilhado): buffer e contador compartilhados.
        total (int): quantas leituras fazer antes de terminar.
        saida (dict): recebe as chaves `recebidas` (list[int]) e `travou`
            (bool) ao final.

    Retorno:
        None. O resultado vai em `saida`.
    """
    recebidas = []
    pos = 0
    ultimo = time.monotonic()
    travou = False
    while len(recebidas) < total:
        # Espera ocupada: gira enquanto o contador diz que o buffer está vazio.
        while estado.ocupadas <= 0:
            if time.monotonic() - ultimo > TIMEOUT_TRAVAMENTO:
                travou = True
                break
            time.sleep(0)           # cede a vez (ver nota no topo)
        if travou:
            break
        recebidas.append(estado.buffer[pos])
        pos = (pos + 1) % estado.n
        # ---- região crítica (sem proteção) ----
        lido = estado.ocupadas
        time.sleep(0)               # interrupção no pior momento
        estado.ocupadas = lido - 1
        # ---------------------------------------
        ultimo = time.monotonic()
    saida["recebidas"] = recebidas
    saida["travou"] = travou


def executar_uma_vez(total, n):
    """Roda uma execução completa da Versão 1.

    Parâmetros:
        total (int): amostras geradas pelo produtor.
        n (int): posições do buffer circular.

    Retorno:
        tuple (recebidas, travou, detalhe): lista do que o consumidor leu,
        se houve travamento e o valor final do contador compartilhado.
    """
    estado = EstadoCompartilhado(n)
    saida = {}
    t_prod = threading.Thread(target=produtor, args=(estado, total), daemon=True)
    t_cons = threading.Thread(target=consumidor, args=(estado, total, saida))
    t_prod.start()
    t_cons.start()
    t_cons.join()
    estado.parar.set()
    t_prod.join(timeout=2)
    detalhe = (f"contador 'ocupadas' no fim = {estado.ocupadas} "
               f"(faixa valida: 0 a {n})")
    return saida["recebidas"], saida["travou"], detalhe


if __name__ == "__main__":
    rodar_experimento("Versao 1 - sem sincronizacao (contador + espera ocupada)",
                      executar_uma_vez, __doc__)
