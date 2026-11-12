"""Priorizacao da zeladoria (US04) como problema da MOCHILA 0/1.

Situacao real: a equipe de zeladoria tem um numero limitado de horas por dia e mais
ocorrencias pendentes do que consegue atender. Qual conjunto de ocorrencias reduz
mais o risco de alagamento dentro do tempo disponivel?

    item      = ocorrencia pendente
    peso      = custo de atendimento, em blocos de 30 minutos
    valor     = pontuacao de risco da ocorrencia
    mochila   = blocos de tempo da equipe no dia

Recorrencia (i = primeiras i ocorrencias, c = blocos disponiveis):

    melhor(0, c) = 0
    melhor(i, c) = melhor(i-1, c)                                   se custo_i > c
    melhor(i, c) = max( melhor(i-1, c),
                        melhor(i-1, c - custo_i) + pontuacao_i )    caso contrario

Tres implementacoes da MESMA recorrencia, para comparar eficiencia:
    - mochila_tabulacao   : bottom-up, preenche a tabela (n+1) x (C+1)
    - mochila_memoizacao  : top-down, so calcula os estados alcancados a partir de
                            (n, C) e guarda cada um em um dicionario
    - mochila_forca_bruta : testa todos os subconjuntos, O(2^n) (apenas referencia)
"""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

BLOCO_MINUTOS = 30

# Risco base por tipo de problema (escala 1-5) e bonus para pontos baixos, que
# alagam com recorrencia. Valores simulados, definidos pela equipe.
RISCO_BASE = {
    "bueiro entupido": 3,
    "boca de lobo danificada": 3,
    "lixo acumulado": 2,
}
BONUS_PONTO_BAIXO = 2

# pontuacao = nivel_risco * PESO_RISCO + min(apoios, LIMITE_APOIOS) * PESO_APOIO
# O risco domina; os apoios dos moradores (US02) reforcam a prioridade, com teto
# para que uma ocorrencia muito apoiada nao ultrapasse uma de risco bem maior.
PESO_RISCO = 10
PESO_APOIO = 2
LIMITE_APOIOS = 10

STATUS_PENDENTES = ("recebida", "em atendimento")


@dataclass(frozen=True)
class Ocorrencia:
    id: str
    tipo: str
    local: str
    ponto_baixo: bool
    apoios: int
    custo_blocos: int            # tempo de atendimento em blocos de 30 min
    status: str = "recebida"     # recebida | em atendimento | resolvida

    def __post_init__(self) -> None:
        if self.tipo not in RISCO_BASE:
            raise ValueError(f"Tipo desconhecido: {self.tipo}")
        if self.apoios < 0:
            raise ValueError("O numero de apoios nao pode ser negativo.")
        if self.custo_blocos < 1:
            raise ValueError("O custo deve ser de pelo menos 1 bloco.")

    @property
    def nivel_risco(self) -> int:
        return RISCO_BASE[self.tipo] + (BONUS_PONTO_BAIXO if self.ponto_baixo else 0)

    @property
    def pontuacao(self) -> int:
        return (self.nivel_risco * PESO_RISCO
                + min(self.apoios, LIMITE_APOIOS) * PESO_APOIO)

    @property
    def pendente(self) -> bool:
        return self.status in STATUS_PENDENTES


@dataclass(frozen=True)
class ResultadoPriorizacao:
    metodo: str
    capacidade_blocos: int
    escolhidas: Tuple[Ocorrencia, ...]   # na ordem de atendimento
    adiadas: Tuple[Ocorrencia, ...]
    pontuacao_total: int
    custo_total: int
    subproblemas: int                    # estados calculados / chamadas feitas
    reutilizacoes: int                   # respostas obtidas do cache (memoizacao)
    tempo_ms: float


# ---------------------------------------------------------------- utilidades
def ranking_por_risco(ocorrencias: Sequence[Ocorrencia]) -> List[Ocorrencia]:
    """Lista de pendentes ordenada por risco (US04): maior pontuacao primeiro;
    empate: mais apoios, depois menor custo, depois id."""
    pendentes = [o for o in ocorrencias if o.pendente]
    return sorted(pendentes, key=lambda o: (-o.pontuacao, -o.apoios, o.custo_blocos, o.id))


