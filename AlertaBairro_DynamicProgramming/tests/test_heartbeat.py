"""Testes deterministas para heartbeat, sem rede ou threads."""

import unittest

from alertabairro.heartbeat import (
    MonitorHeartbeat,
    demonstrar_heartbeat,
    verificacoes_alertabairro,
)


class HeartbeatTestes(unittest.TestCase):

    def setUp(self):
        self.tempo = [100.0]
        self.monitor = MonitorHeartbeat(
            timeout_s=2,
            relogio=lambda: self.tempo[0],
        )

    def test_aguardando_antes_do_primeiro_sinal(self):
        self.monitor.registrar("ROTA")
        self.assertEqual(
            self.monitor.consultar("ROTA").estado,
            "AGUARDANDO",
        )

    def test_sinal_ativo(self):
        self.monitor.bater("ROTA")
        self.assertEqual(
            self.monitor.consultar("ROTA").estado,
            "ATIVO",
        )

    def test_sinal_expirado(self):
        self.monitor.bater("ROTA")
        self.tempo[0] += 2.01
        self.assertEqual(
            self.monitor.consultar("ROTA").estado,
            "ATRASADO",
        )

    def test_falha_isolada_da_verificacao(self):
        estados = self.monitor.executar_verificacoes({
            "ROTA": lambda: True,
            "ZELADORIA": lambda: False,
        })
        self.assertEqual(estados["ROTA"].estado, "ATIVO")
        self.assertEqual(
            estados["ZELADORIA"].estado,
            "INDISPONIVEL",
        )

    def test_excecao_na_verificacao_nao_interrompe_outras(self):
        def erro():
            raise RuntimeError("indisponivel")

        estados = self.monitor.executar_verificacoes({
            "FALHA": erro,
            "OK": lambda: True,
        })

        self.assertIn(
            "RuntimeError",
            estados["FALHA"].detalhe,
        )
        self.assertEqual(estados["OK"].estado, "ATIVO")

    def test_recuperacao_apos_falha(self):
        self.monitor.falhar("ROTA", "teste")
        self.monitor.bater("ROTA")
        self.assertEqual(
            self.monitor.consultar("ROTA").estado,
            "ATIVO",
        )

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            MonitorHeartbeat(0)

        with self.assertRaises(ValueError):
            self.monitor.registrar(" ")

        with self.assertRaises(KeyError):
            self.monitor.consultar("DESCONHECIDO")

        with self.assertRaises(ValueError):
            demonstrar_heartbeat(rodadas=0)

    def test_verificacoes_reais_dos_algoritmos(self):
        estados = self.monitor.executar_verificacoes(
            verificacoes_alertabairro()
        )

        self.assertEqual(
            set(estados),
            {"ROTA_SEGURA", "ZELADORIA"},
        )

        self.assertTrue(
            all(
                estado.estado == "ATIVO"
                for estado in estados.values()
            )
        )

    def test_demo_periodica_controlada(self):
        linhas = []
        pausas = []

        demonstrar_heartbeat(
            rodadas=3,
            intervalo_s=0.1,
            dormir=pausas.append,
            saida=linhas.append,
        )

        self.assertEqual(pausas, [0.1, 0.1])

        self.assertEqual(
            sum(
                "ROTA_SEGURA: ATIVO" in linha
                for linha in linhas
            ),
            3,
        )

        self.assertEqual(
            sum(
                "ZELADORIA: ATIVO" in linha
                for linha in linhas
            ),
            3,
        )


if __name__ == "__main__":
    unittest.main()
