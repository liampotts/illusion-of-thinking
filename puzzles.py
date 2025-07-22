import json
import re


class Puzzle:
    NAME = "Puzzle"
    SHORT_NAME = "Puzzle"
    SYSTEM_PROMPT = ""
    USER_PROMPT = ""

    def __init__(self, n: int = 1):
        self.n = n
        self.board = None
        self.goal = None

    def parse_solution(self, solution: str) -> list[list[int]]:
        raise NotImplementedError("Subclasses must implement this method")

    def play(self, moves: list[list[int]]):
        raise NotImplementedError("Subclasses must implement this method")

    def move(self, *args):
        raise NotImplementedError("Subclasses must implement this method")

    def evaluate(self, solution: str) -> tuple[bool, str]:
        try:
            moves = self.parse_solution(solution)
        except ValueError as e:
            return False, "Failed to parse solution. Error: " + str(e)

        try:
            self.play(moves)
        except ValueError as e:
            return False, "Failed to complete moves. Error: " + str(e)

        solved = self.board == self.goal
        if solved:
            return True, f"Solved in {len(moves)} moves."
        else:
            return (
                False,
                f"Failed after {len(moves)} moves. Got: {self.board}. Expected: {self.goal}",
            )


class TowersOfHanoi(Puzzle):
    NAME = "Towers Of Hanoi"
    SHORT_NAME = "Hanoi"
    SYSTEM_PROMPT = """You are a helpful assistant. Solve this puzzle for me.
There are three pegs and n disks of different sizes stacked on the first peg.
The disks are numbered from 1 (smallest) to n (largest). Disk moves in this puzzle should follow:
1. Only one disk can be moved at a time.
2. Each move consists of taking the upper disk from one stack and placing it on top of another stack.
3. A larger disk may not be placed on top of a smaller disk.
The goal is to move the entire stack to the third peg.

Example: With 3 disks numbered 1 (smallest), 2, and 3 (largest), the initial state is [[3, 2, 1], [], []], and a solution might be:

moves = [[1 , 0, 2], [2, 0, 1], [1, 2, 1], [3, 0, 2], [1, 1, 0], [2, 1, 2], [1, 0, 2]]

This means: Move disk 1 from peg 0 to peg 2, then move disk 2 from peg 0 to peg 1, and so on.

Requirements:
• When exploring potential solutions in your thinking process, always include the corresponding
complete list of moves.
• The positions are 0-indexed (the leftmost peg is 0).
• Ensure your final answer includes the complete list of moves in the format: moves = [[disk id, from peg, to peg], ...]"""

    USER_PROMPT = """I have a puzzle with {n} disks of different sizes with
Initial configuration:
• Peg 0: {initial_state}
• Peg 1: (empty)
• Peg 2: (empty)

Goal configuration:
• Peg 0: (empty)
• Peg 1: (empty)
• Peg 2: {goal_state}

Rules:
• Only one disk can be moved at a time.
• Only the top disk from any stack can be moved.
• A larger disk may not be placed on top of a smaller disk.

Find the sequence of moves to transform the initial configuration into the goal configuration."""

    def __init__(self, n: int = 1):
        self.n = n
        self.board = [list(range(n, 0, -1)), [], []]
        self.goal = [[], [], list(range(n, 0, -1))]

    def user_prompt(self):
        if self.n == 1:
            state = "1 (top)"
        else:
            stack = list(range(self.n, 0, -1))
            state = (
                ", ".join([f"{stack[0]} (botton)"] + list(map(str, stack[1:])))
                + " (top)"
            )

        return self.USER_PROMPT.format(n=self.n, initial_state=state, goal_state=state)

    def parse_solution(self, solution: str) -> list[list[int]]:
        candidates = re.findall(r"moves = (\[\[.*?\]\])", solution)
        if len(candidates) == 0:
            raise ValueError(
                "No moves found in solution. Expected format: moves = [[disk id, from peg, to peg], ...]"
            )
        moves = json.loads(candidates[-1])
        return moves

    def play(self, moves: list[list[int]]):
        for move in moves:
            if len(move) != 3 or not all(isinstance(x, int) for x in move):
                raise ValueError(
                    f"Invalid move: {move}. Must be a list of three integers."
                )
            self.move(*move)

    def move(self, disk: int, from_peg: int, to_peg: int):
        if disk > self.n or disk < 1:
            raise ValueError(
                f"Invalid disk number: {disk}. Must be between 1 and {self.n}"
            )
        if from_peg < 0 or from_peg > 2:
            raise ValueError(
                f"Invalid from peg number: {from_peg}. Must be between 0 and 2"
            )
        if to_peg < 0 or to_peg > 2:
            raise ValueError(
                f"Invalid to peg number: {to_peg}. Must be between 0 and 2"
            )
        if len(self.board[from_peg]) == 0 or self.board[from_peg][-1] != disk:
            raise ValueError(f"From peg {from_peg} does not contain disk {disk}")
        if len(self.board[to_peg]) > 0 and self.board[to_peg][-1] < disk:
            raise ValueError(
                f"Cannot place disk {disk} on top of disk {self.board[to_peg][-1]}"
            )

        self.board[to_peg].append(self.board[from_peg].pop())


