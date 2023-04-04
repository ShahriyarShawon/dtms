from enum import Enum

from attrs import define

# test_str = "CS 260 [Min Grade: C] and (MATH 201 [Min Grade: C] or ENGR 231 [Min Grade: D]) and (MATH 221 [Min Grade: C] or MATH 222 [Min Grade: C]) and (MATH 311 [Min Grade: C] or MATH 410 [Min Grade: C] or ECE 361 [Min Grade: D])"

# test_str = "(DIGM 260 [Min Grade: D] or GMAP 260 [Min Grade: D]) and (CS 265 [Min Grade: C] or DIGM 141 [Min Grade: D])"


class TokenType(Enum):
    course = "course"
    lparen = "lparen"
    rparen = "rparen"
    and_ = "and"
    or_ = "or"


@define
class Token:
    value: str
    type: TokenType


class Lexer:
    def __init__(self, string: str):
        self.tokens = []
        self.index = 0
        self.string = string

    def get_course(self):
        course_name = ""
        while True:
            if self.string[self.index] == "[":
                self.index -= 1
                return course_name
            else:
                course_name += self.string[self.index]
                self.index += 1

    def get_min_grade(self):
        min_grade_str = ""
        while True:
            curr_char = self.string[self.index]
            if curr_char != "]":
                min_grade_str += curr_char
                self.index += 1
            else:
                min_grade_str += curr_char
                self.index += 1
                return min_grade_str

    def get_requirement(self):
        course_name = self.get_course().strip()
        min_grade = self.get_min_grade()
        return Token(f"{course_name} : {min_grade}", TokenType.course)

    def get_word(self):
        word = ""
        while True:
            curr_char = self.string[self.index]
            if curr_char == " ":
                self.index += 1
                tt = None
                if word == "and":
                    tt = TokenType.and_
                elif word == "or":
                    tt = TokenType.or_
                return Token(word, tt)
            else:
                word += curr_char
                self.index += 1

    def lex(self):
        tokens = []
        while True:
            if self.index >= len(self.string):
                break
            curr_char = self.string[self.index]
            if curr_char.isupper():
                tokens.append(self.get_requirement())
            elif curr_char.isalpha():
                tokens.append(self.get_word())
            elif curr_char == "(":
                tokens.append(Token("(", TokenType.lparen))
                self.index += 1
            elif curr_char == ")":
                tokens.append(Token(")", TokenType.rparen))
                self.index += 1
            elif curr_char == " ":
                self.index += 1
                continue
            else:
                print(f"unknown char {self.string[self.index]} at pos {self.index}")
        return tokens


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

    def get_inside_parens(self):
        choices = []
        while True:
            current_token = self.tokens[self.index]
            if current_token.type == TokenType.course:
                choices.append(current_token.value)
                self.index += 1
                continue
            elif current_token.type == TokenType.or_:
                self.index += 1
                continue
            elif current_token.type == TokenType.rparen:
                self.index += 1
                return choices

    def parse(self):
        courses = []
        while True:
            if self.index >= len(self.tokens):
                break
            current_token = self.tokens[self.index]
            if current_token.type == TokenType.course:
                courses.append([current_token.value])
                self.index += 1
                continue
            elif current_token.type == TokenType.and_:
                self.index += 1
                continue
            elif current_token.type == TokenType.lparen:
                self.index += 1
                parens_courses = self.get_inside_parens()
                courses.append(parens_courses)
                continue
            else:
                self.index += 1
        return courses


def organize(choices: list[list[str]]):
    if len(choices) == 1:
        return [[item] for item in choices[0]]

    first: list[str] = choices[0]
    rest: list[list[str]] = organize(choices[1:])

    out = []
    for i in first:
        for j in rest:
            cp = [item for item in j]
            cp.append(i)
            out.append(cp)
    return out


def get_paths(prereq_string):
    l = Lexer(prereq_string)
    lexxed_tokens = l.lex()
    p = Parser(lexxed_tokens)
    course_choices = p.parse()
    items = organize(course_choices)
    items = [item[::-1] for item in items]
    items = [" and ".join(item) for item in items]
    return items
