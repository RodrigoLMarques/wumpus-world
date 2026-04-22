# Wumpus World

Simulação do Mundo do Wumpus em Python para a disciplina de Inteligência Artificial.

## Agentes

**`Agent/`** — Agente determinístico com BFS e heurística de pontuação por célula.

**`LLM/`** — Agente baseado em LLM (Groq) que recebe missões em linguagem natural e age via ReAct. Ferramentas: `andar`, `atirar`, `pegar_ouro`, `escalar_saida`.

## Como rodar

```bash
# Agente clássico
cd Agent && python main.py

# Agente LLM
cp .env.example .env  # preencha GROQ_API_KEY no .env
cd LLM && python main.py
```

## Grupo

- Rodrigo Lopes Marques
- Filipe Depieri
- João Augusto Paixão Rocha