class CheckerJumping(Puzzle):
    NAME = "Checker Jumping"
    SHORT_NAME = "Jumping"
    SYSTEM_PROMPT = """You are a helpful assistant. Solve this puzzle for me.
On a one-dimensional board, there are red checkers ('R'), blue checkers ('B'), and one empty
space ('_'). A checker can move by either:
1. Sliding forward into an adjacent empty space, or
2. Jumping over exactly one checker of the opposite color to land in an empty space.
The goal is to swap the positions of all red and blue checkers, effectively mirroring the initial state.

Example: If the initial state is ['R', '_', 'B'], the goal is to reach ['B', '_', 'R'].
Your solution should be a list of moves where each move is represented as [checker_color, position_from, position_to]. For example:

moves = [['R', 0, 1], ['B', 2, 0], ['R', 1, 2]]

This means: Move the red checker from position 0 to 1, then move the blue checker from position 2 to 0, and so on.

Requirements:
• When exploring potential solutions in your thinking process, always include the corresponding complete list of moves.
• The positions are 0-indexed (the leftmost position is 0).
• Ensure your final answer includes the complete list of moves for final solution in the format: moves = [[checker_color, position_from, position_to], ...]"""

    USER_PROMPT = """I have a puzzle with 2*{n}+1 positions, where {n} red checkers ('R') on left, {n} blue checkers ('B') on right, and one empty space ('_') in between are arranged in a line.
Initial board: {initial_board}

Goal board: {goal_board}

Rules:
• A checker can slide into an adjacent empty space.
• A checker can jump over exactly one checker of the opposite color to land in an empty space.
• Checkers cannot move backwards (towards their starting side).

Find the minimum sequence of moves to transform the initial board into the goal board."""

    def __init__(self, n: int = 1):
        self.n = n
        self.board = ["R"] * n + ["_"] + ["B"] * n
        self.goal = ["B"] * n + ["_"] + ["R"] * n

    def user_prompt(self):
        return self.USER_PROMPT.format(
            n=self.n, initial_board=self.board, goal_board=self.goal
        )

    def parse_solution(self, solution: str) -> list[list[int]]:
        candidates = re.findall(r"moves = (\[\[.*?\]\])", solution)
        if len(candidates) == 0:
            raise ValueError(
                "No moves found in solution. Expected format: moves = [[checker_color, position_from, position_to], ...]"
            )
        candidate = re.sub("'", '"', candidates[-1])
        moves = json.loads(candidate)
        return moves

    def play(self, moves: list[list[int]]):
        for move in moves:
            if (
                len(move) != 3
                or move[0] not in ["B", "R"]
                or not all(isinstance(x, int) for x in move[1:])
            ):
                raise ValueError(
                    f"Invalid move: {move}. Must be a list of three elements: checker_color, position_from, position_to."
                )
            self.move(*move)

    def move(self, checker_color: str, position_from: int, position_to: int):
        if checker_color not in ["B", "R"]:
            raise ValueError(
                f"Invalid checker color: {checker_color}. Must be 'B' or 'R'."
            )
        if position_from < 0 or position_from > len(self.board) - 1:
            raise ValueError(
                f"Invalid position from: {position_from}. Must be between 0 and {len(self.board) - 1}"
            )
        if position_to < 0 or position_to > len(self.board) - 1:
            raise ValueError(
                f"Invalid position to: {position_to}. Must be between 0 and {len(self.board) - 1}"
            )
        if self.board[position_from] != checker_color:
            raise ValueError(
                f"From position {position_from} does not contain checker {checker_color}"
            )
        if self.board[position_to] != "_":
            raise ValueError(f"To position {position_to} is not empty")

        self.board[position_to] = checker_color
        self.board[position_from] = "_"


