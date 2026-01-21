import os
import shutil
import psycopg2
import subprocess

def connect():
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'],
        port=os.environ['DB_PORT'],
        database=os.environ['DB_NAME']
    )

def cuda_available():
    try:
        nvidia_smi = shutil.which("nvidia-smi")
        if not nvidia_smi:
            return 0
        result = subprocess.run(
            [nvidia_smi, "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        vram_mb = int(result.stdout.strip().split('\n')[0])
        return vram_mb / 1024

    except Exception as e:
        print(f"VRAM-check failed: {e}")
        return 0

def estimate_n_gpu_layers(vram_gb):
    if vram_gb <= 0:
        return 0
    elif vram_gb <= 4:
        return 5
    elif vram_gb <= 6:
        return 10
    elif vram_gb <= 8:
        return 15
    elif vram_gb <= 10:
        return 20
    elif vram_gb <= 12:
        return 30
    return 35