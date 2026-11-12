"""AlertaBairro - Dynamic Programming (Global Solution 2026.2 - FIAP).

Modulos:
    grafo         - grafo viario do entorno da estacao e caminho minimo (Dijkstra)
    rota_segura   - rota que desvia dos pontos alagados, com memoizacao de consultas
    priorizacao   - priorizacao da zeladoria como problema da mochila 0/1
                    (tabulacao, memoizacao e forca bruta para comparacao)
    benchmark     - comparacao de eficiencia entre as abordagens
    dados         - dados simulados (mapa, cenarios de chuva e ocorrencias)
"""
