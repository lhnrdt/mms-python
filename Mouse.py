from Direction import Direction
from Maze import Maze, MazeCell
import API


class NotANeighborException(Exception):
    def __init__(self, cell, neighbor_cell: MazeCell, message=""):
        API.setColor(*neighbor_cell.get_position(), "r")
        super().__init__("\n{}\nis not a neighbor to\n{}\n\nReason: {}".format(
            neighbor_cell, cell, message))


class PathBlockedException(Exception):
    def __init__(self, cell, neighbor_cell: MazeCell, message=""):
        API.setColor(*neighbor_cell.get_position(), "r")
        super().__init__("\n{}\nis blocked by\n{}\n\nReason: {}".format(
            neighbor_cell, cell, message))


class Mouse():
    def __init__(self, position, direction: Direction, maze: Maze):
        self.position = position
        self.direction = direction
        self.maze = maze
        self.cell = maze.get_cell(position)
        self.sense_walls()
        self.visited = set()

    def get_position(self):
        return self.position

    def get_direction(self):
        return self.direction

    def turn_left(self):
        API.turnLeft()
        self.direction = self.direction.minus_90()

    def turn_right(self):
        API.turnRight()
        self.direction = self.direction.plus_90()

    def turn_around(self, left=True):
        if left:
            self.turn_left()
            self.turn_left()
        else:
            self.turn_right()
            self.turn_right()

    def move_forward(self, distance=1):
        if API.wallFront():
            raise PathBlockedException(self.cell, self.maze.get_cell(
                self.get_front()), "Wall in the way")
        API.moveForward(distance)
        for _ in range(distance):
            self.position = self.direction.add_to_position(self.position)
            self.cell = self.maze.get_cell(self.position)
            self.visited.add(self.cell)

    def turn_towards_neighbor(self, neighbor: MazeCell):

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
        neighbors = []
        if not API.wallFront() and self.maze.contains(self.get_front()):
            neighbors.append(self.maze.get_cell(self.get_front()))
        if not API.wallLeft() and self.maze.contains(self.get_left()):
            neighbors.append(self.maze.get_cell(self.get_left()))
        if not API.wallRight() and self.maze.contains(self.get_right()):
            neighbors.append(self.maze.get_cell(self.get_right()))

        if len(neighbors) == 0:
            self.turn_around()
            if not API.wallFront() and self.maze.contains(self.get_front()):
                neighbors.append(self.maze.get_cell(
                    self.get_front()))
        return neighbors

    def get_front(self):
        return self.direction.add_to_position(self.position)

    def get_left(self):
        return self.direction.minus_90().add_to_position(self.position)

    def get_right(self):
        return self.direction.plus_90().add_to_position(self.position)

    def get_back(self):
        return self.direction.minus_180().add_to_position(self.position)

    def get_position_from_direction(self, position, direction):
        if direction == Direction.NORTH:
            return position[0], position[1] + 1
        elif direction == Direction.EAST:
            return position[0] + 1, position[1]
        elif direction == Direction.SOUTH:
            return position[0], position[1] - 1
        elif direction == Direction.WEST:
            return position[0] - 1, position[1]

    def sense_walls(self):
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

    def get_best_candidate(self, reachable_neighbors):
        """
        Choose smallest distance
        if tie, choose unvisited
        if tie, choose smallest amount of turns needed to get to the cell
        """

        def heuristic(neighbor): return (
            neighbor.get_distance(),
            1 if neighbor in self.visited else 0,
            self.get_turns(neighbor)
        )
        return min(reachable_neighbors,
                   key=heuristic)

    def get_turns(self, neighbor: MazeCell):
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

    def find_goal_explore(self, goal):
        while self.position != goal:
            self.sense_walls()
            self.maze.update_flood_fill_distances(goal)
            self.cell.set_confirmed_distance(True)
            reachable_neighbors = self.get_reachable_neighbors()

            # select the neighbor with the lowest distance
            min_neighbor = self.get_best_candidate(reachable_neighbors)
            self.turn_towards_neighbor(min_neighbor)
            self.move_forward()

    def find_goal_fast(self, goal):
        while self.position != goal:
            reachable_neighbors = self.get_reachable_neighbors()

            # remove unconfirmed neighbors
            reachable_neighbors = list(
                filter(lambda neighbor: neighbor.distance_is_confirmed(), reachable_neighbors))

            # select the neighbor with the lowest distance
            min_neighbor = self.get_best_candidate(reachable_neighbors)

            self.turn_towards_neighbor(min_neighbor)
            self.move_forward()

    """
    follow the given path, which is a list of MazeCells
    use self.move_forward(n) to move forward n cells in one go until a corner is encountered
    use self.move_to_neighbor(neighbor) to move to the given neighbor if there is a corner
    """

    def follow_path(self, path: list[MazeCell]):
        times_forward = 0
        cell = self.cell
        self.turn_towards_neighbor(path[1])
        forward_direction = self.direction

        for i in range(len(path) - 1):
            cell = path[i]
            next_cell = path[i + 1] if i + 1 < len(path) else None

            next_cell_is_infrontof_cell = next_cell.get_position(
            ) == self.get_position_from_direction(cell.get_position(), forward_direction)

            if next_cell_is_infrontof_cell:
                times_forward += 1
            else:
                if times_forward > 0:
                    self.move_forward(times_forward)
                    API.log("Moved forward {} times".format(times_forward))
                times_forward = 0

                self.turn_towards_neighbor(next_cell)
                times_forward += 1
                i -= 1
                forward_direction = self.direction

    def return_to_start(self, start, goal):
        while self.position != start:
            self.sense_walls()
            self.maze.update_flood_fill_distances(goal, draw=False)
            self.maze.update_flood_fill_distances(start, start=True)
            reachable_neighbors = self.get_reachable_neighbors()

            # select the neighbor with the lowest distance
            min_neighbor = min(reachable_neighbors,
                               key=lambda neighbor: neighbor.get_distance(start=True))
            self.turn_towards_neighbor(min_neighbor)
            self.move_forward()
