import pandas as pd
import os
from typing import Optional, Dict, Any
from lark import Lark, Transformer

# ---------------------------
# FASE 1: ANÁLISIS LÉXICO
# ---------------------------
import re

def tokenize(code):
    tokens = []
    token_specs = [
        ("SOL", r'Sol'),                      # Abrir archivo
        ("CARNIVORA", r'Carnívora'),          # Guardar archivo
        ("PAPAPUM", r'Papapum'),              # Exportar archivo
        ("MAGNETOSETA", r'Magnetoseta'),      # Info del archivo
        ("MELONPULTA", r'melonpulta_gelida'), # Cerrar archivo
        ("STRING", r'"[^"]*"'),               # Cadenas entre comillas
        ("SKIP", r'[ \t]+'),                  # Espacios
    ]
    
    master = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in token_specs))
    pos = 0
    
    while pos < len(code):
        m = master.match(code, pos)
        if not m:
            raise SyntaxError(f"Error léxico cerca de: {code[pos:pos+10]!r}")
        typ = m.lastgroup
        if typ != "SKIP":
            tokens.append((typ, m.group()))
        pos = m.end()
    
    print("[OK] Tokens generados:")
    for t in tokens:
        print("  ", t)
    print()
    
    return tokens

# ---------------------------
# FASE 2: ANÁLISIS SINTÁCTICO
# ---------------------------
grammar = """
start: sol | carnivora | papapum | magnetoseta | melonpulta

sol: "Sol" STRING
carnivora: "Carnívora" STRING?
papapum: "Papapum" STRING STRING?
magnetoseta: "Magnetoseta"
melonpulta: "melonpulta_gelida"

%import common.ESCAPED_STRING -> STRING
%ignore /\\s+/
"""

parser = Lark(grammar, start="start")

# ---------------------------
# FASE 3: INTÉRPRETE (EJECUTOR)
# ---------------------------