class RiverCrossing(Puzzle):
    NAME = "River Crossing"
    SHORT_NAME = "Crossing"
    SYSTEM_PROMPT = """You are a helpful assistant. Solve this puzzle for me.
You can represent actors with a_1, a_2, ... and agents with A_1, A_2, ... .
Your solution must be a list of boat moves where each move indicates the people on the boat. For example, if there were two actors and two agents, you should return:

moves = [["A_2", "a_2"], ["A_2"], ["A_1", "A_2"], ["A_1"], ["A_1", "a_1"]]

which indicates that in the first move, A_2 and a_2 row from left to right, and in the second move, A_2 rows from right to left and so on.

Requirements:
• When exploring potential solutions in your thinking process, always include the corresponding complete list of boat moves.
• The list shouldn’t have comments.
• Ensure your final answer also includes the complete list of moves for final solution."""

    USER_PROMPT = (
        "{n} actors and their {n} agents want to cross a river in a boat that is capable of holding only {k} people at a time, "
        "with the constraint that no actor can be in the presence of another agent, including while riding the boat, unless"
        "their own agent is also present, because each agent is worried their rivals will poach their client. Initially, all"
        "actors and agents are on the left side of the river with the boat. How should they cross the river? (Note: the boat "
        "cannot travel empty)"
    )

    def __init__(self, n: int = 1):
        self.n = n
        self.k = 2 if n <= 3 else 3
        self.people = set()
        for i in range(n):
            self.people.add(f"A_{i+1}")
            self.people.add(f"a_{i+1}")
        self.board = [self.people.copy(), set()]
        self.goal = [set(), self.people.copy()]

    def user_prompt(self):
        return self.USER_PROMPT.format(n=self.n, k=self.k)

    def parse_solution(self, solution: str) -> list[list[int]]:
        candidates = re.findall(r"moves = (\[\[.*?\]\])", solution)
        if len(candidates) == 0:
            raise ValueError(
                "No moves found in solution. Expected format: moves = [[person, ...], ...]"
            )
        candidate = re.sub("'", '"', candidates[-1])
        moves = json.loads(candidate)
        return moves

    def play(self, moves: list[list[str]]):
        boat = 0
        for move in moves:
            self.move(set(move), boat)
            boat = 1 - boat

    def move(self, people: set[str], boat: int):
        def actor_safe(actor: str, group: set[str]) -> bool:
            agent = "A_" + actor[2:]
            return (
                actor not in group
                or agent in group
                or all([p[0] == "a" for p in group])
            )

        if len(people) > self.k:
            raise ValueError(
                f"Invalid move: {people}. Boat can only hold {self.k} people."
            )
        if len(people) == 0:
            raise ValueError(f"Invalid move: {people}. Boat cannot travel empty.")
        for person in people:
            if person not in self.people:
                raise ValueError(
                    f"Invalid person: {person}. Must be one of {self.people}"
                )
            if person not in self.board[boat]:
                raise ValueError(f"Invalid move. {person} not available to move.")

        remain = self.board[boat] - people
        planned = self.board[1 - boat] | people
        for i in range(self.n):
            actor = f"a_{i+1}"
            if (
                not actor_safe(actor, people)
                or not actor_safe(actor, remain)
                or not actor_safe(actor, planned)
            ):
                raise ValueError(
                    f"Invalid move: {people}. Cannot leave an unattended actor in the presence of another agent."
                )

        self.board[boat] -= people
        self.board[1 - boat] |= people


