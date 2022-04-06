from tabulate import tabulate

from csp import CSP_Answer, CSP_Solver, SEQUENTIAL_HEURISTIC, RANDOM_HEURISTIC
from utils import get_answer_in_pos, null_answer


def futoshiki_tester(answer: CSP_Answer, solver: CSP_Solver, answers: list[CSP_Answer], futoshiki):
    futoshiki: Futoshiki
    # condition one - constrains

    for con in futoshiki.bigger_constraint:
        if con.smaller_pos == answer.variable_position:
            second = get_answer_in_pos(con.bigger_pos[0], con.bigger_pos[1], answers)
            answer_smaller = True
        elif con.bigger_pos == answer.variable_position:
            second = get_answer_in_pos(con.smaller_pos[0], con.smaller_pos[1], answers)
            answer_smaller = False
        else:
            continue

        if second == null_answer:
            continue
        if answer_smaller and second.answer_domain <= answer.answer_domain:
            return False
        elif not answer_smaller and answer.answer_domain <= second.answer_domain:
            return False

    # condition two - columns and rows
    table = futoshiki.get_futoshiki_table(answers + [answer], empty_string="x")

    row = list(filter(lambda d: d != "x", table[answer.variable_position[1]]))

    # print(row)
    if len(set(row)) != len(row):
        return False

    column = list(filter(lambda d: d != "x", [x[answer.variable_position[0]] for x in table]))
    # print(column)
    if len(set(column)) != len(column):
        return False

    return True

    # Codition one - CHECK FOR Unique colums?


class FutoshikiConstraint:
    def __init__(self, smaller_pos, bigger_pos):
        self.smaller_pos = smaller_pos
        self.bigger_pos = bigger_pos
        assert smaller_pos[0] == bigger_pos[0] or smaller_pos[1] == bigger_pos[1]

    def __str__(self):
        return str(self.smaller_pos) + " " + str(self.bigger_pos)


class Futoshiki:

    def generate_unsolved_positions(self):
        l = list()
        arra = self.get_futoshiki_table(empty_string=".")
        for y in range(len(arra)):
            for x in range(len(arra[y])):
                if arra[y][x] == ".":
                    l.append((x, y))
        return l

    def __init__(self, n: int, loaded_numbers: list[CSP_Answer], bigger_constraint: list[FutoshikiConstraint]):
        self.n = n
        self.loaded_numbers = loaded_numbers
        self.bigger_constraint = bigger_constraint
        self.solver = CSP_Solver([x for x in range(n)], futoshiki_tester, self, self.generate_unsolved_positions())

    def try_solve_backtracking(self, heuristic, domain_heuristic):
        return self.solver.try_backtrack(self.loaded_numbers, heuristic, domain_heuristic)

    def try_solve_forward(self, heuristic, domain_heuristic):
        return self.solver.try_forward(self.loaded_numbers, heuristic, domain_heuristic)

    def get_futoshiki_table(self, answers: list[CSP_Answer] = None, add_equals: bool = False, empty_string: str = " ",
                            display_format=False):
        if answers is None:
            answers = self.loaded_numbers
        l = list()
        for i in range(self.n):
            l.append([empty_string] * self.n)
        # print(answers)

        for e in answers:
            l[e.variable_position[1]][e.variable_position[0]] = str(e.answer_domain + (1 if display_format else 0))
        if add_equals:
            for a in self.bigger_constraint:
                if a.smaller_pos[0] == a.bigger_pos[0]:
                    if a.smaller_pos[1] > a.bigger_pos[1]:
                        # print(f"{a.smaller_pos} {a.bigger_pos}")
                        l[a.smaller_pos[1]][a.smaller_pos[0]] = "\/\n" + l[a.smaller_pos[1]][a.smaller_pos[0]]
                    else:
                        l[a.smaller_pos[1]][a.smaller_pos[0]] += "\n/\\"
                else:
                    if a.smaller_pos[0] > a.bigger_pos[0]:
                        l[a.smaller_pos[1]][a.smaller_pos[0]] = ">" + l[a.smaller_pos[1]][a.smaller_pos[0]]
                    else:
                        l[a.smaller_pos[1]][a.smaller_pos[0]] += "<"

        return l


