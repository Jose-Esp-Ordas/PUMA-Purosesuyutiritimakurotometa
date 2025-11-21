import re
import pandas as pd
import numpy as np
from lark import Lark, Transformer
from lark.exceptions import LarkError, UnexpectedInput, UnexpectedToken

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
            error_context = code[pos:min(pos+20, len(code))]
            raise SyntaxError(f"Carácter inesperado en posición {pos}: '{error_context}'")
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
        super().__init__()
        self.df = dataframe
        self.modified = False
    
    def maceta(self, args):
        col1 = str(args[0])
        col2 = str(args[1])
        print(f"🌱 Maceta: Sumando columnas '{col1}' + '{col2}'")
        
        if col1 not in self.df.columns:
            raise ValueError(f"La columna '{col1}' no existe. Columnas disponibles: {list(self.df.columns)}")
        if col2 not in self.df.columns:
            raise ValueError(f"La columna '{col2}' no existe. Columnas disponibles: {list(self.df.columns)}")
        
        # Verificar que las columnas sean numéricas
        if not pd.api.types.is_numeric_dtype(self.df[col1]):
            raise ValueError(f"La columna '{col1}' no es numérica")
        if not pd.api.types.is_numeric_dtype(self.df[col2]):
            raise ValueError(f"La columna '{col2}' no es numérica")
        
        # Crear nueva columna con la suma
        new_col_name = f"{col1}_mas_{col2}"
        if new_col_name in self.df.columns:
            self.df[new_col_name] = self.df[new_col_name] + self.df[col1] + self.df[col2]
        else:
            self.df[new_col_name] = self.df[col1] + self.df[col2]
        self.modified = True
        
        print(f"✅ Nueva columna '{new_col_name}' creada:")
        print(self.df[[col1, col2, new_col_name]].head())
        return self.df
    
    def hipnoseta(self, args):
        col = str(args[0])
        print(f"🍄 Hipnoseta: Creando columna de cuadrados de '{col}'")
        
        if col not in self.df.columns:
            raise ValueError(f"La columna '{col}' no existe. Columnas disponibles: {list(self.df.columns)}")
        
        # Verificar que la columna sea numérica
        if not pd.api.types.is_numeric_dtype(self.df[col]):
            raise ValueError(f"La columna '{col}' no es numérica")
        
        # Crear nueva columna con los cuadrados
        new_col_name = f"{col}_cuadrado"
        if new_col_name in self.df.columns:
            self.df[new_col_name] = self.df[new_col_name] + self.df[col] ** 2
        else:
            self.df[new_col_name] = self.df[col] ** 2
        self.modified = True
        
        print(f"✅ Nueva columna '{new_col_name}' creada:")
        print(self.df[[col, new_col_name]].head())
        return self.df
    
    def petacereza(self, args):
        col = str(args[0])
        print(f"🍒 Petacereza: Filtrando solo el Top 10 de '{col}'")
        
        if col not in self.df.columns:
            raise ValueError(f"La columna '{col}' no existe. Columnas disponibles: {list(self.df.columns)}")
        
        # Verificar que la columna sea numérica
        if not pd.api.types.is_numeric_dtype(self.df[col]):
            raise ValueError(f"La columna '{col}' no es numérica")
        
        if len(self.df) == 0:
            raise ValueError("El DataFrame está vacío, no se puede filtrar")
        
        # Mantener solo el top 10
        n_rows = min(10, len(self.df))
        self.df = self.df.nlargest(n_rows, col)
        self.modified = True
        
        print(f"✅ DataFrame reducido al Top {n_rows} de '{col}':")
        print(self.df)
        return self.df
    
    def jalapeno(self, args):
        col = str(args[0])
        print(f"🌶️ Jalapeño: Eliminando columna '{col}'")
        
        if col not in self.df.columns:
            raise ValueError(f"La columna '{col}' no existe. Columnas disponibles: {list(self.df.columns)}")
        
        if len(self.df.columns) == 1:
            raise ValueError("No se puede eliminar la única columna del DataFrame")
        
        self.df = self.df.drop(columns=[col])
        self.modified = True
        
        print(f"✅ Columna '{col}' eliminada. Columnas restantes:")
        print(list(self.df.columns))
        return self.df
    
    def COLUMN(self, token):
        return token.value

