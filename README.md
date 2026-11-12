# AlertaBairro · Dynamic Programming

**FIAP · Global Solution 2026.2 · CitizenTech · Engenharia de Software · Turma 2ESPG**

## Ficha da CitizenTech

| Campo | Resposta |
|---|---|
| **Nome da CitizenTech** | AlertaBairro |
| **Cidade e bairro** | São Paulo (SP), bairro Jardim São Paulo, entorno da Estação Jardim São Paulo-Ayrton Senna (Linha 1-Azul) |
| **Cidadão beneficiado** | Moradores e trabalhadores do entorno da estação que se deslocam a pé por ruas baixas sujeitas a alagamento e usuários do metrô que dependem da estação. Do lado do poder público, o agente de zeladoria da subprefeitura |
| **Problema, em uma frase** | Moradores, comerciantes e passageiros que circulam pelo entorno da Estação Jardim São Paulo não têm como avisar a subprefeitura sobre bueiros entupidos e lixo acumulado antes da chuva, nem como saber em tempo real onde está alagado e por onde desviar quando ela chega |
| **Como funciona** | (1) Antes da chuva, o morador registra e apoia ocorrências de drenagem. (2) A zeladoria prioriza a limpeza por risco de alagamento. (3) Durante a chuva, os moradores reportam pontos alagados e o sistema alerta quem está na região. (4) O cidadão informa origem e destino e recebe um trajeto que evita os trechos alagados |
| **O que cada parte faz** | **Dynamic Programming (este repositório):** a rota segura (grafos + programação dinâmica por tabulação, Dijkstra para referência e cache de consultas) e a priorização da zeladoria (problema da mochila 0/1, por tabulação e por memoização). As demais disciplinas constroem as outras partes da mesma solução |
| **Link do repositório** | *[https://github.com/AlertaBairro/DynamicProgramming-GSCitizenTech.git]* |
| **Indicador de impacto** | Tempo médio entre o registro e a limpeza do bueiro; número de pessoas alertadas por evento de chuva; redução de alagamentos recorrentes no mesmo ponto ao longo do semestre. *Neste código:* pontuação de risco eliminada por dia de equipe (ver seção 4) |
| **ODS conectados** | **ODS 9** (dados colaborativos para manutenção preventiva da drenagem), **ODS 11** (menos pessoas expostas a alagamentos e mais previsibilidade no deslocamento) e **ODS 13** (adaptação a eventos extremos de chuva, com resposta mais rápida) |

## Integrantes

| Nome | RM |
|---|---|
| Arthur Araújo Tenório | 562272 |
| Breno Gonçalves Báo | 564037 |
| Rafael Falaguasta Ferraz | 561714 |
| Vinicius Cavalcanti dos Reis | 562063 |

---

## 1. O que este código resolve

O código implementa em Python duas necessidades do AlertaBairro que aparecem no backlog do projeto:

| Funcionalidade | Histórias do backlog | Técnica |
|---|---|---|
| **Rota segura**: trajeto que desvia dos pontos alagados reportados | US09 e US10 | Grafos + tabulação de rotas + Dijkstra de referência + cache de consultas |
| **Priorização da zeladoria**: o que a equipe atende no dia | US04 (com US02 e US05) | Tabulação e memoização (mochila 0/1) |

As técnicas de Programação Dinâmica pedidas na atividade (memoização, tabulação e grafos) estão todas presentes. Cada uma resolve um pedaço real do problema.

## 2. Como executar

Requisitos: **Python 3.9 ou superior**. Não há dependências externas (só a biblioteca padrão).

```bash
python main.py            # menu interativo
python main.py --demo     # demonstração completa, sem interação
python main.py --testes   # roda os 34 testes automáticos
```

Menu: (1) rota segura, (2) priorizar ocorrências do dia, (3) comparar eficiência, (4) demonstração completa, (5) testes.

## 3. Estrutura do projeto

```
├── main.py                  menu, demonstração e execução dos testes
├── alertabairro/
│   ├── grafo.py             grafo viário e Dijkstra
│   ├── rota_segura.py       comparação de rotas, com cache de consultas
│   ├── tabulacao_rotas.py  rota segura por programação dinâmica bottom-up
│   ├── priorizacao.py       mochila 0/1: tabulação, memoização, força bruta e guloso
│   ├── benchmark.py         comparação de eficiência
│   └── dados.py             mapa, cenários de chuva e ocorrências (simulados)
├── tests/                   34 testes automatizados (unittest)
├── prompts.md               registro dos prompts de IA usados
└── README.md
```

## 4. Algoritmos e funcionalidades

### 4.1 Rota segura: grafos + tabulação (`grafo.py`, `tabulacao_rotas.py`, `rota_segura.py`)

**Modelagem.** Cada esquina é um nó e cada trecho de rua é uma aresta com distância em metros. Um ponto alagado reportado por um morador marca o trecho como alagado.

**Algoritmo principal.** Programação dinâmica por tabulação (bottom-up). O estado `dp[k][v]` representa o menor par lexicográfico `(quantidade de trechos alagados, distância em metros)` para chegar ao nó `v` utilizando **no máximo** `k` arestas. A transição compara o estado anterior com a extensão de uma aresta de um nó vizinho. Como as distâncias são positivas, um caminho ótimo simples usa no máximo `V-1` arestas. O algoritmo guarda predecessores para reconstruir o trajeto.

**Algoritmo de referência.** Dijkstra com fila de prioridade (`heapq`). O custo de um trecho é `distância + penalidade` quando ele está alagado. A penalidade automática é a **soma de todas as distâncias do mapa + 1**, o que garante duas propriedades:

1. Qualquer rota com menos trechos alagados vence qualquer rota com mais.
2. Entre rotas com o mesmo número de trechos alagados, vence a mais curta.

Assim a rota sempre existe, mesmo com o mapa muito alagado. Se não houver caminho 100% seco (ex.: todas as ruas ao redor da estação alagadas), o sistema devolve o trajeto de **menor exposição** e avisa o cidadão para considerar adiar o deslocamento.

**O que a funcionalidade entrega:** o trajeto padrão (mais curto, ignorando alagamentos), o trajeto seguro, o desvio em metros e uma mensagem em linguagem simples.

**Cache de consultas (reutilização de resultados).** O `RoteadorSeguro` guarda cada resposta em um dicionário com chave `(origem, destino, conjunto de trechos alagados)`. Consultas repetidas (vários moradores indo do mesmo ponto para a estação sob a mesma chuva) vêm do cache. Quando um novo ponto alagado é reportado, o conjunto muda e portanto a chave também, então a rota é recalculada e nunca se devolve uma resposta desatualizada (há teste para isso).

**Complexidade.** Tabulação: `O(V·(V+E))` tempo e `O(V²)` memória para as tabelas e predecessores. Dijkstra: `O((V+E) log V)` tempo (fila de prioridade). Cada consulta nova executa um Dijkstra para a rota padrão e uma tabulação para a rota segura. A tabulação é didática, mas menos eficiente que Dijkstra em redes maiores. O cache acelera consultas repetidas sem mudanças no cenário.

> **Observação sobre a técnica.** Dijkstra é um algoritmo guloso, não programação dinâmica. A programação dinâmica propriamente dita está na **tabulação de rotas** e na **mochila 0/1** (seção 4.2). O cache de consultas evita recálculos, mas não é, por si só, a recorrência de programação dinâmica.

### 4.2 Priorização da zeladoria: mochila 0/1 (`priorizacao.py`)

**Problema real.** A equipe da subprefeitura tem poucas horas por dia e mais ocorrências pendentes do que consegue atender. Qual conjunto de ocorrências reduz mais o risco de alagamento dentro do tempo disponível?

| Mochila | No AlertaBairro |
|---|---|
| Item | Ocorrência pendente (status "recebida" ou "em atendimento"; as resolvidas ficam de fora) |
| Peso | Tempo de atendimento, em blocos de 30 minutos |
| Valor | Pontuação de risco da ocorrência |
| Capacidade | Horas da equipe no dia, convertidas em blocos |

**Pontuação de risco** (valores simulados, definidos pela equipe):

```
nível de risco = risco base do tipo + 2 se o ponto é baixo (alaga com recorrência)
   bueiro entupido = 3 · boca de lobo danificada = 3 · lixo acumulado = 2   (nível máximo 5)

pontuação = nível de risco × 10 + min(apoios, 10) × 2
```

O risco domina e os apoios dos moradores (US02) reforçam a prioridade, com teto de 10 apoios para que uma ocorrência muito apoiada não passe uma de risco bem maior.

**Recorrência** (i = primeiras i ocorrências, c = blocos disponíveis):

```
melhor(0, c) = 0
melhor(i, c) = melhor(i-1, c)                                   se custo_i > c
melhor(i, c) = max( melhor(i-1, c),
                    melhor(i-1, c - custo_i) + pontuacao_i )    caso contrário
```

A mesma recorrência foi implementada de quatro formas, para comparar:

| Implementação | Abordagem | Tempo | Espaço |
|---|---|---|---|
| `mochila_tabulacao` | **Tabulação** (bottom-up): preenche a tabela (n+1) × (C+1) e reconstrói a escolha de trás para frente | O(n·C) | O(n·C) |
| `mochila_memoizacao` | **Memoização** (top-down): recursão com dicionário, calcula só os estados alcançados a partir de (n, C) | O(n·C) no pior caso | O(n·C) |
| `mochila_forca_bruta` | Testa todos os subconjuntos (referência e conferência nos testes) | O(2ⁿ) | O(n) |
| `guloso_por_densidade` | Pega primeiro quem tem maior pontuação por bloco (estratégia intuitiva, **sem garantia de ótimo**) | O(n log n) | O(n) |

Tabulação e memoização sempre escolhem **exatamente o mesmo conjunto** (a reconstrução segue a mesma regra, e há teste para isso).

**Por que programação dinâmica e não o guloso?** Com 5h30 de equipe (11 blocos), o guloso alcança **342 pontos** e a programação dinâmica **358**: o guloso fecha o dia com a O-006 e a O-011 (22 + 20 = 42 pontos, 2 blocos) e deixa de fora a O-004, que sozinha vale 36 pontos e, junto com a O-006, rende 58 em 3 blocos. É uma diferença de **16 pontos de risco eliminado**, e é isso que a PD garante: o ótimo.

**Funcionalidades:** `ranking_por_risco` (lista ordenada de pendentes, US04), `planejar_dia` (seleção do dia por horas de equipe, com a ordem de atendimento, as ocorrências adiadas, o custo usado e os estados calculados) e a comparação entre os métodos.

### 4.3 Eficiência (`benchmark.py`)

Execução de `python main.py --demo` (n ocorrências geradas com semente fixa; capacidade = 40% do custo total). Os tempos variam conforme a máquina; as contagens de chamadas e estados são determinísticas.

| n | Força bruta | Memoização | Tabulação |
|---|---|---|---|
| 8 | 203 chamadas | 43 estados | 99 estados |
| 12 | 2.797 chamadas | 131 estados | 195 estados |
| 16 | 46.727 chamadas | 269 estados | 391 estados |
| 20 | 642.737 chamadas (~84 ms) | 436 estados | 609 estados |
| 50, 100, 200 | inviável (2ⁿ) | 2.789 · 10.467 · 44.048 estados | 3.672 · 13.231 · 55.074 estados |

Conclusões:
- A força bruta explode (mais de 13× a cada 4 ocorrências a mais) e já é impraticável acima de 20.
- A PD cresce de forma polinomial (n·C): com 200 ocorrências ainda leva alguns milissegundos.
- A **memoização calcula menos estados** que a tabulação (só os alcançáveis), mas em Python acaba **mais lenta** no tempo real, por causa do custo das chamadas recursivas. Menos estados não significa necessariamente menos tempo.
- A mochila é pseudopolinomial: o custo depende do **valor numérico** da capacidade (C), não só do número de itens. Por isso o tempo é medido em blocos de 30 minutos, não em minutos.

## 5. Dados utilizados

Nenhum dado pessoal real. Todos os dados são **simulados** e a origem está declarada em `alertabairro/dados.py`:

- **Mapa:** malha de 20 esquinas (colunas A–E, linhas 1–4, cerca de 120 m entre esquinas), criada à mão com leve desalinhamento e 4 quadras fechadas. O layout é inspirado no entorno da estação, mas **as coordenadas e os nomes (A1 a E4) não são reais**. Para usar dados reais, basta trocar `NOS` e `TRECHOS_AUSENTES` por esquinas e ruas do OpenStreetMap.
- **Cenários de chuva** (`Sem chuva`, `Chuva moderada`, `Chuva forte`, `Estação isolada`) e **13 ocorrências**: inventados para a demonstração.
- **Contexto real:** o alagamento da estação em janeiro de 2025 (186,6 mm, segundo a Defesa Civil) está descrito no trabalho de Agile Methodology.

## 6. Testes

`python main.py --testes` (ou `python -m unittest`) executa 28 testes que verificam, entre outros pontos:

- O grafo é conexo e os trechos não têm direção.
- A rota segura nunca atravessa mais trechos alagados que a padrão.
- Estação isolada gera aviso e rota de menor exposição.
- O cache não devolve resposta de um cenário diferente.
- Tabulação e memoização igualam a força bruta em todas as capacidades de 0 a 25 e em 30 casos aleatórios.
- A solução nunca excede a capacidade e nunca perde para o guloso.
- Casos de borda: sem ocorrências, capacidade zero, capacidade grande, ids repetidos, 1.500 ocorrências (recursão profunda).

## 7. Limitações

- O mapa é fictício e estático. Em produção, as ruas viriam do OpenStreetMap e os alagamentos seriam atualizados em tempo real pelos relatos.
- Os pontos alagados são modelados por trecho inteiro de rua, sem gradação de nível de água.
- A priorização não considera o deslocamento da equipe entre as ocorrências nem dependências entre elas.
- Os pesos da pontuação de risco são escolhas da equipe e poderiam ser calibrados com dados históricos da Defesa Civil.
- Neste projeto o código é uma demonstração em linha de comando. A integração com o aplicativo (tela, banco de dados e API) pertence às outras disciplinas.

## 8. Uso de IA

Foi usada IA como copiloto para estruturar e revisar o código. Os prompts estão registrados em [`prompts.md`](prompts.md).


## 6. Integração e validação final (11/11/2026)

Esta versão preserva a estrutura e a funcionalidade de priorização do trabalho prévio e integra o algoritmo `rota_segura_tabulacao` como **método principal de rota segura**. O Dijkstra permanece como rota padrão e como referência independente nos testes.

**Recorrência da rota:** para cada `k=1..V-1`, inicia-se `dp[k][v] = dp[k-1][v]` e, para cada aresta `(u,v)` de distância `d` e indicador `a` (1 se alagada, 0 caso contrário), compara-se `dp[k][v]` com `dp[k-1][u] + (a,d)`; escolhe-se o menor par lexicográfico. A condição inicial é `dp[0][origem]=(0,0)` e infinito para os demais nós. Os predecessores reconstroem o caminho.

**Validação executada:** `python main.py --testes` — **34 testes aprovados**; `python main.py --demo` — execução concluída. Os seis testes adicionados incluem comparação com Dijkstra para todos os pares de nós nos cenários de chuva, 30 grafos aleatórios reprodutíveis, grafo desconexo, origem igual ao destino, nó inexistente e preferência por trajeto sem alagamento. Testes aprovados não garantem ausência total de defeitos.

**Limitações e segurança:** mapa, distâncias, pontos alagados, ocorrências e tempos são simulados e **não correspondem a ruas reais**. A rota minimiza a quantidade de trechos reportados como alagados e, em caso de empate, a distância; não é garantia de segurança física. Em ausência de rota seca, o sistema avisa para considerar adiar o deslocamento. Não utilizar como orientação de emergência ou navegação real. O MVP web e sua integração com OpenStreetMap/serviço de roteamento estão descritos no Agile, mas **não são implementados neste ZIP**.
