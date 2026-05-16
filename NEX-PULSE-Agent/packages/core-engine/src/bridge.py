import ctypes
import json
import os
import platform

class NativeScannerBridge:
    def __init__(self):
        # Determinar la extensión de la librería según el SO
        system = platform.system()
        if system == "Windows":
            lib_name = "native_scanner.dll"
        elif system == "Darwin":
            lib_name = "libnative_scanner.dylib"
        else:
            lib_name = "libnative_scanner.so"
            
        # Ruta simulada asumiendo que se compila en la raíz de native-scanner/target/release
        # En producción esto se copiaría al lado del core-engine
        base_dir = os.path.dirname(__file__)
        self.lib_path = os.path.abspath(os.path.join(base_dir, "..", "..", "native-scanner", "target", "release", lib_name))
        
        self.scanner = None
        self._load_library()

    def _load_library(self):
        try:
            self.scanner = ctypes.CDLL(self.lib_path)
            
            # Definir firmas de funciones
            self.scanner.scan_mft_for_junk.argtypes = [ctypes.c_char_p]
            self.scanner.scan_mft_for_junk.restype = ctypes.c_void_p

            self.scanner.free_string.argtypes = [ctypes.c_void_p]
        except Exception as e:
            print(f"Advertencia: No se pudo cargar el escáner nativo en {self.lib_path}.")
            print(f"Error: {e}")
            print("Asegúrate de compilar el módulo de Rust primero con 'cargo build --release'.")

    def run_deep_scan(self, drive="C:"):
        if not self.scanner:
            return {"error": "Librería nativa no cargada. Fallback a Python scan."}

        drive_bytes = drive.encode('utf-8')
        ptr = self.scanner.scan_mft_for_junk(drive_bytes)
        
        # Leer el string de C
        result_str = ctypes.cast(ptr, ctypes.c_char_p).value.decode('utf-8')
        
        # Liberar la memoria
        self.scanner.free_string(ptr)
        
        return json.loads(result_str)

if __name__ == "__main__":
    bridge = NativeScannerBridge()
    print("Probando bridge...")
    res = bridge.run_deep_scan("C:")
    print("Resultado:", res)
