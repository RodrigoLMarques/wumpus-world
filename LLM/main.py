# Nomes:
# - Rodrigo Lopes Marques
# - Filipe Depieri
# - João Augusto Paixão Rocha

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from LegolasAgent import LegolasAgent
from Types import WorldConfig
from World import WumpusWorldEnv

llm = ChatGroq(
    model="qwen/qwen3-32b",
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.0,
    reasoning_format="parsed",
)

config = WorldConfig(size_x=4, size_y=4, wumpus_count=1, pit_count=1, gold_count=1)
world = WumpusWorldEnv(config)
agente = LegolasAgent(world)

world.print_world()

SYSTEM_PROMPT = """Você é um agente explorando o Mundo de Wumpus: uma caverna 4x4 com perigos e um tesouro.
A posição inicial e saída é (0,0). O objetivo é pegar o ouro e escalar a saída.

Sistema de coordenadas (IMPORTANTE):
  (0,0) é o canto superior esquerdo do mapa.
  "direita" aumenta x | "esquerda" diminui x
  "baixo"   aumenta y | "cima"     diminui y
  Da posição (0,0): "cima" e "esquerda" são paredes (inválidas).
  O mapa vai de x=0..3 e y=0..3. Sempre verifique "Movimentos válidos" no estado antes de agir.

Pontuação:
  +1000: Sair vivo com o ouro
  -1000: Morrer (Wumpus ou Abismo)
     -1: Por cada ação executada
    -10: Por usar a flecha

Sensores da célula atual (válidos desde o início, não apenas ao mover):
  stench (fedor): Wumpus em célula adjacente — NÃO entre em células adjacentes sem atirar ou ter certeza de qual é segura
  breeze (brisa): Abismo em célula adjacente — NÃO entre em células adjacentes sem ter certeza de qual é segura
  glitter (brilho): Ouro na célula atual — use pegar_ouro imediatamente

REGRA CRÍTICA: Sempre analise os sensores do estado atual ANTES de decidir o próximo movimento.
Se stench=True ou breeze=True, deduza quais células adjacentes são perigosas antes de agir.

Ferramentas disponíveis:

andar: Move o agente em uma direção.
Args: direcao (string): "direita", "esquerda", "cima", "baixo"
Exemplo:
{
  "action": "andar",
  "action_input": {"direcao": "direita"}
}
Moveu para (1,0). Sensores: stench=False breeze=True glitter=False

atirar: Dispara uma flecha em linha reta. Veja "Flechas" no estado atual para saber quantas restam.
Args: direcao (string): "direita", "esquerda", "cima", "baixo"
Exemplo:
{
  "action": "atirar",
  "action_input": {"direcao": "cima"}
}
A flecha errou o alvo. Silêncio.

pegar_ouro: Coleta o ouro se estiver na mesma célula (use quando glitter=True).
Exemplo:
{
  "action": "pegar_ouro",
  "action_input": {}
}
Ouro coletado!

escalar_saida: Sai da caverna. Só funciona na posição (0,0). Use após pegar o ouro.
Exemplo:
{
  "action": "escalar_saida",
  "action_input": {}
}
Você saiu da caverna com o ouro! Missão cumprida!

Para usar uma ferramenta, responda com:
Action:
{
  "action": "NOME_DA_FERRAMENTA",
  "action_input": {"PARAMETRO": "VALOR"}
}

O ciclo deve ser SEMPRE:
Thought: O que devo fazer agora com base no que sei?
Action: (bloco JSON acima)
Observation: (resultado da ferramenta)
... (repetir se necessário)
Final Answer: Resposta final em linguagem natural quando a missão estiver concluída ou for impossível.
"""


def get_celulas_adjacentes() -> dict:
    s = agente.status
    adjacentes = {}
    if s.x > 0: adjacentes["esquerda"] = f"({s.x-1},{s.y})"
    if s.x < world.config.size_x - 1: adjacentes["direita"] = f"({s.x+1},{s.y})"
    if s.y > 0: adjacentes["cima"] = f"({s.x},{s.y-1})"
    if s.y < world.config.size_y - 1: adjacentes["baixo"] = f"({s.x},{s.y+1})"
    return adjacentes


def get_estado() -> str:
    s = agente.status
    p = world.get_perception(s.x, s.y)
    wumpus = "vivo" if world.wumpus_alive else "morto"
    adjacentes = get_celulas_adjacentes()
    adj_str = " | ".join(f"{d}→{pos}" for d, pos in adjacentes.items())
    return (
        f"\nEstado atual:\n"
        f"  Posição: ({s.x},{s.y}) | Direção: {s.direction.name}\n"
        f"  Vivo: {s.is_alive} | Ouro em mãos: {s.has_gold} | Flechas: {s.arrows}\n"
        f"  Wumpus: {wumpus} | Pontuação: {agente.score}\n"
        f"  Sensores: stench={p.stench} breeze={p.breeze} glitter={p.glitter}\n"
        f"  Células adjacentes: {adj_str}\n"
    )


def call_tool(texto: str) -> str:
    try:
        inicio = texto.index("Action:") + len("Action:")
        resto = texto[inicio:].strip()
        inicio_json = resto.index("{")
        fim_json = resto.rindex("}") + 1
        data = json.loads(resto[inicio_json:fim_json])

        action = data["action"]
        params = data.get("action_input", {})

        if action == "andar":
            resultado = agente.andar(params["direcao"])
        elif action == "atirar":
            resultado = agente.atirar(params["direcao"])
        elif action == "pegar_ouro":
            resultado = agente.pegar_ouro()
        elif action == "escalar_saida":
            resultado = agente.escalar_saida()
        else:
            return f"Ferramenta desconhecida: {action}"

        return resultado + "\n" + get_estado()
    except Exception as e:
        return f"Erro ao executar ferramenta: {e}"


missao = input("Missão: ")
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": f"Missão: {missao}\n{get_estado()}"},
]

MAX_ITERACOES = 20

print("\n=== INICIANDO O AGENTE ===\n")

for i in range(MAX_ITERACOES):
    if not agente.status.is_alive or agente.status.has_exited:
        break

    print(f"--- Iteração {i + 1} ---")

    response = llm.invoke(messages, stop=["Observation:"])
    texto_gerado = response.content
    print(texto_gerado)

    if "Final Answer:" in texto_gerado:
        print("\nAgente concluiu a missão!")
        break

    if "Action:" in texto_gerado:
        resultado_ferramenta = call_tool(texto_gerado)
        print(f"Observation:\n{resultado_ferramenta}\n")
        historico_turno = texto_gerado + "\nObservation:\n" + resultado_ferramenta + "\n"
        messages.append({"role": "assistant", "content": historico_turno})
    else:
        print("\nO modelo quebrou a formatação esperada.")
        break
else:
    print("\nLimite de iterações atingido.")

print("\n=== RESULTADO FINAL ===")
print(f"Status : {'Vivo' if agente.status.is_alive else 'Morto'}")
print(f"Ouro   : {'Sim' if agente.status.has_gold else 'Não'}")
print(f"Saiu   : {'Sim' if agente.status.has_exited else 'Não'}")
print(f"Pontos : {agente.score}")
agente.print_memory()
