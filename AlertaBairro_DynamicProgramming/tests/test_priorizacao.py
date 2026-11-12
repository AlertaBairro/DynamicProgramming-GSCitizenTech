import random
import unittest

from alertabairro.benchmark import gerar_ocorrencias
from alertabairro.dados import OCORRENCIAS_EXEMPLO
from alertabairro.priorizacao import (Ocorrencia, guloso_por_densidade,
                                      horas_para_blocos, mochila_forca_bruta,
                                      mochila_memoizacao, mochila_tabulacao,
                                      planejar_dia, ranking_por_risco)

PENDENTES = [o for o in OCORRENCIAS_EXEMPLO if o.pendente]


class TestOcorrencia(unittest.TestCase):
    def test_pontuacao(self):
        o = Ocorrencia("X", "bueiro entupido", "A1-B1", True, 14, 2)
        self.assertEqual(o.nivel_risco, 5)
        self.assertEqual(o.pontuacao, 5 * 10 + 10 * 2)  # apoios limitados a 10

    def test_validacoes(self):
        with self.assertRaises(ValueError):
            Ocorrencia("X", "tipo inexistente", "A1-B1", False, 0, 1)
        with self.assertRaises(ValueError):
            Ocorrencia("X", "lixo acumulado", "A1-B1", False, -1, 1)
        with self.assertRaises(ValueError):
            Ocorrencia("X", "lixo acumulado", "A1-B1", False, 0, 0)

    def test_ranking_ignora_resolvidas_e_ordena(self):
        ranking = ranking_por_risco(OCORRENCIAS_EXEMPLO)
        self.assertNotIn("O-013", [o.id for o in ranking])
        pontos = [o.pontuacao for o in ranking]
        self.assertEqual(pontos, sorted(pontos, reverse=True))


class TestMochila(unittest.TestCase):
    def test_tres_metodos_dao_o_mesmo_valor_otimo(self):
        for cap in range(0, 26):
            tab = mochila_tabulacao(PENDENTES, cap)
            memo = mochila_memoizacao(PENDENTES, cap)
            bruta = mochila_forca_bruta(PENDENTES, cap)
            self.assertEqual(tab.pontuacao_total, bruta.pontuacao_total, f"cap={cap}")
            self.assertEqual(memo.pontuacao_total, bruta.pontuacao_total, f"cap={cap}")

    def test_tabulacao_e_memoizacao_escolhem_o_mesmo_conjunto(self):
        for cap in range(0, 26):
            ids_t = [o.id for o in mochila_tabulacao(PENDENTES, cap).escolhidas]
            ids_m = [o.id for o in mochila_memoizacao(PENDENTES, cap).escolhidas]
            self.assertEqual(ids_t, ids_m)

    def test_aleatorios_contra_forca_bruta(self):
        for semente in range(30):
            itens = gerar_ocorrencias(random.Random(semente).randint(1, 12), semente)
            cap = random.Random(semente).randint(0, 20)
            self.assertEqual(mochila_tabulacao(itens, cap).pontuacao_total,
                             mochila_forca_bruta(itens, cap).pontuacao_total)

    def test_nunca_excede_capacidade(self):
        for cap in range(0, 26):
            r = mochila_tabulacao(PENDENTES, cap)
            self.assertLessEqual(r.custo_total, cap)
            self.assertEqual(r.custo_total, sum(o.custo_blocos for o in r.escolhidas))

    def test_escolhidas_e_adiadas_particionam_as_pendentes(self):
        r = mochila_tabulacao(PENDENTES, 11)
        ids = [o.id for o in r.escolhidas] + [o.id for o in r.adiadas]
        self.assertEqual(sorted(ids), sorted(o.id for o in PENDENTES))

    def test_dp_vence_o_guloso_em_5h30(self):
        cap = horas_para_blocos(5.5)
        self.assertEqual(cap, 11)
        self.assertEqual(mochila_tabulacao(PENDENTES, cap).pontuacao_total, 358)
        self.assertEqual(guloso_por_densidade(PENDENTES, cap).pontuacao_total, 342)

    def test_dp_nunca_perde_para_o_guloso(self):
        for cap in range(0, 26):
            self.assertGreaterEqual(mochila_tabulacao(PENDENTES, cap).pontuacao_total,
                                    guloso_por_densidade(PENDENTES, cap).pontuacao_total)

    def test_memoizacao_reaproveita_estados(self):
        r = mochila_memoizacao(PENDENTES, 11)
        self.assertGreater(r.reutilizacoes, 0)
        self.assertLess(r.subproblemas, mochila_tabulacao(PENDENTES, 11).subproblemas)

    def test_casos_de_borda(self):
        self.assertEqual(mochila_tabulacao([], 10).pontuacao_total, 0)
        self.assertEqual(mochila_tabulacao(PENDENTES, 0).escolhidas, ())
        self.assertEqual(mochila_memoizacao(PENDENTES, 0).pontuacao_total, 0)
        # capacidade grande: atende tudo
        r = mochila_tabulacao(PENDENTES, 1000)
        self.assertEqual(len(r.escolhidas), len(PENDENTES))
        with self.assertRaises(ValueError):
            mochila_tabulacao(PENDENTES, -1)

    def test_ids_repetidos(self):
        a = Ocorrencia("X", "lixo acumulado", "A1-B1", False, 0, 1)
        with self.assertRaises(ValueError):
            mochila_tabulacao([a, a], 5)

    def test_memoizacao_com_muitos_itens(self):
        itens = gerar_ocorrencias(1500)  # exige profundidade de recursao > 1000
        cap = 300
        self.assertEqual(mochila_memoizacao(itens, cap).pontuacao_total,
                         mochila_tabulacao(itens, cap).pontuacao_total)

    def test_planejar_dia_ignora_resolvidas(self):
        r = planejar_dia(OCORRENCIAS_EXEMPLO, 100)
        self.assertNotIn("O-013", [o.id for o in r.escolhidas])
        with self.assertRaises(ValueError):
            planejar_dia(OCORRENCIAS_EXEMPLO, 4, "xyz")


if __name__ == "__main__":
    unittest.main()