def horas_para_blocos(horas: float) -> int:
    return int(horas * 60 // BLOCO_MINUTOS)


def _montar(metodo: str, itens: Sequence[Ocorrencia], capacidade: int,
            indices: List[int], subproblemas: int, reutilizacoes: int,
            inicio: float) -> ResultadoPriorizacao:
    escolhidas = sorted((itens[i] for i in indices),
                        key=lambda o: (-o.pontuacao, o.custo_blocos, o.id))
    ids = {o.id for o in escolhidas}
    adiadas = tuple(o for o in ranking_por_risco(itens) if o.id not in ids)
    return ResultadoPriorizacao(
        metodo=metodo,
        capacidade_blocos=capacidade,
        escolhidas=tuple(escolhidas),
        adiadas=adiadas,
        pontuacao_total=sum(o.pontuacao for o in escolhidas),
        custo_total=sum(o.custo_blocos for o in escolhidas),
        subproblemas=subproblemas,
        reutilizacoes=reutilizacoes,
        tempo_ms=(time.perf_counter() - inicio) * 1000,
    )


def _validar(itens: Sequence[Ocorrencia], capacidade: int) -> None:
    if capacidade < 0:
        raise ValueError("A capacidade da equipe nao pode ser negativa.")
    ids = [o.id for o in itens]
    if len(ids) != len(set(ids)):
        raise ValueError("Ha ocorrencias com id repetido.")


# ---------------------------------------------------------------- tabulacao
def mochila_tabulacao(itens: Sequence[Ocorrencia], capacidade: int) -> ResultadoPriorizacao:
    """Bottom-up. Tempo O(n * C); espaco O(n * C) (a tabela inteira e necessaria
    para reconstruir QUAIS ocorrencias foram escolhidas, e nao so o valor total)."""
    inicio = time.perf_counter()
    _validar(itens, capacidade)
    n = len(itens)

    dp = [[0] * (capacidade + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        custo, valor = itens[i - 1].custo_blocos, itens[i - 1].pontuacao
        for c in range(capacidade + 1):
            dp[i][c] = dp[i - 1][c]                       # nao atende a ocorrencia i
            if custo <= c:                                # ou atende, se couber
                dp[i][c] = max(dp[i][c], dp[i - 1][c - custo] + valor)

    # Reconstrucao: percorre a tabela de tras para frente.
    indices, c = [], capacidade
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:                      # o item i foi usado
            indices.append(i - 1)
            c -= itens[i - 1].custo_blocos
    return _montar("tabulacao", itens, capacidade, indices,
                   subproblemas=(n + 1) * (capacidade + 1), reutilizacoes=0,
                   inicio=inicio)


# -------------------------------------------------------------- memoizacao
def mochila_memoizacao(itens: Sequence[Ocorrencia], capacidade: int) -> ResultadoPriorizacao:
    """Top-down com cache. Tempo e espaco O(n * C) no pior caso, mas so calcula os
    estados (i, c) realmente alcancados a partir de (n, C)."""
    inicio = time.perf_counter()
    _validar(itens, capacidade)
    n = len(itens)
    memo: Dict[Tuple[int, int], int] = {}
    reutilizacoes = 0

    limite_anterior = sys.getrecursionlimit()
    sys.setrecursionlimit(max(limite_anterior, n + 100))  # profundidade maxima = n

    def melhor(i: int, c: int) -> int:
        nonlocal reutilizacoes
        if i == 0:
            return 0
        if (i, c) in memo:
            reutilizacoes += 1
            return memo[(i, c)]
        resultado = melhor(i - 1, c)
        custo = itens[i - 1].custo_blocos
        if custo <= c:
            resultado = max(resultado, melhor(i - 1, c - custo) + itens[i - 1].pontuacao)
        memo[(i, c)] = resultado
        return resultado

    try:
        melhor(n, capacidade)

        # Reconstrucao com a mesma regra da tabulacao (resultados identicos).
        indices, c = [], capacidade
        for i in range(n, 0, -1):
            if melhor(i, c) != melhor(i - 1, c):
                indices.append(i - 1)
                c -= itens[i - 1].custo_blocos
    finally:
        sys.setrecursionlimit(limite_anterior)

    return _montar("memoizacao", itens, capacidade, indices,
                   subproblemas=len(memo), reutilizacoes=reutilizacoes, inicio=inicio)


# -------------------------------------------------------------- forca bruta
def mochila_forca_bruta(itens: Sequence[Ocorrencia], capacidade: int) -> ResultadoPriorizacao:
    """Testa todos os subconjuntos, O(2^n). Serve de referencia: mostra por que a
    programacao dinamica e necessaria e confere a resposta nos testes."""
    inicio = time.perf_counter()
    _validar(itens, capacidade)
    n = len(itens)
    melhor_valor, melhor_indices = -1, []
    chamadas = 0
    atuais: List[int] = []

    def explorar(i: int, restante: int, valor: int) -> None:
        nonlocal melhor_valor, melhor_indices, chamadas
        chamadas += 1
        if i == n:
            if valor > melhor_valor:
                melhor_valor, melhor_indices = valor, list(atuais)
            return
        explorar(i + 1, restante, valor)                  # nao atende
        if itens[i].custo_blocos <= restante:             # atende
            atuais.append(i)
            explorar(i + 1, restante - itens[i].custo_blocos, valor + itens[i].pontuacao)
            atuais.pop()

    explorar(0, capacidade, 0)
    return _montar("forca bruta", itens, capacidade, melhor_indices,
                   subproblemas=chamadas, reutilizacoes=0, inicio=inicio)


# ------------------------------------------------------ comparacao (guloso)
def guloso_por_densidade(itens: Sequence[Ocorrencia], capacidade: int) -> ResultadoPriorizacao:
    """Estrategia intuitiva: pega primeiro quem tem maior pontuacao POR bloco.
    Rapida, mas NAO garante o melhor conjunto. Usada na demonstracao para mostrar
    o ganho da programacao dinamica."""
    inicio = time.perf_counter()
    _validar(itens, capacidade)
    ordem = sorted(range(len(itens)),
                   key=lambda i: (-itens[i].pontuacao / itens[i].custo_blocos, itens[i].id))
    indices, restante = [], capacidade
    for i in ordem:
        if itens[i].custo_blocos <= restante:
            indices.append(i)
            restante -= itens[i].custo_blocos
    return _montar("guloso", itens, capacidade, indices, len(itens), 0, inicio)


# --------------------------------------------------------------- conveniencia
def planejar_dia(ocorrencias: Sequence[Ocorrencia], horas_equipe: float,
                 metodo: str = "tabulacao") -> ResultadoPriorizacao:
    """Seleciona as ocorrencias PENDENTES a atender no dia, dado o tempo da equipe."""
    metodos = {"tabulacao": mochila_tabulacao, "memoizacao": mochila_memoizacao}
    if metodo not in metodos:
        raise ValueError(f"Metodo invalido: {metodo}")
    pendentes = [o for o in ocorrencias if o.pendente]
    return metodos[metodo](pendentes, horas_para_blocos(horas_equipe))
