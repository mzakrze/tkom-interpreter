from lexer import *
from tokens import *
from parser import *
import copy

literals = (TokenType.STRING_LITERAL, TokenType.NUM_LITERAL_INT, TokenType.NUM_LITERAL_DOUBLE, TokenType.TRUE, TokenType.FALSE)
binaryOperators = (TokenType.PLUS, TokenType.MINUS, TokenType.ADDEQ, TokenType.SUBEQ, TokenType.MULEQ, TokenType.DIVEQ, TokenType.ASTERISK, TokenType.SLASH, TokenType.EQ, TokenType.EQEQ, TokenType.LESS, TokenType.LESS_EQ, TokenType.GREATER, TokenType.GREATER_EQ, TokenType.AND, TokenType.OR)
unaryOperators = (TokenType.EXCL_MARK, None)
separators = (TokenType.SEMICOLON, TokenType.RIGHT_PARENTH)

class Expression:
    def __init__(self, expression):
        self.expression = expression

    def calc_expression(self, scope):
        """ shunting-yard algorithm """
        lineNr = -1
        stack = []
        for index in range(len(self.expression)):
            symbol = self.expression[index]
            if isinstance(symbol, Token):
                lineNr = symbol.pointer
            if isinstance(symbol, MoveableType):
                stack.append(symbol)
            elif symbol.tokenType in unaryOperators:
                el = stack.pop()
                stack.append(self.calcUnaryOp(scope, symbol, el))
            elif symbol.tokenType in binaryOperators:
                a = stack.pop()
                b = stack.pop()
                stack.append(self.calcBinaryOp(scope, b, symbol, a))
            elif symbol.value in map(lambda e: e.name, functions) and ((index >= 2 and self.expression[index - 3].value != "moveable.setOnCollision") or index < 2):
                function = [f for f in functions if f.name == symbol.value][0]
                args = []
                for i in range(len(function.formal_arguments)):
                    el = stack.pop()
                    if isinstance(el, Token) and [f for f in functions if f.name == el.value]:
                        val = el.value # pass function as it's name
                    elif isinstance(el, Token) and el.tokenType == TokenType.IDENTIFIER:
                        val = scope.get_value_by_name(el.value)
                    elif isinstance(el,Token):
                        val = el.value
                    else:
                        val = el
                    args.append(val)
                # check  here is arguments match
                for index in range(len(function.formal_arguments)):
                    formal_arg = function.formal_arguments[index]
                    actual_arg = args[-index]
                    if formal_arg[1] == type(""):
                        continue # everything can be casted to string
                    if isinstance(actual_arg, Token) and formal_arg[1] != actual_arg.type:
                        raise ParserException("Argument mismatch, got: " + str(actual_arg.type) + ", expected: " + str(formal_arg[1]) + " at line " + str(lineNr))
                    elif formal_arg[1] != type(actual_arg):
                        raise ParserException("Argument mismatch, got: " + str(type(actual_arg)) + ", expected: " + str(formal_arg[1]) + " at line " + str(lineNr))
                stack.append(function.execute(args))
            elif symbol.tokenType == TokenType.TRUE:
                symbol.value = True
                stack.append(symbol)
            elif symbol.tokenType == TokenType.FALSE:
                symbol.value = False
                stack.append(symbol)
            elif symbol.tokenType in literals or symbol.tokenType == TokenType.IDENTIFIER:
                stack.append(symbol)
        to_Ret = stack.pop()
        if stack:
            raise ParserException("Error calculating expression at line: " + str(lineNr))
        if isinstance(to_Ret, Token):
            if to_Ret.tokenType == TokenType.IDENTIFIER:
                return scope.get_value_by_name(to_Ret.value)
            else:
                return to_Ret.value
        else:
            return to_Ret

    def calcUnaryOp(self,scope, symbol, token):
        if symbol.tokenType == TokenType.EXCL_MARK:
            to_return = not token
            return to_return

    def calcBinaryOp(self, scope, tokenB, symbol, tokenA):
        # both tokenB and tokenA can be: TokenType, int, str, double, bool, later moveable, position
        if isinstance(tokenA, Token) and tokenA.tokenType == TokenType.IDENTIFIER:
            aVal = scope.get_value_by_name(tokenA.value)
        elif isinstance(tokenA, Token):
            aVal = tokenA.value
        else:
            aVal = tokenA
        if isinstance(tokenB, Token) and tokenB.tokenType == TokenType.IDENTIFIER:
            bVal = scope.get_value_by_name(tokenB.value)
        elif isinstance(tokenB, Token):
            bVal = tokenB.value
        else:
            bVal = tokenB
        if symbol.tokenType == TokenType.MINUS:
            result = bVal - aVal
        elif symbol.tokenType == TokenType.PLUS:
            if isinstance(bVal, str) or isinstance(aVal, str):
                result = str(bVal) + str(aVal)
            else:
                result = bVal + aVal
        elif symbol.tokenType == TokenType.ASTERISK:
            result = bVal * aVal
        elif symbol.tokenType == TokenType.SLASH:
            result = bVal / aVal
        elif symbol.tokenType == TokenType.AND:
            result = bVal and aVal
        elif symbol.tokenType == TokenType.OR:
            result = bVal or aVal
        elif symbol.tokenType == TokenType.EQ:
            result = aVal
        elif symbol.tokenType == TokenType.LESS:
            result = bVal < aVal
        elif symbol.tokenType == TokenType.LESS_EQ:
            result = bVal <= aVal
        elif symbol.tokenType == TokenType.GREATER:
            result = bVal > aVal
        elif symbol.tokenType == TokenType.GREATER_EQ:
            result = bVal >= aVal
        elif symbol.tokenType == TokenType.SUBEQ:
            result = bVal - aVal
        elif symbol.tokenType == TokenType.ADDEQ:
            result = bVal + aVal
        elif symbol.tokenType == TokenType.MULEQ:
            result = bVal * aVal
        elif symbol.tokenType == TokenType.DIVEQ:
            result = bVal / aVal
        elif symbol.tokenType == TokenType.EQEQ:
            result = bVal == aVal
        else:
            raise ParserException("not supported operator " + op + " for: " + str(bVal) + "and: " + str(aVal))
        if symbol.tokenType in (TokenType.EQ, TokenType.ADDEQ, TokenType.SUBEQ, TokenType.MULEQ, TokenType.DIVEQ):
            self.check_types_before_assignement(scope, tokenB, result)
            scope.update_variable(tokenB.value, result)
        return result

    def check_types_before_assignement(self, scope, token, result):
        if type(scope.get_variable_by_name(token.value)[1]) != type(result):
            raise ParserException('Type mismatch for ' + token.value)

