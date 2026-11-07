"""
versao2.py - A4, Versão 2: buffer circular COM três semáforos.

Ponderada CC08 (pulseira Tato) - Maria Clara Oliveira Santos (N = 7)

Solução clássica do produtor/consumidor com buffer limitado:
  - vazio (começa em N): conta posições livres. O produtor faz wait(vazio)
    antes de escrever, então nunca sobrescreve amostra não lida.
  - cheio (começa em 0): conta posições ocupadas. O consumidor faz
    wait(cheio) antes de ler, então nunca lê posição vazia ou já lida.
  - mutex (começa em 1): só uma thread por vez mexe no buffer e nos índices.

O time.sleep(0) da Versão 1 continua dentro da região crítica, para mostrar
que a interrupção no pior momento deixa de causar erro quando a região está
protegida pelo mutex.

Uso: python versao2.py            (3 execuções, 20.000 amostras, N = 7)
     python versao2.py --help     (parâmetros opcionais)
"""

import threading
import time

from comum import TIMEOUT_TRAVAMENTO, rodar_experimento


class BufferProtegido:
    """Buffer circular e os três semáforos que o protegem.

    Atributos:
        buffer (list[int]): N posições; -1 marca posição nunca escrita.
        vazio (threading.Semaphore): posições livres, começa em N.
        cheio (threading.Semaphore): posições ocupadas, começa em 0.
        mutex (threading.Semaphore): exclusão mútua, começa em 1.
    """

    def __init__(self, n):
        """Cria o buffer vazio e os semáforos.

        Parâmetros:
            n (int): número de posições do buffer circular.

        Retorno:
            None.
        """
        self.n = n
        self.buffer = [-1] * n
        self.vazio = threading.Semaphore(n)
        self.cheio = threading.Semaphore(0)
        self.mutex = threading.Semaphore(1)


def produtor(b, total):
    """Thread do sensor: wait(vazio) -> wait(mutex) -> escreve -> signals.

    Parâmetros:
        b (BufferProtegido): buffer e semáforos compartilhados.
        total (int): quantas amostras gerar.

    Retorno:
        None.
    """
    entrada = 0
    for amostra in range(total):
        b.vazio.acquire()           # wait(vazio): espera uma posição livre
        b.mutex.acquire()           # wait(mutex): entra na região crítica
        b.buffer[entrada] = amostra
        time.sleep(0)               # mesma interrupção da Versão 1
        entrada = (entrada + 1) % b.n
        b.mutex.release()           # signal(mutex)
        b.cheio.release()           # signal(cheio): mais uma posição ocupada


def consumidor(b, total, saida):
    """Thread do motor: wait(cheio) -> wait(mutex) -> lê -> signals.

    Usa timeout de 1 s nos waits só para detectar travamento; numa execução
    correta o timeout nunca dispara.

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
        if not b.cheio.acquire(timeout=TIMEOUT_TRAVAMENTO):   # wait(cheio)
            travou = True
            break
        if not b.mutex.acquire(timeout=TIMEOUT_TRAVAMENTO):   # wait(mutex)
            travou = True
            break
        recebidas.append(b.buffer[pos])
        time.sleep(0)
        pos = (pos + 1) % b.n
        b.mutex.release()           # signal(mutex)
        b.vazio.release()           # signal(vazio): mais uma posição livre
    saida["recebidas"] = recebidas
    saida["travou"] = travou


def executar_uma_vez(total, n):
    """Roda uma execução completa da Versão 2.

    Parâmetros:
        total (int): amostras geradas pelo produtor.
        n (int): posições do buffer circular.

    Retorno:
        tuple (recebidas, travou, detalhe).
    """
    b = BufferProtegido(n)
    saida = {}
    t_prod = threading.Thread(target=produtor, args=(b, total), daemon=True)
    t_cons = threading.Thread(target=consumidor, args=(b, total, saida))
    t_prod.start()
    t_cons.start()
    t_cons.join()
    t_prod.join(timeout=2)
    return saida["recebidas"], saida["travou"], ""


if __name__ == "__main__":
    rodar_experimento("Versao 2 - semaforos vazio(N), cheio(0), mutex(1)",
                      executar_uma_vez, __doc__)
