import random
from Types import Cell, CELL_SYMBOLS, WorldConfig, PerceptionAround, Direction

class WumpusWorldEnv:
    def __init__(self, config: WorldConfig):
        self.map = []
        self.config = config
        self.wumpus_alive = True
        if self.config.seed is None:
            self.config.seed = random.randint(0, 2**32 - 1)
        self.generate_world()

    def generate_world(self):
        random.seed(self.config.seed)

        # gera todas as posições possíveis, exceto a posição inicial (0, 0)
        all_positions = []
        for i in range(self.config.size_x):
            for j in range(self.config.size_y):
                if (i, j) == (0, 0):
                    continue
                all_positions.append((i, j))

        # sorteia as posições para colocar os wumpus, poços e ouro
        total = self.config.wumpus_count + self.config.pit_count + self.config.gold_count
        entity_positions = random.sample(all_positions, total)

        # atribui os tipos de entidades às posições sorteadas
        assigned = {}
        index = 0
        for _ in range(self.config.wumpus_count):
            assigned[entity_positions[index]] = Cell.WUMPUS
            index += 1
        for _ in range(self.config.pit_count):
            assigned[entity_positions[index]] = Cell.PIT
            index += 1
        for _ in range(self.config.gold_count):
            assigned[entity_positions[index]] = Cell.GOLD
            index += 1

        # constrói o mapa do mundo com base nas posições atribuídas
        self.map = []
        for i in range(self.config.size_x):
            row = []
            for j in range(self.config.size_y):
                if (i, j) in assigned:
                    cell = assigned[(i, j)]
                else:
                    cell = Cell.EMPTY
                row.append(cell)
            self.map.append(row)

    def print_world(self):
        print()
        for y in range(self.config.size_y):
            line = ""
            for x in range(self.config.size_x):
                line += CELL_SYMBOLS[self.map[x][y]] + " "
            print(line)
        print()

    def get_perception(self, pos_x: int, pos_y: int) -> PerceptionAround:
        # calcula as posições adjacentes à posição atual
        adjacent = [
            (pos_x - 1, pos_y),
            (pos_x + 1, pos_y),
            (pos_x, pos_y - 1),
            (pos_x, pos_y + 1),
        ]

        # verifica se há wumpus ou poço nas posições adjacentes
        stench = False
        breeze = False
        for (i, j) in adjacent:
            if (i < 0 or i >= self.config.size_x) or (j < 0 or j >= self.config.size_y): 
                continue
            if self.map[i][j] == Cell.WUMPUS:
                stench = True
            if self.map[i][j] == Cell.PIT:
                breeze = True

        # verifica se há ouro na mesma célula
        glitter = self.map[pos_x][pos_y] == Cell.GOLD

        return PerceptionAround(
            stench=stench,
            breeze=breeze,
            glitter=glitter,
        )

    def shoot_arrow(self, pos_x: int, pos_y: int, direction: Direction) -> bool:
        deltas = {
            Direction.RIGHT:  ( 1,  0),
            Direction.LEFT:   (-1,  0),
            Direction.TOP:    ( 0, -1),
            Direction.BOTTOM: ( 0,  1),
        }
        dx, dy = deltas[direction]
        x, y = pos_x + dx, pos_y + dy
        while 0 <= x < self.config.size_x and 0 <= y < self.config.size_y:
            if self.map[x][y] == Cell.WUMPUS:
                self.map[x][y] = Cell.EMPTY
                self.wumpus_alive = False
                return True
            x += dx
            y += dy
        return False