class Function:
    def __init__(self,name, formal_arguments, return__type, body):
        self.name = name
        self.formal_arguments = formal_arguments
        self.body = body
        if return__type is not None:
            self.return_type = Token(TokenType.getMatchingElseNone(return__type), return__type, 0)
            if self.return_type.tokenType not in (TokenType.INT, TokenType.double, TokenType.MOVEABLE, TokenType.BOOLEAN, TokenType.STRING, TokenType.POSITION):
                raise ParserException('Undefined type ' + str(return__type) + ' in function ' + str(name))
        else:
            self.return_type = None

    def execute(self, actual_arguments):
        scope = Scope()
        for index, value in enumerate(actual_arguments[::-1]):
            name = self.formal_arguments[index][0]
            var_type = self.formal_arguments[index][1]
            scope.add_variable(name, var_type, value)
        to_ret = None
        for statement in self.body:
            try:
                some = statement.execute(scope)
                value, is_returning = some
                if is_returning:
                    return self.map_value_to_return_type(value)
            except ParserException as pe:
                raise pe
            except Exception:
                raise ParserException('Error evaluating line ' + str(statement.line))
        return None

    def map_value_to_return_type(self, value):
        if self.return_type is None:
            raise ParserException('Function ' + self.name + ' returns void')
        if self.return_type.tokenType == TokenType.INT:
            if isinstance(value, int):
                return int(value)
            else:
                raise ParserException('Function ' + str(self.name) + ' returns int')
        elif self.return_type.tokenType == TokenType.double:
            if isinstance(value, float) or isinstance(value, int):
                return float(value)
            else:
                raise ParserException('Function ' + str(self.name) + ' returns double')
        elif self.return_type.tokenType == TokenType.STRING:
            if isinstance(value, str):
                return value
            else:
                raise ParserException('Function ' + str(self.name) + ' returns string')
        elif self.return_type.tokenType == TokenType.BOOLEAN:
            if isinstance(value, bool) or isinstance(value, int) or isinstance(value, float):
                return bool(value)
            else:
                raise ParserException('Function ' + str(self.name) + ' returns boolean')
        elif self.return_type.tokenType == TokenType.MOVEABLE:
            if isinstance(value, MoveableType):
                return value
            else:
                raise ParserException('Function ' + str(self.name) + ' returns moveable')

