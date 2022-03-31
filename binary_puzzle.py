from typing import Any

import numpy as np
from tabulate import tabulate

from csp import CSP_Solver, SEQUENTIAL_HEURISTIC, RANDOM_HEURISTIC
from utils import *


def check_unique_columns_rows(answers: list, answer: CSP_Answer, puzzle):
    puzzle: BinaryPuzzle
    table = puzzle.binary_puzzle_get_array(answers + [answer], "x")

    zeros = 0
    ones = 0
    for y in range(puzzle.size_y):
        if table[y][answer.variable_position[0]] == "x":
            zeros = -1
            break
        elif table[y][answer.variable_position[0]] == 0:
            zeros += 1
        elif table[y][answer.variable_position[0]] == 1:
            ones += 1
        else:
            assert False

    if zeros != -1 and zeros != ones:
        return False

    zeros = 0
    ones = 0
    for x in range(puzzle.size_x):
        if table[answer.variable_position[1]][x] == "x":
            zeros = -1
            break
        elif table[answer.variable_position[1]][x] == 0:
            zeros += 1
        elif table[answer.variable_position[1]][x] == 1:
            ones += 1
        else:
            assert False

    if zeros != -1 and zeros != ones:
        return False

    uniques = list()

    for row in table:
        if "x" not in row:
            n = (np.packbits(row))[0]
            if n in uniques:
                return False
            uniques.append(n)

    # u = "".join(list(map(lambda d: str(d), row)))
    #
    #     if "x" not in u:
    #         if u in uniques:
    #             return False
    #         uniques.append(u)

    uniques.clear()
    np.transpose(table)
    for row in table:
        if "x" not in row:
            n = (np.packbits(row))[0]
            if n in uniques:
                return False
            uniques.append(n)

    # for column in range(len(table[0])):
    #     u = ""
    #     for row in range(len(table)):
    #         u += str(table[row][column])
    #
    #     if "x" not in u:
    #         if u in uniques:
    #             return False
    #         uniques.append(u)
    return True


def binary_puzzle_tester(answer: CSP_Answer, solver: CSP_Solver, answers: list[CSP_Answer], puzzle) -> bool:
    assert answer != null_answer
    assert answer.answer_domain in [0, 1]  # FIRST CASE
    puzzle: BinaryPuzzle
    x_pos, y_pos = answer.variable_position

    # SECOND CASE
    if x_pos > 0 and get_answer_in_pos(x_pos - 1, y_pos, answers).answer_domain == answer.answer_domain:
        if x_pos - 1 > 0 and get_answer_in_pos(x_pos - 2, y_pos, answers).answer_domain == answer.answer_domain:
            return False
    if x_pos < puzzle.size_x and get_answer_in_pos(x_pos + 1, y_pos, answers).answer_domain == answer.answer_domain:
        if x_pos + 1 < puzzle.size_x and get_answer_in_pos(x_pos + 2, y_pos,
                                                           answers).answer_domain == answer.answer_domain:
            return False

    if y_pos > 0 and get_answer_in_pos(x_pos, y_pos - 1, answers).answer_domain == answer.answer_domain:
        if y_pos - 1 > 0 and get_answer_in_pos(x_pos, y_pos - 2, answers).answer_domain == answer.answer_domain:
            return False
    if y_pos < puzzle.size_y and get_answer_in_pos(x_pos, y_pos + 1, answers).answer_domain == answer.answer_domain:
        if y_pos + 1 < puzzle.size_y and get_answer_in_pos(x_pos, y_pos + 2,
                                                           answers).answer_domain == answer.answer_domain:
            return False

    # THIRD CASE FOURTH CASE
    if not check_unique_columns_rows(answers, answer, puzzle):
        return False

    # FOURTH CASE

    return True


