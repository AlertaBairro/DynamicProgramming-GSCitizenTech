import unittest

from alertabairro.dados import CENARIOS_ALAGAMENTO, LOCAIS, construir_grafo
from alertabairro.grafo import Grafo, chave_trecho, menor_caminho
from alertabairro.rota_segura import RoteadorSeguro

ESTACAO = LOCAIS["Estacao Jardim Sao Paulo-Ayrton Senna"]


class TestGrafo(unittest.TestCase):
    def setUp(self):
        self.g = construir_grafo()

    def test_mapa_tem_20_esquinas_e_e_conexo(self):
        self.assertEqual(len(self.g.nos), 20)
        for no in self.g.nos:
            self.assertIsNotNone(menor_caminho(self.g, ESTACAO, no))

    def test_trecho_nao_direcionado(self):
        self.assertEqual(self.g.vizinhos("A1")["B1"], self.g.vizinhos("B1")["A1"])
        self.assertEqual(chave_trecho("B1", "A1"), chave_trecho("A1", "B1"))

    def test_origem_igual_destino(self):
        r = menor_caminho(self.g, "A1", "A1")
        self.assertEqual((r.caminho, r.distancia_m), (("A1",), 0))

    def test_no_desconhecido(self):
        with self.assertRaises(ValueError):
            menor_caminho(self.g, "Z9", "A1")

    def test_grafo_simples_escolhe_menor(self):
        g = Grafo()
        for n, x in zip("ABC", (0, 1, 2)):
            g.adicionar_no(n, x, 0)
        g.adicionar_trecho("A", "B", 10)
        g.adicionar_trecho("B", "C", 10)
        g.adicionar_trecho("A", "C", 50)
        self.assertEqual(menor_caminho(g, "A", "C").caminho, ("A", "B", "C"))

    def test_sem_caminho_retorna_none(self):
        g = Grafo()
        g.adicionar_no("A", 0, 0)
        g.adicionar_no("B", 1, 1)
        self.assertIsNone(menor_caminho(g, "A", "B"))


class TestRotaSegura(unittest.TestCase):
    def setUp(self):
        self.r = RoteadorSeguro(construir_grafo())

    def test_sem_alagamento_padrao_igual_seguro(self):
        c = self.r.comparar("A4", ESTACAO, [])
        self.assertEqual(c.padrao.caminho, c.segura.caminho)
        self.assertEqual(c.desvio_m, 0)

    def test_chuva_forte_desvia_dos_alagados(self):
        c = self.r.comparar("B3", ESTACAO, CENARIOS_ALAGAMENTO["Chuva forte"])
        self.assertGreater(c.padrao.trechos_alagados, 0)
        self.assertEqual(c.segura.trechos_alagados, 0)
        self.assertGreater(c.desvio_m, 0)

    def test_rota_segura_nunca_expoe_mais_que_a_padrao(self):
        for cenario in CENARIOS_ALAGAMENTO.values():
            for origem in self.r.grafo.nos:
                c = self.r.comparar(origem, ESTACAO, cenario)
                self.assertLessEqual(c.segura.trechos_alagados, c.padrao.trechos_alagados)
                self.assertGreaterEqual(c.segura.distancia_m, c.padrao.distancia_m)

    def test_estacao_isolada_avisa_e_minimiza_exposicao(self):
        c = self.r.comparar("A4", ESTACAO, CENARIOS_ALAGAMENTO["Estacao isolada"])
        self.assertEqual(c.segura.trechos_alagados, 1)
        self.assertIn("ATENCAO", c.aviso)

    def test_ordem_do_trecho_nao_importa(self):
        a = self.r.comparar("B3", ESTACAO, [("C3", "C2")])
        b = self.r.comparar("B3", ESTACAO, [("C2", "C3")])
        self.assertEqual(a, b)
        self.assertEqual(self.r.acertos_cache, 1)

    def test_cache_nao_devolve_resposta_de_outro_cenario(self):
        a = self.r.comparar("B3", ESTACAO, [])
        b = self.r.comparar("B3", ESTACAO, CENARIOS_ALAGAMENTO["Chuva forte"])
        self.assertNotEqual(a.segura.caminho, b.segura.caminho)
        self.assertEqual(self.r.acertos_cache, 0)

    def test_trecho_inexistente(self):
        with self.assertRaises(ValueError):
            self.r.comparar("A1", "B3", [("A1", "E4")])


if __name__ == "__main__":
    unittest.main()
