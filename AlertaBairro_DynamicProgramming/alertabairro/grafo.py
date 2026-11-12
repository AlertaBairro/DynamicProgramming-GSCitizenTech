"""Grafo viario e caminho minimo.

Modelo: cada esquina e um no; cada trecho de rua entre duas esquinas e uma aresta
nao direcionada com distancia em metros. Pontos alagados reportados pelos moradores
sao trechos (arestas) marcados como alagados.
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Tuple

Trecho = Tuple[str, str]


def chave_trecho(a: str, b: str) -> Trecho:
    """Chave canonica de um trecho: (A, B) e (B, A) representam a mesma rua."""
    return (a, b) if a <= b else (b, a)


class Grafo:
    """Grafo nao direcionado e ponderado (lista de adjacencia)."""

    def __init__(self) -> None:
        self._adj: Dict[str, Dict[str, int]] = {}
        self._coord: Dict[str, Tuple[float, float]] = {}

    # ---------- construcao ----------
    def adicionar_no(self, nome: str, x: float, y: float) -> None:
        self._adj.setdefault(nome, {})
        self._coord[nome] = (x, y)

    def adicionar_trecho(self, a: str, b: str, distancia: Optional[int] = None) -> None:
        """Liga duas esquinas. Se a distancia nao for informada, usa a euclidiana."""
        if a not in self._adj or b not in self._adj:
            raise ValueError(f"Esquina desconhecida no trecho {a}-{b}.")
        if distancia is None:
            (xa, ya), (xb, yb) = self._coord[a], self._coord[b]
            distancia = round(math.hypot(xa - xb, ya - yb))
        if distancia <= 0:
            raise ValueError("A distancia do trecho deve ser positiva.")
        self._adj[a][b] = distancia
        self._adj[b][a] = distancia

    # ---------- consulta ----------
    @property
    def nos(self) -> List[str]:
        return sorted(self._adj)

    def vizinhos(self, no: str) -> Dict[str, int]:
        return self._adj[no]

    def tem_no(self, no: str) -> bool:
        return no in self._adj

    def tem_trecho(self, a: str, b: str) -> bool:
        return a in self._adj and b in self._adj[a]

    def trechos(self) -> List[Trecho]:
        return sorted({chave_trecho(a, b) for a in self._adj for b in self._adj[a]})

    def distancia_total(self) -> int:
        """Soma das distancias de todos os trechos (cada um contado uma vez)."""
        return sum(self._adj[a][b] for a, b in self.trechos())


@dataclass(frozen=True)
class Rota:
    caminho: Tuple[str, ...]
    distancia_m: int
    trechos_alagados: int


def menor_caminho(
    grafo: Grafo,
    origem: str,
    destino: str,
    alagados: FrozenSet[Trecho] = frozenset(),
    penalidade: Optional[int] = None,
) -> Optional[Rota]:
    """Dijkstra com penalidade nos trechos alagados.

    custo do trecho = distancia + penalidade (se o trecho esta alagado).

    penalidade=None  -> automatica: soma de todas as distancias do mapa + 1. Com esse
                        valor, QUALQUER rota com menos trechos alagados vence QUALQUER
                        rota com mais trechos alagados; entre rotas com o mesmo numero
                        de trechos alagados, vence a mais curta.
    penalidade=0     -> ignora os alagamentos (rota "padrao", so a mais curta), mas
                        ainda conta quantos trechos alagados ela atravessa.

    Complexidade: O((V + E) log V) com fila de prioridade (heap).
    Retorna None se nao existe caminho entre origem e destino.
    """
    for no in (origem, destino):
        if not grafo.tem_no(no):
            raise ValueError(f"Esquina desconhecida: {no}")
    if penalidade is None:
        penalidade = grafo.distancia_total() + 1

    custo: Dict[str, int] = {origem: 0}
    anterior: Dict[str, str] = {}
    visitados = set()
    fila: List[Tuple[int, str]] = [(0, origem)]

    while fila:
        custo_atual, u = heapq.heappop(fila)
        if u in visitados:
            continue
        visitados.add(u)
        if u == destino:
            break
        for v, dist in grafo.vizinhos(u).items():
            if v in visitados:
                continue
            peso = dist + (penalidade if chave_trecho(u, v) in alagados else 0)
            novo = custo_atual + peso
            if novo < custo.get(v, math.inf):
                custo[v] = novo
                anterior[v] = u
                heapq.heappush(fila, (novo, v))

    if destino not in visitados:
        return None

    caminho = [destino]
    while caminho[-1] != origem:
        caminho.append(anterior[caminho[-1]])
    caminho.reverse()

    distancia = 0
    n_alagados = 0
    for a, b in zip(caminho, caminho[1:]):
        distancia += grafo.vizinhos(a)[b]
        if chave_trecho(a, b) in alagados:
            n_alagados += 1
    return Rota(tuple(caminho), distancia, n_alagados)
