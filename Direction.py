import enum


class Direction(enum.Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    def minus_90(self):
        return Direction((self.value - 1) % 4)

    def plus_90(self):
        return Direction((self.value + 1) % 4)

    def minus_180(self):
        return Direction((self.value - 2) % 4)

    def get_API_representation(self):
        if self == Direction.NORTH:
            return "n"
        elif self == Direction.EAST:
            return "e"
        elif self == Direction.SOUTH:
            return "s"
        elif self == Direction.WEST:
            return "w"

    def add_to_direction(self, direction):
        return (self.value + direction.value) % 4

    def add_to_position(self, position: tuple[int, int]):
        if self == Direction.NORTH:
            return position[0], position[1] + 1
        elif self == Direction.EAST:
            return position[0] + 1, position[1]
        elif self == Direction.SOUTH:
            return position[0], position[1] - 1
        elif self == Direction.WEST:
            return position[0] - 1, position[1]
