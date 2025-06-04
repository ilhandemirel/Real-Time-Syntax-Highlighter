# parser.py
from dataclasses import dataclass, field
from typing import List, Optional
from lexer import TokenType, Token # TokenType enum'ını import ediyoruz ve Token sınıfını içe aktar

class ParseError(Exception):
    def __init__(self, message, token=None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f"Satır {token.line}, Sütun {token.column}: {message} (Token: {token.value}, Tip: {token.type.name})")
        else:
            super().__init__(message)


class ASTNode:
    """Tüm AST düğüm sınıflarının miras alacağı temel sınıf."""
    pass


@dataclass
class Program(ASTNode):
    statements: List[ASTNode]

@dataclass
class Declaration(ASTNode):
    type_token: Token
    name: Token
    initializer: Optional[ASTNode]
    is_array: bool = False
    array_dims: List[Optional[ASTNode]] = field(default_factory=list)

@dataclass
class FunctionDeclaration(ASTNode):
    return_type: Token
    name: Token
    parameters: List['Parameter']
    body: 'Block'
    is_array_return: bool = False
    array_dims: List[Optional[ASTNode]] = field(default_factory=list)

@dataclass
class Parameter(ASTNode):
    type_token: Token
    name: Token
    is_array: bool = False

@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_branch: ASTNode
    else_branch: Optional[ASTNode] = None

@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: ASTNode

@dataclass
class ForStatement(ASTNode):
    initializer: Optional[ASTNode]
    condition: Optional[ASTNode]
    increment: Optional[ASTNode]
    body: ASTNode

@dataclass
class ReturnStatement(ASTNode):
    value: Optional[ASTNode]

@dataclass
class PrintStatement(ASTNode):
    expression: ASTNode

@dataclass
class Block(ASTNode):
    statements: List[ASTNode]

@dataclass
class ExpressionStatement(ASTNode):
    expression: ASTNode

@dataclass
class Assignment(ASTNode):
    target: ASTNode
    value: ASTNode

@dataclass
class Binary(ASTNode):
    left: ASTNode
    operator: Token
    right: ASTNode

@dataclass
class Unary(ASTNode):
    operator: Token
    right: ASTNode

@dataclass
class Call(ASTNode):
    callee: ASTNode
    arguments: List[ASTNode]

@dataclass
class ArrayAccess(ASTNode):
    name: ASTNode
    index: ASTNode

@dataclass
class PropertyAccess(ASTNode):
    object: ASTNode
    property: Token

@dataclass
class Variable(ASTNode):
    name: Token

@dataclass
class Literal(ASTNode):
    value: Token

