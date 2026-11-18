"""Heartbeat local para os algoritmos do AlertaBairro.

Verifica os algoritmos periodicamente e registra o ultimo sinal
de funcionamento. Nao acessa equipamentos ou servidores externos.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Dict, Mapping, Optional


@dataclass(frozen=True)
class EstadoHeartbeat:
    componente: str
    estado: str
    ultimo_sinal_s: Optional[float]
    detalhe: str


class MonitorHeartbeat:
    """Registra sinais e verifica a disponibilidade dos componentes."""

    def __init__(
        self,
        timeout_s: float = 2.0,
        relogio: Callable[[], float] = time.monotonic,
    ) -> None:
        if timeout_s <= 0:
            raise ValueError("O timeout deve ser positivo.")

        self.timeout_s = timeout_s
        self._relogio = relogio
        self._sinais: Dict[str, float] = {}
        self._erros: Dict[str, str] = {}
        self._componentes: set[str] = set()

    def registrar(self, componente: str) -> None:
        if not componente.strip():
            raise ValueError("O componente precisa de um nome.")

        self._componentes.add(componente)

    def bater(self, componente: str) -> None:
        self.registrar(componente)
        self._sinais[componente] = self._relogio()
        self._erros.pop(componente, None)

    def falhar(self, componente: str, detalhe: str) -> None:
        self.registrar(componente)
        self._erros[componente] = detalhe or "Falha na verificacao"

    def consultar(self, componente: str) -> EstadoHeartbeat:
        if componente not in self._componentes:
            raise KeyError(
                f"Componente nao registrado: {componente}"
            )

        ultimo = self._sinais.get(componente)

        if componente in self._erros:
            return EstadoHeartbeat(
                componente,
                "INDISPONIVEL",
                ultimo,
                self._erros[componente],
            )

        if ultimo is None:
            return EstadoHeartbeat(
                componente,
                "AGUARDANDO",
                None,
                "Nenhum sinal recebido",
            )

        idade = max(0.0, self._relogio() - ultimo)

        if idade > self.timeout_s:
            return EstadoHeartbeat(
                componente,
                "ATRASADO",
                ultimo,
                f"Ultimo sinal ha {idade:.2f}s",
            )

        return EstadoHeartbeat(
            componente,
            "ATIVO",
            ultimo,
            f"Ultimo sinal ha {idade:.2f}s",
        )

    def executar_verificacoes(
        self,
        verificacoes: Mapping[str, Callable[[], bool]],
    ) -> Dict[str, EstadoHeartbeat]:

        for componente, verificar in verificacoes.items():
            self.registrar(componente)

            try:
                if verificar() is False:
                    self.falhar(
                        componente,
                        "Verificacao retornou False",
                    )
                else:
                    self.bater(componente)

            except Exception as erro:
                self.falhar(
                    componente,
                    f"{type(erro).__name__}: {erro}",
                )

        return {
            nome: self.consultar(nome)
            for nome in verificacoes
        }


def verificacoes_alertabairro() -> Dict[str, Callable[[], bool]]:
    """Verifica rota segura e zeladoria com dados simulados."""

    from .dados import (
        CENARIOS_ALAGAMENTO,
        LOCAIS,
        OCORRENCIAS_EXEMPLO,
        construir_grafo,
    )
    from .priorizacao import planejar_dia
    from .rota_segura import RoteadorSeguro

    def rota_segura() -> bool:
        roteador = RoteadorSeguro(construir_grafo())

        resultado = roteador.comparar(
            LOCAIS["Casa da Marcia"],
            LOCAIS["Estacao Jardim Sao Paulo-Ayrton Senna"],
            CENARIOS_ALAGAMENTO["Chuva forte"],
        )

        return (
            resultado.segura is not None
            and resultado.padrao is not None
        )

    def zeladoria() -> bool:
        plano = planejar_dia(
            OCORRENCIAS_EXEMPLO,
            5.5,
            "tabulacao",
        )

        return (
            plano.pontuacao_total >= 0
            and plano.custo_total <= plano.capacidade_blocos
        )

    return {
        "ROTA_SEGURA": rota_segura,
        "ZELADORIA": zeladoria,
    }


def demonstrar_heartbeat(
    rodadas: int = 3,
    intervalo_s: float = 0.5,
    dormir: Callable[[float], None] = time.sleep,
    saida: Callable[[str], None] = print,
) -> None:
    """Executa um numero limitado de verificacoes periodicas."""

    if rodadas < 1 or intervalo_s < 0:
        raise ValueError(
            "Rodadas deve ser >= 1 e intervalo >= 0."
        )

    monitor = MonitorHeartbeat(
        timeout_s=max(1.0, intervalo_s * 3)
    )

    verificacoes = verificacoes_alertabairro()

    saida(
        "HEARTBEAT LOCAL - algoritmos do AlertaBairro (simulacao)"
    )

    for rodada in range(1, rodadas + 1):
        estados = monitor.executar_verificacoes(verificacoes)

        for estado in estados.values():
            saida(
                f"Rodada {rodada}/{rodadas} | "
                f"{estado.componente}: {estado.estado} | "
                f"{estado.detalhe}"
            )

        if rodada < rodadas:
            dormir(intervalo_s)
