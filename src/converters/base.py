"""
Clase base para todos los conversores
"""
from abc import ABC, abstractmethod
import subprocess
import resource
from ..config import Config


class TimeoutException(Exception):
    """Excepción cuando una conversión excede el timeout"""
    pass


class BaseConverter(ABC):
    """Clase base abstracta para conversores"""
    
    # Timeout por defecto en segundos (5 minutos)
    DEFAULT_TIMEOUT = 300
    
    @abstractmethod
    def convert(self, input_path: str, output_path: str, from_ext: str, to_ext: str) -> dict:
        """
        Convierte un archivo de un formato a otro
        
        Args:
            input_path: Ruta del archivo de entrada
            output_path: Ruta del archivo de salida
            from_ext: Extensión del archivo de entrada
            to_ext: Extensión del archivo de salida
            
        Returns:
            dict: Resultado de la conversión con 'success' y 'error' (si aplica)
        """
        pass

    def _set_resource_limits(self):
        """
        Sets resource limits for the subprocess (CPU, Memory).
        """
        # Limit CPU time (soft, hard) in seconds - maybe 5 mins cpu time
        # This is CPU time, not wall clock time.
        resource.setrlimit(resource.RLIMIT_CPU, (300, 300))

        # Limit Memory (AS - Address Space) - e.g. 2GB
        # 2 * 1024 * 1024 * 1024 bytes
        mem_limit = 2 * 1024 * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem_limit, mem_limit))
    
    def run_command(self, command: list, timeout_seconds: int = None) -> dict:
        """
        Ejecuta un comando con timeout y límites de recursos
        
        Args:
            command: Lista con el comando y argumentos
            timeout_seconds: Timeout en segundos (None usa DEFAULT_TIMEOUT)
            
        Returns:
            dict: Resultado con 'success', 'stdout', 'stderr', 'error'
        """
        if timeout_seconds is None:
            timeout_seconds = self.DEFAULT_TIMEOUT
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=True,
                preexec_fn=self._set_resource_limits
            )
            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {timeout_seconds} seconds: {' '.join(command)}"
            return {
                'success': False,
                'error': error_msg,
                'timeout': True
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': f'Conversion failed: {e.stderr or str(e)}',
                'returncode': e.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