class BlocksWorld(Puzzle):
    NAME = "Blocks World"
    SHORT_NAME = "Blocks"
    SYSTEM_PROMPT = """You are a helpful assistant. Solve this puzzle for me.
In this puzzle, there are stacks of blocks, and the goal is to rearrange them into a target configuration using a sequence of moves where:
• Only the topmost block from any stack can be moved.
• A block can be placed either on an empty position or on top of another block.

Example: With initial state [["A", "B"], ["C"], []] and goal state [["A"], ["B"], ["C"]], a solution might be:
moves = [[" C " , 1 , 2] , [" B " , 0 , 1]]

This means: Move block C from stack 1 to stack 2, then move block B from stack 0 to stack 1.

Requirements:
• When exploring potential solutions in your thinking process, always include the corresponding complete list of moves.
• Ensure your final answer also includes the complete list of moves for final solution in the format: moves = [[block, from stack, to stack], ...]"""

    USER_PROMPT = """I have a puzzle with {n} blocks.
Initial state:
{initial_state}

Goal state:
{goal_state}

Find the minimum sequence of moves to transform the initial state into the goal state.
Remember that only the topmost block of each stack can be moved."""

    def __init__(self, n: int):
        self.n = n
        self.blocks = [chr(i) for i in range(65, 65 + n)]
        split = (n + 1) // 2
        self.board = [self.blocks[:split], self.blocks[split:], []]
        self.goal = [[], [], []]
        if n % 2 == 0:
            for i in range(split):
                self.goal[0].append(self.board[1][-(i + 1)])
                self.goal[0].append(self.board[0][-(i + 1)])
        else:
            for i in range(split - 1):
                self.goal[0].append(self.board[0][-(i + 1)])
                self.goal[0].append(self.board[1][-(i + 1)])
            self.goal[0].append(self.board[0][0])

    def user_prompt(self):
        initial_state = "\n".join(
            [f"Stack {i}: {self.board[i]} (top)" for i in range(len(self.board))]
        )
        goal_state = "\n".join(
            [f"Stack {i}: {self.goal[i]} (top)" for i in range(len(self.goal))]
        )
        return self.USER_PROMPT.format(
            n=self.n, initial_state=initial_state, goal_state=goal_state
        )

    def parse_solution(self, solution: str) -> list[list[int]]:
        candidates = re.findall(r"moves = (\[\[.*?\]\])", solution)
        if len(candidates) == 0:
            raise ValueError(
                "No moves found in solution. Expected format: moves = [[block, position_from, position_to], ...]"
            )
        candidate = re.sub("'", '"', candidates[-1])
        moves = json.loads(candidate)
        return moves

    def play(self, moves: list[list[int]]):
        for move in moves:
            if len(move) != 3 or not all(isinstance(x, int) for x in move[1:]):
                raise ValueError(
                    f"Invalid move: {move}. Must be a list of three elements: block, position_from, position_to."
                )
            self.move(*move)

    def move(self, block: str, position_from: int, position_to: int):
        if block not in self.blocks:
            raise ValueError(f"Invalid block: {block}. Must be one of {self.blocks}")
        if position_from < 0 or position_from > len(self.board) - 1:
            raise ValueError(
                f"Invalid position from: {position_from}. Must be between 0 and {len(self.board) - 1}"
            )
        if position_to < 0 or position_to > len(self.board) - 1:
            raise ValueError(
                f"Invalid position to: {position_to}. Must be between 0 and {len(self.board) - 1}"
            )
        if self.board[position_from][-1] != block:
            raise ValueError(
                f"From position {position_from} does not have block {block} on top"
            )

        self.board[position_to].append(self.board[position_from].pop())


