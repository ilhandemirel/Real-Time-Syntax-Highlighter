# gui.py
import tkinter as tk
from tkinter import ttk
from lexer import tokenize, TokenType
from parser import Parser, ParseError

class ModernTheme:
    BG_COLOR = "#1a1b26"  # Daha koyu ve modern bir arka plan
    TEXT_BG = "#24283b"   # Kod editörü arka planı
    TEXT_FG = "#a9b1d6"   # Daha yumuşak bir metin rengi
    LINE_NUM_BG = "#1a1b26"  # Satır numarası arka planı
    LINE_NUM_FG = "#565f89"  # Satır numarası rengi
    
    COLORS = {
        # Anahtar kelimeler - Daha canlı renkler
        TokenType.IF: "#7aa2f7",
        TokenType.ELSE: "#7aa2f7",
        TokenType.WHILE: "#7aa2f7",
        TokenType.FOR: "#7aa2f7",
        TokenType.RETURN: "#7aa2f7",
        TokenType.TRUE: "#7aa2f7",
        TokenType.FALSE: "#7aa2f7",
        TokenType.PRINT: "#e0af68",

        # Veri Tipleri
        TokenType.INT: "#7dcfff",
        TokenType.FLOAT: "#7dcfff",
        TokenType.STRING_TYPE: "#7dcfff",
        TokenType.BOOL: "#7dcfff",

        # Tanımlayıcılar ve değişkenler
        TokenType.IDENTIFIER: "#c0caf5",
        TokenType.NUMBER: "#9ece6a",
        TokenType.STRING_LITERAL: "#f7768e",

        # Operatörler
        TokenType.PLUS: "#bb9af7",
        TokenType.MINUS: "#bb9af7",
        TokenType.MULTIPLY: "#bb9af7",
        TokenType.DIVIDE: "#bb9af7",
        TokenType.ASSIGN: "#bb9af7",
        TokenType.EQUALS: "#bb9af7",
        TokenType.NOT_EQUALS: "#bb9af7",
        TokenType.LESS_THAN: "#bb9af7",
        TokenType.GREATER_THAN: "#bb9af7",
        TokenType.LESS_EQUALS: "#bb9af7",
        TokenType.GREATER_EQUALS: "#bb9af7",
        TokenType.AND: "#bb9af7",
        TokenType.OR: "#bb9af7",
        TokenType.NOT: "#bb9af7",

        # Ayraçlar
        TokenType.LEFT_PAREN: "#c0caf5",
        TokenType.RIGHT_PAREN: "#c0caf5",
        TokenType.LEFT_BRACE: "#c0caf5",
        TokenType.RIGHT_BRACE: "#c0caf5",
        TokenType.LEFT_BRACKET: "#c0caf5",
        TokenType.RIGHT_BRACKET: "#c0caf5",
        TokenType.SEMICOLON: "#c0caf5",
        TokenType.COMMA: "#c0caf5",

        # Yorumlar
        TokenType.COMMENT: "#565f89",
        TokenType.MULTILINE_COMMENT: "#565f89",

        # Bilinmeyen
        TokenType.UNKNOWN: "#f7768e"
    }
    
    ERROR_COLOR = "#f7768e"
    ERROR_TAG = "error_tag"

class LineNumbers(tk.Text):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.text_widget.bind('<Key>', self.on_key)
        self.text_widget.bind('<MouseWheel>', self.on_mousewheel)
        self.text_widget.bind('<Configure>', self.on_configure)
        self.update_line_numbers()

    def on_key(self, event=None):
        self.update_line_numbers()

    def on_mousewheel(self, event=None):
        self.update_line_numbers()

    def on_configure(self, event=None):
        self.update_line_numbers()

    def update_line_numbers(self):
        self.delete('1.0', tk.END)
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.insert(tk.END, f"{linenum}\n")
            i = self.text_widget.index(f"{i}+1line")

