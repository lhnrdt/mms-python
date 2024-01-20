import API
from Direction import Direction
from Maze import Maze
from Mouse import Mouse


def main():
    dimensions = (API.mazeWidth(), API.mazeHeight())
    # goal = (r.randint(0, dimensions[0] - 1),
    # r.randint(0, dimensions[1] - 1))
    # dimensions = (5, 5)
    start = (0, 0)
    goal = (dimensions[0] // 2, dimensions[1] // 2)
    API.log("Goal: {}".format(goal))
    API.setColor(*goal, "g")
    maze = Maze(*dimensions)
    mouse = Mouse(start, direction=Direction.NORTH, maze=maze)

    API.log("Starting mouse exploration")
    mouse.find_goal_explore(goal)
    API.log("Starting mouse return to start")
    mouse.return_to_start(start, goal)
    fastest_path = maze.find_fastest_path(start, goal)
    API.log("Starting mouse follow path")
    mouse.follow_path(fastest_path)
    API.log("Starting mouse fast goal search")
    mouse.find_goal_fast(goal)
    API.log("Mouse found goal")


if __name__ == "__main__":
    main()
