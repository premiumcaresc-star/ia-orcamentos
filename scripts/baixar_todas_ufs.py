import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.baixar_sinapi import atualizar_todas_uFs

if __name__ == "__main__":
    print("🔄 Iniciando atualização de todas as UFs...")
    resultados = atualizar_todas_uFs()
    
    print("\n✅ Processo concluído!")
