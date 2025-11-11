import re
from lark import Lark, Transformer
import pandas as pd
from transformacion_filtrado import DataFrameInterpreter, parser as action_parser
import time
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
    # Definimos los patrones válidos
    tokens = []
    token_specs = [
        ("FOOTBALL", r'Football'),       # Realizar la acción hasta que pasen 10 seg.
        ("INGENIERO", r'Ingeniero'),     # Guarda las columnas en 3 variables
        ("ZOMBIDITO", r'Zombidito'),     # Realiza ELSE siempre
        ("ZOMBISTEIN", r'Zombistein'),   # Bucle FOR 3 veces
        ("LPAREN", r'\('),               # Paréntesis izquierdo
        ("RPAREN", r'\)'),               # Paréntesis derecho
        ("ACTION", r'(Maceta|Hipnoseta|Petacereza|Jalapeño)'),  # Acciones válidas
        ("COLUMN", r'[a-zA-Z_]\w*'),     # Nombres de columnas
        ("SKIP", r'[ \t]+'),             # Espacios
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

    print("✅ Tokens generados:")
    for t in tokens:
        print("  ", t)
    print()
    return tokens

# ---------------------------
# FASE 2: ANÁLISIS SINTÁCTICO
# ---------------------------
grammar = """
start: football | ingeniero | zombidito | zombistein

football: "Football" "(" action ")"
ingeniero: "Ingeniero" COLUMN COLUMN COLUMN
zombidito: "Zombidito" "(" action action ")"
zombistein: "Zombistein" "(" action ")"

action: maceta | hipnoseta | petacereza | jalapeno

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
class control_de_flujo_variables(Transformer):
    def __init__(self, dataframe):
        self.df = dataframe
        self.base_interpreter = DataFrameInterpreter(dataframe)
        
    def football(self, items):
        """Ejecuta una acción repetidamente durante 10 segundos"""
        action_tree = items[0]
        print(f"⚽ Football: Ejecutando acción durante 10 segundos...")
        
        start_time = time.time()
        count = 0
        result = None
        
        while (time.time() - start_time) < 10:
            count += 1
            result = action_tree
            print(result)
            action_tree = items[0]  # Re-evaluar la acción
            time.sleep(0.5)  # Pequeña pausa para no saturar
        
        print(f"✅ Acción ejecutada {count} veces en 10 segundos")
        return result
    
    def ingeniero(self, items):
        """Guarda una columna en 3 variables diferentes"""
        col1 = str(items[0])
        col2 = str(items[1])
        col3 = str(items[2])
        
        print(f"👷 Ingeniero: Guardando columnas '{col1}', '{col2}', '{col3}' en variables")
        
        vars_dict = {}
        for col in [col1, col2, col3]:
            if col not in self.df.columns:
                raise ValueError(f"❌ La columna '{col}' no existe")
            vars_dict[col] = self.df[col].copy()
        
        print(f"✅ Variables guardadas:")
        for name, data in vars_dict.items():
            print(f"   {name}: {len(data)} valores")
        
        return vars_dict
    
    def zombidito(self, items):
        """Ejecuta dos acciones alternadamente (simula if-else)"""
        action1 = items[0]
        action2 = items[1]
        
        print(f"🧟 Zombidito: Ejecutando dos acciones (ELSE siempre)")
        print("  → Ejecutando acción 1:")
        result1 = action1
        print("  → Ejecutando acción 2:")
        result2 = action2
        
        return (result1, result2)
    
    def zombistein(self, items):
        """Ejecuta una acción en un bucle 3 veces"""
        action_tree = items[0]
        
        print(f"🧟‍♂️ Zombistein: Ejecutando acción 3 veces (bucle FOR)")
        results = []
        
        for i in range(3):
            print(f"  → Iteración {i+1}:")
            result = action_tree
            results.append(result)
        
        print(f"✅ Bucle completado (3 iteraciones)")
        return results
    
    # Delegamos las acciones básicas al intérprete de transformación_filtrado
    def action(self, items):
        """Delega la ejecución de acciones básicas"""
        return items[0]
    
    def maceta(self, args):
        return self.base_interpreter.maceta(args)
    
    def hipnoseta(self, args):
        return self.base_interpreter.hipnoseta(args)
    
    def petacereza(self, args):
        return self.base_interpreter.petacereza(args)
    
    def jalapeno(self, args):
        return self.base_interpreter.jalapeno(args)
    
    def COLUMN(self, token):
        return token.value
            
# ---------------------------
# Función Principal
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
        interpreter = control_de_flujo_variables(dataframe)
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
print("\n🎮 Modo interactivo - Escribe tus comandos:")
print("Comandos disponibles:")
print("  • Football(accion col1 col2)          - Realizar la acción durante 10 seg.")
print("  • Ingeniero col1 col2 col3            - Guarda 3 columnas en variables")
print("  • Zombidito(Maceta c1 c2 Hipnoseta c3)- Ejecuta 2 acciones (ELSE)")
print("  • Zombistein(Petacereza columna)      - Bucle FOR 3 veces")
print("  • salir                               - Terminar")
print()
print("Acciones básicas disponibles:")
print("  • Maceta col1 col2    - Sumar dos columnas")
print("  • Hipnoseta columna   - Cuadrados aleatorios")
print("  • Petacereza columna  - Top 10 más grandes")
print("  • Jalapeño columna    - Eliminar columna")
print()

while True:
    comando = input("🌿 > ").strip()
    if comando.lower() == 'salir':
        print("👋 ¡Hasta luego!")
        break
    if comando:
        ejecutar(comando, df)
