import re
import pandas as pd
from lark import Lark, Transformer
from lark.exceptions import LarkError, UnexpectedInput, UnexpectedToken
import matplotlib.pyplot as plt
import numpy as numpy
from comunicacion_accion_final import AccionFinal
from transformacion_filtrado import DataFrameInterpreter as Filtrado
from comando_especial import DataFrameInterpreter as ComandoEspecial
from control_flujo_variables import control_de_flujo_variables as Flujo
from manejo_archivos import ManejoArchivos 


# --------------------------- 
# FASE 1: ANÁLISIS LÉXICO
# ---------------------------
def tokenize(code):
    tokens = []
    token_specs = [
        ("ZEREBROS", r'Zerebros'),
        ("SOL", r'Sol'),
        ("CARNIVORA", r'Carnivora'),
        ("PAPAPUM", r'Papapum'),
        ("MAGNETOSETA", r'Magnetoseta'),
        ("MELONPULTA", r'melonpulta_gelida'),
        ("MACETA", r'Maceta'),
        ("HIPNOSETA", r'Hipnoseta'),
        ("PETACEREZA", r'Petacereza'),
        ("JALAPENO", r'Jalapeño'),
        ("FOOTBALL", r'Football'),
        ("INGENIERO", r'Ingeniero'),
        ("ZOMBIDITO", r'Zombidito'),
        ("ZOMBISTEIN", r'Zombistein'),
        ("ROSA", r'rosa'),
        ("LPAREN", r'\('),
        ("RPAREN", r'\)'),
        ("NUMBER", r'\d+'),
        ("STRING", r'"[^"]*"'),
        ("COLUMN", r'[a-zA-Z_áéíóúÁÉÍÓÚñÑ]\w*'),
        ("SKIP", r'[ \t]+'),
    ]
    master = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in token_specs))
    pos = 0
    while pos < len(code):
        m = master.match(code, pos)
        if not m:
            error_char = code[pos]
            error_context = code[max(0, pos-10):min(pos+20, len(code))]
            
            # Mensajes de error específicos
            if error_char in '[]{}':
                raise SyntaxError(f"❌ Error léxico en posición {pos}: Carácter '{error_char}' no válido.\n"
                                f"   Contexto: ...{error_context}...\n"
                                f"   💡 Usa paréntesis () en lugar de corchetes o llaves")
            elif error_char in '!@#$%^&*+=<>?/\\|~`':
                raise SyntaxError(f"❌ Error léxico en posición {pos}: Carácter especial '{error_char}' no reconocido.\n"
                                f"   Contexto: ...{error_context}...\n"
                                f"   💡 Revisa la sintaxis del comando")
            elif error_char == "'":
                raise SyntaxError(f"❌ Error léxico en posición {pos}: Comillas simples no permitidas.\n"
                                f"   Contexto: ...{error_context}...\n"
                                f"   💡 Usa comillas dobles \" \" para cadenas de texto")
            else:
                raise SyntaxError(f"❌ Error léxico en posición {pos}: Carácter inesperado '{error_char}'.\n"
                                f"   Contexto: ...{error_context}...\n"
                                f"   💡 Verifica que el comando esté escrito correctamente")
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
start: zerebros | sol | carnivora | papapum | magnetoseta | melonpulta | maceta | hipnoseta | petacereza | jalapeno | football | ingeniero | zombidito | zombistein | rosa

zerebros: "Zerebros"

sol: "Sol" STRING
carnivora: "Carnivora" STRING?
papapum: "Papapum" STRING STRING?
magnetoseta: "Magnetoseta"
melonpulta: "melonpulta_gelida"

maceta: "Maceta" COLUMN COLUMN
hipnoseta: "Hipnoseta" COLUMN
petacereza: "Petacereza" COLUMN
jalapeno: "Jalapeño" COLUMN

football: "Football" "(" action ")"
ingeniero: "Ingeniero" COLUMN COLUMN COLUMN
zombidito: "Zombidito" "(" action action ")"
zombistein: "Zombistein" "(" action ")"

rosa: "Rosa" NUMBER

action: maceta | hipnoseta | petacereza | jalapeno

