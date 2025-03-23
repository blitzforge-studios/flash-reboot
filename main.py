import os
import sys

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.server import start_server

if __name__ == "__main__":
    start_server()