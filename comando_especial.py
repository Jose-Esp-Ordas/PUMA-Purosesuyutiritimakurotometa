import re
import pandas as pd
import numpy as np
from lark import Lark, Transformer
from lark.exceptions import LarkError, UnexpectedInput, UnexpectedToken
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ---------------------------
# FASE 1: ANÁLISIS LÉXICO
# ---------------------------
def tokenize(code):
    tokens = []
    token_specs = [
        ("ROSA", r'[Rr]osa'),      # Acepta Rosa o rosa
        ("NUMBER", r'\d+'),         # Número de veces
        ("SKIP", r'[ \t]+')         # Espacios    
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
start: "rosa" NUMBER
%import common.NUMBER
%ignore /\\s+/
"""
parser = Lark(grammar, start="start")

# ---------------------------
# FASE 3: INTÉRPRETE (EJECUTOR)
# ---------------------------
class DataFrameInterpreter(Transformer):
    def __init__(self, dataframe):
        self.df = dataframe
        self.error_occurred = False
        self.error_message = ""
    
    def start(self, items):
        """Procesa el comando rosa"""
        try:
            n = int(items[0])
            
            if n <= 0:
                raise ValueError("El número debe ser mayor a 0")
            
            if n > 100:
                print("⚠️ Advertencia: ¿Estás seguro de ejecutar más de 100 acciones?")
                confirmacion = input("Escribe 'sí' para continuar: ")
                if confirmacion.lower() != 'sí':
                    print("❌ Operación cancelada")
                    return self.df
            
            print(f"🌹 Rosa: Ejecutando acción {n} veces...")
            for i in range(n):
                try:
                    action = np.random.choice([
                        self.reemplazar_valores_por_cabra,
                        self.mostrar_imagen_cabra,
                        self.cambiar_nombres_columnas_random,
                        self.mezclar_filas_random,
                        self.eliminar_fila_aleatoria,
                        self.duplicar_fila_aleatoria,
                        self.invertir_columnas,
                        self.cabra_csv,
                        self.cabra_grafico
                    ])
                    action()
                except Exception as e:
                    print(f"  - ⚠️ Error en acción {i+1}: {e}")
                    continue
            
            return self.df
        
        except ValueError as e:
            self.error_occurred = True
            self.error_message = f"Error de valor: {e}"
            raise
    
    def reemplazar_valores_por_cabra(self):
        print("  - 🐐 Reemplazando valores aleatorios por 'cabra'")
        if len(self.df) == 0:
            print("    ⚠️ DataFrame vacío, saltando acción")
            return
        if len(self.df.columns) == 0:
            print("    ⚠️ No hay columnas, saltando acción")
            return
        col = np.random.choice(self.df.columns)
        idx = np.random.randint(0, len(self.df))
        self.df.at[idx, col] = "🐐 cabra"
    
    def mostrar_imagen_cabra(self):
        print("  - 🐐 ¡Mostrando la cabra!")
        try:
            img = plt.imread("cabra.jpg")
            fig, ax = plt.subplots()
            ax.imshow(img)
            ax.axis('off')
            plt.show()
        except FileNotFoundError:
            print("    ⚠️ No se encontró 'cabra.jpg', mostrando cabra alternativa")
            self.cabra_grafico()
        except Exception as e:
            print(f"    ⚠️ Error al mostrar imagen: {e}")
    
    def cambiar_nombres_columnas_random(self):
        print("  - 🎲 Cambiando nombres de columnas aleatoriamente")
        if len(self.df.columns) == 0:
            print("    ⚠️ No hay columnas para renombrar")
            return
        new_names = {}
        for col in self.df.columns:
            new_names[col] = f"col_{np.random.randint(1000, 9999)}"
        self.df.rename(columns=new_names, inplace=True)
    
    def mezclar_filas_random(self):
        print("  - 🔀 Mezclando filas aleatoriamente")
        if len(self.df) == 0:
            print("    ⚠️ DataFrame vacío, no se puede mezclar")
            return
        self.df = self.df.sample(frac=1).reset_index(drop=True)
    
    def eliminar_fila_aleatoria(self):
        if len(self.df) == 0:
            print("  - ⚠️  No hay filas para eliminar")
            return
        idx = np.random.randint(0, len(self.df))
        print(f"  - ❌ Eliminando la fila en el índice {idx}")
        self.df = self.df.drop(idx).reset_index(drop=True)
    
    def duplicar_fila_aleatoria(self):
        if len(self.df) == 0:
            print("  - ⚠️  No hay filas para duplicar")
            return
        idx = np.random.randint(0, len(self.df))
        print(f"  - 📋 Duplicando la fila en el índice {idx}")
        row = self.df.iloc[idx:idx+1]
        self.df = pd.concat([self.df, row], ignore_index=True)
    
    def invertir_columnas(self):
        print("  - 🔄 Invirtiendo el orden de las columnas")
        if len(self.df.columns) == 0:
            print("    ⚠️ No hay columnas para invertir")
            return
        self.df = self.df[self.df.columns[::-1]]
        
    def cabra_csv(self): 
        print("  - 🐐 Transformando todo el DataFrame a 'cabra'")
        if len(self.df.columns) == 0:
            print("    ⚠️ No hay columnas para transformar")
            return
        for col in self.df.columns:
            self.df[col] = "🐐 cabra"
            
    def cabra_grafico(self):
        print("  - 🐐 Mostrando gráfico de cabra")
        try:
            fig, ax = plt.subplots()
            ax.add_patch(Rectangle((0, 0), 1, 1, color='brown'))
            ax.text(0.5, 0.5, '🐐 CABRA', fontsize=50, ha='center', va='center', color='white')
            ax.axis('off')
            plt.show()
        except Exception as e:
            print(f"    ⚠️ Error al mostrar gráfico: {e}")

# ---------------------------
# Función principal
# ---------------------------
def main():
    print("="*60)
    print("🌹 COMANDO ESPECIAL: ROSA (RULETA RUSA) 🐐")
    print("="*60)
    
    # Cargar el DataFrame desde el CSV
    try:
        df = pd.read_csv("datos_prueba.csv")
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
    print()
    
    while True:
        try:
            code = input("Escribe tu comando especial (ejemplo: 'rosa 3') o 'salir' para terminar:\n🌹 > ").strip()
            
            if code.lower() in ['salir', 'exit', 'quit']:
                print("👋 ¡Hasta luego!")
                break
            
            if not code:
                print("⚠️ Por favor ingresa un comando válido")
                continue
            
            # 1️⃣ Fase léxica
            try:
                tokens = tokenize(code)
            except SyntaxError as e:
                print(f"❌ Error léxico: {e}")
                print("💡 Formato correcto: 'rosa <número>'")
                print("   Ejemplo: rosa 3")
                continue
            
            # 2️⃣ Fase sintáctica
            try:
                tree = parser.parse(code)
                print("✅ Árbol sintáctico:")
                print(tree.pretty())
                print()
            except UnexpectedToken as e:
                print(f"❌ Error sintáctico: Token inesperado '{e.token}'")
                print("💡 Formato correcto: 'rosa <número>'")
                print("   Ejemplo: rosa 3")
                continue
            except UnexpectedInput as e:
                print(f"❌ Error sintáctico: Entrada inesperada")
                print("💡 Formato correcto: 'rosa <número>'")
                print("   Ejemplo: rosa 3")
                continue
            except LarkError as e:
                print(f"❌ Error sintáctico: {e}")
                print("💡 Formato correcto: 'rosa <número>'")
                print("   Ejemplo: rosa 3")
                continue
            
            # 3️⃣ Fase de interpretación
            try:
                interpreter = DataFrameInterpreter(df)
                result_df = interpreter.transform(tree)
                
                print("\n📊 DataFrame final (después del caos):")
                print(result_df)
                
                # Guardar el resultado
                try:
                    result_df.to_csv("datos_resultado.csv", index=False)
                    print("\n💾 Resultado guardado en 'datos_resultado.csv'")
                except Exception as e:
                    print(f"\n⚠️ No se pudo guardar el resultado: {e}")
                
                # Actualizar el DataFrame para la siguiente iteración
                df = result_df
                
            except ValueError as e:
                print(f"❌ Error de ejecución: {e}")
                continue
            except Exception as e:
                print(f"❌ Error inesperado durante la ejecución: {e}")
                continue
            
            print("\n" + "="*60 + "\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Programa interrumpido por el usuario")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            continue

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error crítico: {e}")