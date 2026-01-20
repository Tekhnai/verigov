import sys
import os
import json
import logging

# Add the current directory to sys.path so we can import 'app'
sys.path.append(os.getcwd())

from app.connectors.receita import fetch_cnpj

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)

try:
    print("Iniciando consulta para CNPJ 45997418000153...")
    # Call the function directly
    result = fetch_cnpj("45997418000153")
    
    print("\n--- SUCESSO ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print("\n--- ERRO ---")
    print(str(e))
    # Print traceback for details
    import traceback
    traceback.print_exc()
