#!/usr/bin/env python3
"""
Script para inicializar o servidor RecifeMais Conteúdo
"""
import sys
import os
import uvicorn

# Adicionar o diretório backend ao PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("🚀 Iniciando RecifeMais Conteúdo Server...")
    print(f"📁 Diretório: {current_dir}")
    
    # Configurar e iniciar o servidor
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    ) 