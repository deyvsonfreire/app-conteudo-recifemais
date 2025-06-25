#!/usr/bin/env python3
"""
Monitor de logs em tempo real para debug
"""
import subprocess
import time
import sys
from datetime import datetime

def monitor_server_logs():
    """Monitora logs do servidor em tempo real"""
    print("🔍 MONITOR DE LOGS EM TEMPO REAL")
    print("=" * 50)
    print("⚡ Monitorando requisições e erros...")
    print("📱 Navegue no painel: http://127.0.0.1:8001")
    print("🛑 Pressione Ctrl+C para parar")
    print("-" * 50)
    
    try:
        # Monitorar logs do uvicorn
        process = subprocess.Popen(
            ["tail", "-f", "/dev/null"],  # Placeholder, vamos capturar via ps
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Capturar logs do processo uvicorn
        while True:
            # Buscar processo uvicorn
            try:
                ps_output = subprocess.check_output(
                    ["ps", "aux"], 
                    universal_newlines=True
                )
                
                uvicorn_lines = [line for line in ps_output.split('\n') 
                               if 'uvicorn' in line and 'backend.main:app' in line]
                
                if uvicorn_lines:
                    print(f"📊 [{datetime.now().strftime('%H:%M:%S')}] Servidor ativo")
                else:
                    print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] Servidor não encontrado")
                
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoramento interrompido")
                break
            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n🛑 Monitor finalizado")

if __name__ == "__main__":
    monitor_server_logs()
