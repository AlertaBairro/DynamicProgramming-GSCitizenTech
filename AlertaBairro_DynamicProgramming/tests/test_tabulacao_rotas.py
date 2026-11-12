"""Testes da integracao: DP versus Dijkstra em cenarios e grafos pequenos."""
import random
import unittest
from alertabairro.dados import CENARIOS_ALAGAMENTO, construir_grafo
from alertabairro.grafo import Grafo, chave_trecho, menor_caminho
from alertabairro.tabulacao_rotas import rota_segura_tabulacao


class TestTabulacaoRotas(unittest.TestCase):
    def test_equivalencia_todos_pares_e_cenarios(self):
        g = construir_grafo()
        for alagados in CENARIOS_ALAGAMENTO.values():
            marcados = frozenset(chave_trecho(*t) for t in alagados)
            for origem in g.nos:
                for destino in g.nos:
                    dp = rota_segura_tabulacao(g, origem, destino, marcados)
                    dj = menor_caminho(g, origem, destino, marcados)
                    self.assertEqual((dp.trechos_alagados, dp.distancia_m),
                                     (dj.trechos_alagados, dj.distancia_m))
                    self.assertEqual(dp.caminho[0], origem)
                    self.assertEqual(dp.caminho[-1], destino)
                    self.assertEqual(len(dp.caminho), len(set(dp.caminho)))

    def test_grafo_desconexo(self):
        g = Grafo()
        g.adicionar_no('A', 0, 0)
        g.adicionar_no('B', 1, 1)
        self.assertIsNone(rota_segura_tabulacao(g, 'A', 'B'))

    def test_origem_igual_destino(self):
        g = construir_grafo()
        rota = rota_segura_tabulacao(g, 'A1', 'A1')
        self.assertEqual((rota.caminho, rota.distancia_m, rota.trechos_alagados),
                         (('A1',), 0, 0))

    def test_no_inexistente(self):
        with self.assertRaises(ValueError):
            rota_segura_tabulacao(construir_grafo(), 'X9', 'A1')

    def test_risco_tem_prioridade_sobre_distancia(self):
        g = Grafo()
        for nome in 'ABC':
            g.adicionar_no(nome, 0, 0)
        g.adicionar_trecho('A', 'C', 10)
        g.adicionar_trecho('A', 'B', 40)
        g.adicionar_trecho('B', 'C', 40)
        rota = rota_segura_tabulacao(g, 'A', 'C', frozenset({chave_trecho('A', 'C')}))
        self.assertEqual((rota.caminho, rota.distancia_m, rota.trechos_alagados),
                         (('A', 'B', 'C'), 80, 0))

    def test_aleatorios_equivalencia(self):
        rng = random.Random(2026)
        for _ in range(30):
            g = Grafo()
            for i in range(6):
                g.adicionar_no(str(i), i, 0)
            for i in range(5):
                g.adicionar_trecho(str(i), str(i+1), rng.randint(1, 30))
            for i in range(6):
                for j in range(i+2, 6):
                    if rng.random() < 0.3:
                        g.adicionar_trecho(str(i), str(j), rng.randint(1, 30))
            alagados = frozenset(t for t in g.trechos() if rng.random() < 0.35)
            for origem, destino in [('0', '5'), ('2', '4'), ('5', '0')]:
                dp = rota_segura_tabulacao(g, origem, destino, alagados)
                dj = menor_caminho(g, origem, destino, alagados)
                self.assertEqual((dp.trechos_alagados, dp.distancia_m),
                                 (dj.trechos_alagados, dj.distancia_m))


if __name__ == '__main__':
    unittest.main()