class ManejoArchivos(Transformer):
    """Clase para gestionar las operaciones de archivos CSV del lenguaje PUMA"""
    
    def __init__(self):
        """Inicializa el gestor de archivos"""
        super().__init__()
        self.archivo_actual: Optional[pd.DataFrame] = None
        self.nombre_archivo: Optional[str] = None
        self.archivo_cargado: bool = False
    
    # Métodos del Transformer
    def STRING(self, token):
        """Transforma un token STRING (ESCAPED_STRING) quitando las comillas"""
        # ESCAPED_STRING de Lark ya viene sin comillas
        return str(token).strip('"')
    
    def start(self, items):
        """Procesa el nodo start y retorna el resultado del comando"""
        # items[0] contiene el resultado del comando (sol, carnivora, etc.)
        return items[0]
    
    # Método del Transformer para ejecutar comando sol
    def sol(self, items):
        """Método del Transformer - ejecuta comando Sol"""
        ruta = items[0]
        return self._sol(ruta)
    
    def _sol(self, ruta_archivo: str):
        """
        Sol - Comando para abrir un archivo CSV
        
        Args:
            ruta_archivo: Ruta del archivo CSV a abrir
            
        Returns:
            Dict con el resultado de la operación
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el archivo no es CSV
        """
        # Asegurar que sea string
        ruta_archivo = str(ruta_archivo)
        
        # Validación léxica: verificar que sea una ruta válida
        if not ruta_archivo or not ruta_archivo.strip():
            return {
                "error": "Error léxico: La ruta del archivo debe ser una cadena válida",
                "tipo": "LEXICO",
                "linea": 1
            }
        
        # Validación sintáctica: verificar extensión CSV
        if not ruta_archivo.lower().endswith('.csv'):
            return {
                "error": "Error sintáctico: El archivo debe tener extensión .csv",
                "tipo": "SINTACTICO",
                "archivo": ruta_archivo
            }
        
        # Validación semántica: verificar que el archivo existe
        if not os.path.exists(ruta_archivo):
            return {
                "error": f"Error semántico: El archivo '{ruta_archivo}' no existe",
                "tipo": "SEMANTICO",
                "archivo": ruta_archivo
            }
        
        try:
            # Cargar el archivo CSV
            self.archivo_actual = pd.read_csv(ruta_archivo)
            self.nombre_archivo = ruta_archivo
            self.archivo_cargado = True
            
            return {
                "exito": True,
                "mensaje": f"Sol: Archivo '{os.path.basename(ruta_archivo)}' abierto exitosamente"
            }
            
        except pd.errors.EmptyDataError:
            return {
                "error": "Error semántico: El archivo CSV está vacío",
                "tipo": "SEMANTICO",
                "archivo": ruta_archivo
            }
        except pd.errors.ParserError as e:
            return {
                "error": f"Error sintáctico: El archivo CSV tiene formato inválido - {str(e)}",
                "tipo": "SINTACTICO",
                "archivo": ruta_archivo
            }
        except Exception as e:
            return {
                "error": f"Error inesperado al abrir el archivo: {str(e)}",
                "tipo": "RUNTIME",
                "archivo": ruta_archivo
            }
    
    # Método del Transformer para ejecutar comando carnivora
    def carnivora(self, items):
        """Método del Transformer - ejecuta comando Carnívora"""
        # items contiene los valores ya procesados (puede estar vacío si no hay path)
        ruta = items[0] if items else None
        return self._carnivora(ruta)
    
    def _carnivora(self, ruta_archivo: Optional[str] = None):
        """
        Carnívora - Comando para guardar el archivo CSV actual
        
        Args:
            ruta_archivo: Ruta donde guardar. Si es None, sobrescribe el archivo actual
            
        Returns:
            Dict con el resultado de la operación
        """
        # Validación semántica: verificar que hay un archivo cargado
        if not self.archivo_cargado or self.archivo_actual is None:
            return {
                "error": "Error semántico: No hay ningún archivo cargado. Use 'Sol' primero para abrir un archivo",
                "tipo": "SEMANTICO",
                "comando": "Carnívora"
            }
        
        # Si no se proporciona ruta, usar la del archivo actual
        if ruta_archivo is None:
            if self.nombre_archivo is None:
                return {
                    "error": "Error semántico: No hay ruta de archivo definida. Proporcione una ruta",
                    "tipo": "SEMANTICO",
                    "comando": "Carnívora"
                }
            ruta_archivo = self.nombre_archivo
        
        # Asegurar que sea string
        ruta_archivo = str(ruta_archivo)
        
        # Validación sintáctica: verificar extensión CSV
        if not ruta_archivo.lower().endswith('.csv'):
            return {
                "error": "Error sintáctico: El archivo debe tener extensión .csv",
                "tipo": "SINTACTICO",
                "archivo": ruta_archivo
            }
        
        try:
            # Guardar el archivo
            self.archivo_actual.to_csv(ruta_archivo, index=False)
            
            return {
                "exito": True,
                "mensaje": f"Carnívora: Archivo guardado exitosamente en '{os.path.basename(ruta_archivo)}'",
                "archivo": ruta_archivo,
                "filas_guardadas": len(self.archivo_actual)
            }
            
        except PermissionError:
            return {
                "error": f"Error de permisos: No se puede escribir en '{ruta_archivo}'",
                "tipo": "RUNTIME",
                "archivo": ruta_archivo
            }
        except Exception as e:
            return {
                "error": f"Error al guardar el archivo: {str(e)}",
                "tipo": "RUNTIME",
                "archivo": ruta_archivo
            }
    
    # Método del Transformer para ejecutar comando papapum
    def papapum(self, items):
        """Método del Transformer - ejecuta comando Papapum"""
        # items contiene los valores ya procesados
        ruta = items[0]
        formato = items[1] if len(items) > 1 else 'csv'
        return self._papapum(ruta, formato)
    
    def _papapum(self, ruta_exportacion: str, formato: str = 'csv') -> Dict[str, Any]:
        """
        Papapum - Comando para exportar el archivo en diferentes formatos
        
        Args:
            ruta_exportacion: Ruta donde exportar el archivo
            formato: Formato de exportación ('csv', 'json', 'excel')
            
        Returns:
            Dict con el resultado de la operación
        """
        # Asegurar que sean strings
        ruta_exportacion = str(ruta_exportacion)
        formato = str(formato)
        
        # Validación semántica: verificar que hay un archivo cargado
        if not self.archivo_cargado or self.archivo_actual is None:
            return {
                "error": "Error semántico: No hay ningún archivo cargado. Use 'Sol' primero para abrir un archivo",
                "tipo": "SEMANTICO",
                "comando": "Papapum"
            }
        
        # Validación léxica: verificar ruta válida
        if not ruta_exportacion or not ruta_exportacion.strip():
            return {
                "error": "Error léxico: La ruta de exportación debe ser una cadena válida",
                "tipo": "LEXICO",
                "comando": "Papapum"
            }
        
        # Validación sintáctica: verificar formato válido
        formatos_validos = ['csv', 'json', 'excel', 'xlsx']
        if formato.lower() not in formatos_validos:
            return {
                "error": f"Error sintáctico: Formato '{formato}' no válido. Use: {', '.join(formatos_validos)}",
                "tipo": "SINTACTICO",
                "comando": "Papapum"
            }
        
        try:
            formato = formato.lower()
            
            # Exportar según el formato
            if formato == 'csv':
                if not ruta_exportacion.endswith('.csv'):
                    ruta_exportacion += '.csv'
                self.archivo_actual.to_csv(ruta_exportacion, index=False)
                
            elif formato == 'json':
                if not ruta_exportacion.endswith('.json'):
                    ruta_exportacion += '.json'
                self.archivo_actual.to_json(ruta_exportacion, orient='records', indent=2)
                
            elif formato in ['excel', 'xlsx']:
                if not ruta_exportacion.endswith('.xlsx'):
                    ruta_exportacion += '.xlsx'
                self.archivo_actual.to_excel(ruta_exportacion, index=False, engine='openpyxl')
            
            return {
                "exito": True,
                "mensaje": f"Papapum: Archivo exportado exitosamente como '{formato.upper()}' en '{os.path.basename(ruta_exportacion)}'",
                "archivo": ruta_exportacion,
                "formato": formato.upper(),
                "filas_exportadas": len(self.archivo_actual)
            }
            
        except ImportError as e:
            return {
                "error": f"Error: Librería faltante para exportar a {formato.upper()}. Instale 'openpyxl' para Excel",
                "tipo": "RUNTIME",
                "detalle": str(e)
            }
        except Exception as e:
            return {
                "error": f"Error al exportar el archivo: {str(e)}",
                "tipo": "RUNTIME",
                "archivo": ruta_exportacion
            }
    
    # Método del Transformer para ejecutar comando magnetoseta
    def magnetoseta(self, items):
        """Método del Transformer - ejecuta comando Magnetoseta"""
        return self._Magnetoseta()
    
    def _Magnetoseta(self) -> Dict[str, Any]:
        """
        Magnetoseta - Obtiene información sobre el archivo actualmente cargado
        
        Returns:
            Dict con información del archivo o None si no hay archivo cargado
        """
        if not self.archivo_cargado or self.archivo_actual is None:
            return {
                "cargado": False,
                "mensaje": "No hay ningún archivo cargado"
            }
        
        return {
            "exito": True,
            "mensaje": "Magnetoseta: Información del archivo actual",
            "cargado": True,
            "archivo": os.path.basename(self.nombre_archivo) if self.nombre_archivo else "Sin nombre",
            "filas": len(self.archivo_actual),
            "columnas": len(self.archivo_actual.columns),
            "columnas_nombres": list(self.archivo_actual.columns),
            "tipos_datos": {k: str(v) for k, v in self.archivo_actual.dtypes.to_dict().items()}
        }
    
    # Método del Transformer para ejecutar comando melonpulta
    def melonpulta(self, items):
        """Método del Transformer - ejecuta comando melonpulta_gelida"""
        return self._melonpulta_gelida()
    
    def _melonpulta_gelida(self) -> Dict[str, Any]:
        """
        melonpulta_gelida - Cierra el archivo actual y limpia el estado
        
        Returns:
            Dict con el resultado de la operación
        """
        if not self.archivo_cargado:
            return {
                "mensaje": "melonpulta_gelida: No hay ningún archivo abierto para cerrar"
            }
        
        archivo_cerrado = self.nombre_archivo
        self.archivo_actual = None
        self.nombre_archivo = None
        self.archivo_cargado = False
        
        return {
            "exito": True,
            "mensaje": f"melonpulta_gelida: Archivo '{os.path.basename(archivo_cerrado) if archivo_cerrado else 'Sin nombre'}' cerrado exitosamente"
        }



