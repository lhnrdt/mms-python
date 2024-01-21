import API
from Direction import Direction
from collections import deque
import heapq


class MazeCell():
    """
    A class representing a cell in the maze.

    Attributes:
        position (tuple[int, int]): The x and y coordinates of the cell.
        walls (dict[int, bool]): A dictionary representing the walls in the cell.
        distance_to_goal (int): The distance from the cell to the goal.
        distance_to_start (int): The distance from the cell to the start.
        confirmedDistance (bool): Whether the distance to the goal has been confirmed.
    """

    def __init__(self, position):
        self.position = position
        self.walls = {
            Direction.NORTH.value: False,
            Direction.EAST.value: False,
            Direction.SOUTH.value: False,
            Direction.WEST.value: False
        }
        self.distance_to_goal = None
        self.distance_to_start = None
        self.confirmed_distance = False

    def get_position(self) -> tuple[int, int]:
        """
        Returns the current position of the maze object.

        Returns:
            tuple[int, int]: The x and y coordinates of the position.
        """
        return self.position

    def get_walls(self) -> dict[int, bool]:
        """
        Returns a dictionary representing the walls in the maze.

        The dictionary maps each cell index to a boolean value, where True indicates the presence of a wall and False
        indicates the absence of a wall.

        Returns:
            dict[int, bool]: A dictionary representing the walls in the maze.
        """
        return self.walls

    def get_wall(self, direction: Direction) -> bool:
        """
        Returns the wall status in the given direction.

        Args:
            direction (Direction): The direction to check for a wall.

        Returns:
            bool: True if there is a wall in the given direction, False otherwise.
        """
        return self.walls[direction.value]

    def set_wall(self, direction: Direction) -> None:
        """
        Sets a wall in the specified direction.

        Args:
            direction (Direction): The direction in which to set the wall.

        Returns:
            None
        """
        API.setWall(*self.position,
                    direction.get_API_representation())
        self.walls[direction.value] = True

    def clear_wall(self, direction: Direction) -> None:
        """
        Clears the wall in the specified direction.

        Args:
            direction (Direction): The direction in which to clear the wall.

        Returns:
            None
        """
        API.clearWall(*self.position,
                      direction.get_API_representation())
        self.walls[direction.value] = False

    def get_distance(self, start=False) -> int:
        """
        Get the distance from the current position to either the start or the goal.

        Args:
            start (bool, optional): If True, returns the distance to the start.
                Otherwise, returns the distance to the goal. Defaults to False.

        Returns:
            int: The distance from the current position to the specified point.
        """
        if start:
            return self.distance_to_start
        return self.distance_to_goal

    def set_distance(self, distance, start=False) -> None:
        """
        Set the distance from either the start or goal position.

        Parameters:
        - distance: The distance to set.
        - start: A boolean indicating whether the distance is from the start position (True)
        or the goal position (False).

        Returns:
        - None
        """
        if start:
            self.distance_to_start = distance
        else:
            self.distance_to_goal = distance

    def set_confirmed_distance(self, confirmed) -> None:
        """
        Sets the the distance to the goal as confirmed.

        Args:
            confirmed: The confirmed distance value to set.

        Returns:
            None
        """
        self.confirmed_distance = confirmed
        API.setColor(*self.position, "b")

    def distance_is_confirmed(self) -> bool:
        """
        Checks if the distance is confirmed, meaning that the mouse has explored the cell.

        Returns:
            bool: True if the distance is confirmed
        """
        return self.confirmed_distance

    def __repr__(self) -> str:
        """
        Returns a string representation of the MazeCell object.

        The string representation includes the position, walls, and distance to the goal.

        Returns:
            str: A string representation of the MazeCell object.
        """
        return "MazeCell(position={}, walls={}, distance={})".format(
            self.position, [wall for wall in self.walls.values()], self.distance_to_goal)

    def __eq__(self, o: object) -> bool:
        """
        Check if the current MazeCell is equal to another object.

        Args:
            o (object): The object to compare with.

        Returns:
            bool: True if the MazeCell is equal to the other object, False otherwise.
        """
        if isinstance(o, MazeCell):
            return self.distance_to_goal == o.distance_to_goal
        return False

    def __lt__(self, o: object) -> bool:
        """
        Compare the current MazeCell object with another object.

        Args:
            o (object): The object to compare with.

        Returns:
            bool: True if the current MazeCell's distance to goal is less than the other object's distance to goal,
                  False otherwise.
        """
        if isinstance(o, MazeCell):
            return self.distance_to_goal < o.distance_to_goal
        return False

    def __gt__(self, o: object) -> bool:
        """
        Compare the current MazeCell object with another object.

        Args:
            o (object): The object to compare with.

        Returns:
            bool: True if the current MazeCell's distance_to_goal is greater than the other object's distance_to_goal,
              False otherwise.
        """
        if isinstance(o, MazeCell):
            return self.distance_to_goal > o.distance_to_goal
        return False

    def __hash__(self) -> int:
        """
        Calculate the hash value of the Maze object.

        Returns:
            int: The hash value of the Maze object.
        """
        return hash(repr(self))


