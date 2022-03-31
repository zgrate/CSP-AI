from csp import CSP_Answer

null_answer = CSP_Answer((-1, -1), -1)


def get_answer_in_pos(x, y, answers):
    p = (x, y)
    for e in answers:
        if e.variable_position == p:
            return e
    return null_answer
