# Registro de prompts de IA · AlertaBairro · Dynamic Programming

**Global Solution 2026.2 · FIAP · Turma 2ESPG**

Ferramenta: Claude e Chat GPT, usados como copilotos para planejar, gerar e revisar o código desta entrega.
Integrantes: Arthur Araújo Tenório (562272) · Breno Gonçalves Báo (564037) · Rafael Falaguasta Ferraz (561714) · Vinicius Cavalcanti dos Reis (562063)

## Prompts utilizados

| # | Prompt | O que a IA gerou | Como foi usado |
|---|---|---|---|
| 1 | Anexo do briefing da GS (PDF) + "analise esse documento" | Resumo do briefing: regras, prazos, entregas das 7 disciplinas e pontos de atenção | Entender as exigências antes de dividir as tarefas |
| 2 | Anexo do trabalho de Agile (AlertaBairro) + "esse é nosso trabalho de agile e eu irei ficar responsável por network e dynamic programming, qual o melhor jeito de fazer esses trabalhos? e por qual fica melhor começar" | Proposta de ordem de trabalho e de algoritmos (grafos, tabulação e memoização) ligados ao backlog | Definir o desenho da solução de Dynamic Programming |
| 3 | "a partir desse contexto de análise dos documentos quero que faça a parte de dynamic programming com tudo que é pedido e seguindo todas as orientações passadas [...] só não precisa fazer o README ainda" | Código Python completo (`main.py`, pacote `alertabairro/` e 28 testes) | Base do código entregue |
| 4 | Envio dos nomes e RMs dos integrantes | `README.md` com a Ficha da CitizenTech e este `prompts.md` | Documentação da entrega |


## Integração realizada com ChatGPT (11/11/2026)

**Solicitação do integrante:** "quero que realize essa integração e deixe tudo pronto para minha entrega ao professor". Contexto: comparação do ZIP prévio com uma segunda versão contendo rota segura por tabulação.

**Uso:** preservação do projeto prévio, incorporação do algoritmo de tabulação em `alertabairro/tabulacao_rotas.py`, integração em `rota_segura.py`, atualização de `main.py` e do README, e inclusão de seis testes em `tests/test_tabulacao_rotas.py`. Foram executados os testes e a demonstração.