class MoveableType:
    def __init__(self, val):
        self.accY = val[5]
        self.accX = val[4]
        self.speedY = val[3]
        self.speedX = val[2]
        self.posY = val[1]
        self.posX = val[0]

    def __str__(self):
        return "[[" + str(self.posX) + "," + str(self.posY) + "],[" + str(self.speedX) + "," + str(self.speedY) + "],[" + str(self.accX) + "," + str(self.accY) + "]]"

class Scope:
    def __init__(self):
        self.stack = [{}]
        
    def is_var_defined_in_head_layer(self, name):
        return name in self.stack[-1]

    def add_variable(self, name, var_type, value):
        dictt = self.stack[-1]
        dictt[name] = (var_type, value)
        if isinstance(value, MoveableType):
            x = SingletonScope.Instance()
            x.add_moveable_object(name, value)

    def update_variable(self, name, value):
        if name == "moveable.globalTime":
            x = SingletonScope.Instance()
            x.update_variable(name, value)
            return
        for layer in self.stack[::-1]:
            if name in layer:
                var_type, whatever = layer[name]
                layer[name] = (var_type, value)
                break

    def get_value_by_name(self, name):
        variable = self.get_variable_by_name(name)
        if variable is not None:
            return variable[1]
        else:
            return None

    def get_variable_by_name(self, name):
        if name == "moveable.globalTime":
            x = SingletonScope.Instance()
            return (int ,x.get_variable_by_name(name))
        for layer in self.stack[::-1]:
            if name in layer:
                return layer[name]
        return None

    def levelUp(self):
        self.stack.append({})

    def levelDown(self):
        self.stack.pop()

class Statement:
    def __init__(self, expression, is_returning, line):
        self.expression = Expression(expression)
        self.is_returning = is_returning
        self.line = line

    def execute(self, scope):
        return (self.expression.calc_expression(scope), self.is_returning)

class BlockStatement:
    def __init__(self, body):
        self.body = body
    
    def execute(self, scope):
        scope.levelUp()
        for stat in self.body:
            value, is_returning = stat.execute(scope)
            if is_returning:
                scope.levelDown()
                return (value, True)
        scope.levelDown()
        return (None, False)

class IfStatement:
    def __init__(self, condition, true_body, false_body, line):
        self.condition = Expression(condition)
        self.true_body = true_body
        self.false_body = false_body
        self.line = line

    def execute(self, scope):
        if self.condition.calc_expression(scope):
            return self.true_body.execute(scope)
        elif self.false_body is not None:
            return self.false_body.execute(scope)
        else:
            return (None, None)

class WhileStatement:
    def __init__(self, condition, body, line):
        self.condition = Expression(condition)
        self.body = body
        self.line = line

    def execute(self, scope):
        while self.condition.calc_expression(scope):
            for stat in self.body:
                value, is_returning = stat.execute(scope)
                if is_returning:
                    return (value, is_returning)
        return (None, False)

class VarDefinition:
    def __init__(self, name, var_type, expression, line):
        self.name = name
        self.var_type = var_type
        self.expression = Expression(expression)
        self.is_returning = False
        self.line = line
    
    def execute(self, scope):
        if scope.is_var_defined_in_head_layer(self.name):
            raise ParserException("Reassignment to a variable")
        val = self.expression.calc_expression(scope)
        if self.var_type != type(val):
            raise ParserException("Variable type mismatch for variable: " + self.name)
        if self.var_type == "moveable":
            scope.add_variable(self.name, MoveableType, val)
        else:
            scope.add_variable(copy.copy(self.name), copy.copy(self.var_type), copy.copy(val))
        return (None, False)

