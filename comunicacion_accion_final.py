import re
import pandas as pd
from lark import Lark, Transformer
from lark.exceptions import LarkError, UnexpectedInput, UnexpectedToken
import matplotlib.pyplot as plt
import numpy as numpy

# ---------------------------
# FASE 1: ANÁLISIS LÉXICO
# ---------------------------
def tokenize(code):
    tokens = []
    token_specs = [
        ("Zerebros", r'Zerebros'),       # Saludo final
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
start: zerebros
zerebros: "Zerebros"
%ignore /\\s+/
"""
parser = Lark(grammar, start="start")

# ---------------------------
# FASE 3: INTÉRPRETE (EJECUTOR)
# ---------------------------
class AccionFinal(Transformer):

    def zerebros(self, args):
        print(f"🧠 Zerebros ")
        try:
            num = numpy.random.randint(1, 4)
            img = plt.imread(f"./resources/zombis{num}.png")
            fig, ax = plt.subplots()
            ax.imshow(img)
            ax.axis('off')
            plt.title("Mensaje importante de los Zombis")
            plt.show()
            exit(0)
        except FileNotFoundError:
            print("    ⚠️ No se encontró 'zombis.png', mostrando zombis alternativa")
            self.cabra_grafico()
        except Exception as e:
            print(f"    ⚠️ Error al mostrar imagen: {e}")
    
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
    print("  • Zerebros   - Fin del programa")
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
                print("   • Zerebros")
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
                interpreter = AccionFinal(df)
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