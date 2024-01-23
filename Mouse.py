from Direction import Direction
from Maze import Maze, MazeCell
import API

from collections import deque


class NotANeighborException(Exception):
    """
    Exception raised when a cell is not a neighbor to another cell in the maze.

    Attributes:
        cell (MazeCell): The cell that is not a neighbor.
        neighbor_cell (MazeCell): The cell that is expected to be a neighbor.
        message (str): Additional message explaining the reason for the exception.
    """

    def __init__(self, cell: MazeCell, neighbor_cell: MazeCell, message: str = ""):
        API.setColor(*neighbor_cell.get_position(), "r")
        super().__init__("\n{}\nis not a neighbor to\n{}\n\nReason: {}".format(
            neighbor_cell, cell, message))


class PathBlockedException(Exception):
    """
    Exception raised when a path is blocked by a neighboring cell.

    Attributes:
        cell (MazeCell): The current cell.
        neighbor_cell (MazeCell): The neighboring cell that is blocking the path.
        message (str): Additional message explaining the reason for the blockage.
    """

    def __init__(self, cell: MazeCell, neighbor_cell: MazeCell, message: str = ""):
        API.setColor(*neighbor_cell.get_position(), "r")
        super().__init__("\n{}\nis blocked by\n{}\n\nReason: {}".format(
            neighbor_cell, cell, message))


