import re
import pandas as pd
import numpy as np
from lark import Lark, Transformer

# ---------------------------
# CARGAR DATOS DESDE CSV
# ---------------------------
try:
    df = pd.read_csv('datos_prueba.csv')
    print("📊 DataFrame cargado desde 'datos_prueba.csv':")
    print(df.head())
    print(f"\n📋 Columnas disponibles: {list(df.columns)}")
    print(f"📏 Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
    print("="*60)
    print()
except FileNotFoundError:
    print("❌ Error: No se encontró el archivo 'datos_prueba.csv'")
    exit()
except Exception as e:
    print(f"❌ Error al cargar el CSV: {e}")
    exit()

# ---------------------------
# FASE 1: ANÁLISIS LÉXICO
# ---------------------------
def tokenize(code):
    tokens = []
    token_specs = [
        ("MACETA", r'Maceta'),           # Sumar columnas
        ("HIPNOSETA", r'Hipnoseta'),     # Cuadrados aleatorios
        ("PETACEREZA", r'Petacereza'),   # Top 10
        ("JALAPENO", r'Jalapeño'),       # Eliminar columna
        ("COLUMN", r'[a-zA-Z_]\w*'),     # Nombres de columnas
        ("SKIP", r'[ \t]+'),             # Espacios
    ]
    
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
    
    print("✅ Tokens generados:")
    for t in tokens:
        print("  ", t)
    print()
    
    return tokens

# ---------------------------
# FASE 2: ANÁLISIS SINTÁCTICO
# ---------------------------
grammar = """
start: maceta | hipnoseta | petacereza | jalapeno

maceta: "Maceta" COLUMN COLUMN
hipnoseta: "Hipnoseta" COLUMN
petacereza: "Petacereza" COLUMN
jalapeno: "Jalapeño" COLUMN

COLUMN: /[a-zA-Z_]\\w*/

%ignore /\\s+/
"""

parser = Lark(grammar, start="start")

# ---------------------------
# FASE 3: INTÉRPRETE (EJECUTOR)
# ---------------------------
class DataFrameInterpreter(Transformer):
    def __init__(self, dataframe):
        self.df = dataframe
        
    def maceta(self, args):
        col1 = str(args[0])
        col2 = str(args[1])
        print(f"🌱 Maceta: Sumando columnas '{col1}' + '{col2}'")
        
        if col1 not in self.df.columns or col2 not in self.df.columns:
            raise ValueError(f"❌ Una o ambas columnas no existen: {col1}, {col2}")
        
        result = self.df[col1] + self.df[col2]
        print(f"✅ Resultado:")
        print(result)
        return result
    
    def hipnoseta(self, args):
        col = str(args[0])
        print(f"🍄 Hipnoseta: Sacando cuadrados aleatorios de '{col}'")
        
        if col not in self.df.columns:
            raise ValueError(f"❌ La columna '{col}' no existe")
        
        # Tomar una muestra aleatoria y calcular su cuadrado
        sample = self.df[col].sample(n=min(5, len(self.df)))
        result = sample ** 2
        print(f"✅ Valores al cuadrado (muestra aleatoria):")
        print(result)
        return result
    
    def petacereza(self, args):
        col = str(args[0])
        print(f"🍒 Petacereza: Top 10 datos más grandes de '{col}'")
        
        if col not in self.df.columns:
            raise ValueError(f"❌ La columna '{col}' no existe")
        
        result = self.df.nlargest(min(10, len(self.df)), col)[[col]]
        print(f"✅ Top 10:")
        print(result)
        return result
    
    def jalapeno(self, args):
        col = str(args[0])
        print(f"🌶️ Jalapeño: Eliminando columna '{col}'")
        
        if col not in self.df.columns:
            raise ValueError(f"❌ La columna '{col}' no existe")
        
        result = self.df.drop(columns=[col])
        print(f"✅ DataFrame sin la columna '{col}':")
        print(result)
        return result
    
    def COLUMN(self, token):
        return token.value

# ---------------------------
# FUNCIÓN PRINCIPAL
# ---------------------------
def ejecutar(codigo, dataframe):
    print(f"💻 Ejecutando: {codigo!r}\n")
    
    try:
        # 1️⃣ Análisis Léxico
        tokens = tokenize(codigo)
        
        # 2️⃣ Análisis Sintáctico
        tree = parser.parse(codigo)
        print("✅ Árbol sintáctico:")
        print(tree.pretty())
        print()
        
        # 3️⃣ Interpretación/Ejecución
        interpreter = DataFrameInterpreter(dataframe)
        result = interpreter.transform(tree)
        print("="*60)
        print()
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        print("="*60)
        print()
        return None

# --------------------------
# MODO INTERACTIVO (OPCIONAL)
# ---------------------------
if __name__ == "__main__":
    print("\n🎮 Modo interactivo - Escribe tus comandos:")
    print("Comandos disponibles:")
    print("  • Maceta col1 col2    - Sumar dos columnas")
    print("  • Hipnoseta columna   - Cuadrados aleatorios")
    print("  • Petacereza columna  - Top 10 más grandes")
    print("  • Jalapeño columna    - Eliminar columna")
    print("  • salir               - Terminar")
    print()

    while True:
        comando = input("🌿 > ").strip()
        if comando.lower() == 'salir':
            print("👋 ¡Hasta luego!")
            break
        if comando:
            ejecutar(comando, df)
