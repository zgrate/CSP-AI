import random
from typing import Callable, Optional, Any

SEQUENTIAL_HEURISTIC = 0
RANDOM_HEURISTIC = 1


class CSP_Answer:
    def __init__(self, variable_position, answer_domain):
        self.answer_domain = answer_domain
        self.variable_position = variable_position

    def __str__(self):
        return f"VARIABLE/POSITION: {self.variable_position} HAS VALUE {self.answer_domain}"

    def __eq__(self, other):
        if not isinstance(other, CSP_Answer):
            return False
        return self.answer_domain == other.answer_domain and self.variable_position == other.variable_position


class CSP_Solver:
    variables: list  # w binary - pozycje wszystkie wolne, w futuszimie - wszystkie wolne pola
    domain: list  # lista numerów

    def __init__(self, domain, goal_test, additional_data: Optional = None, variables: Optional[list] = None):
        self.variables = variables
        self.domain = domain
        self.additional_data = additional_data
        self.goal_test: Callable[[CSP_Answer, CSP_Solver, list[CSP_Answer], Optional], bool] = goal_test

    def try_backtrack(self, start_solution: list[CSP_Answer], heuristic: int) -> list[list[CSP_Answer]]:
        total_solutions = list()
        variables_counter = list(self.variables)
        if heuristic == RANDOM_HEURISTIC:
            random.shuffle(variables_counter)

        self.backtracking_recurrence(start_solution, list(self.variables), total_solutions, 0)
        return total_solutions

    def backtracking_recurrence(self, current_solution: list[CSP_Answer], variable_solutions_list: list,
                                total_solutions: list[list[CSP_Answer]], variable_index: int):
        if len(variable_solutions_list) == variable_index:
            total_solutions.append(current_solution)
        else:
            variable = variable_solutions_list[variable_index]
            for d in self.domain:
                answer = CSP_Answer(variable, d)
                if self.goal_test(answer, self, current_solution, self.additional_data):
                    l = list(current_solution)
                    l.append(answer)
                    self.backtracking_recurrence(l, variable_solutions_list, total_solutions, variable_index + 1)

    def try_forward(self, start_solution: list[CSP_Answer], heuristic: int):
        total_solutions = list()
        tf = list(map(lambda d: (d, list(self.domain)), self.variables))
        if heuristic == RANDOM_HEURISTIC:
            random.shuffle(tf)
        self.forward_checking_recurrence(start_solution, tf, total_solutions, 0)
        return total_solutions

    def forward_checking_recurrence(self, current_solution: list[CSP_Answer],
                                    variable_solutions_list: list[Any, list[Any]],
                                    total_solutions: list[list[CSP_Answer]], variable_index: int):
        if len(total_solutions) > 0:
            return

        if len(variable_solutions_list) == variable_index:
            total_solutions.append(current_solution)
        else:
            variable, domain = variable_solutions_list[variable_index]
            assert len(domain) > 0
            if len(domain) == 1:
                answer = CSP_Answer(variable, domain[0])
                current = current_solution + [answer]
                if self.goal_test(answer, self, current, self.additional_data):
                    self.forward_checking_recurrence(current, variable_solutions_list, total_solutions,
                                                     variable_index + 1)
            else:
                for d in domain:
                    answer = CSP_Answer(variable, d)
                    if self.goal_test(answer, self, current_solution, self.additional_data):
                        curr_sol = current_solution + [answer]
                        assert curr_sol != current_solution
                        variables = variable_deep_clone(variable_solutions_list)
                        invalid = False
                        v = variable_index
                        # for variable, domain in variables:
                        for i in range(v + 1, len(variables)):
                            var_in, do_in = variables[i]
                            do_in: list
                            for do in list(do_in):
                                if not self.goal_test(CSP_Answer(var_in, do), self, curr_sol, self.additional_data):
                                    do_in.remove(do)
                                if len(do_in) == 0:
                                    invalid = True
                                    break
                        if not invalid:
                            self.forward_checking_recurrence(curr_sol, variables, total_solutions, v + 1)


def variable_deep_clone(variable_solutions_list: list[Any, list[Any]]):
    l = list()
    for variable, domain in variable_solutions_list:
        l.append((variable, list(domain)))
    return l
