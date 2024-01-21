import API
from Direction import Direction
from collections import deque
import heapq


class MazeCell():
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
        self.confirmedDistance = False

    def get_position(self):
        return self.position

    def get_walls(self):
        return self.walls

    def get_wall(self, direction: Direction):
        return self.walls[direction.value]

    def set_wall(self, direction: Direction):
        API.setWall(*self.position,
                    direction.get_API_representation())
        self.walls[direction.value] = True

    def clear_wall(self, direction: Direction):
        API.clearWall(*self.position,
                      direction.get_API_representation())
        self.walls[direction.value] = False

    def get_distance(self, start=False):
        if start:
            return self.distance_to_start
        return self.distance_to_goal

    def set_distance(self, distance, start=False):
        if start:
            self.distance_to_start = distance
        else:
            self.distance_to_goal = distance

    def set_confirmed_distance(self, confirmed):
        self.confirmedDistance = confirmed
        API.setColor(*self.position, "b")

    def distance_is_confirmed(self):
        return self.confirmedDistance

    def __repr__(self) -> str:
        return "MazeCell(position={}, walls={}, distance={})".format(
            self.position, [wall for wall in self.walls.values()], self.distance_to_goal)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, MazeCell):
            return self.distance_to_goal == o.distance_to_goal
        return False

    def __lt__(self, o: object) -> bool:
        if isinstance(o, MazeCell):
            return self.distance_to_goal < o.distance_to_goal
        return False

    def __gt__(self, o: object) -> bool:
        if isinstance(o, MazeCell):
            return self.distance_to_goal > o.distance_to_goal
        return False

    def __hash__(self) -> int:
        return hash(repr(self))


class Maze():
    def __init__(self, width, height):
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

    def contains(self, position):
        return position[0] >= 0 and position[0] < self.width and position[1] >= 0 and position[1] < self.height

    def update_flood_fill_distances(self, goal, start=False, draw=True):
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

    def get_cell(self, position) -> MazeCell:
        if not self.contains(position):
            raise IndexError("Cell position {} out of bounds".format(position))
        return self.cells[position[1] * self.width + position[0]]

    def set_wall(self, cell: MazeCell, direction: Direction):
        cell.set_wall(direction)
        try:
            neighbor = direction.add_to_position(cell.get_position())
            self.get_cell(neighbor).set_wall(direction.minus_180())
        except IndexError:
            pass

    def get_neighbors(self, position):
        neighbors = []
        for direction in Direction:
            neighbor = direction.add_to_position(position)
            if self.contains(neighbor):
                neighbors.append(self.get_cell(neighbor))
        return neighbors

    def get_reachable_neighbors(self, position):
        neighbors = []
        for direction in Direction:
            neighbor = direction.add_to_position(position)
            if self.contains(neighbor) and not self.get_cell(position).get_wall(direction):
                neighbors.append(self.get_cell(neighbor))
        return neighbors

    def __str__(self) -> str:
        string = ""
        for y in range(self.height - 1, -1, -1):
            for x in range(self.width):
                string += str(self.get_cell((x, y)).get_distance()) + "\t"
            string += "\n"
        return string

    def find_fastest_path(self, start, goal, draw=True) -> list[MazeCell]:

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

    def path_cost(self, corners, distance):
        CORNER_WEIGHT = 2
        DISTANCE_WEIGHT = 1
        return CORNER_WEIGHT * corners + DISTANCE_WEIGHT * distance

    def count_corners(self, path: list[MazeCell]):
        return sum(1 for i in range(1, len(path) - 1) if not self.is_straight(path[i - 1].get_position(),
                                                                              path[i].get_position(
        ),
            path[i + 1].get_position()))

    def is_straight(self, a, b, c):
        return (b[0] - a[0], b[1] - a[1]) == (c[0] - b[0], c[1] - b[1])
