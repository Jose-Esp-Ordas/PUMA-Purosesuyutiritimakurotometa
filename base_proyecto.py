import re
from lark import Lark

# ---------------------------
# FASE 1: ANÁLISIS LÉXICO
# ---------------------------
def tokenize(code):
    # Definimos los patrones válidos
    tokens = []
    token_specs = [
        ("HELLO", r'HELLO'),   # palabra clave
        ("NUMBER", r'\d+'),    # número
        ("SKIP", r'[ \t]+'),   # espacios
    ]

    # Unimos los patrones
    master = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in token_specs))
    pos = 0
    while pos < len(code):
        m = master.match(code, pos)
        if not m:
            raise SyntaxError(f"❌ Error léxico cerca de: {code[pos:pos+10]!r}")
        typ = m.lastgroup
        if typ != "SKIP":
            tokens.append((typ, m.group()))
        pos = m.end()

    print("✅ Tokens generados por el análisis léxico:")
    for t in tokens:
        print(" ", t)
    return " ".join(value for _, value in tokens)  # texto limpio para parser

# ---------------------------
# FASE 2: ANÁLISIS SINTÁCTICO
# ---------------------------
grammar = """
start: "HELLO" NUMBER
%import common.NUMBER
%ignore /\\s+/
"""

parser = Lark(grammar, start="start")

# ---------------------------
# DEMOSTRACIÓN
# ---------------------------
code = "HELLO 123"

# 1️⃣ Fase léxica
lexical_output = tokenize(code)

# 2️⃣ Fase sintáctica (usa el resultado del léxico)
tree = parser.parse(lexical_output)

print("\n✅ Árbol sintáctico:")
print(tree.pretty())
