import enum


class Direction(enum.Enum):
    """
    Represents the cardinal directions: NORTH, EAST, SOUTH, WEST.
    """

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    def minus_90(self) -> "Direction":
        """
        Returns the direction obtained by rotating 90 degrees counter-clockwise.
        """
        return Direction((self.value - 1) % 4)

    def plus_90(self) -> "Direction":
        """
        Returns the direction obtained by rotating 90 degrees clockwise.
        """
        return Direction((self.value + 1) % 4)

    def minus_180(self) -> "Direction":
        """
        Returns the direction obtained by rotating 180 degrees.
        """
        return Direction((self.value - 2) % 4)

    def get_API_representation(self) -> str:
        """
        Returns the API representation of the direction.
        """
        if self == Direction.NORTH:
            return "n"
        elif self == Direction.EAST:
            return "e"
        elif self == Direction.SOUTH:
            return "s"
        elif self == Direction.WEST:
            return "w"

    def add_to_direction(self, direction: "Direction") -> "Direction":
        """
        Adds the given direction to the current direction and returns the resulting direction.
        """
        return (self.value + direction.value) % 4

    def add_to_position(self, position: tuple[int, int]) -> tuple[int, int]:
        """
        Adds the current direction to the given position and returns the resulting position.
        """
        if self == Direction.NORTH:
            return position[0], position[1] + 1
        elif self == Direction.EAST:
            return position[0] + 1, position[1]
        elif self == Direction.SOUTH:
            return position[0], position[1] - 1
        elif self == Direction.WEST:
            return position[0] - 1, position[1]

    @staticmethod
    def get_position_from_direction(position: tuple[int, int], direction: tuple[int, int]) -> tuple[int, int]:
        """
        Returns the new position based on the given position and direction.

        Args:
            position (tuple): The current position as a tuple of (x, y) coordinates.
            direction (Direction): The direction to move in.

        Returns:
            tuple: The new position as a tuple of (x, y) coordinates.
        """
        if direction == Direction.NORTH:
            return position[0], position[1] + 1
        elif direction == Direction.EAST:
            return position[0] + 1, position[1]
        elif direction == Direction.SOUTH:
            return position[0], position[1] - 1
        elif direction == Direction.WEST:
            return position[0] - 1, position[1]