class SyntaxHighlighter:
    def __init__(self, root):
        self.root = root
        self.root.title("Syntax Highlighter")
        self.root.configure(bg=ModernTheme.BG_COLOR)
        
        # Ana frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Text widget ve scrollbar
        self.text_frame = ttk.Frame(self.main_frame)
        self.text_frame.pack(expand=True, fill="both")
        
        # Ana metin widget'ı
        self.text = tk.Text(
            self.text_frame,
            wrap="none",
            font=("Consolas", 12),
            bg=ModernTheme.TEXT_BG,
            fg=ModernTheme.TEXT_FG,
            insertbackground=ModernTheme.TEXT_FG,
            selectbackground="#414868",
            selectforeground=ModernTheme.TEXT_FG,
            padx=5,
            pady=5,
            highlightthickness=0
        )
        
        # Satır numaraları için frame
        self.line_numbers_frame = ttk.Frame(self.text_frame)
        self.line_numbers_frame.grid(row=0, column=0, sticky="ns")
        
        # Satır numaraları widget'ı
        self.line_numbers = LineNumbers(
            self.line_numbers_frame,
            self.text,  # text_widget'ı burada geçiyoruz
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            background=ModernTheme.LINE_NUM_BG,
            foreground=ModernTheme.LINE_NUM_FG,
            font=("Consolas", 12),
            highlightthickness=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        self.vsb = ttk.Scrollbar(self.text_frame, orient="vertical", command=self.text.yview)
        self.hsb = ttk.Scrollbar(self.text_frame, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        
        # Grid layout
        self.text.grid(row=0, column=1, sticky="nsew")
        self.vsb.grid(row=0, column=2, sticky="ns")
        self.hsb.grid(row=1, column=1, sticky="ew")
        
        self.text_frame.grid_columnconfigure(1, weight=1)
        self.text_frame.grid_rowconfigure(0, weight=1)
        
        # Renk stillerini ayarla
        for token_type, color in ModernTheme.COLORS.items():
            self.text.tag_configure(token_type.name, foreground=color)
            
        # Hata tag'ini ayarla
        self.text.tag_configure(ModernTheme.ERROR_TAG, background=ModernTheme.ERROR_COLOR, underline=True)
        
        # Event binding
        self.text.bind("<KeyRelease>", self.highlight)
        self.text.bind("<<Paste>>", self.highlight)
        
        # Hata mesajı etiketi
        self.error_label = ttk.Label(
            self.main_frame,
            text="",
            foreground=ModernTheme.ERROR_COLOR,
            background=ModernTheme.BG_COLOR,
            font=("Consolas", 10)
        )
        self.error_label.pack(fill="x", pady=(5, 0))
        
        # Başlangıç metni
        self.text.insert("1.0", """// Örnek kod
int topla(int a, int b) {
    return a + b;
}

float ortalama(int[] dizi) {
    int toplam = 0;
    for (int i = 0; i < dizi.length; i = i + 1) {
        toplam = toplam + dizi[i];
    }
    return toplam / dizi.length;
}

/* Çok satırlı
   yorum örneği */

if (sayi > 0) {
    print("Pozitif");
} else {
    print("Negatif");
}
""")
        self.highlight()

    def highlight(self, event=None):
        code = self.text.get("1.0", tk.END)
        
        # Tüm tag'leri temizle
        for token_type in ModernTheme.COLORS.keys():
            self.text.tag_remove(token_type.name, "1.0", tk.END)
        self.text.tag_remove(ModernTheme.ERROR_TAG, "1.0", tk.END)
        self.error_label.config(text="")

        tokens = tokenize(code)
        
        # Lexer renklendirmesi
        for token in tokens:
            if token.type in ModernTheme.COLORS:
                start_index = f"1.0+{token.start_pos}c"
                end_index = f"1.0+{token.end_pos}c"
                self.text.tag_add(token.type.name, start_index, end_index)

        # Parser'ı çalıştır ve ParseError istisnasını yakala
        parser = Parser(tokens)
        try:
            parser.parse()
        except ParseError as e:
            self.error_label.config(text=str(e))
            if e.token:
                start_index = f"1.0+{e.token.start_pos}c"
                end_index = f"1.0+{e.token.end_pos}c"
                self.text.tag_add(ModernTheme.ERROR_TAG, start_index, end_index)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x700")  # Daha büyük pencere
    app = SyntaxHighlighter(root)
    root.mainloop()
