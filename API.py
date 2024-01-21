import sys


class MouseCrashedError(Exception):
    """
    Exception raised when the mouse crashes during the simulation.
    """
    pass


def log(string):
    """
    Logs the given string to the standard error stream.

    Args:
        string (str): The string to be logged.
    """
    sys.stderr.write("{}\n".format(string))
    sys.stderr.flush()


def command(args, return_type=None) -> str:
    """
    Sends a command to the micromouse simulator and returns the response.

    Args:
        args (list): The arguments to be sent as a command.
        return_type (type, optional): The expected return type of the response. Defaults to None.

    Returns:
        The response from the micromouse simulator, converted to the specified return type if provided.
    """
    line = " ".join([str(x) for x in args]) + "\n"
    sys.stdout.write(line)
    sys.stdout.flush()
    if return_type:
        response = sys.stdin.readline().strip()
        if return_type == bool:
            return response == "true"
        return return_type(response)


def mazeWidth() -> int:
    """
    Returns the width of the maze.

    :return: The width of the maze as an integer.
    """
    return command(args=["mazeWidth"], return_type=int)


def mazeHeight() -> int:
    """
    Returns the height of the maze.

    :return: The height of the maze as an integer.
    """
    return command(args=["mazeHeight"], return_type=int)


def checkWall(wallCommand, half_steps_away=None) -> bool:
    """
    Check if there is a wall at the specified position.

    Args:
        wallCommand (str): The command to check the wall.
        half_steps_away (int, optional): The number of half steps away from the current position. Defaults to None.

    Returns:
        bool: True if there is a wall, False otherwise.
    """
    args = [wallCommand]
    if half_steps_away is not None:
        args.append(half_steps_away)
    return command(args, return_type=bool)


def wallFront(half_steps_away=None) -> bool:
    """
    Check if there is a wall in front of the micromouse.

    Args:
        half_steps_away (int, optional): The number of half steps away from the micromouse to check for a wall.
          Defaults to None.

    Returns:
        bool: True if there is a wall in front, False otherwise.
    """
    return checkWall("wallFront", half_steps_away)


def wallBack(half_steps_away=None) -> bool:
    """
    Check if there is a wall behind the micromouse.

    Args:
        half_steps_away (int, optional): The number of half steps away from the current position to check for a wall.
          Defaults to None.

    Returns:
        bool: True if there is a wall behind, False otherwise.
    """
    return checkWall("wallBack", half_steps_away)


def wallLeft(half_steps_away=None) -> bool:
    """
    Check if there is a wall on the left side of the micromouse.

    Args:
        half_steps_away (int, optional): The number of half steps away from the micromouse's current position.
          Defaults to None.

    Returns:
        bool: True if there is a wall on the left side, False otherwise.
    """
    return checkWall("wallLeft", half_steps_away)


def wallRight(half_steps_away=None) -> bool:
    """
    Check if there is a wall on the right side of the micromouse.

    Args:
        half_steps_away (int, optional): The number of half steps away from the micromouse's current position.
        Defaults to None.

    Returns:
        bool: True if there is a wall on the right side, False otherwise.
    """
    return checkWall("wallRight", half_steps_away)


def wallFrontLeft(half_steps_away=None) -> bool:
    """
    Check if there is a wall in the front left direction.

    Args:
        half_steps_away (int, optional): The number of half steps away from the current position. Defaults to None.

    Returns:
        bool: True if there is a wall, False otherwise.
    """
    return checkWall("wallFrontLeft", half_steps_away)


def wallFrontRight(half_steps_away=None) -> bool:
    """
    Check if there is a wall in the front-right direction.

    Args:
        half_steps_away (int, optional): The number of half steps away to check for a wall. Defaults to None.

    Returns:
        bool: True if there is a wall, False otherwise.
    """
    return checkWall("wallFrontRight", half_steps_away)


def wallBackLeft(half_steps_away=None) -> bool:
    """
    Check if there is a wall at the back left of the micromouse.

    Args:
        half_steps_away (int, optional): The number of half steps away from the micromouse. Defaults to None.

    Returns:
        bool: True if there is a wall, False otherwise.
    """
    return checkWall("wallBackLeft", half_steps_away)


def wallBackRight(half_steps_away=None) -> bool:
    """
    Check if there is a wall at the back-right position.

    Args:
        half_steps_away (int, optional): The number of half steps away from the current position. Defaults to None.

    Returns:
        bool: True if there is a wall, False otherwise.
    """
    return checkWall("wallBackRight", half_steps_away)


