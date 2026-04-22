from Types import WorldConfig, AgentStatus, Direction, PerceptionCell, Cell
from World import WumpusWorldEnv

DIRECTION_MAP = {
    "direita": Direction.RIGHT,
    "esquerda": Direction.LEFT,
    "cima": Direction.TOP,
    "baixo": Direction.BOTTOM,
}

class LegolasAgent:
    def __init__(self, world: WumpusWorldEnv):
        self.score = 0
        self.world = world
        self.memory_world = {} # dicionario de "struct" de percetpion_cell
        self.feel_cell(0, 0)
        self.status = AgentStatus(x=0, y=0, direction=Direction.RIGHT, has_gold=False, is_alive=True)

    def find_path(self):
        from collections import deque

        # atualiza pontuação de todas as células conhecidas
        for pos in list(self.memory_world.keys()):
            if self.memory_world[pos].travel > 0:
                self.cell_points(pos[0], pos[1])

        start = (self.status.x, self.status.y)

        # BFS: expande por células visitadas, busca a melhor não visitada
        queue = deque([(start, [start])])
        seen = {start}
        candidates = []  # (pontos, caminho)

        while queue:
            (cx, cy), path = queue.popleft()

            for nx, ny in [(cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)]:
                if (nx, ny) in seen:
                    continue
                cell = self.memory_world.get((nx, ny))
                if cell is None or cell.points == -999:
                    continue

                seen.add((nx, ny))
                new_path = path + [(nx, ny)]

                if cell.travel == 0:
                    # célula não visitada: candidata a destino
                    candidates.append((cell.points, new_path))
                else:
                    # célula visitada: pode atravessar
                    queue.append(((nx, ny), new_path))

        if not candidates:
            return None

        # retorna o caminho até a célula com maior pontuação
        candidates.sort(key=lambda x: -x[0])
        return candidates[0][1]  # lista de (x, y), sem incluir a posição atual

    def find_best_direction(self):
        pass
    
    def turn_around(self, direction_end, direction_ini):
        count = abs(direction_end - direction_ini)
        facing = direction_ini
        for _ in range(count):
            facing = (facing % 4) + 1
    
        self.status.direction = facing
        return facing 
    
    def cell_points(self, pos_x, pos_y):
        adjacent = [
            (pos_x - 1, pos_y),
            (pos_x + 1, pos_y),
            (pos_x, pos_y - 1),
            (pos_x, pos_y + 1),
        ]

        for item in adjacent:
            cell = self.memory_world.get(item)
            if cell is None:
                continue

            if cell.travel > 0:
                points = max(0, 5 - cell.travel)
            else:
                points = 5 + cell.stench * (-5) + cell.breeze * (-5)
                if points < -5:
                    points = -999

            self.memory_world[item] = PerceptionCell(
                stench=cell.stench,
                breeze=cell.breeze,
                glitter=cell.glitter,
                travel=cell.travel,
                points=points,
            )
    def feel_cell(self, pos_x, pos_y):
        perception = self.world.get_perception(pos_x, pos_y)


        stench = 1 if perception.stench else 0
        breeze = 1 if perception.breeze else 0
        glitter = 1 if perception.glitter else 0

        # alterar informações da célula atual
        existing = self.memory_world.get((pos_x, pos_y))
        self.memory_world[(pos_x, pos_y)] = PerceptionCell(
            stench = 0,
            breeze = 0,
            glitter = glitter,
            travel = existing.travel + 1 if existing else 1,
            points = 0,
        )

        # atualizar informações das células adjacentes
        adjacent = [
            (pos_x - 1, pos_y),
            (pos_x + 1, pos_y),
            (pos_x, pos_y - 1),
            (pos_x, pos_y + 1),
        ]
        for (i, j) in adjacent:
            if (i < 0 or i >= self.world.config.size_x) or (j < 0 or j >= self.world.config.size_y):
                continue
            
            existing = self.memory_world.get((i, j))

            # o agente viajou aqui, então já sabe o que tem nessa célula
            if existing and existing.travel > 0:
                continue

            if existing:
                # se já tem alguma informação sobre a célula, atualiza somando os valores
                self.memory_world[(i, j)] = PerceptionCell(
                    stench=existing.stench + stench,
                    breeze=existing.breeze + breeze,
                    glitter=existing.glitter,
                    travel=existing.travel,
                    points=0,
                )
            else:
                # se não tem informação, cria uma nova entrada com os valores atuais
                self.memory_world[(i, j)] = PerceptionCell(
                    stench=stench,
                    breeze=breeze,
                    glitter=False,
                    travel=0,
                    points=0,
                )
                
        return perception

    def print_memory(self):
        size_x = self.world.config.size_x
        size_y = self.world.config.size_y

        print("\n=== MEMÓRIA DO AGENTE ===")
        print(f"Posição atual: ({self.status.x}, {self.status.y})\n")

        for y in range(size_y):
            row = ""
            for x in range(size_x):
                if (x, y) == (self.status.x, self.status.y):
                    row += "[ AGT ]"
                elif (x, y) in self.memory_world:
                    cell = self.memory_world[(x, y)]
                    symbols = ""
                    symbols += "W" if cell.stench > 0 else "."
                    symbols += "P" if cell.breeze > 0 else "."
                    symbols += "G" if cell.glitter > 0 else "."
                    symbols += "V" if cell.travel > 0 else "."
                    row += f"[{symbols}]"
                else:
                    row += "[     ]"
            print(row)
        print()

    def move_forward(self):
        new_x = self.status.x
        new_y = self.status.y

        if self.status.direction == Direction.RIGHT:
            new_x += 1
        elif self.status.direction == Direction.LEFT:
            new_x -= 1
        elif self.status.direction == Direction.TOP:
            new_y -= 1
        elif self.status.direction == Direction.BOTTOM:
            new_y += 1

        if (new_x < 0 or new_x >= self.world.config.size_x) or (new_y < 0 or new_y >= self.world.config.size_y):
            # tentou atravessar parede
            return
        
        if (self.world.map[new_x][new_y] == Cell.WUMPUS):
            print("Morreu ao entrar na célula com Wumpus!")
            self.status.is_alive = False
            return
        if (self.world.map[new_x][new_y] == Cell.PIT):
            print("Morreu ao entrar na célula com Poço!")
            self.status.is_alive = False
            return

        perception = self.feel_cell(new_x, new_y)

        self.status.x = new_x
        self.status.y = new_y

        return perception

    # ── Ferramentas da LLM ──────────────────────────────────────────────

    def andar(self, direcao: str) -> str:
        direction = DIRECTION_MAP.get(direcao.lower())
        if not direction:
            return f"Direção inválida: '{direcao}'. Use: direita, esquerda, cima, baixo"

        self.score -= 1
        self.status.direction = direction
        perception = self.move_forward()

        if not self.status.is_alive:
            self.score -= 1000
            return "Você morreu! Havia um perigo nessa célula."
        if perception is None:
            return "Não foi possível mover nessa direção (parede)."

        return (
            f"Moveu para ({self.status.x},{self.status.y}). "
            f"Sensores: stench={perception.stench} breeze={perception.breeze} glitter={perception.glitter}"
        )

    def atirar(self, direcao: str) -> str:
        if self.status.arrows <= 0:
            return "Sem flechas disponíveis."

        direction = DIRECTION_MAP.get(direcao.lower())
        if not direction:
            return f"Direção inválida: '{direcao}'. Use: direita, esquerda, cima, baixo"

        self.score -= 1   # ação
        self.score -= 10  # uso da flecha
        self.status.arrows -= 1

        killed = self.world.shoot_arrow(self.status.x, self.status.y, direction)
        if killed:
            return "Você ouviu um grito! O Wumpus foi morto!"
        return "A flecha errou o alvo. Silêncio."

    def pegar_ouro(self) -> str:
        self.score -= 1
        if self.world.map[self.status.x][self.status.y] != Cell.GOLD:
            return "Não há ouro aqui."
        self.status.has_gold = True
        self.world.map[self.status.x][self.status.y] = Cell.EMPTY
        return "Ouro coletado!"

    def escalar_saida(self) -> str:
        self.score -= 1
        if self.status.x != 0 or self.status.y != 0:
            return "Você só pode sair pela posição inicial (0,0)."
        if not self.status.has_gold:
            self.status.has_exited = True
            return "Você saiu da caverna sem o ouro."
        self.score += 1000
        self.status.has_exited = True
        return "Você saiu da caverna com o ouro! Missão cumprida!"

