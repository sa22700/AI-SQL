import psycopg2
import subprocess

def connect():
    return psycopg2.connect(
        host='192.168.68.109',
        user='admin',
        password='admin123',
        port='5432',
        database='postgres'
    )

def cuda_available():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total', '--format=csv,nounits,noheader'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        vram_mb = int(result.stdout.strip().split('\n')[0])
        return vram_mb / 1024
    except Exception as e:
        print(f"VRAM-check failed: {e}")
        return 0

def estimate_n_gpu_layers(vram_gb):
    if vram_gb <= 4:
        return 5
    elif vram_gb <= 6:
        return 10
    elif vram_gb <= 8:
        return 15
    elif vram_gb <= 10:
        return 20
    elif vram_gb <= 12:
        return 30
    else:
        return 35