def moveForward(distance=None) -> None:
    """
    Moves the mouse forward by the specified distance.

    Args:
        distance (float, optional): The distance to move forward. If not specified,
            the mouse will move forward by a default distance.

    Raises:
        MouseCrashedError: If the mouse crashes while moving forward.

    Returns:
        None
    """
    args = ["moveForward"]
    # Don't append distance argument unless explicitly specified, for
    # backwards compatibility with older versions of the simulator
    if distance is not None:
        args.append(distance)
    response = command(args=args, return_type=str)
    if response == "crash":
        raise MouseCrashedError()


def moveForwardHalf(num_half_steps=None) -> None:
    """
    Moves the mouse forward by half the number of steps specified.

    Args:
        num_half_steps (int, optional): The number of half steps to move forward. Defaults to None.

    Raises:
        MouseCrashedError: If the mouse crashes during the movement.

    Returns:
        str: The response from the command.
    """
    args = ["moveForwardHalf"]
    if num_half_steps is not None:
        args.append(num_half_steps)
    response = command(args=args, return_type=str)
    if response == "crash":
        raise MouseCrashedError()


def turnRight() -> str:
    """
    Turns the micromouse simulator robot to the right.

    Args:
        None

    Returns:
        str: The result of the turnRight command.
    """
    command(args=["turnRight"], return_type=str)


def turnLeft() -> str:
    """
    Turns the micromouse left.

    Returns:
        str: The command to turn left.
    """
    command(args=["turnLeft"], return_type=str)


def turnRight90() -> None:
    """
    Turns the micromouse robot 90 degrees to the right.
    """
    turnRight()


def turnLeft90() -> None:
    """
    Turns the micromouse 90 degrees to the left.
    """
    turnLeft()


def turnRight45() -> str:
    """
    Turns the micromouse robot 45 degrees to the right.

    Args:
        None

    Returns:
        str: The command to turn the robot 45 degrees to the right.
    """
    command(args=["turnRight45"], return_type=str)


def turnLeft45() -> None:
    """
    Turns the micromouse left by 45 degrees.
    Returns:
        str: The command executed.
    """
    command(args=["turnLeft45"], return_type=str)


def setWall(x, y, direction) -> None:
    """
    Sets a wall at the specified coordinates and direction.

    Args:
        x (int): The x-coordinate of the cell.
        y (int): The y-coordinate of the cell.
        direction (str): The direction of the wall to set ('north', 'south', 'east', 'west').

    Returns:
        None
    """
    command(args=["setWall", x, y, direction])


def clearWall(x, y, direction) -> None:
    """
    Clears the wall at the specified coordinates and direction.

    Args:
        x (int): The x-coordinate of the cell.
        y (int): The y-coordinate of the cell.
        direction (str): The direction of the wall to clear ('N', 'E', 'S', 'W').

    Returns:
        None
    """
    command(args=["clearWall", x, y, direction])


def setColor(x, y, color) -> None:
    """
    Set the color of a specific location on the micromouse simulator grid.

    Args:
        x (int): The x-coordinate of the location.
        y (int): The y-coordinate of the location.
        color (str): The color to set at the location.

    Returns:
        None
    """
    command(args=["setColor", x, y, color])


def clearColor(x, y) -> None:
    """
    Clears the color at the specified coordinates.

    Args:
        x (int): The x-coordinate of the color to clear.
        y (int): The y-coordinate of the color to clear.
    """
    command(args=["clearColor", x, y])


def clearAllColor() -> None:
    """
    Clears all color settings.
    """
    command(args=["clearAllColor"])


def setText(x, y, text) -> None:
    """
    Set the text at the specified coordinates.

    Args:
        x (int): The x-coordinate of the text.
        y (int): The y-coordinate of the text.
        text (str): The text to be set.

    Returns:
        None
    """
    command(args=["setText", x, y, text])


def clearText(x, y) -> None:
    """
    Clears the text at the specified coordinates (x, y).

    Args:
        x (int): The x-coordinate of the text.
        y (int): The y-coordinate of the text.
    """
    command(args=["clearText", x, y])


def clearAllText() -> None:
    """
    Clears all text in the simulator.
    """
    command(args=["clearAllText"])


def wasReset() -> bool:
    """
    Checks if the micromouse simulator was reset.

    Returns:
        bool: True if the simulator was reset, False otherwise.
    """
    return command(args=["wasReset"], return_type=bool)


def ackReset() -> str:
    """
    Resets the acknowledgement state.

    Returns:
        str: The acknowledgement reset command.
    """
    command(args=["ackReset"], return_type=str)