class TokenFacade:
    def __init__(self, lexer):
        self.lexer = lexer
        self.set_previous = False
        self.previousToken = None
        self.currentLine = 0

    def next(self):
        if self.set_previous:
            self.set_previous = False
        else:
            self.previousToken = self.lexer.calc_single_token()
        if self.previousToken is not None:
            self.currentLine = self.previousToken.pointer
        return self.previousToken

    def previous(self):
        if self.set_previous:
            raise Exception("Facade does not allow previous ran twice")
        self.set_previous = True
        return self.previousToken

class Parser:
    def __init__(self, lexer, output_stream):
        global functions
        functions = [PredefinedPrintFunction(output_stream), PredefinedOnCollisionFunctionHandler()]
        global registered_on_collisions
        registered_on_collisions = []
        global token_facade
        token_facade = TokenFacade(lexer)
        while True:
            token = token_facade.next()
            if token is None:
                break
            self.consume_token(token, TokenType.DEF)
            function_name = token_facade.next().value
            self.consume_token(token_facade.next(), TokenType.LEFT_PARENTH)
            arguments = self.parse_arguments()
            self.consume_token(token_facade.next(), TokenType.RIGHT_PARENTH)
            return_type = self.parse_return_type()
            self.consume_token(token_facade.next(), TokenType.LEFT_BRACET)
            body = []
            while True:
                statement = self.parse_statement()
                if statement is not None:
                    body.append(statement)
                else:
                    break
            self.consume_token(token_facade.next(), TokenType.RIGHT_BRACET)
            functions.append(Function(function_name, arguments, return_type, body))

    def parse_arguments(self):
        arguments = []
        can_expect_comma = False
        while True:
            token = token_facade.next()
            if token.tokenType == TokenType.RIGHT_PARENTH:
                token_facade.previous()
                break
            else:
                if can_expect_comma:
                    self.consume_token(token, TokenType.COMMA)
                    token = token_facade.next()
                can_expect_comma = True # at least one arg given, therefore next argument(name : type) will begin with ','
                name = token.value
                self.consume_token(token_facade.next(), TokenType.COLON)
                value_type = self.mapStringToType(token_facade.next().value)
                if value_type is None:
                    raise ParserException("Cannot resolve: ", token)
                arguments.append((name, value_type))
        return arguments
    
    def mapStringToType(self, asString):
        if asString == "int":
            return type(0)
        elif asString == "moveable":
            return type(MoveableType((0,0,0,0,0,0)))
        elif asString == "double":
            return type(0.0)
        elif asString == "boolean":
            return type(True)
        elif asString == "string":
            return type("")
        elif asString == "position":
            return type((0,0))
        else:
            return None 

    def parse_return_type(self):
        token = token_facade.next()
        if token.tokenType == TokenType.LEFT_BRACET:
            token_facade.previous()
            return 
        self.consume_token(token, TokenType.COLON)
        return_type = token_facade.next().value
        return return_type

    def parse_statement(self):
        token = token_facade.next()
        if (not token) or token.tokenType == TokenType.RIGHT_BRACET:
            token_facade.previous()
            return
        if token.tokenType == TokenType.LEFT_BRACET:
            return self.parse_block()
        elif token.tokenType == TokenType.IF:
            return self.parse_if_statement()
        elif token.tokenType == TokenType.WHILE:
            return self.parse_while_statement()
        elif token.tokenType == TokenType.RETURN:
            return Statement(self.parse_expression(), True, token_facade.currentLine)
        elif token.tokenType == TokenType.IDENTIFIER:
            token_facade.previous()
            expression = self.parse_expression() # will run twice throught IDENTIFIER token, but simplifies code a lot, so its ok
            return Statement(expression, False, token_facade.currentLine)
        elif token.tokenType == TokenType.VAR:
            return self.parse_var_statement()
        raise Exception('Error at line ' + str(token_facade.currentLine))
            

    def parse_if_statement(self):
        self.consume_token(token_facade.next(), TokenType.LEFT_PARENTH)
        condition = self.parse_expression()
        self.consume_token(token_facade.next(), TokenType.RIGHT_PARENTH)
        true_body = self.parse_statement()
        token = token_facade.next()
        if token.tokenType == TokenType.ELSE:
            false_body = self.parse_statement()
            return IfStatement(condition, true_body, false_body, token_facade.currentLine)
        else:
            token_facade.previous()
            return IfStatement(condition, true_body, None, token_facade.currentLine)
    
    def parse_while_statement(self):
        line = token_facade.currentLine 
        self.consume_token(token_facade.next(), TokenType.LEFT_PARENTH)
        condition = self.parse_expression()
        self.consume_token(token_facade.next(), TokenType.RIGHT_PARENTH)
        token = token_facade.next()
        if token.tokenType == TokenType.LEFT_BRACET:
            body = self.parse_statement_block()
            self.consume_token(token_facade.next(), TokenType.RIGHT_BRACET)
        else:
            token_facade.previous()
            body = [self.parse_statement()]
        return WhileStatement(condition, body, line)

    def parse_var_statement(self):
        name = token_facade.next().value
        token = token_facade.next()
        self.consume_token(token, TokenType.COLON)
        var_type = self.mapStringToType(token_facade.next().value)
        token = token_facade.next()
        if token.tokenType == TokenType.EQ:
            expression = self.parse_expression()
            return VarDefinition(name, var_type, expression, token_facade.currentLine)
        elif token.tokenType == TokenType.SEMICOLON:
            return VarDefinition(name, var_type, None, token_facade.currentLine)
        else:
            self.consume_token(token, (TokenType.SEMICOLON, TokenType.EQ)) # will raise an exception

    def parse_block(self):
        body = []
        while True:
            body.append(self.parse_statement())
            if token_facade.next().tokenType == TokenType.RIGHT_BRACET:
                return BlockStatement(body)
            else:
                token_facade.previous()

    def parse_expression(self):
        """ shunting-yard algorithm """
        stack = []
        out = []
        open_paranths = 0
        lineNr = -1
        while True:
            token = token_facade.next()
            lineNr = token.pointer
            if (not token) or token.tokenType == TokenType.SEMICOLON:
                break
            elif token.tokenType == TokenType.LEFT_SQ_BRACKET:
                m = [token]
                for i in range(18):
                    m.append(token_facade.next())
                indexes = {TokenType.LEFT_SQ_BRACKET : (0, 1, 7, 13), TokenType.RIGHT_SQ_BRACKET : (5, 11, 17, 18), TokenType.COMMA : (3, 6, 9, 12, 15), TokenType.NUM_LITERAL_INT : (2, 4, 8, 10, 14, 16)}
                for key, value in indexes.items():
                    for v in value:
                        self.consume_token(m[v], key)
                out.append(MoveableType([m[2].value, m[4].value, m[8].value, m[10].value, m[14].value, m[16].value]))
            elif token.tokenType == TokenType.DOT:
                next_token = token_facade.next()
                self.consume_token(next_token, TokenType.IDENTIFIER)
                concat = Token(TokenType.IDENTIFIER, out[-1].value + "." + next_token.value, token.pointer)
                out.pop()
                if token_facade.next().tokenType == TokenType.LEFT_PARENTH: # can be a function or variable
                    stack.append(concat)
                else:
                    out.append(concat) 
                token_facade.previous()
            elif token.tokenType == TokenType.RIGHT_PARENTH and open_paranths == 0:
                token_facade.previous()
                break
            elif token.tokenType in literals or token.tokenType == TokenType.IDENTIFIER:
                if token_facade.next().tokenType == TokenType.LEFT_PARENTH: # can be a function or variable
                    stack.append(token)
                else:
                    out.append(token) 
                token_facade.previous()
            elif token.tokenType == TokenType.LEFT_PARENTH:
                open_paranths += 1
                stack.append(token)
            elif token.tokenType in unaryOperators or token.tokenType in binaryOperators:
                while stack:
                    e2 = stack[-1]
                    if e2.tokenType not in unaryOperators and e2.tokenType not in binaryOperators:
                        break
                    if self.is_left_linking(token) and self.get_order(token) <= self.get_order(e2) or self.is_right_linking(token) and self.get_order(token) < self.get_order(e2):
                        out.append(stack.pop())
                    else:
                        break
                stack.append(token)
            elif token.tokenType == TokenType.RIGHT_PARENTH:
                open_paranths -= 1
                while stack:
                    if stack[-1].tokenType == TokenType.LEFT_PARENTH:
                        stack.pop()
                        break
                    else:
                        out.append(stack.pop())
                if stack and stack[-1].tokenType == TokenType.IDENTIFIER:
                    out.append(stack.pop())
        while stack:
            out.append(stack.pop())
        if open_paranths != 0:
            raise ParserException("Error parsing expression at: " + str(lineNr))
        return out

    def parse_statement_block(self):
        body = []
        while True:
            statement = self.parse_statement()
            body.append(statement)
            token = token_facade.next()
            if token.tokenType == TokenType.RIGHT_BRACET:
                token_facade.previous()
                break
            else:
                token_facade.previous()
        return body

    def consume_token(self,token, expected_token_type):
        if isinstance(token, Token):
            token = token.tokenType
        if isinstance(expected_token_type, tuple) and token in expected_token_type:
            return
        if token == expected_token_type:
            return
        raise ParserException("Expected: " + str(expected_token_type) + ", is: " + str(token))

    def get_order(self, token_type):
        token_type = token_type.tokenType
        if token_type in (TokenType.EQ, TokenType.ADDEQ, TokenType.SUBEQ, TokenType.MULEQ, TokenType.DIVEQ, TokenType.AND,TokenType.OR):
            return -1
        if token_type in (TokenType.LESS, TokenType.EQEQ, TokenType.LESS_EQ, TokenType.GREATER, TokenType.GREATER_EQ, TokenType.EXCL_MARK): # relational
            return 0
        elif token_type in (TokenType.PLUS,TokenType.MINUS):
            return 2
        else: # multiply , divide
            return 3

    def is_left_linking(self,token_type):
        return token_type != TokenType.EQ
        return token_type in (TokenType.ASTERISK, TokenType.SLASH, TokenType.PLUS, TokenType.MINUS, TokenType.EQEQ, TokenType.LESS, TokenType.AND, TokenType.OR)
	
    def is_right_linking(self,token_type):
        return token_type in (TokenType.PLUS, TokenType.MINUS, TokenType.ASTERISK, TokenType.EQ, TokenType.EXCL_MARK)

    def execute_main(self):
        for function in functions:
            if function.name == "main":
                args = []
                function.execute(args)
                return
        raise ParserException("No main function found")