# ---------------------------
# Función principal
# ---------------------------
def main():
    print("="*60)
    print("🌿 PUMA - Purosesuyutiritimakurotometa 🌱")
    print("="*60)
    
    # Cargar el DataFrame desde el CSV
    CSV_FILE = 'datos_prueba.csv'
    
    try:
        df = pd.read_csv(CSV_FILE)
        print("✅ CSV cargado exitosamente!")
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'datos_prueba.csv'")
        print("Asegúrate de que el archivo esté en el mismo directorio.")
        return
    except pd.errors.EmptyDataError:
        print("❌ Error: El archivo CSV está vacío")
        return
    except pd.errors.ParserError:
        print("❌ Error: El archivo CSV tiene un formato inválido")
        return
    except Exception as e:
        print(f"❌ Error inesperado al cargar el CSV: {e}")
        return
    
    print("\n📊 DataFrame inicial:")
    print(df)
    print(f"\n📋 Columnas disponibles: {list(df.columns)}")
    print(f"📏 Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
    print("="*60)
    print()
    
    # Modo interactivo
    print("🎮 Modo interactivo - Escribe tus comandos:")
    print("Comandos disponibles:")
    print("  • Maceta col1 col2    - Sumar dos columnas (crea nueva columna)")
    print("  • Hipnoseta columna   - Elevar al cuadrado (crea nueva columna)")
    print("  • Petacereza columna  - Filtrar Top 10 más grandes")
    print("  • Jalapeño columna    - Eliminar columna")
    print("  • mostrar             - Ver DataFrame actual")
    print("  • columnas            - Ver lista de columnas")
    print("  • salir               - Terminar")
    print()
    
    while True:
        try:
            comando = input("🌿 > ").strip()
            
            if comando.lower() in ['salir', 'exit', 'quit']:
                print("👋 ¡Hasta luego!")
                break
            
            if not comando:
                continue
            
            if comando.lower() == 'mostrar':
                print("\n📊 DataFrame actual:")
                print(df)
                print(f"\n📋 Columnas: {list(df.columns)}")
                print(f"📏 Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
                print("="*60)
                print()
                continue
            
            if comando.lower() == 'columnas':
                print("\n📋 Columnas disponibles:")
                for i, col in enumerate(df.columns, 1):
                    tipo = df[col].dtype
                    print(f"  {i}. {col} (tipo: {tipo})")
                print("="*60)
                print()
                continue
            
            print(f"💻 Ejecutando: {comando!r}\n")
            
            # 1️⃣ Fase léxica
            try:
                tokens = tokenize(comando)
            except SyntaxError as e:
                print(f"❌ Error léxico: {e}")
                print("💡 Comandos válidos:")
                print("   • Maceta columna1 columna2")
                print("   • Hipnoseta columna")
                print("   • Petacereza columna")
                print("   • Jalapeño columna")
                print("="*60)
                print()
                continue
            
            # 2️⃣ Fase sintáctica
            try:
                tree = parser.parse(comando)
                print("✅ Árbol sintáctico:")
                print(tree.pretty())
                print()
            except UnexpectedToken as e:
                print(f"❌ Error sintáctico: Token inesperado '{e.token}'")
                print("💡 Verifica que el comando esté bien escrito")
                print("="*60)
                print()
                continue
            except UnexpectedInput as e:
                print(f"❌ Error sintáctico: Entrada inesperada")
                print("💡 Verifica el formato del comando")
                print("="*60)
                print()
                continue
            except LarkError as e:
                print(f"❌ Error sintáctico: {e}")
                print("="*60)
                print()
                continue
            
            # 3️⃣ Fase de interpretación
            try:
                interpreter = DataFrameInterpreter(df)
                result = interpreter.transform(tree)
                
                # Si se modificó el DataFrame, actualizar y guardar
                if interpreter.modified:
                    df = interpreter.df
                    try:
                        df.to_csv(CSV_FILE, index=False)
                        print(f"\n💾 Cambios guardados en '{CSV_FILE}'")
                    except PermissionError:
                        print(f"\n⚠️ Error: No se puede guardar '{CSV_FILE}' (archivo abierto en otro programa)")
                    except Exception as e:
                        print(f"\n⚠️ Error al guardar: {e}")
                    
                    print("\n📊 DataFrame actualizado:")
                    print(df)
                
                print("="*60)
                print()
            
            except ValueError as e:
                print(f"❌ Error de ejecución: {e}")
                print("="*60)
                print()
                continue
            except KeyError as e:
                print(f"❌ Error: Columna no encontrada: {e}")
                print(f"💡 Columnas disponibles: {list(df.columns)}")
                print("="*60)
                print()
                continue
            except Exception as e:
                print(f"❌ Error inesperado durante la ejecución: {e}")
                print("="*60)
                print()
                continue
        
        except KeyboardInterrupt:
            print("\n\n👋 Programa interrumpido por el usuario")
            break
        except EOFError:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            continue

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error crítico: {e}")