class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type not in (TokenType.COMMENT, TokenType.MULTILINE_COMMENT)]
        self.current = 0

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return Program(statements)

    def declaration(self):
        try:
            if self.check(TokenType.INT, TokenType.FLOAT, TokenType.STRING_TYPE, TokenType.BOOL):
                # Bir sonraki token'a bakarak fonksiyon mu değişken mi olduğuna karar ver
                if self.peek(1) and self.peek(1).type == TokenType.IDENTIFIER and self.peek(2) and self.peek(2).type == TokenType.LEFT_PAREN:
                    return self.function_declaration()
                
                # Dizi kontrolü ve ardından fonksiyon kontrolü
                if self.peek(1) and self.peek(1).type == TokenType.LEFT_BRACKET:
                     # int[] func() gibi bir durum olabilir
                     # Geçici olarak ilerleyip bakalım
                     temp_current = self.current
                     temp_current += 2 # tip ve [
                     while temp_current < len(self.tokens) and self.tokens[temp_current].type == TokenType.RIGHT_BRACKET:
                         temp_current +=1 # ]
                     
                     if temp_current < len(self.tokens) and self.tokens[temp_current].type == TokenType.IDENTIFIER:
                         temp_current +=1 # isim
                         if temp_current < len(self.tokens) and self.tokens[temp_current].type == TokenType.LEFT_PAREN:
                             return self.function_declaration()

                return self.variable_declaration()
            return self.statement()
        except ParseError as error:
            self.synchronize()
            raise error # Hatayı tekrar fırlat ki GUI yakalasın

    def function_declaration(self):
        return_type = self.advance()
        is_array_return = False
        if self.match(TokenType.LEFT_BRACKET):
            is_array_return = True
            self.consume(TokenType.RIGHT_BRACKET, "Fonksiyon dönüş tipi için ']' bekleniyordu.")
        
        name = self.consume(TokenType.IDENTIFIER, "Fonksiyon ismi bekleniyordu.")
        self.consume(TokenType.LEFT_PAREN, "'(' bekleniyordu.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                param_type = self.advance()
                is_array_param = False
                if self.match(TokenType.LEFT_BRACKET):
                    is_array_param = True
                    self.consume(TokenType.RIGHT_BRACKET, "Parametre tipi için ']' bekleniyordu.")
                
                param_name = self.consume(TokenType.IDENTIFIER, "Parametre ismi bekleniyordu.")
                parameters.append(Parameter(param_type, param_name, is_array_param))
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "')' bekleniyordu.")
        self.consume(TokenType.LEFT_BRACE, "Fonksiyon gövdesi için '{' bekleniyordu.")
        body = self.block()
        return FunctionDeclaration(return_type, name, parameters, body, is_array_return)

    def variable_declaration(self):
        type_token = self.advance()
        is_array = False
        if self.match(TokenType.LEFT_BRACKET):
            is_array = True
            self.consume(TokenType.RIGHT_BRACKET, "Dizi tipi için ']' bekleniyordu.")

        name = self.consume(TokenType.IDENTIFIER, "Değişken ismi bekleniyordu.")
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Değişken bildiriminden sonra ';' bekleniyordu.")
        return Declaration(type_token, name, initializer, is_array)

    def statement(self):
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return self.block()
        return self.expression_statement()

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, "'for' döngüsünden sonra '(' bekleniyordu.")
        
        # DÜZELTME: Başlatıcıdan sonraki gereksiz noktalı virgül kontrolü kaldırıldı.
        initializer = None
        if self.match(TokenType.SEMICOLON):
            pass # Başlatıcı yok
        elif self.check(TokenType.INT, TokenType.FLOAT, TokenType.STRING_TYPE, TokenType.BOOL):
            initializer = self.variable_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Döngü koşulundan sonra ';' bekleniyordu.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Döngü ifadesinden sonra ')' bekleniyordu.")

        body = self.statement()
        return ForStatement(initializer, condition, increment, body)

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "'if' sonrası '(' bekleniyordu.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Koşul sonrası ')' bekleniyordu.")
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return IfStatement(condition, then_branch, else_branch)

    def print_statement(self):
        # DÜZELTME: Tekrarlanan 'print' tüketimi kaldırıldı. `match` zaten yapmıştı.
        self.consume(TokenType.LEFT_PAREN, "'print' sonrası '(' bekleniyordu.")
        value = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "İfadeler sonrası ')' bekleniyordu.")
        self.consume(TokenType.SEMICOLON, "'print' deyimi sonrası ';' bekleniyordu.")
        return PrintStatement(value)

    def return_statement(self):
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "'return' sonrası ';' bekleniyordu.")
        return ReturnStatement(value)
    
    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "'while' sonrası '(' bekleniyordu.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Koşul sonrası ')' bekleniyordu.")
        body = self.statement()
        return WhileStatement(condition, body)

    def block(self):
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Blok sonrası '}' bekleniyordu.")
        return Block(statements)

    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "İfade sonrası ';' bekleniyordu.")
        return ExpressionStatement(expr)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.logical_or()
        if self.match(TokenType.ASSIGN):
            equals = self.previous()
            value = self.assignment() # Sağ taraf da bir atama olabilir (a = b = 5)
            if isinstance(expr, (Variable, ArrayAccess, PropertyAccess)):
                return Assignment(expr, value)
            raise ParseError("Geçersiz atama hedefi.", equals)
        return expr

    def logical_or(self):
        expr = self.logical_and()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logical_and()
            expr = Binary(expr, operator, right)
        return expr

    def logical_and(self):
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Binary(expr, operator, right)
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(TokenType.NOT_EQUALS, TokenType.EQUALS):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(TokenType.GREATER_THAN, TokenType.GREATER_EQUALS, TokenType.LESS_THAN, TokenType.LESS_EQUALS):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.DIVIDE, TokenType.MULTIPLY):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self):
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.call()

    def call(self):
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.LEFT_BRACKET):
                index = self.expression()
                self.consume(TokenType.RIGHT_BRACKET, "Dizi indeksi sonrası ']' bekleniyordu.")
                expr = ArrayAccess(expr, index)
            # DÜZELTME: .length gibi erişimleri tanıma
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "'.' sonrası özellik ismi bekleniyordu.")
                expr = PropertyAccess(expr, name)
            else:
                break
        return expr

    def finish_call(self, callee):
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Argümanlar sonrası ')' bekleniyordu.")
        return Call(callee, arguments)

    def primary(self):
        if self.match(TokenType.FALSE, TokenType.TRUE, TokenType.NULL, TokenType.NUMBER, TokenType.STRING_LITERAL):
            return Literal(self.previous())
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "İfade sonrası ')' bekleniyordu.")
            return expr
        raise ParseError("İfade bekleniyordu.", self.peek())

    # --- Yardımcı Fonksiyonlar ---
    def match(self, *types):
        if self.check(*types):
            self.advance()
            return True
        return False

    def consume(self, type, message):
        if self.check(type):
            return self.advance()
        raise ParseError(message, self.peek())

    def check(self, *types):
        if self.is_at_end():
            return False
        return self.peek().type in types

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self, n=0):
        if self.current + n >= len(self.tokens):
            return self.tokens[-1] # EOF
        return self.tokens[self.current + n]

    def previous(self):
        return self.tokens[self.current - 1]

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            if self.peek().type in [TokenType.FOR, TokenType.IF, TokenType.WHILE, TokenType.PRINT, TokenType.RETURN]:
                return
            self.advance()
