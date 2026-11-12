"""Dados SIMULADOS do AlertaBairro (nenhum dado pessoal real).

Origem dos dados
----------------
- Mapa: malha de 20 esquinas (colunas A-E, linhas 1-4) com espacamento de cerca de
  120 m, criada a mao com um leve desalinhamento para parecer um bairro de verdade.
  O layout e inspirado no entorno da Estacao Jardim Sao Paulo-Ayrton Senna (Linha
  1-Azul, zona norte de Sao Paulo), mas as coordenadas NAO sao reais.
- Ocorrencias e pontos alagados: inventados para a demonstracao.
- Contexto real do problema (alagamento da estacao em janeiro de 2025) esta
  documentado no trabalho de Agile Methodology.

Para usar dados reais: troque NOS/TRECHOS_AUSENTES por esquinas e ruas extraidas do
OpenStreetMap; o restante do codigo nao precisa mudar.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from .grafo import Grafo, Trecho
from .priorizacao import Ocorrencia

# ------------------------------------------------------------------ mapa
NOS: Dict[str, Tuple[float, float]] = {
    "A1": (0, 0),     "B1": (130, 10),  "C1": (250, -5),  "D1": (380, 15),  "E1": (500, 0),
    "A2": (-10, 110), "B2": (120, 105), "C2": (255, 100), "D2": (375, 120), "E2": (505, 105),
    "A3": (5, 215),   "B3": (135, 220), "C3": (245, 210), "D3": (380, 225), "E3": (495, 215),
    "A4": (0, 330),   "B4": (125, 320), "C4": (250, 325), "D4": (385, 335), "E4": (500, 330),
}

# Trechos da malha regular que NAO existem (quadras fechadas), para o mapa nao ser
# uma grade perfeita.
TRECHOS_AUSENTES = {("B1", "B2"), ("D3", "D4"), ("A2", "B2"), ("C4", "D4")}

LOCAIS: Dict[str, str] = {
    "Estacao Jardim Sao Paulo-Ayrton Senna": "C2",
    "Casa da Mariana": "A4",
    "Casa da Marcia": "B3",
    "Mercado do bairro": "E4",
    "Posto de saude": "A1",
}


def construir_grafo() -> Grafo:
    grafo = Grafo()
    for nome, (x, y) in NOS.items():
        grafo.adicionar_no(nome, x, y)
    colunas, linhas = "ABCDE", "1234"
    for ci, col in enumerate(colunas):
        for li, lin in enumerate(linhas):
            atual = f"{col}{lin}"
            if ci + 1 < len(colunas):
                direita = f"{colunas[ci + 1]}{lin}"
                if (atual, direita) not in TRECHOS_AUSENTES:
                    grafo.adicionar_trecho(atual, direita)
            if li + 1 < len(linhas):
                abaixo = f"{col}{linhas[li + 1]}"
                if (atual, abaixo) not in TRECHOS_AUSENTES:
                    grafo.adicionar_trecho(atual, abaixo)
    return grafo


# --------------------------------------------------- cenarios de chuva
CENARIOS_ALAGAMENTO: Dict[str, List[Trecho]] = {
    "Sem chuva": [],
    "Chuva moderada": [("C2", "C3")],
    "Chuva forte": [("C2", "C3"), ("B3", "C3"), ("C3", "C4")],
    "Estacao isolada": [("C2", "C1"), ("C2", "B2"), ("C2", "D2"), ("C2", "C3")],
}

# ------------------------------------------------------- ocorrencias
OCORRENCIAS_EXEMPLO: List[Ocorrencia] = [
    Ocorrencia("O-001", "bueiro entupido",         "C2-C3", True,  14, 2),
    Ocorrencia("O-002", "boca de lobo danificada", "C2-D2", True,   6, 4),
    Ocorrencia("O-003", "lixo acumulado",          "B3-C3", True,   9, 1),
    Ocorrencia("O-004", "bueiro entupido",         "A4-B4", False,  3, 2),
    Ocorrencia("O-005", "bueiro entupido",         "B2-B3", True,   5, 2),
    Ocorrencia("O-006", "lixo acumulado",          "D3-E3", False,  1, 1),
    Ocorrencia("O-007", "boca de lobo danificada", "A2-A3", False,  2, 4),
    Ocorrencia("O-008", "lixo acumulado",          "C3-C4", True,   4, 1),
    Ocorrencia("O-009", "bueiro entupido",         "D1-D2", False,  0, 2),
    Ocorrencia("O-010", "bueiro entupido",         "E2-E3", True,   7, 2),
    Ocorrencia("O-011", "lixo acumulado",          "B1-C1", False,  0, 1),
    Ocorrencia("O-012", "boca de lobo danificada", "C4-D4", True,   2, 3),
    Ocorrencia("O-013", "bueiro entupido",         "A1-A2", False, 11, 2, "resolvida"),
]
