# has no effect on the decorated function, only used for self-documenting purposes.
def overrideable(f):
    return f

__all__ = []
def public(f):
    __all__.append(f.__name__)
    return f

class LexerError(ValueError): pass
class ParserError(ValueError): pass

class EnumMetaDict(dict):

    def __init__(self):
        self.n = -1

    def __getitem__(self, item):
        if item.isupper():
            self.n += 1
            self[item] = self.n
            return self.n
        return super().__getitem__(item)


class EnumMeta(type):

    @classmethod
    def __prepare__(meta, name, bases):
        return EnumMetaDict()

@public
class Enum(metaclass = EnumMeta):
    pass


@public
class Lexer:

    def __init__(self, text: str):
        self.index = 0
        self.text = text

    def peek(self) -> str:
        try:
            return self.text[self.index]
        except IndexError:
            return ""

    def peek_next() -> str:
        try:
            return self.text[self.index + 1]
        except IndexError:
            return ""

    def next(self) -> str:
        self.index += 1
        try:
            self.text[self.index]
        except IndexError:
            return ""

    def match(self, c: str) -> bool:
        if self.peek() == c:
            self.next()
            return True
        return False

    def match_one_or_more(self, c: str):
        if self.match(c):
            while self.match(c):
                pass
            return True
        return False

    def pass(self, c: str):
        while self.match(c):
            pass

    def at_eof(self) -> bool:
        return self.peek() == ""

    @overrideable
    def error(self, msg: str):
        raise LexerError("Invalid character {!r} at index {}: {}".format(self.peek(), self.index, msg))

    @overrideable
    def token(self):
        raise NotImplementedError()

@public
class Parser:
    lex_class = Lexer

    def __init__(self, text: str):
        self.lexer = self.lex_class(text)
        self.token = self.lexer.token()

        self.prefix_parselets = {}
        self.infix_parselets = {}
        
        self.build_parselets()

    def peek(self):
        return self.token

    def next(self) -> None:
        self.token = self.lexer.token()

    def consume(self):
        t = self.peek()
        self.next()
        return t

    def match(self, type_):
        if self.peek().type == type_:
            self.next()
            return True
        return False

    def expect(self, type_):
        if not self.match(type_):
            self.error("Expected a {!r} token.".format(type_))

    @overrideable
    def error(self, msg):
        raise ParserError("Invalid token {!r} at index {}: {}".format(self.peek(), self.lexer.index, msg))

    @overrideable
    def build_parselets(self):
        raise NotImplementedError()

    def get_prefix_parselet(self, token):
        try:
            return self.prefix_parselets[token.type]
        except KeyError:
            self.error("Expected a prefix operator or value.")
            
    def get_infix_parselet(self, token):
        return self.infix_parselets[token.type]

    def get_precedence(self):
        try:
            infix_parselet = self.get_infix_parselet(self.peek())
        except KeyError:
            return 0
        else:
            return infix_parselet.precedence

    def parse(self, precedence: int) -> tuple:
        token = self.consume()

        prefix_parselet = self.get_prefix_parselet(token)
        left = prefix_parselet(self, token)
        
        while precedence < self.get_precedence():
            token = self.consume()

            infix_parselet = self.get_infix_parselet(token)
            left = infix_parselet(self, token, left)
            
        return left

            
    def expr(self):
        ast = self.parse(0)
        if self.lexer.at_eof():
            return ast
        self.error("Expected EOF.")

@public
class FixRegister:

    def register_eof(self, token_type):
        self.register_postfix_operator(token_type, 0)

    def register_operand(self, token_type):
        def parselet(parser, token):
            return (token.type, token.value)

        parselet.precedence = precedence = 0
        self.prefix_parselets[token_type] = parselet

    def register_prefix_operator(self, token_type, precedence):
        def parselet(parser, token):
            operand = self.parse(parselet.precedence)
            return (operand, token.type)

        parselet.precedence = precedence
        self.prefix_parselets[token_type] = parselet

    def register_infix_operator(self, token_type, precedence):
        def parselet(parser, token, left):
            right = parser.parse(parselet.precedence)
            return ((left, right), token.type)
        
        parselet.precedence = precedence
        self.infix_parselets[token_type] = parselet

    def register_postfix_operator(self, token_type, precedence):
        def parselet(parser, token, left):
            return (left, token.type)

        parselet.precedence = precedence 
        self.infix_parselets[token_type] = parselet

    def register_mixfix_operator(self, left_token_type, right_token_type, precedence):
        def parselet(parser, token, left):
            middle = parser.parse(parselet.precedence)
            parser.expect(right_token_type)
            right = parser.parse(parselet.precedence)
            return ((left, middle, right), (left_token_type, right_token_type))

        parselet.precedence = precedence
        self.infix_parselets[left_token_type] = parselet

    def register_parenthesis(self, left_token_type, right_token_type, precedence = 0):
        def parselet(parser, token):
            expr = self.parse(parselet.precedence)
            parser.expect(right_token_type)
            return expr

        parselet.precedence = precedence
        self.prefix_parselets[left_token_type] = parselet
