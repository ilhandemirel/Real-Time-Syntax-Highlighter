# lexer.py
import re
from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    # Anahtar kelimeler
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    INT = auto()
    FLOAT = auto()
    STRING_TYPE = auto() # TokenType.STRING yerine STRING_TYPE kullandım çakışmaması için
    BOOL = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    PRINT = auto()

    # Tanımlayıcılar ve değişkenler
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING_LITERAL = auto()

    # Operatörler
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    ASSIGN = auto()
    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUALS = auto()
    GREATER_EQUALS = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # Ayraçlar
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    SEMICOLON = auto()
    COMMA = auto()
    DOT = auto()

    # Yorumlar
    COMMENT = auto()
    MULTILINE_COMMENT = auto()

    # Boşluk ve diğer
    WHITESPACE = auto()
    EOF = auto()
    UNKNOWN = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    start_pos: int
    end_pos: int
    line: int
    column: int

class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.current_pos = 0
        self.line = 1
        self.column = 1
        self.keywords = {
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'return': TokenType.RETURN,
            'int': TokenType.INT,
            'float': TokenType.FLOAT,
            'string': TokenType.STRING_TYPE,
            'bool': TokenType.BOOL,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
            'null': TokenType.NULL,
            'print': TokenType.PRINT
        }

    def tokenize(self):
        while self.current_pos < len(self.code):
            self._skip_whitespace()

            if self.current_pos >= len(self.code):
                break # Dosya sonu

            start_pos = self.current_pos
            start_line = self.line
            start_column = self.column
            current_char = self._current_char()
            next_char = self._peek_char()

            if current_char is None:
                 break # Kod bitti

            if current_char == '/' and next_char == '/':
                self.handle_single_line_comment(start_pos, start_line, start_column)
            elif current_char == '/' and next_char == '*':
                self.handle_multi_line_comment(start_pos, start_line, start_column)
            elif current_char in ['"', "'"]:
                self.handle_string(start_pos, start_line, start_column)
            elif self._is_digit():
                self.handle_number(start_pos, start_line, start_column)
            elif self._is_identifier_start():
                self.handle_identifier(start_pos, start_line, start_column)
            else:
                self.handle_operator_or_delimiter(start_pos, start_line, start_column)

        self.tokens.append(self.create_token(TokenType.EOF, "EOF", self.current_pos, self.line, self.column))
        return self.tokens

    def _current_char(self):
        if self.current_pos < len(self.code):
            return self.code[self.current_pos]
        return None

    def _peek_char(self):
        if self.current_pos + 1 < len(self.code):
            return self.code[self.current_pos + 1]
        return None

    def _advance(self):
        char = self._current_char()
        if char == '\n':
            self.line += 1
            self.column = 0 # Yeni satır başlangıcı (bir sonraki karakter 1. sütun olacak)
        else:
            self.column += 1
        self.current_pos += 1
        # advance sonrası column 1'den başlamalı eğer newline olduysa
        if char == '\n':
             self.column = 1

    def _is_whitespace(self, char):
        return char is not None and char.isspace()

    def _skip_whitespace(self):
        while self.current_pos < len(self.code) and self._is_whitespace(self._current_char()):
            self._advance()

    def _is_digit(self):
        return self._current_char() is not None and self._current_char().isdigit()

    def _is_identifier_start(self):
        char = self._current_char()
        return char is not None and (char.isalpha() or char == '_')

    def _is_identifier_char(self):
        char = self._current_char()
        return char is not None and (char.isalnum() or char == '_')

    def handle_single_line_comment(self, start_pos, start_line, start_column):
        self._advance() # Skip first /
        self._advance() # Skip second /
        while self.current_pos < len(self.code) and self._current_char() != '\n':
            self._advance()
        # Tek satırlık yorum newline ile biter veya dosya sonu gelir.
        # Newline karakterini de yorum tokenına dahil edelim ki konumu doğru olsun.
        if self._current_char() == '\n':
             self._advance() # Newline karakterini de dahil et
        
        comment = self.code[start_pos:self.current_pos]
        self.tokens.append(self.create_token(TokenType.COMMENT, comment, start_pos, start_line, start_column))

    def handle_multi_line_comment(self, start_pos, start_line, start_column):
        self._advance()  # Skip /
        self._advance()  # Skip *
        # Yorum içeriğini tara
        while self.current_pos < len(self.code):
            if self._current_char() == '*' and self._peek_char() == '/':
                self._advance()  # Skip *
                self._advance()  # Skip /
                break
            # Eğer dosya sonuna geldiysek ve yorum kapanmadıysa, yorumu sonuna kadar al
            if self._current_char() is None:
                 break
            self._advance()
            
        comment = self.code[start_pos:self.current_pos]
        # Eğer yorum kapanmadıysa UNKNOWN token olarak işaretlenebilir veya hata verilebilir.
        # Şimdilik yorum olarak alalım ve GUI kırmızı renklendirsin.
        if not comment.endswith('*/'):
             # Yorum kapanmamış, isterseniz burada bir hata tokenı ekleyebilirsiniz.
             # Şimdilik token tipini UNKNOWN yapalım.
             token_type = TokenType.UNKNOWN
        else:
             token_type = TokenType.MULTILINE_COMMENT

        self.tokens.append(self.create_token(token_type, comment, start_pos, start_line, start_column))

    def handle_number(self, start_pos, start_line, start_column):
        is_float = False
        while self.current_pos < len(self.code):
            if self._is_digit():
                self._advance()
            elif self._current_char() == '.' and not is_float:
                # Noktadan sonra rakam gelmeli, aksi halde operatör veya hata olabilir.
                if self._peek_char() is not None and self._peek_char().isdigit():
                    is_float = True
                    self._advance()
                else:
                    break # Noktadan sonra rakam yok, sayıyı bitir
            else:
                break
        number = self.code[start_pos:self.current_pos]
        self.tokens.append(self.create_token(TokenType.NUMBER, number, start_pos, start_line, start_column))

    def handle_string(self, start_pos, start_line, start_column):
        quote = self._current_char()
        self._advance()  # Skip opening quote
        # String içeriğini tara
        while self.current_pos < len(self.code) and self._current_char() != quote:
            if self._current_char() == '\\': # Escape character
                 self._advance() # Skip \
                 if self._current_char() is not None: # Kaçış karakterinden sonra bir karakter olmalı
                      self._advance() # Kaçış karakterinden sonraki karakteri de atla
                 else:
                      # Hata: String sonunda kaçış karakteri var ama sonra bir karakter yok
                      break # Stringi burada bitir
            elif self._current_char() == '\n':
                 # Hata: String içinde new line karakteri var (izin vermiyorsak)
                 # Gramerimize göre stringler tek satırda olmalı, newline hata sayılmalı
                 break # Newline karakterini görmeden stringi bitir
            else:
                self._advance()

        if self.current_pos < len(self.code) and self._current_char() == quote: # Kapanış tırnak işareti
            self._advance()
            string_literal = self.code[start_pos:self.current_pos]
            self.tokens.append(self.create_token(TokenType.STRING_LITERAL, string_literal, start_pos, start_line, start_column))
        else:
             # Hata: Kapanış tırnak işareti bulunamadı
             string_literal = self.code[start_pos:self.current_pos]
             self.tokens.append(self.create_token(TokenType.UNKNOWN, string_literal, start_pos, start_line, start_column)) # Bilinmeyen token olarak işaretle

    def handle_identifier(self, start_pos, start_line, start_column):
        while self.current_pos < len(self.code) and self._is_identifier_char():
            self._advance()
        identifier = self.code[start_pos:self.current_pos]
        token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
        self.tokens.append(self.create_token(token_type, identifier, start_pos, start_line, start_column))

    def handle_operator_or_delimiter(self, start_pos, start_line, start_column):
        char = self._current_char()
        # char is guaranteed not to be None here because of check at the start of tokenize()

        two_char_operators = {
            '==': TokenType.EQUALS,
            '!=': TokenType.NOT_EQUALS,
            '<=': TokenType.LESS_EQUALS,
            '>=': TokenType.GREATER_EQUALS,
            '&&': TokenType.AND,
            '||': TokenType.OR
        }

        next_char = self._peek_char()
        if next_char is not None and (char + next_char) in two_char_operators:
            operator = char + next_char
            self._advance()
            self._advance()
            self.tokens.append(self.create_token(two_char_operators[operator], operator, start_pos, start_line, start_column))
            return

        one_char_operators_delimiters = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE, # Tek / operatör olarak kalmalı, yorumlar yukarıda işleniyor
            '=': TokenType.ASSIGN,
            '<': TokenType.LESS_THAN,
            '>': TokenType.GREATER_THAN,
            '!': TokenType.NOT,
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            '[': TokenType.LEFT_BRACKET,
            ']': TokenType.RIGHT_BRACKET,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '.': TokenType.DOT
        }

        if char in one_char_operators_delimiters:
            self._advance()
            self.tokens.append(self.create_token(one_char_operators_delimiters[char], char, start_pos, start_line, start_column))
            return

        # Bilinmeyen karakter
        self.tokens.append(self.create_token(TokenType.UNKNOWN, char, start_pos, start_line, start_column))
        self._advance()

    def create_token(self, type, value, start_pos, start_line, start_column):
        return Token(
            type=type,
            value=value,
            start_pos=start_pos,
            end_pos=self.current_pos,
            line=start_line,
            column=start_column
        )

def tokenize(code):
    lexer = Lexer(code)
    return lexer.tokenize()

# Test kodu
if __name__ == "__main__":
    test_code = "int sayi = 10; // Bu bir yorum\nstring mesaj = \"Merhaba\"; /* Çok\nsatırlı\nyorum */ if (sayi > 5) { print(\"Büyük\"); }\nint x; /* kapanmayan yorum"
    tokens = tokenize(test_code)
    for token in tokens:
        print(token)