class BinaryPuzzle:
    loaded_data: list[CSP_Answer]

    def generate_unsolved_positions(self):
        l = list()
        arra = self.binary_puzzle_get_array()
        for y in range(len(arra)):
            for x in range(len(arra[y])):
                if arra[y][x] == ".":
                    l.append((x, y))

        return l

    def __init__(self, size_x, size_y, loaded_data):
        self.loaded_data = loaded_data
        self.size_x = size_x
        self.size_y = size_y
        self.solver = CSP_Solver([0, 1], binary_puzzle_tester, self, self.generate_unsolved_positions())

    def binary_puzzle_get_array(self, answers: list[CSP_Answer] = None, nothing_symbol: Any = "."):
        if answers is None:
            answers = self.loaded_data
        l = list()
        for i in range(self.size_y):
            l.append([nothing_symbol] * self.size_x)
        for e in answers:
            l[e.variable_position[1]][e.variable_position[0]] = e.answer_domain
        return l

    def try_solve_backtracking(self, heuristic: int):
        return self.solver.try_backtrack(self.loaded_data, heuristic)

    def __str__(self):
        return tabulate(self.binary_puzzle_get_array())

    def try_solve_forward(self, heuristic: int):
        return self.solver.try_forward(self.loaded_data, heuristic)


def load_binary_puzzle(filename: str) -> BinaryPuzzle:
    with open(filename, "r", encoding="utf-8") as file:
        loaded_data = list()
        y = 0
        for l in file.readlines():
            x = 0
            for c in l:
                if c == "1":
                    loaded_data.append(CSP_Answer((x, y), 1))
                elif c == "0":
                    loaded_data.append(CSP_Answer((x, y), 0))
                x += 1
            y += 1
        return BinaryPuzzle(x, y, loaded_data)


def solve_puzzle_backtrack(file_name, print_solutions=False, heuristic=SEQUENTIAL_HEURISTIC):
    puzzle = load_binary_puzzle(file_name)
    sol = puzzle.try_solve_backtracking(heuristic)
    print(f"FOUND {len(sol)} SOLUTIONS FOR {file_name}")
    if print_solutions:
        i = 1
        for e in sol:
            print(f"SOLUTION {i}")
            print(tabulate(puzzle.binary_puzzle_get_array(e, "x")))
            i += 1


def solve_puzzle_forward(file_name, print_solutions=False, heuristic=SEQUENTIAL_HEURISTIC):
    puzzle = load_binary_puzzle(file_name)
    sol = puzzle.try_solve_forward(heuristic)
    print(f"FOUND {len(sol)} SOLUTIONS FOR {file_name}")
    if print_solutions:
        i = 1
        for e in sol:
            print(f"SOLUTION {i}")
            print(tabulate(puzzle.binary_puzzle_get_array(e, "x")))
            i += 1


if __name__ == '__main__':
    puzzle = BinaryPuzzle(4, 4, [
        CSP_Answer((0, 0), 1),
        CSP_Answer((0, 1), 0),
        CSP_Answer((0, 2), 1),
        CSP_Answer((0, 3), 1),

        CSP_Answer((1, 0), 0),
        CSP_Answer((1, 1), 0),
        CSP_Answer((1, 2), 1),
        CSP_Answer((1, 3), 1),

        CSP_Answer((2, 0), 1),
        CSP_Answer((2, 1), 1),
        CSP_Answer((2, 2), 0),
        CSP_Answer((2, 3), 0),

        CSP_Answer((3, 0), 1),
        CSP_Answer((3, 1), 0),
        CSP_Answer((3, 2), 1),
        CSP_Answer((3, 3), 0),
    ])
    a = [1, 2, 3]
    b = [5, 6]
    c = a + b

    solve_puzzle_forward("dane\\binary_6x6", True, SEQUENTIAL_HEURISTIC)
    solve_puzzle_forward("dane\\binary_6x6", True, RANDOM_HEURISTIC)
    exit(0)
    solve_puzzle_forward("dane\\binary_8x8", False)
    solve_puzzle_forward("dane\\binary_10x10", False)

    solve_puzzle_backtrack("dane\\binary_6x6", True)
    solve_puzzle_backtrack("dane\\binary_8x8", False)
    solve_puzzle_backtrack("dane\\binary_10x10", False)

# binary_puzzle_tester(CSP_Answer((4, 3), 0), None, puzzle.loaded_data, puzzle)