def load_futoshiki(file_name):
    answers = []
    constraints = []
    with open(file_name, "r", encoding="utf-8") as file:
        y = 0
        for l in file.readlines():
            l = l.strip()
            if "x" in l:
                x = 0
                for c in l:
                    if c == "x":
                        x += 1
                    elif c == ">":
                        constraints.append(FutoshikiConstraint((x, y), (x - 1, y)))
                    elif c == "<":
                        constraints.append(FutoshikiConstraint((x - 1, y), (x, y)))
                    elif c == "-":
                        continue
                    else:
                        answers.append(CSP_Answer((x, y), int(c) - 1))
                        x += 1
                y += 1
            else:
                x = 0
                for c in l:
                    if c == "-":
                        x += 1
                    elif c == ">":
                        constraints.append(FutoshikiConstraint((x, y), (x, y - 1)))
                        x += 1
                    elif c == "<":
                        constraints.append(FutoshikiConstraint((x, y - 1), (x, y)))
                        x += 1
                    else:
                        assert False
    # print(x)
    # print(y)
    return Futoshiki(y, answers, constraints)


def solve_futoshiki_backtrack(file_name, print_solutions=False, heuristic=SEQUENTIAL_HEURISTIC,
                              domain_heuristic=SEQUENTIAL_HEURISTIC):
    print(
        f"Trying futoshiki Backtracking with Heuristic: {'sequential' if heuristic == SEQUENTIAL_HEURISTIC else 'randomised'} and domain {domain_heuristic}")
    futoshiki = load_futoshiki(file_name)
    # print(tabulate(futoshiki.get_futoshiki_table(None, True, "x")))
    # for c in futoshiki.bigger_constraint:
    #     print(c)
    sol, tup = futoshiki.try_solve_backtracking(heuristic, domain_heuristic)
    print(f"FOUND {len(sol)} SOLUTIONS FOR {file_name}")
    if print_solutions:
        i = 1
        for e in sol:
            print(f"SOLUTION {i}")
            print(tabulate(futoshiki.get_futoshiki_table(e, True, "ERROR", display_format=True)))
            i += 1
    return tup


def solve_futoshiki_forward(file_name, print_solutions=False, heuristic=SEQUENTIAL_HEURISTIC,
                            domain_heuristic=SEQUENTIAL_HEURISTIC):
    print(
        f"Trying futoshiki Forward Checking with Heuristic: {'sequential' if heuristic == SEQUENTIAL_HEURISTIC else 'randomised'} and doamin {domain_heuristic}")
    futoshiki = load_futoshiki(file_name)
    sol, tup = futoshiki.try_solve_forward(heuristic, domain_heuristic)
    print(f"FOUND {len(sol)} SOLUTIONS FOR {file_name}")
    if print_solutions:
        i = 1
        for e in sol:
            print(f"SOLUTION {i}")
            print(tabulate(futoshiki.get_futoshiki_table(e, True, "ERROR", display_format=True)))
            i += 1
    return tup


if __name__ == '__main__':
    solve_futoshiki_backtrack("dane\\futoshiki", True, SEQUENTIAL_HEURISTIC, SEQUENTIAL_HEURISTIC)
    exit()
    with open("futoshiki_results3.txt", "w", encoding="utf-8") as output:
        output.write("input;method;heuristic;domain_heuristic;nodes;time\n")
        for heuristic in [SEQUENTIAL_HEURISTIC, RANDOM_HEURISTIC]:
            for domain_heuristic in [SEQUENTIAL_HEURISTIC, RANDOM_HEURISTIC]:
                for input_file in ["dane\\futoshiki_4x4", "dane\\futoshiki_5x5", "dane\\futoshiki_6x6"]:
                    sol = solve_futoshiki_backtrack(input_file, False, heuristic, domain_heuristic)
                    output.write(f"{input_file};backtracking;{heuristic};{domain_heuristic};{sol[0]};{sol[1]}\n")
                    sol = solve_futoshiki_forward(input_file, False, heuristic, domain_heuristic)
                    output.write(f"{input_file};forward;{heuristic};{domain_heuristic};{sol[0]};{sol[1]}\n")
    exit()

    solve_futoshiki_forward("dane\\futoshiki_4x4", True, SEQUENTIAL_HEURISTIC)
    solve_futoshiki_forward("dane\\futoshiki_4x4", False, SEQUENTIAL_HEURISTIC)
    solve_futoshiki_forward("dane\\futoshiki_4x4", False, RANDOM_HEURISTIC)
    solve_futoshiki_backtrack("dane\\futoshiki_4x4", False, SEQUENTIAL_HEURISTIC)
    solve_futoshiki_backtrack("dane\\futoshiki_4x4", False, RANDOM_HEURISTIC)
    exit(0)
    solve_futoshiki_forward("dane\\futoshiki_5x5", False)
    solve_futoshiki_forward("dane\\futoshiki_6x6", False)

    solve_futoshiki_backtrack("dane\\futoshiki_4x4", True)
    solve_futoshiki_backtrack("dane\\futoshiki_5x5", False)
    solve_futoshiki_backtrack("dane\\futoshiki_6x6", False)
    # print(tabulate(load_futoshiki("dane\\futoshiki_4x4").get_futoshiki_table(add_equals=True, empty_string="x")))