COLUMN: /[a-zA-Z_]\\w*/
STRING: /"[^"]*"/
NUMBER: /\\d+/
%ignore /\\s+/
"""
parser = Lark(grammar, start="start")

# ---------------------------
# FASE 3: INTÉRPRETE (EJECUTOR)
# ---------------------------
class InterpretadorFinal(Transformer):
    """Clase que integra todos los intérpretes del lenguaje PUMA"""
    
    def __init__(self, dataframe):
        super().__init__()
        self.df = dataframe
        self.modified = False
        
        # Inicializar intérpretes especializados
        self.base_interpreter = ManejoArchivos()  # No recibe dataframe, maneja archivos
        self.especial_interpreter = ComandoEspecial(dataframe)
        self.final_interpreter = AccionFinal()  # No recibe parámetros
        self.flujo_interpreter = Flujo(dataframe)
        self.filtrado_interpreter = Filtrado(dataframe)
    
    # Métodos de transformación/filtrado
    def maceta(self, args):
        return self.filtrado_interpreter.maceta(args)
    
    def hipnoseta(self, args):
        return self.filtrado_interpreter.hipnoseta(args)
    
    def petacereza(self, args):
        return self.filtrado_interpreter.petacereza(args)
    
    def jalapeno(self, args):
        return self.filtrado_interpreter.jalapeno(args)
    
    # Métodos de manejo de archivos
    def sol(self, args):
        return self.base_interpreter.sol(args)
    
    def carnivora(self, args):
        return self.base_interpreter.carnivora(args)
    
    def papapum(self, args):
        return self.base_interpreter.papapum(args)
    
    def magnetoseta(self, args):
        return self.base_interpreter.magnetoseta(args)
    
    def melonpulta(self, args):
        return self.base_interpreter.melonpulta(args)
    
    # Métodos de control de flujo
    def football(self, args):
        return self.flujo_interpreter.football(args)
    
    def ingeniero(self, args):
        return self.flujo_interpreter.ingeniero(args)
    
    def zombidito(self, args):
        return self.flujo_interpreter.zombidito(args)
    
    def zombistein(self, args):
        return self.flujo_interpreter.zombistein(args)
    
    # Comando especial Rosa
    def rosa(self, args):
        """Procesa comando rosa"""
        return self.especial_interpreter.start(args)
    
    # Comando de salida
    def zerebros(self, args):
        return self.final_interpreter.zerebros(args)
    
    def COLUMN(self, token):
        return token.value
    
    def STRING(self, token):
        return str(token).strip('"')
    
    def NUMBER(self, token):
        return token.value
    
    def start(self, items):
        """Procesa el nodo start y retorna el resultado del comando"""
        # items[0] contiene el resultado del comando
        return items[0]
    
    def action(self, items):
        """Procesa el nodo action y retorna el resultado"""
        return items[0]

# ---------------------------
# Función para mostrar ayuda completa
# ---------------------------
def mostrar_ayuda_completa():
    """Muestra todos los comandos disponibles después de cargar archivo"""
    print("\n" + "="*60)
    print("📚 COMANDOS DISPONIBLES")
    print("="*60)
    print("\n📁 Manejo de archivos:")
    print("  • Sol \"archivo.csv\"              - Abrir archivo CSV")
    print("  • Carnivora \"archivo.csv\"      - Guardar archivo")
    print("  • Papapum \"ruta\" [formato]       - Exportar archivo")
    print("  • Magnetoseta                     - Info del archivo")
    print("  • melonpulta_gelida               - Cerrar archivo")
    print("\n🔄 Transformación y filtrado:")
    print("  • Maceta col1 col2                - Sumar columnas")
    print("  • Hipnoseta columna               - Elevar al cuadrado")
    print("  • Petacereza columna              - Top 10")
    print("  • Jalapeño columna                - Eliminar columna")
    print("\n🎮 Control de flujo:")
    print("  • Football (accion)               - Repetir 10 segundos")
    print("  • Ingeniero col1 col2 col3        - Guardar en variables")
    print("  • Zombidito (accion1 accion2)     - Ejecutar ambas")
    print("  • Zombistein (accion)             - Bucle 3 veces")
    print("\n🎲 Comando especial:")
    print("  • Rosa N                          - Acción aleatoria N veces")
    print("\n🧠 Salida:")
    print("  • Zerebros                        - Fin del programa")
    print("="*60)
    print()

# ---------------------------
# Función principal
# ---------------------------
def main():
    print("="*60)
    print("🌿 PUMA - Purosesuyutiritimakurotometa 🌱")
    print("="*60)
    print("\n⚠️  IMPORTANTE: Debes comenzar cargando un archivo CSV")
    print("="*60)
    print("\n🚀 Para comenzar usa:")
    print("  • Sol \"archivo.csv\"    - Cargar archivo CSV")
    print("  • Zerebros              - Salir del programa")
    print("="*60)
    print()
    
    # DataFrame inicialmente vacío, se carga con Sol
    df = None
    archivo_cargado = False  # Bandera para verificar si ya se cargó un archivo
    
    # Crear una única instancia del intérprete que se mantiene durante toda la sesión
    interpreter = InterpretadorFinal(pd.DataFrame())
    
    print("🎮 Modo interactivo - Esperando comando Sol...\n")
    
    while True:
        try:
            comando = input("🌿 > ").strip()
            
            if not comando:
                continue
            
            # Verificar que el primer comando sea Sol o Zerebros (excepto salir)
            if not archivo_cargado and not comando.startswith('Sol') and comando != 'Zerebros':
                print("\n⚠️  ERROR: Debes cargar un archivo primero usando:")
                print("   Sol \"archivo.csv\"")
                print("   O salir del programa con: Zerebros")
                print("="*60)
                print()
                continue
            
            print(f"💻 Ejecutando: {comando!r}\n")
            
            # 1️⃣ Fase léxica
            try:
                tokens = tokenize(comando)
            except SyntaxError as e:
                print(f"{e}")
                print("\n💡 Comandos básicos disponibles:")
                if not archivo_cargado:
                    print("   • Sol \"archivo.csv\" - Cargar archivo")
                else:
                    print("   • Usa un comando válido (escribe 'ayuda' para ver todos)")
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
                print(f"   Se esperaba: {', '.join(str(x) for x in e.expected)}")
                print("💡 Verifica que el comando esté bien escrito")
                print("="*60)
                print()
                continue
            except UnexpectedInput as e:
                print(f"❌ Error sintáctico: Entrada inesperada en la posición {e.pos_in_stream}")
                print("💡 Verifica el formato del comando")
                if not archivo_cargado:
                    print("   Recuerda: Sol \"archivo.csv\"")
                print("="*60)
                print()
                continue
            except LarkError as e:
                print(f"❌ Error sintáctico: {e}")
                print("💡 Revisa la estructura del comando")
                print("="*60)
                print()
                continue
            
            # 3️⃣ Fase de interpretación
            try:
                # Reutilizar el mismo intérprete para mantener el estado
                result = interpreter.transform(tree)
                
                # Si Sol cargó un archivo, actualizar el DataFrame
                if hasattr(interpreter.base_interpreter, 'archivo_actual') and interpreter.base_interpreter.archivo_actual is not None:
                    df = interpreter.base_interpreter.archivo_actual
                    
                    # Actualizar el DataFrame en todos los intérpretes
                    interpreter.df = df
                    interpreter.filtrado_interpreter.df = df
                    interpreter.especial_interpreter.df = df
                    interpreter.flujo_interpreter.df = df
                    interpreter.flujo_interpreter.base_interpreter.df = df
                    
                    print(f"\n✅ Archivo cargado exitosamente")
                    print(f"📊 DataFrame:")
                    print(df.head())
                    print(f"\n📋 Columnas: {list(df.columns)}")
                    print(f"📏 Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
                    
                    # Marcar que ya se cargó un archivo y mostrar ayuda completa
                    if not archivo_cargado:
                        archivo_cargado = True
                        mostrar_ayuda_completa()
                
                # Si se modificó el DataFrame con transformaciones, actualizar
                if hasattr(interpreter.filtrado_interpreter, 'modified') and interpreter.filtrado_interpreter.modified:
                    df = interpreter.filtrado_interpreter.df
                    # Sincronizar el DataFrame actualizado con base_interpreter para que Carnivora pueda guardarlo
                    interpreter.base_interpreter.archivo_actual = df
                    print("\n📊 DataFrame actualizado:")
                    print(df)
                
                # Si comando especial modifico el DataFrame, actualizar
                if hasattr(interpreter.especial_interpreter, 'df') and interpreter.especial_interpreter.df is not None:
                    # Verificar si el DataFrame cambio
                    if df is None or not df.equals(interpreter.especial_interpreter.df):
                        df = interpreter.especial_interpreter.df
                        # Sincronizar con base_interpreter
                        interpreter.base_interpreter.archivo_actual = df
                
                # Si es un resultado de un comando (dict), mostrarlo
                if isinstance(result, dict):
                    if "error" in result:
                        print(f"\n❌ {result['error']}")
                        if "tipo" in result:
                            print(f"   Tipo: {result['tipo']}")
                    elif "exito" in result:
                        print(f"\n✅ {result.get('mensaje', 'Operación exitosa')}")
                        # Mostrar información adicional si es Magnetoseta
                        if "columnas_nombres" in result:
                            print(f"\n📋 Información del archivo:")
                            print(f"   Archivo: {result.get('archivo', 'N/A')}")
                            print(f"   Filas: {result.get('filas', 0)}")
                            print(f"   Columnas: {result.get('columnas', 0)}")
                            print(f"\n   Nombres de columnas:")
                            for col in result.get('columnas_nombres', []):
                                tipo = result.get('tipos_datos', {}).get(col, 'desconocido')
                                print(f"      • {col} ({tipo})")
                        # Mostrar otros datos del resultado
                        else:
                            for key, value in result.items():
                                if key not in ['exito', 'mensaje', 'tipo']:
                                    print(f"   {key}: {value}")
                    elif "cargado" in result and not result["cargado"]:
                        print(f"\n⚠️  {result.get('mensaje', 'Sin información')}")
                    else:
                        print(f"\n📋 {result.get('mensaje', result)}")
                
                print("="*60)
                print()
            
            except ValueError as e:
                print(f"❌ Error de ejecución: {e}")
                print("="*60)
                print()
                continue
            except KeyError as e:
                print(f"❌ Error: Columna no encontrada: {e}")
                if df is not None:
                    print(f"💡 Columnas disponibles: {list(df.columns)}")
                else:
                    print(f"💡 No hay archivo cargado")
                print("="*60)
                print()
                continue
            except Exception as e:
                print(f"❌ Error inesperado durante la ejecución: {e}")
                import traceback
                traceback.print_exc()
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
            import traceback
            traceback.print_exc()
            continue

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()