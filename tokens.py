from enum import Enum

class TokenType(Enum):
    INT = "int"
    double = "double"
    BOOLEAN = "boolean"
    STRING = "string"
    POSITION = "position"
    MOVEABLE = "moveable"
    DEF = "def"
    WHILE = "while"
    IF = "if"
    ELSE = "else"
    RETURN = "return"
    NULL = "null"
    VAR = "var"
    TRUE = "true"
    FALSE = "false"
    ASTERISK = "*"
    SLASH = "/"
    PLUS = "+"
    MINUS = "-"
    MODUL = "%"
    ADDEQ = "+="
    SUBEQ = "-="
    MULEQ = "*="
    DIVEQ = "/="
    EXCL_MARK = "!"
    LEFT_BRACET = "{"
    RIGHT_BRACET = "}"
    LEFT_PARENTH = "("
    RIGHT_PARENTH = ")"
    LEFT_SQ_BRACKET = "["
    RIGHT_SQ_BRACKET = "]"
    SEMICOLON = ";"
    COLON = ":"
    COMMA = ","
    DOT = "."
    EQ = "="
    EQEQ = "=="
    LESS = "<"
    GREATER = ">"
    LESS_EQ = "<="
    GREATER_EQ = ">="
    AND = "&&"
    OR = "||"
    STRING_LITERAL = 1
    NUM_LITERAL_INT = 2
    NUM_LITERAL_DOUBLE = 3
    IDENTIFIER = 4
    FUNCTION_IDENTIFIER = 5
    ILLEGAL_TOKEN = 6

    @staticmethod
    def printAll():
        for member in TokenType.__members__:
            print(member)

    @staticmethod
    def getMatchingElseNone(string):
        for symbolic, member in TokenType.__members__.items():
            if member is not None and member.value == string:
                return member
        return None

class Token:
	def __init__(self, tokenType, value, pointer):
		self.tokenType = tokenType
		self.value = value
		self.pointer = pointer # self.pointer points at last character of that token

	def __str__(self):
		return (str(self.pointer) + ":").ljust(5) + ("\"" + str(self.value) + "\"").ljust(30) + str(self.tokenType)[10:]