# ---------------------------
# FUNCIÓN PRINCIPAL
# ---------------------------
def ejecutar(codigo, gestor_archivos=None):
    """
    Ejecuta un comando del lenguaje PUMA
    
    Args:
        codigo: Comando a ejecutar
        gestor_archivos: Instancia de ManejoArchivos (si es None, se crea una nueva)
    
    Returns:
        Tupla (resultado, gestor) donde resultado es el dict de salida y gestor es la instancia actualizada
    """
    print(f"[EJECUTANDO] {codigo!r}\n")
    
    # Si no se proporciona un gestor, crear uno nuevo
    if gestor_archivos is None:
        gestor_archivos = ManejoArchivos()
    
    try:
        # 1. Análisis Léxico
        tokens = tokenize(codigo)
        
        # 2. Análisis Sintáctico
        tree = parser.parse(codigo)
        print("[OK] Árbol sintáctico:")
        print(tree.pretty())
        print()
        
        # 3. Interpretación/Ejecución
        result = gestor_archivos.transform(tree)
        
        # Mostrar resultado
        print("="*60)
        if result:
            if "error" in result:
                print(f"[ERROR] {result['error']}")
                print(f"  Tipo: {result.get('tipo', 'DESCONOCIDO')}")
            elif "exito" in result:
                print(f"[EXITO] {result.get('mensaje', 'Operación completada')}")
                for key, value in result.items():
                    if key not in ['exito', 'mensaje']:
                        print(f"  {key}: {value}")
            else:
                print(f"[INFO] {result.get('mensaje', result)}")
        print("="*60)
        print()
        
        return result, gestor_archivos
        
    except Exception as e:
        print(f"[ERROR FATAL] {e}")
        print("="*60)
        print()
        return {"error": str(e), "tipo": "FATAL"}, gestor_archivos

# --------------------------
# MODO INTERACTIVO (OPCIONAL)
# ---------------------------
if __name__ == "__main__":
    print("\n[MODO INTERACTIVO] Escribe tus comandos:")
    print("Comandos disponibles:")
    print("  • Sol <ruta.csv>               - Abrir archivo CSV")
    print("  • Carnívora [ruta.csv]         - Guardar archivo")
    print("  • Papapum <ruta> [formato]     - Exportar archivo")
    print("  • Magnetoseta                  - Info del archivo actual")
    print("  • melonpulta_gelida            - Cerrar archivo")
    print("  • salir                        - Terminar")
    print()
    
    # Crear gestor de archivos compartido para mantener estado entre comandos
    gestor = ManejoArchivos()

    while True:
        comando = input("> ").strip()
        if comando.lower() == 'salir':
            print("[INFO] Hasta luego!")
            break
        if comando:
            resultado, gestor = ejecutar(comando, gestor)
