"""AlertaBairro - Dynamic Programming (Global Solution 2026.2 - FIAP).

Uso:
    python main.py              --> menu interativo
    python main.py --demo       --> demonstracao completa, sem interacao
    python main.py --testes     --> executa os testes automaticos
    python main.py --heartbeat  --> verifica periodicamente os componentes

Requer apenas Python 3.9+ (biblioteca padrao, sem instalar nada).
"""
from __future__ import annotations

import sys
import unittest
from typing import List, Optional

from alertabairro import benchmark
from alertabairro.dados import (CENARIOS_ALAGAMENTO, LOCAIS, OCORRENCIAS_EXEMPLO,
                                construir_grafo)
from alertabairro.priorizacao import (ResultadoPriorizacao, guloso_por_densidade,
                                      horas_para_blocos, mochila_memoizacao,
                                      mochila_tabulacao, planejar_dia,
                                      ranking_por_risco)
from alertabairro.rota_segura import ComparacaoRotas, RoteadorSeguro
from alertabairro.heartbeat import demonstrar_heartbeat

LINHA = "=" * 78


def titulo(texto: str) -> None:
    print(f"\n{LINHA}\n{texto}\n{LINHA}")


# ------------------------------------------------------------ rota segura
def mostrar_comparacao(c: ComparacaoRotas) -> None:
    print(f"\nDe {c.origem} para {c.destino}")
    for nome, rota in (("Trajeto padrao", c.padrao), ("Trajeto seguro", c.segura)):
        if rota is None:
            print(f"  {nome}: sem caminho")
        else:
            print(f"  {nome}: {' -> '.join(rota.caminho)}  "
                  f"({rota.distancia_m} m, {rota.trechos_alagados} trecho(s) alagado(s))")
    print(f"  >> {c.aviso}")


def nome_do_local(codigo: str) -> str:
    for nome, cod in LOCAIS.items():
        if cod == codigo:
            return f"{nome} ({codigo})"
    return codigo


def demo_rotas() -> None:
    titulo("1) ROTA SEGURA - grafo + programacao dinamica por tabulacao")
    roteador = RoteadorSeguro(construir_grafo())
    estacao = LOCAIS["Estacao Jardim Sao Paulo-Ayrton Senna"]
    casas = [LOCAIS["Casa da Marcia"], LOCAIS["Casa da Mariana"]]
    for cenario in ("Chuva forte", "Estacao isolada"):
        print(f"\n--- Cenario: {cenario} | alagados: "
              f"{', '.join('-'.join(t) for t in CENARIOS_ALAGAMENTO[cenario])}")
        for casa in casas:
            mostrar_comparacao(roteador.comparar(casa, estacao, CENARIOS_ALAGAMENTO[cenario]))

    print("\n--- Memoizacao: repetindo consultas ja feitas")
    for casa in casas:
        roteador.comparar(casa, estacao, CENARIOS_ALAGAMENTO["Chuva forte"])
    print(f"  Consultas: {roteador.consultas} | respondidas pelo cache: "
          f"{roteador.acertos_cache}")


# ------------------------------------------------------------ priorizacao
def mostrar_ranking() -> None:
    print(f"\n{'Pos':>3} {'ID':<6} {'Tipo':<24} {'Local':<7} {'Risco':>5} {'Apoios':>6} "
          f"{'Custo':>5} {'Pontos':>6}")
    for pos, o in enumerate(ranking_por_risco(OCORRENCIAS_EXEMPLO), 1):
        print(f"{pos:>3} {o.id:<6} {o.tipo:<24} {o.local:<7} {o.nivel_risco:>5} "
              f"{o.apoios:>6} {o.custo_blocos:>5} {o.pontuacao:>6}")
    print("  (custo em blocos de 30 min; ocorrencias resolvidas nao entram)")


def mostrar_plano(r: ResultadoPriorizacao) -> None:
    print(f"\n[{r.metodo}] pontuacao {r.pontuacao_total} | "
          f"{r.custo_total}/{r.capacidade_blocos} blocos usados | "
          f"estados: {r.subproblemas} | cache: {r.reutilizacoes} | {r.tempo_ms:.2f} ms")
    for ordem, o in enumerate(r.escolhidas, 1):
        print(f"   {ordem}. {o.id} {o.tipo} em {o.local} "
              f"({o.pontuacao} pts, {o.custo_blocos * 30} min)")
    if r.adiadas:
        print(f"   Adiadas: {', '.join(o.id for o in r.adiadas)}")


