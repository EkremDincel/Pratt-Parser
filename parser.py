class ParserError(ValueError): pass

class Parser:

    def __init__(self, text):
        self.index = 0
        self.text = text
        self.state = True # whether parser in the initial state or not
        
    def next(self):
        self.index += 1

    def current(self):
        try:
            return self.text[self.index]
        except IndexError:
            raise EOFError()

    def match(self, c):
        if self.current() == c:
            self.next()
            return True
        return False
        
    def expect(self, c):
        if self.current() != c: raise ParserError()
        self.next()

    def stmt(self):
        if self.match('('):
            while self.inner_stmt(): pass
            self.expect(')')
            return True
        if self.match('['):
            while self.inner_stmt(): pass
            self.expect(']')
            return True
        if self.match('{'):
            while self.inner_stmt(): pass
            self.expect('}')
            return True
        return False

    def inner_stmt(self):
        try:
            self.stmt()
        except EOFError:
            raise ParserError()

    # main entry point for checking the validity of text
    def check(self):
        try:
            while self.stmt(): pass
        except ParserError:
            return False
        except EOFError:
            return True
        return False


def solution(s): return Parser(s).check()

##assert solution("[({()}([])[(){}])]") == True
assert solution("((())())") == True
assert solution("") == True
assert solution("[(){}]") == True
assert solution("()()") == True
assert solution("[(])") == False
assert solution("(") == False
        
        
