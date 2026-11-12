"""Rota segura (US09 e US10): compara o trajeto padrao com o trajeto que desvia
dos pontos alagados reportados.

CACHE DE CONSULTAS (reutilizacao de resultados): o roteador guarda o resultado de cada consulta, identificada por
(origem, destino, conjunto de trechos alagados). Se a mesma consulta se repete
(varios moradores indo do mesmo bairro para a estacao com o mesmo cenario de chuva),
a resposta vem do cache. Quando um novo ponto alagado e reportado, o conjunto muda,
a chave muda e a rota e recalculada automaticamente (sem risco de resposta velha).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, Optional, Tuple

from .grafo import Grafo, Rota, Trecho, chave_trecho, menor_caminho
from .tabulacao_rotas import rota_segura_tabulacao


@dataclass(frozen=True)
class ComparacaoRotas:
    origem: str
    destino: str
    padrao: Optional[Rota]   # mais curta, ignorando alagamentos
    segura: Optional[Rota]   # menos trechos alagados e, depois, mais curta
    aviso: str               # mensagem em linguagem simples para o cidadao

    @property
    def desvio_m(self) -> int:
        """Metros a mais que o trajeto seguro tem em relacao ao padrao."""
        if self.padrao is None or self.segura is None:
            return 0
        return self.segura.distancia_m - self.padrao.distancia_m


class RoteadorSeguro:
    def __init__(self, grafo: Grafo) -> None:
        self.grafo = grafo
        self._cache: Dict[Tuple[str, str, FrozenSet[Trecho]], ComparacaoRotas] = {}
        self.consultas = 0
        self.acertos_cache = 0

    def _normalizar(self, alagados: Iterable[Trecho]) -> FrozenSet[Trecho]:
        normalizados = set()
        for a, b in alagados:
            if not self.grafo.tem_trecho(a, b):
                raise ValueError(f"Nao existe trecho entre {a} e {b} no mapa.")
            normalizados.add(chave_trecho(a, b))
        return frozenset(normalizados)

    def comparar(self, origem: str, destino: str,
                 alagados: Iterable[Trecho] = ()) -> ComparacaoRotas:
        alag = self._normalizar(alagados)
        chave = (origem, destino, alag)
        self.consultas += 1
        if chave in self._cache:
            self.acertos_cache += 1
            return self._cache[chave]

        padrao = menor_caminho(self.grafo, origem, destino, alag, penalidade=0)
        segura = rota_segura_tabulacao(self.grafo, origem, destino, alag)
        resultado = ComparacaoRotas(origem, destino, padrao, segura,
                                    self._montar_aviso(padrao, segura))
        self._cache[chave] = resultado
        return resultado

    @staticmethod
    def _montar_aviso(padrao: Optional[Rota], segura: Optional[Rota]) -> str:
        if padrao is None or segura is None:
            return "Nao foi possivel encontrar um trajeto entre esses dois pontos."
        if segura.trechos_alagados > 0:
            return (f"ATENCAO: nao existe trajeto sem alagamento. Este e o de menor "
                    f"exposicao ({segura.trechos_alagados} trecho(s) alagado(s)). "
                    f"Considere adiar o deslocamento.")
        if padrao.trechos_alagados == 0:
            return "O trajeto mais curto ja esta livre dos pontos alagados reportados."
        return (f"Desvio de {padrao.trechos_alagados} trecho(s) alagado(s): "
                f"+{segura.distancia_m - padrao.distancia_m} m no trajeto seguro.")
