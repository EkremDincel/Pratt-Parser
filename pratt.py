from interpreter import *
from collections import namedtuple
from enum import IntEnum

Token = namedtuple("Token", ("type", "value"))

class TokenTypes(IntEnum):
    (PLUS,
    MINUS,
    MULTI,
    DIVIDE,
    BANG,
    CONST,
    NAME,
    LPAREN,
    RPAREN,
    EOF,)=range(10)

class Lexer(Lexer):

    def token(self) -> Token:
        while self.peek().isspace():
            self.next()

        if self.match("("): return Token(TokenTypes.LPAREN, "(")
        if self.match(")"): return Token(TokenTypes.RPAREN, ")")

        if self.match("+"): return Token(TokenTypes.PLUS, "+")
        if self.match("-"): return Token(TokenTypes.MINUS, "+")
        if self.match("*"): return Token(TokenTypes.MULTI, "+")
        if self.match("/"): return Token(TokenTypes.DIVIDE, "+")

        if self.match("!"): return Token(TokenTypes.BANG, "!")

        start = self.index

        if self.peek().isnumeric():
            self.next()
            while self.peek().isnumeric():
                self.next()

            if self.match("."):
                while self.peek().isnumeric():
                    self.next()
                if self.peek().isalpha():
                    self.error("Variable names can't start with numbers.")
                return Token(TokenTypes.CONST, float(self.text[start:self.index]))

            if self.peek().isalpha():
                self.error("Variable names can't start with numbers.")
            return Token(TokenTypes.CONST, int(self.text[start:self.index]))

        if self.peek().isalpha():
            self.next()
            while self.peek().isalpha():
                self.next()
            return Token(TokenTypes.NAME, self.text[start:self.index])

        if self.peek() == "":
            return Token(TokenTypes.EOF, "")

        self.error("Can't find any valid token.")



class Parser(Parser, FixRegister):
    lex_class = Lexer

    def build_parselets(self):
        self.register_eof(TokenTypes.EOF)
        
        self.register_operand(TokenTypes.NAME)
        self.register_operand(TokenTypes.CONST)

        self.register_prefix_operator(TokenTypes.PLUS, 4)
        self.register_prefix_operator(TokenTypes.MINUS, 4)

        self.register_infix_operator(TokenTypes.PLUS, 1)
        self.register_infix_operator(TokenTypes.MINUS, 1)

        self.register_infix_operator(TokenTypes.MULTI, 2)
        self.register_infix_operator(TokenTypes.DIVIDE, 2)

        self.register_postfix_operator(TokenTypes.BANG, 3)

        self.register_parenthesis(TokenTypes.LPAREN, TokenTypes.RPAREN)
