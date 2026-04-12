# Nomes:
# - Rodrigo Lopes Marques
# - Filipe Depieri
# - João Augusto Paixão Rocha

from LegolasAgent import LegolasAgent
from Types import DIRECTION_FROM_DELTA, WorldConfig
from World import WumpusWorldEnv

def step_to_direction(from_pos, to_pos):
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    return DIRECTION_FROM_DELTA[(dx, dy)]

config = WorldConfig(size_x=4, size_y=4, wumpus_count=1, pit_count=1, gold_count=1)

world = WumpusWorldEnv(config)
world.print_world()

legolas = LegolasAgent(world)

action_count = 0
path_taken = [(legolas.status.x, legolas.status.y)]

print(f"Início: pos=({legolas.status.x},{legolas.status.y}) dir={legolas.status.direction.name}\n")

iteration = 0
while legolas.status.is_alive and not legolas.status.has_gold:
    path = legolas.find_path()

    if not path or len(path) < 2:
        print("Sem caminho disponível. Exploração encerrada.")
        break

    print(f"--- Iteração {iteration} | Destino: {path[-1]} | Caminho: {path} ---")

    for i in range(1, len(path)):
        if not legolas.status.is_alive or legolas.status.has_gold:
            break

        direction = step_to_direction(path[i - 1], path[i])
        legolas.status.direction = direction
        perception = legolas.move_forward()
        action_count += 1
        path_taken.append((legolas.status.x, legolas.status.y))

        if not legolas.status.is_alive:
            print(f"  MOVE_FORWARD | pos=({legolas.status.x},{legolas.status.y}) dir={legolas.status.direction.name} | [sem percepção]")
            print("\n=== AGENTE MORREU. ===")
            break

        print(
            f"  MOVE_FORWARD | pos=({legolas.status.x},{legolas.status.y})"
            f" dir={legolas.status.direction.name}"
            f" | stench={perception.stench} breeze={perception.breeze} glitter={perception.glitter}"
        )

        if legolas.status.has_gold:
            print("\n=== OURO ENCONTRADO! AGENTE PARA. ===")
            break

    iteration += 1
    if iteration > 30:
        print("Limite de iterações atingido.")
        break

print("\n=== RESULTADO FINAL ===")
print(f"Status : {'Vivo' if legolas.status.is_alive else 'Morto'}")
print(f"Ouro   : {'Sim' if legolas.status.has_gold else 'Não'}")
print(f"Ações  : {action_count}")
print(f"Caminho: {path_taken}")
legolas.print_memory()