class Mouse():
    """
    Represents a mouse in the micromouse simulator.

    Attributes:
    - position: The current position of the mouse in the maze.
    - direction: The current direction the mouse is facing.
    - maze: The maze object representing the maze the mouse is in.
    - cell: The current cell the mouse is in.
    - visited: A set of cells that the mouse has visited.
    - updating_distances: A flag indicating whether the mouse is updating distances in the maze.
    """

    MAX_SPEED_M_PER_S = 1.5
    MAX_ACCELERATION_M_PER_S2 = 2
    MAX_NEG_ACCELERATION_M_PER_S2 = 1.5

    D_MIN_MAX_ACC = \
        MAX_SPEED_M_PER_S ** 2 / (2 * MAX_ACCELERATION_M_PER_S2) + \
        MAX_SPEED_M_PER_S ** 2 / (2 * MAX_NEG_ACCELERATION_M_PER_S2)

    def __init__(self, position: tuple[int, int], direction: Direction, maze: Maze):
        self.position = position
        self.direction = direction
        self.maze = maze
        self.cell = maze.get_cell(position)
        self.sense_walls()
        self.visited = set()
        self.updating_distances = True

    def get_position(self) -> tuple[int, int]:
        """
        Returns the current position of the mouse.

        Returns:
            tuple: A tuple containing the x and y coordinates of the mouse's position.
        """
        return self.position

    def get_direction(self) -> Direction:
        """
        Returns the current direction of the mouse.

        Returns:
            int: The current direction of the mouse.
        """
        return self.direction

    def turn_left(self) -> None:
        """
        Turns the mouse to the left by 90 degrees.
        """
        API.turnLeft()
        self.direction = self.direction.minus_90()

    def turn_right(self) -> None:
        """
        Turns the mouse 90 degrees to the right.
        """
        API.turnRight()
        self.direction = self.direction.plus_90()

    def turn_around(self, left: bool = True) -> None:
        """
        Turns the mouse around by making it perform two consecutive turns in the specified direction.

        Parameters:
        - left (bool): If True, the mouse turns left twice. If False, the mouse turns right twice.
        """
        if left:
            self.turn_left()
            self.turn_left()
        else:
            self.turn_right()
            self.turn_right()

    def move_forward(self, distance: int = 1) -> None:
        """
        Move the mouse forward by the specified distance.

        Args:
            distance (int): The distance to move forward (default is 1).

        Raises:
            PathBlockedException: If there is a wall in the way.

        """
        if API.wallFront():
            raise PathBlockedException(self.cell, self.maze.get_cell(
                self.get_front()), "Wall in the way")
        API.moveForward(distance)
        for _ in range(distance):
            self.position = self.direction.add_to_position(self.position)
            self.cell = self.maze.get_cell(self.position)
            self.visited.add(self.cell)
            if self.updating_distances:
                self.cell.set_distance_is_confirmed(True)

    def turn_towards_neighbor(self, neighbor: MazeCell) -> None:
        """
        Turns the mouse towards the given neighbor cell.

        Args:
            neighbor (MazeCell): The neighbor cell to turn towards.

        Raises:
            NotANeighborException: If the given cell is not a valid neighbor.

        Returns:
            None
        """

        if neighbor.get_position() == self.get_front():
            pass
        elif neighbor.get_position() == self.get_left():
            self.turn_left()
        elif neighbor.get_position() == self.get_right():
            self.turn_right()
        elif neighbor.get_position() == self.get_back():
            self.turn_around()
        else:
            raise NotANeighborException(self.cell, neighbor, "Too far away")

    def get_reachable_neighbors(self) -> list[MazeCell]:
        """
        Returns a list of reachable neighboring cells.

        This method checks the surrounding cells of the mouse's current position and returns a list of neighboring
          cells that are reachable (i.e., not blocked by walls).

        Returns:
            list[MazeCell]: A list of reachable neighboring cells.
        """
        neighbors = []
        if not API.wallFront() and self.maze.contains(self.get_front()):
            neighbors.append(self.maze.get_cell(self.get_front()))
        if not API.wallLeft() and self.maze.contains(self.get_left()):
            neighbors.append(self.maze.get_cell(self.get_left()))
        if not API.wallRight() and self.maze.contains(self.get_right()):
            neighbors.append(self.maze.get_cell(self.get_right()))

        # if no neighbors are reachable, turn around and check again
        if len(neighbors) == 0:
            self.turn_around()
            if not API.wallFront() and self.maze.contains(self.get_front()):
                neighbors.append(self.maze.get_cell(
                    self.get_front()))
        return neighbors

    def get_front(self) -> tuple[int, int]:
        """
        Returns the position of the cell in front of the mouse based on its current direction.
        """
        return self.direction.add_to_position(self.position)

    def get_left(self) -> tuple[int, int]:
        """
        Returns the position of the cell to the left of the current position, based on the current direction.
        """
        return self.direction.minus_90().add_to_position(self.position)

    def get_right(self) -> tuple[int, int]:
        """
        Returns the position of the cell to the right of the current cell,
        based on the current direction and position of the mouse.
        """
        return self.direction.plus_90().add_to_position(self.position)

    def get_back(self) -> tuple[int, int]:
        """
        Returns the position that is opposite to the current direction.

        Returns:
            Position: The position that is opposite to the current direction.
        """
        return self.direction.minus_180().add_to_position(self.position)

    def sense_walls(self) -> None:
        """
        Sense the walls in the current direction and update the maze accordingly.
        """
        direction_offset = self.direction.value - Direction.NORTH.value
        walls = [False, False, False, False]
        if API.wallFront():
            walls[self.direction.value] = True
            API.setWall(*self.position,
                        self.direction.get_API_representation())
            self.maze.set_wall(self.cell, self.direction)
        if API.wallLeft():
            walls[(self.direction.minus_90().value + direction_offset) % 4] = True
            API.setWall(*self.position,
                        self.direction.minus_90().get_API_representation())
            self.maze.set_wall(self.cell, self.direction.minus_90())
        if API.wallRight():
            walls[(self.direction.plus_90().value + direction_offset) % 4] = True
            API.setWall(*self.position,
                        self.direction.plus_90().get_API_representation())
            self.maze.set_wall(self.cell, self.direction.plus_90())

    def get_best_candidate(self, reachable_neighbors: list[MazeCell]) -> MazeCell:
        """
        Choose the best candidate from a list of reachable neighbors based on the following criteria:
        1. Smallest distance
        2. If there is a tie in distance, choose the unvisited neighbor
        3. If there is a tie in distance and visitation status,
          choose the neighbor with the smallest amount of turns needed to reach it.

        Args:
            reachable_neighbors (list): A list of reachable neighbors.

        Returns:
            The best candidate neighbor based on the defined criteria.
        """

        def heuristic(neighbor: MazeCell): return (
            neighbor.get_distance(),
            1 if neighbor in self.visited else 0,
            self.get_turns(neighbor)
        )
        return min(reachable_neighbors,
                   key=heuristic)

    def get_turns(self, neighbor: MazeCell) -> int:
        """
        Calculates the number of turns required to turn towards a neighboring cell.

        Args:
            neighbor (MazeCell): The neighboring cell to calculate turns for.

        Returns:
            int: The number of turns required to turn towards the neighboring cell.
        """
        desired_direction = None

        if neighbor.get_position() == self.get_front():
            desired_direction = self.direction
        elif neighbor.get_position() == self.get_left():
            desired_direction = self.direction.minus_90()
        elif neighbor.get_position() == self.get_right():
            desired_direction = self.direction.plus_90()
        elif neighbor.get_position() == self.get_back():
            desired_direction = self.direction.minus_180()

        diff = (desired_direction.value - self.direction.value) % 4
        return min(diff, 4 - diff)

    def find_goal_explore(self, goal: tuple[int, int]) -> None:
        """
        Finds the goal and explores the maze until the mouse reaches the goal.

        Parameters:
        - goal: The goal position in the maze.

        Returns:
        None
        """
        while self.position != goal:
            self.sense_walls()
            self.maze.update_flood_fill_distances(goal)
            # self.update_flood_fill_distances_dynamic(goal, returning=False)
            self.cell.set_distance_is_confirmed(True)
            reachable_neighbors = self.get_reachable_neighbors()

            # select the neighbor with the lowest distance
            min_neighbor = self.get_best_candidate(reachable_neighbors)
            self.turn_towards_neighbor(min_neighbor)
            self.move_forward(1)

    def calculate_fastest_path(self):
        open_set = [(0, self.cell, [])]
        visited = set()

    def follow_path(self, path: list[MazeCell]) -> None:
        """
        Follows the given path of MazeCells.

        Args:
            path (list[MazeCell]): The path to follow.

        Returns:
            None
        """
        for cell in path[1:]:
            axis = self.turn_to_target(cell)
            self.move_to_target_infront(cell, axis)

    def turn_to_target(self, target: MazeCell) -> int:
        target_position = target.get_position()

        if not (target_position[0] == self.position[0] or target_position[1] == self.position[1]):
            raise ValueError("Target is not reachable in a straight line")

        if target_position == self.position:
            raise ValueError("Target is the same as current position")

        # aligned on x-axis
        if target_position[1] == self.position[1]:
            if target_position[0] > self.position[0]:
                self.turn_to_direction(Direction.EAST)
            else:
                self.turn_to_direction(Direction.WEST)
            return 0

        # aligned on y-axis
        if target_position[0] == self.position[0]:
            if target_position[1] > self.position[1]:
                self.turn_to_direction(Direction.NORTH)
            else:
                self.turn_to_direction(Direction.SOUTH)
            return 1

    def move_to_target_infront(self, target: MazeCell, axis: int) -> None:
        target_position = target.get_position()
        if axis == 0:
            if target_position[0] > self.position[0]:
                API.log("Moving forward {} cells".format(target_position[0] - self.position[0]))
                self.move_forward(target_position[0] - self.position[0])
            else:
                API.log("Moving forward {} cells".format(self.position[0] - target_position[0]))
                self.move_forward(self.position[0] - target_position[0])
        else:
            if target_position[1] > self.position[1]:
                API.log("Moving forward {} cells".format(target_position[1] - self.position[1]))
                self.move_forward(target_position[1] - self.position[1])
            else:
                API.log("Moving forward {} cells".format(self.position[1] - target_position[1]))
                self.move_forward(self.position[1] - target_position[1])

    def turn_to_direction(self, direction: Direction) -> None:
        """
        Turns the mouse to the given direction.

        Args:
            direction (Direction): The direction to turn to.

        Returns:
            None
        """
        if direction == self.direction:
            return
        elif direction == self.direction.minus_90():
            self.turn_left()
        elif direction == self.direction.plus_90():
            self.turn_right()
        elif direction == self.direction.minus_180():
            self.turn_around()
        else:
            raise ValueError("Invalid direction")

    def return_to_start(self, start: tuple[int, int], goal: tuple[int, int]) -> None:
        """
        Moves the mouse back to the start position using flood fill algorithm.

        Args:
            start (tuple): The start position coordinates.
            goal (tuple): The goal position coordinates.

        Returns:
            None
        """
        while self.position != start:
            self.sense_walls()
            self.maze.update_flood_fill_distances(
                goal, returning=False, draw=True)
            self.maze.update_flood_fill_distances(
                start, returning=True, draw=False)
            reachable_neighbors = self.get_reachable_neighbors()

            # select the neighbor with the lowest distance
            min_neighbor = min(reachable_neighbors,
                               key=lambda neighbor: neighbor.get_distance(start=True))
            self.turn_towards_neighbor(min_neighbor)
            self.move_forward(1)

    @staticmethod
    def calculate_travel_time(n_cells) -> float:
        """
        Calculates the travel time between two positions.

        Args:
            n_cells (int): The number of cells to travel.

        Returns:
            float: The travel time between the two positions.
        """
        distance_m = n_cells * MazeCell.CELL_SIZE_CM / 100

        if distance_m >= Mouse.D_MIN_MAX_ACC:
            return Mouse.MAX_SPEED_M_PER_S / Mouse.MAX_ACCELERATION_M_PER_S2 + \
                (distance_m - .5 * Mouse.MAX_SPEED_M_PER_S ** 2 * (1/Mouse.MAX_ACCELERATION_M_PER_S2 +
                 1/Mouse.MAX_NEG_ACCELERATION_M_PER_S2)) / Mouse.MAX_SPEED_M_PER_S + \
                Mouse.MAX_SPEED_M_PER_S / Mouse.MAX_NEG_ACCELERATION_M_PER_S2
        else:
            return 2 * (distance_m / (0.5 * Mouse.MAX_ACCELERATION_M_PER_S2 +
                                      0.5 * Mouse.MAX_NEG_ACCELERATION_M_PER_S2)) ** 0.5

    def update_flood_fill_distances_dynamic(self, goal: tuple[int, int], returning=False, draw=True) -> None:
        for cell in self.maze.cells:
            cell.set_distance(None, returning=returning)
        if draw:
            API.clearAllText()
        API.clearAllColor()

        self.maze.get_cell(goal).set_distance(0, returning=returning)
        if draw:
            API.setText(*goal, "0")

        queue = deque([(self.maze.get_cell(goal))])
        while queue:
            cell = queue.popleft()
            reachable_neighbors_in_straight_line = self.maze.get_straightline_reachable(cell.get_position())

            for neighbor in reachable_neighbors_in_straight_line:
                if neighbor.get_distance(start=returning) is None:

                    distance_penalty = Mouse.calculate_travel_time(
                        Maze.get_distance_between_positions(cell.get_position(), neighbor.get_position()))
                    distance = cell.get_distance(
                        start=returning) + distance_penalty
                    neighbor.set_distance(distance, returning=returning)

                    if draw:
                        API.setText(*neighbor.get_position(), str(round(distance, 2)))
                    queue.append(neighbor)


if __name__ == "__main__":
    for i in range(8):
        print(Mouse.calculate_travel_time(i))