class Maze():
    def __init__(self, width: int, height: int):
        """
        Initializes a Maze object with the specified width and height.

        Args:
            width (int): The width of the maze.
            height (int): The height of the maze.
        """
        # 2D array of cells
        self.width = width
        self.height = height
        self.cells = [MazeCell((x, y)) for y in range(height)
                      for x in range(width)]

        # set surrounding walls
        for cell in self.cells:
            if cell.position[0] == 0:
                cell.set_wall(Direction.WEST)
            if cell.position[0] == self.width - 1:
                cell.set_wall(Direction.EAST)
            if cell.position[1] == 0:
                cell.set_wall(Direction.SOUTH)
            if cell.position[1] == self.height - 1:
                cell.set_wall(Direction.NORTH)

    def contains(self, position: tuple[int, int]) -> bool:
        """
        Check if a given position is within the bounds of the maze.

        Args:
            position (tuple[int, int]): The position to check.

        Returns:
            bool: True if the position is within the maze bounds, False otherwise.
        """
        return position[0] >= 0 and position[0] < self.width and position[1] >= 0 and position[1] < self.height

    def update_flood_fill_distances(self, goal: tuple[int, int], start=False, draw=True) -> None:
        """
        Update the flood fill distances of all cells in the maze.

        Args:
            goal (tuple[int, int]): The coordinates of the goal cell.
            start (bool, optional): Whether to start the flood fill from the goal cell. Defaults to False.
            draw (bool, optional): Whether to draw the updated distances on the maze. Defaults to True.
        """
        # Set all cells to have no distance
        for cell in self.cells:
            cell.set_distance(None, start=start)
        if draw:
            API.clearAllText()
        num_updates = 0

        # Set the goal cell to have distance 0
        self.get_cell(goal).set_distance(0, start=start)
        if draw:
            API.setText(*goal, "0")

        # Set the distance of all cells to the distance of the previous cell + 1
        queue = deque([self.get_cell(goal)])
        while queue:
            cell = queue.popleft()
            reachable_neighbors = self.get_reachable_neighbors(
                cell.get_position())
            for neighbor in reachable_neighbors:
                if neighbor.get_distance(start=start) is None:
                    distance = cell.get_distance(start=start) + 1
                    neighbor.set_distance(distance, start=start)
                    if draw:
                        API.setText(*neighbor.get_position(), str(distance))
                    num_updates += 1
                    queue.append(neighbor)

    def get_cell(self, position: tuple[int, int]) -> MazeCell:
        """
        Retrieves the MazeCell object at the specified position.

        Args:
            position (tuple[int, int]): The position of the cell in the maze.

        Returns:
            MazeCell: The MazeCell object at the specified position.

        Raises:
            IndexError: If the position is out of bounds.
        """
        if not self.contains(position):
            raise IndexError("Cell position {} out of bounds".format(position))
        return self.cells[position[1] * self.width + position[0]]

    def set_wall(self, cell: MazeCell, direction: Direction) -> None:
        """
        Sets a wall in the specified direction for the given cell.

        Args:
            cell (MazeCell): The cell for which to set the wall.
            direction (Direction): The direction in which to set the wall.

        Returns:
            None
        """
        cell.set_wall(direction)
        try:
            neighbor = direction.add_to_position(cell.get_position())
            self.get_cell(neighbor).set_wall(direction.minus_180())
        except IndexError:
            pass

    def get_neighbors(self, position: tuple[int, int]) -> list[MazeCell]:
        """
        Returns a list of neighboring MazeCell objects for the given position.

        Args:
            position (tuple[int, int]): The position for which to find neighbors.

        Returns:
            list[MazeCell]: A list of neighboring MazeCell objects.
        """
        neighbors = []
        for direction in Direction:
            neighbor = direction.add_to_position(position)
            if self.contains(neighbor):
                neighbors.append(self.get_cell(neighbor))
        return neighbors

    def get_reachable_neighbors(self, position: tuple[int, int]) -> list[MazeCell]:
        """
        Returns a list of reachable neighboring MazeCells from the given position.

        Args:
            position (tuple[int, int]): The position from which to find reachable neighbors.

        Returns:
            list[MazeCell]: A list of MazeCell objects representing the reachable neighbors.
        """
        neighbors = []
        for direction in Direction:
            neighbor = direction.add_to_position(position)
            if self.contains(neighbor) and not self.get_cell(position).get_wall(direction):
                neighbors.append(self.get_cell(neighbor))
        return neighbors

    def __str__(self) -> str:
        """
        Returns a string representation of the Maze object.

        The string representation consists of the distances of each cell in the maze,
        separated by tabs and newlines to represent the maze structure.

        Returns:
            str: A string representation of the Maze object.
        """
        string = ""
        for y in range(self.height - 1, -1, -1):
            for x in range(self.width):
                string += str(self.get_cell((x, y)).get_distance()) + "\t"
            string += "\n"
        return string

    def find_fastest_path(self, start: tuple[int, int], goal: tuple[int, int], draw=True) -> list[MazeCell]:
        """
        Finds the fastest path from the start cell to the goal cell using A* search algorithm.

        Args:
            start (tuple[int, int]): The coordinates of the start cell.
            goal (tuple[int, int]): The coordinates of the goal cell.
            draw (bool, optional): Whether to draw the path on the maze. Defaults to True.

        Returns:
            list[MazeCell]: The list of MazeCell objects representing the fastest path from start to goal.
        """
        # A* search
        # open_set is a priority queue of (cost, cell, path)
        open_set = [(0, self.get_cell(start), [])]

        # closed_set is a set of cells that have already been visited
        visited = set()

        # While there are still cells to visit
        while open_set:

            # Get the cell with the lowest cost
            cost, current_cell, path = heapq.heappop(open_set)

            # If the cell is the goal, return the path
            if current_cell.get_position() == goal:
                final_path = path + [current_cell]
                API.log("Path found, distance: {}, corners: {}".format(
                    cost, self.count_corners(final_path)))
                if draw:
                    for cell in final_path:
                        API.setColor(*cell.get_position(), "y")
                return final_path

            # If the cell has already been visited, skip it
            if current_cell in visited:
                continue

            # Add the cell to the visited set
            visited.add(current_cell)

            candidate_cells = self.get_reachable_neighbors(
                current_cell.get_position())

            # remove cells with unconfirmed distances
            candidate_cells = list(
                filter(lambda cell: cell.distance_is_confirmed(), candidate_cells))

            API.log("\nCurrent cell: {}".format(current_cell))
            API.log("Choosing from {} candidate cells".format(
                len(candidate_cells)))

            for neighbor in candidate_cells:

                # calculate the cost of the neighbor
                corners = self.count_corners(path + [current_cell, neighbor])
                distance = neighbor.get_distance()
                added_cost = self.path_cost(corners, distance)
                new_cost = cost + added_cost
                API.log("{}: corners: {}, distance: {}".format(neighbor,
                                                               corners, distance))

                # add the neighbor to the open set
                heapq.heappush(
                    open_set, (new_cost, neighbor, path + [current_cell]))

        API.log("No path found, path so far:")
        for cell in path:
            API.log(str(cell))
        # If there are no more cells to visit, return None
        return None

    def path_cost(self, corners: int, distance: int) -> int:
        """
        Calculates the cost of a path based on the number of corners and distance.

        Args:
            corners (int): The number of corners in the path.
            distance (int): The distance of the path.

        Returns:
            int: The cost of the path.
        """
        CORNER_WEIGHT = 2
        DISTANCE_WEIGHT = 1
        return CORNER_WEIGHT * corners + DISTANCE_WEIGHT * distance

    def count_corners(self, path: list[MazeCell]) -> int:
        """
        Counts the number of corners in a given path.

        Args:
            path (list[MazeCell]): The path to count corners in.

        Returns:
            int: The number of corners in the path.
        """
        return sum(1 for i in range(1, len(path) - 1) if not self.is_straight(path[i - 1].get_position(),
                                                                              path[i].get_position(
        ),
            path[i + 1].get_position()))

    def is_straight(self, position1: tuple[int, int], position2: tuple[int, int], position3: tuple[int, int]):
        """
        Check if three positions form a straight line.

        Args:
            position1 (tuple[int, int]): The first position.
            position2 (tuple[int, int]): The second position.
            position3 (tuple[int, int]): The third position.

        Returns:
            bool: True if the positions form a straight line, False otherwise.
        """
        return (position2[0] - position1[0], position2[1] - position1[1]) == \
            (position3[0] - position2[0], position3[1] - position2[1])
