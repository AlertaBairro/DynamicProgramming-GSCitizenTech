"""Comparacao de eficiencia: forca bruta x memoizacao x tabulacao."""
from __future__ import annotations

import random
from typing import List, Sequence

from .priorizacao import (RISCO_BASE, Ocorrencia, mochila_forca_bruta,
                          mochila_memoizacao, mochila_tabulacao)


def gerar_ocorrencias(n: int, semente: int = 42) -> List[Ocorrencia]:
    """Ocorrencias aleatorias (reproduziveis pela semente) para medir desempenho."""
    rng = random.Random(semente)
    tipos = list(RISCO_BASE)
    return [
        Ocorrencia(f"S-{i:03d}", rng.choice(tipos), f"trecho {i}",
                   rng.random() < 0.4, rng.randint(0, 15), rng.randint(1, 6))
        for i in range(n)
    ]


def executar(tamanhos: Sequence[int], limite_forca_bruta: int = 20) -> List[str]:
    """Roda os tres metodos para cada n. A forca bruta so roda ate o limite, pois
    cresce como 2^n. Capacidade = 40% do custo total das ocorrencias."""
    linhas = [
        f"{'n':>5} {'cap':>5} | {'forca bruta':>22} | {'memoizacao':>22} | {'tabulacao':>22} | valor",
        "-" * 96,
    ]
    for n in tamanhos:
        itens = gerar_ocorrencias(n)
        cap = max(1, int(0.4 * sum(o.custo_blocos for o in itens)))
        tab = mochila_tabulacao(itens, cap)
        memo = mochila_memoizacao(itens, cap)
        if n <= limite_forca_bruta:
            fb = mochila_forca_bruta(itens, cap)
            col_fb = f"{fb.subproblemas:>9} cham {fb.tempo_ms:>7.1f} ms"
            assert fb.pontuacao_total == tab.pontuacao_total
        else:
            col_fb = f"{'(inviavel: 2^n)':>22}"
        assert memo.pontuacao_total == tab.pontuacao_total
        linhas.append(
            f"{n:>5} {cap:>5} | {col_fb} | "
            f"{memo.subproblemas:>9} est  {memo.tempo_ms:>7.1f} ms | "
            f"{tab.subproblemas:>9} est  {tab.tempo_ms:>7.1f} ms | {tab.pontuacao_total}"
        )
    return linhas