class NQueens(Puzzle):
    NAME = "N Queens"
    SHORT_NAME = "Queens"
    SYSTEM_PROMPT = """You are a helpful assistant. Solve this puzzle for me. Place n queens on an n x n chess board so that no two queens threaten each other. The board is 0-indexed where the top-left corner is [0, 0].

Example: With n=4 one valid placement is:

moves = [[0, 1], [1, 3], [2, 0], [3, 2]]

This means a queen is placed at row 0 column 1, row 1 column 3, and so on.

Requirements:
• When exploring potential solutions in your thinking process, always include the corresponding complete list of queen positions.
• Ensure your final answer includes the list of positions in the format: moves = [[row, column], ...]."""

    USER_PROMPT = "Place {n} queens on a {n}x{n} board so that no two queens attack each other. Provide their positions as 0-indexed coordinates."

    def __init__(self, n: int = 1):
        self.n = n
        self.board: list[tuple[int, int]] = []

    def user_prompt(self):
        return self.USER_PROMPT.format(n=self.n)

    def parse_solution(self, solution: str) -> list[list[int]]:
        candidates = re.findall(r"moves = (\[\[.*?\]\])", solution)
        if len(candidates) == 0:
            raise ValueError(
                "No moves found in solution. Expected format: moves = [[row, column], ...]"
            )
        moves = json.loads(candidates[-1])
        return moves

    def play(self, moves: list[list[int]]):
        if len(moves) != self.n:
            raise ValueError(
                f"Invalid solution length: {len(moves)}. Expected {self.n} positions."
            )
        self.board = []
        for move in moves:
            if len(move) != 2 or not all(isinstance(x, int) for x in move):
                raise ValueError(
                    f"Invalid position: {move}. Must be a list of two integers: row and column."
                )
            self.move(*move)

    def move(self, row: int, col: int):
        if row < 0 or row >= self.n or col < 0 or col >= self.n:
            raise ValueError(
                f"Invalid position: [{row}, {col}]. Must be between 0 and {self.n - 1}."
            )
        for r, c in self.board:
            if r == row or c == col or abs(r - row) == abs(c - col):
                raise ValueError(
                    f"Invalid position: [{row}, {col}] conflicts with existing queen at [{r}, {c}]."
                )
        self.board.append((row, col))

    def evaluate(self, solution: str) -> tuple[bool, str]:
        try:
            moves = self.parse_solution(solution)
        except ValueError as e:
            return False, "Failed to parse solution. Error: " + str(e)

        try:
            self.play(moves)
        except ValueError as e:
            return False, "Failed to place queens. Error: " + str(e)

        return True, f"Solved with {self.n} queens."


if __name__ == "__main__":
    puzzle = TowersOfHanoi(3)
    solution = "text\nmoves = [[1 , 0, 2], [2, 0, 1], [1, 2, 1], [3, 0, 2], [1, 1, 0], [2, 1, 2], [1, 0, 2]]\ntext"
    print(puzzle.evaluate(solution))

    puzzle = CheckerJumping(1)
    solution = "text\nmoves = [['R', 0, 1], ['B', 2, 0], ['R', 1, 2]]\ntext"
    print(puzzle.evaluate(solution))

    puzzle = RiverCrossing(2)
    solution = "text\nmoves = [['A_2', 'a_2'], ['A_2'], ['A_1', 'A_2'], ['A_1'], ['A_1', 'a_1']]\ntext"
    print(puzzle.evaluate(solution))

    puzzle = BlocksWorld(3)
    solution = "text\nmoves = [['B', 0, 2], ['A', 0, 1], ['B', 2, 0], ['A', 1, 2], ['C', 1, 0], ['A', 2, 0]]\ntext"
    print(puzzle.evaluate(solution))

    puzzle = NQueens(4)
    solution = "text\nmoves = [[0, 1], [1, 3], [2, 0], [3, 2]]\ntext"
    print(puzzle.evaluate(solution))
