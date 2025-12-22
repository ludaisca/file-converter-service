from abc import ABC, abstractmethod
import subprocess
from ..config import Config

class BaseConverter(ABC):
    @abstractmethod
    def convert(self, input_path: str, output_path: str, from_ext: str, to_ext: str) -> dict:
        pass

    def run_command(self, command: list):
        try:
            subprocess.run(command, check=True)
            return {'success': True}
        except subprocess.CalledProcessError as e:
            return {'success': False, 'error': f'Conversion failed: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
