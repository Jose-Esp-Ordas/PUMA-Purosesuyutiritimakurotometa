"""
PUMA - Purosesuyutiritimakurotometa
Módulo de Manejo de Archivos

Este módulo implementa las palabras reservadas para operaciones de archivos CSV:
- Sol: Abrir archivo
- Carnívora: Guardar archivo
- Papapum: Exportar archivo
"""

import pandas as pd
import re
import os
from typing import Optional, Dict, Any


class ManejoArchivos:
    """Clase para gestionar las operaciones de archivos CSV del lenguaje PUMA"""
    
    def __init__(self):
        """Inicializa el gestor de archivos"""
        self.archivo_actual: Optional[pd.DataFrame] = None
        self.nombre_archivo: Optional[str] = None
        self.archivo_cargado: bool = False
        
    def sol(self, ruta_archivo: str) -> Dict[str, Any]:
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
        # Validación léxica: verificar que sea una ruta válida
        if not isinstance(ruta_archivo, str) or not ruta_archivo.strip():
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
                "mensaje": f"Sol: Archivo '{os.path.basename(ruta_archivo)}' abierto exitosamente",
                "filas": len(self.archivo_actual),
                "columnas": len(self.archivo_actual.columns),
                "columnas_nombres": list(self.archivo_actual.columns)
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
    
    def carnivora(self, ruta_archivo: Optional[str] = None) -> Dict[str, Any]:
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
    
    def papapum(self, ruta_exportacion: str, formato: str = 'csv') -> Dict[str, Any]:
        """
        Papapum - Comando para exportar el archivo en diferentes formatos
        
        Args:
            ruta_exportacion: Ruta donde exportar el archivo
            formato: Formato de exportación ('csv', 'json', 'excel')
            
        Returns:
            Dict con el resultado de la operación
        """
        # Validación semántica: verificar que hay un archivo cargado
        if not self.archivo_cargado or self.archivo_actual is None:
            return {
                "error": "Error semántico: No hay ningún archivo cargado. Use 'Sol' primero para abrir un archivo",
                "tipo": "SEMANTICO",
                "comando": "Papapum"
            }
        
        # Validación léxica: verificar ruta válida
        if not isinstance(ruta_exportacion, str) or not ruta_exportacion.strip():
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
    
    def Magnetoseta(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el archivo actualmente cargado
        
        Returns:
            Dict con información del archivo o None si no hay archivo cargado
        """
        if not self.archivo_cargado or self.archivo_actual is None:
            return {
                "cargado": False,
                "mensaje": "No hay ningún archivo cargado"
            }
        
        return {
            "cargado": True,
            "archivo": self.nombre_archivo,
            "filas": len(self.archivo_actual),
            "columnas": len(self.archivo_actual.columns),
            "columnas_nombres": list(self.archivo_actual.columns),
            "tipos_datos": self.archivo_actual.dtypes.to_dict()
        }
    
    def melonpulta_gelida(self) -> Dict[str, Any]:
        """
        Cierra el archivo actual y limpia el estado
        
        Returns:
            Dict con el resultado de la operación
        """
        if not self.archivo_cargado:
            return {
                "mensaje": "No hay ningún archivo abierto para cerrar"
            }
        
        archivo_cerrado = self.nombre_archivo
        self.archivo_actual = None
        self.nombre_archivo = None
        self.archivo_cargado = False
        
        return {
            "exito": True,
            "mensaje": f"Archivo '{os.path.basename(archivo_cerrado)}' cerrado exitosamente"
        }


# Ejemplo de uso y pruebas
if __name__ == "__main__":
    print("=" * 60)
    print("PUMA - Sistema de Manejo de Archivos")
    print("Comandos: Sol (Abrir) | Carnívora (Guardar) | Papapum (Exportar)")
    print("=" * 60)
    
    # Crear instancia del manejador
    gestor = ManejoArchivos()
    
    # Ejemplo 1: Intentar guardar sin archivo cargado (ERROR SEMÁNTICO)
    print("\n[TEST 1] Intentar guardar sin abrir archivo:")
    resultado = gestor.carnivora("test.csv")
    print(resultado)
    
    # Ejemplo 2: Intentar abrir archivo con extensión incorrecta (ERROR SINTÁCTICO)
    print("\n[TEST 2] Intentar abrir archivo sin extensión .csv:")
    resultado = gestor.sol("archivo.txt")
    print(resultado)
    
    # Ejemplo 3: Intentar abrir archivo inexistente (ERROR SEMÁNTICO)
    print("\n[TEST 3] Intentar abrir archivo que no existe:")
    resultado = gestor.sol("noexiste.csv")
    print(resultado)
    
    print("\n" + "=" * 60)
    print("Pruebas de manejo de errores completadas")
    print("=" * 60)