class ParserException(Exception):
    def __init__(self, msg):
        self.msg = msg

class PredefinedPrintFunction(Function):
    def __init__(self, output_stream):
        self.output_stream = output_stream
        self.name = "print"
        self.formal_arguments = [("arg", type(""))]
        self.return__type = None

    def execute(self, arguments):
        arg =  arguments[0]
        self.output_stream.write(str(arg) + "\n")
        return None

class PredefinedOnCollisionFunctionHandler(Function):
    def __init__(self):
        self.name = "moveable.setOnCollision"
        self.formal_arguments = [("mov1", type("")), ("mov2", type("")), ("function", type(""))]
        self.return_type = None

    def execute(self, arguments):
        mov1 = arguments[2]
        mov2 = arguments[1]
        function = arguments[0]
        function = [f for f in functions if f.name == function][0]
        registered_on_collisions.append((mov1, mov2, function))

class Singleton:
    def __init__(self, decorated):
        self._decorated = decorated
    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance
    def __call__(self):
        raise TypeError("Singletons must be accessed through 'Instance()'")
    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

@Singleton
class SingletonScope:
    def __init__(self):
        self.stack = {"moveable.globalTime" : 0}
        self.moveable_objects = []
    def get_variable_by_name(self, name):
        return self.stack[name]
    def add_moveable_object(self, name, value):
        self.moveable_objects.append((name, value))
    def pairsGenerator(self):
        for i in range(len(self.moveable_objects)):
            for j in range(i,len(self.moveable_objects)):
                yield (i,j)
    def update_variable(self, name, new_value):
        pairs = ((i, j) for i in self.moveable_objects for j in self.moveable_objects if i != j)
        for time in range(self.stack[name], new_value):
            for m in self.moveable_objects:
                m[1].posX += m[1].speedX
                m[1].speedX += m[1].accX
                m[1].posY += m[1].speedY
                m[1].speedY += m[1].accY
            for roc in registered_on_collisions:
                mov1 = roc[0]
                mov2 = roc[1]
                function = roc[2]
                if mov1.posX != mov2.posX or mov1.posY != mov2.posY:
                    continue
                function.execute([mov1, mov2, [mov1.posX, mov1.posY], time][::-1])
        self.stack[name] = new_value        
    
