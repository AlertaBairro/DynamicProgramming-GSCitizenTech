"""Programacao dinamica bottom-up para rota de menor exposicao.

Estado DP[k][v]: melhor par (quantidade de trechos alagados, metros)
para chegar de origem a v usando NO MAXIMO k arestas.
A recorrencia mantem DP[k-1][v] ou estende uma aresta (u,v).
Pesos positivos garantem que uma solucao otima pode ser simples, com
no maximo |V|-1 arestas. Complexidade O(V*(V+E)) em tempo e O(V^2)
em memoria para tabela e predecessores; adequada ao mapa didatico.
"""
from __future__ import annotations

from typing import FrozenSet, Optional
from .grafo import Grafo, Rota, Trecho, chave_trecho


def rota_segura_tabulacao(grafo: Grafo, origem: str, destino: str,
                          alagados: FrozenSet[Trecho] = frozenset()) -> Optional[Rota]:
    for no in (origem, destino):
        if not grafo.tem_no(no):
            raise ValueError(f"Esquina desconhecida: {no}")
    nos = grafo.nos
    infinito = (float('inf'), float('inf'))
    anterior = {v: infinito for v in nos}
    anterior[origem] = (0, 0)
    tabelas = [anterior]
    predecessores = [{}]
    for _ in range(1, len(nos)):
        atual = anterior.copy()
        pais = {v: v for v in nos if anterior[v] != infinito}
        for u in nos:
            if anterior[u] == infinito:
                continue
            for v, metros in sorted(grafo.vizinhos(u).items()):
                risco = int(chave_trecho(u, v) in alagados)
                candidato = (anterior[u][0] + risco, anterior[u][1] + metros)
                if candidato < atual[v]:
                    atual[v] = candidato
                    pais[v] = u
        tabelas.append(atual)
        predecessores.append(pais)
        anterior = atual
    custo = tabelas[-1][destino]
    if custo == infinito:
        return None
    caminho = [destino]
    atual = destino
    for k in range(len(nos)-1, 0, -1):
        if atual == origem:
            break
        pai = predecessores[k][atual]
        if pai != atual:
            caminho.append(pai)
        atual = pai
    if atual != origem:
        raise RuntimeError('Falha ao reconstruir caminho da tabulacao')
    caminho.reverse()
    return Rota(tuple(caminho), int(custo[1]), int(custo[0]))