def demo_priorizacao(horas: float = 5.5) -> None:
    titulo(f"2) PRIORIZACAO DA ZELADORIA - mochila 0/1 ({horas} h de equipe no dia)")
    print("\nRanking de risco das ocorrencias pendentes:")
    mostrar_ranking()

    tab = planejar_dia(OCORRENCIAS_EXEMPLO, horas, "tabulacao")
    memo = planejar_dia(OCORRENCIAS_EXEMPLO, horas, "memoizacao")
    pendentes = [o for o in OCORRENCIAS_EXEMPLO if o.pendente]
    gul = guloso_por_densidade(pendentes, horas_para_blocos(horas))
    mostrar_plano(tab)
    mostrar_plano(memo)
    mostrar_plano(gul)
    print(f"\nTabulacao e memoizacao chegam ao mesmo valor: "
          f"{tab.pontuacao_total == memo.pontuacao_total}")
    ganho = tab.pontuacao_total - gul.pontuacao_total
    print(f"Ganho do Dynamic Programming sobre o greddy: {ganho:+d} pontos de risco")


def demo_benchmark() -> None:
    titulo("3) EFICIENCIA - forca bruta x memoizacao x tabulacao")
    for linha in benchmark.executar([8, 12, 16, 20, 50, 100, 200]):
        print(linha)
    print("\ncham = chamadas recursivas | est = estados (i, c) calculados")


def demo() -> None:
    demo_rotas()
    demo_priorizacao()
    demo_benchmark()


# ------------------------------------------------------------------ menu
def ler(msg: str) -> Optional[str]:
    try:
        return input(msg).strip()
    except EOFError:
        return None


def escolher_indice(msg: str, tamanho: int) -> Optional[int]:
    valor = ler(msg)
    if valor is not None and valor.isdigit() and 1 <= int(valor) <= tamanho:
        return int(valor) - 1
    print("Opcao invalida.")
    return None


def menu_rota(roteador: RoteadorSeguro) -> None:
    nomes = list(LOCAIS)
    for i, nome in enumerate(nomes, 1):
        print(f"  {i}. {nome} ({LOCAIS[nome]})")
    o = escolher_indice("Origem (numero): ", len(nomes))
    d = escolher_indice("Destino (numero): ", len(nomes))
    if o is None or d is None:
        return
    cenarios = list(CENARIOS_ALAGAMENTO)
    for i, nome in enumerate(cenarios, 1):
        print(f"  {i}. {nome}")
    print(f"  {len(cenarios) + 1}. Informar trechos alagados manualmente")
    s = escolher_indice("Cenario (numero): ", len(cenarios) + 1)
    if s is None:
        return
    if s < len(cenarios):
        alagados = CENARIOS_ALAGAMENTO[cenarios[s]]
    else:
        texto = ler("Trechos alagados (ex.: C2-C3, B3-C3): ") or ""
        try:
            alagados = [tuple(p.strip().upper().split("-")) for p in texto.split(",") if p.strip()]
            if any(len(t) != 2 for t in alagados):
                raise ValueError("Use o formato A1-B1, separado por virgulas.")
        except ValueError as erro:
            print(f"Entrada invalida: {erro}")
            return
    try:
        mostrar_comparacao(roteador.comparar(LOCAIS[nomes[o]], LOCAIS[nomes[d]], alagados))
    except ValueError as erro:
        print(f"Erro: {erro}")


def menu_priorizacao() -> None:
    texto = ler("Horas de equipe disponiveis no dia (ex.: 5.5): ")
    try:
        horas = float((texto or "").replace(",", "."))
        if horas <= 0:
            raise ValueError
    except ValueError:
        print("Valor invalido.")
        return
    demo_priorizacao(horas)


def menu() -> None:
    roteador = RoteadorSeguro(construir_grafo())
    while True:
        print(f"\n{LINHA}\nALERTABAIRRO - Dynamic Programming\n{LINHA}")
        print("1. Rota segura (grafo + tabulacao)")
        print("2. Priorizar ocorrencias do dia (tabulacao e memoizacao)")
        print("3. Comparar eficiencia dos algoritmos")
        print("4. Demonstracao completa")
        print("5. Rodar testes")
        print("6. Heartbeat (monitoramento dos algoritmos)")
        print("0. Sair")
        
        opcao = ler("Escolha: ")
        if opcao in (None, "0"):
            break
        if opcao == "1":
            menu_rota(roteador)
        elif opcao == "2":
            menu_priorizacao()
        elif opcao == "3":
            demo_benchmark()
        elif opcao == "4":
            demo()
        elif opcao == "5":
            rodar_testes()
        elif opcao == "6":
            demonstrar_heartbeat()
        else:
            print("Opcao invalida.")


def rodar_testes() -> bool:
    suite = unittest.defaultTestLoader.discover("tests", top_level_dir=".")
    return unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful()


def main(argv: List[str]) -> int:
    try:  # acentos corretos no terminal do Windows
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    if "--demo" in argv:
        demo()
    elif "--testes" in argv:
        return 0 if rodar_testes() else 1
    elif "--heartbeat" in argv:
        demonstrar_heartbeat()
    else:
        menu()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
