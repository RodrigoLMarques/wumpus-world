from enum import Enum
from dataclasses import dataclass

class Cell(Enum):
    EMPTY = 0
    WUMPUS = 1
    PIT = 2
    GOLD = 3

CELL_SYMBOLS = {
    Cell.EMPTY:  ".",
    Cell.WUMPUS: "W",
    Cell.PIT:    "P",
    Cell.GOLD:   "G",
}

@dataclass
class WorldConfig:
    size_x: int
    size_y: int
    wumpus_count: int
    pit_count: int
    gold_count: int
    seed: int = None

@dataclass
class PerceptionAround:
    stench: bool   # wumpus adjacente
    breeze: bool   # poço adjacente
    glitter: bool  # ouro na mesma celula

@dataclass
class PerceptionCell:
    stench : int   # wumpus adjacente
    breeze : int   # poço adjacente
    glitter: bool   # ouro na mesma celula
    travel : int   # quantidade viajada da celula
    points : int   #pontuação da celula

class Direction(Enum):
    RIGHT  = 1
    TOP    = 2
    LEFT   = 3
    BOTTOM = 4
    
@dataclass
class AgentStatus:
    x: int
    y: int
    direction: Direction
    has_gold: bool
    is_alive: bool

DIRECTION_FROM_DELTA = {
    ( 1,  0): Direction.RIGHT,
    (-1,  0): Direction.LEFT,
    ( 0, -1): Direction.TOP,
    ( 0,  1): Direction.BOTTOM,
}