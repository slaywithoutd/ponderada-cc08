"""
versao3.py - A4, Versão 3: semáforos com a ORDEM TROCADA no produtor.

Ponderada CC08 (pulseira Tato) - Maria Clara Oliveira Santos (N = 7)

Igual à Versão 2, mas o produtor faz wait(mutex) ANTES de wait(vazio).
Quando o buffer enche, o produtor dorme em wait(vazio) segurando o mutex.
O consumidor passa por wait(cheio), mas fica preso em wait(mutex): ele
nunca libera uma posição, então o produtor nunca acorda. É um deadlock
(espera circular entre duas threads, cada uma segurando o que a outra
precisa).

O consumidor usa timeout de 1 s só para detectar o travamento e encerrar
a execução; o produtor fica preso para sempre (é daemon, morre com o
programa).

Uso: python versao3.py            (3 execuções, 20.000 amostras, N = 7)
     python versao3.py --help     (parâmetros opcionais)
"""

import threading
import time

from comum import TIMEOUT_TRAVAMENTO, rodar_experimento


class BufferProtegido:
    """Buffer circular, semáforos e o estado de cada thread (para o relatório).

    Atributos:
        buffer (list[int]): N posições; -1 marca posição nunca escrita.
        vazio, cheio, mutex (threading.Semaphore): como na Versão 2.
        onde_produtor, onde_consumidor (str): última operação de cada thread,
            usada para mostrar onde cada uma parou.
    """

    def __init__(self, n):
        """Cria o buffer vazio e os semáforos.

        Parâmetros:
            n (int): número de posições do buffer circular.
        """
        self.n = n
        self.buffer = [-1] * n
        self.vazio = threading.Semaphore(n)
        self.cheio = threading.Semaphore(0)
        self.mutex = threading.Semaphore(1)
        self.onde_produtor = "nao iniciou"
        self.onde_consumidor = "nao iniciou"


def produtor(b, total):
    """Thread do sensor com a ordem errada: wait(mutex) -> wait(vazio).

    Parâmetros:
        b (BufferProtegido): buffer e semáforos compartilhados.
        total (int): quantas amostras gerar.

    Retorno:
        None (na prática fica bloqueado quando o buffer enche).
    """
    entrada = 0
    for amostra in range(total):
        b.onde_produtor = "esperando mutex"
        b.mutex.acquire()           # wait(mutex) primeiro (ERRADO)
        b.onde_produtor = "SEGURA mutex, esperando vazio"
        b.vazio.acquire()           # wait(vazio) com o mutex na mão
        b.buffer[entrada] = amostra
        time.sleep(0)
        entrada = (entrada + 1) % b.n
        b.mutex.release()
        b.cheio.release()
    b.onde_produtor = "terminou"


def consumidor(b, total, saida):
    """Thread do motor, igual à Versão 2.

    Parâmetros:
        b (BufferProtegido): buffer e semáforos compartilhados.
        total (int): quantas amostras ler.
        saida (dict): recebe `recebidas` (list[int]) e `travou` (bool).

    Retorno:
        None. O resultado vai em `saida`.
    """
    recebidas = []
    pos = 0
    travou = False
    while len(recebidas) < total:
        b.onde_consumidor = "esperando cheio"
        if not b.cheio.acquire(timeout=TIMEOUT_TRAVAMENTO):
            travou = True
            break
        b.onde_consumidor = "passou de cheio, esperando mutex"
        if not b.mutex.acquire(timeout=TIMEOUT_TRAVAMENTO):
            travou = True
            break
        recebidas.append(b.buffer[pos])
        time.sleep(0)
        pos = (pos + 1) % b.n
        b.mutex.release()
        b.vazio.release()
    b.onde_consumidor = "terminou" if not travou else b.onde_consumidor
    saida["recebidas"] = recebidas
    saida["travou"] = travou


def executar_uma_vez(total, n):
    """Roda uma execução completa da Versão 3.

    Parâmetros:
        total (int): amostras geradas pelo produtor.
        n (int): posições do buffer circular.

    Retorno:
        tuple (recebidas, travou, detalhe): o detalhe diz onde cada thread
        estava parada quando o travamento foi detectado.
    """
    b = BufferProtegido(n)
    saida = {}
    t_prod = threading.Thread(target=produtor, args=(b, total), daemon=True)
    t_cons = threading.Thread(target=consumidor, args=(b, total, saida))
    t_prod.start()
    t_cons.start()
    t_cons.join()
    detalhe = (f"produtor: {b.onde_produtor} | consumidor: {b.onde_consumidor}"
               f" | produtor ainda vivo: {t_prod.is_alive()}")
    return saida["recebidas"], saida["travou"], detalhe


if __name__ == "__main__":
    rodar_experimento("Versao 3 - ordem trocada: produtor faz wait(mutex) antes de wait(vazio)",
                      executar_uma_vez, __doc__)
