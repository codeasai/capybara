import subprocess
import sys
import os
import torch
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

def load_default_config() -> Dict[str, str]:
    """กำหนดค่า default config"""
    return {
        "DEVICE": "auto",
        "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
        "VECTOR_DB": "chroma",
        "VECTOR_DB_PATH": "db",
        "FASTAPI_HOST": "127.0.0.1",
        "FASTAPI_PORT": "8000",
        "NEXTJS_PORT": "3000",
        "MAX_FILE_SIZE": "104857600",
        "CHUNK_SIZE": "1000"
    }

def create_env_file():
    """สร้างหรืออัพเดทไฟล์ .env"""
    env_path = Path('.env')
    default_config = load_default_config()
    
    if env_path.exists():
        print("Loading existing .env file...")
        load_dotenv()
        # ตรวจสอบและเพิ่มค่าที่หายไป
        with open(env_path, 'a') as f:
            for key, value in default_config.items():
                if not os.getenv(key):
                    f.write(f"\n{key}={value}")
    else:
        print("Creating new .env file...")
        with open(env_path, 'w') as f:
            for key, value in default_config.items():
                f.write(f"{key}={value}\n")

def validate_config():
    """ตรวจสอบความถูกต้องของค่า config"""
    valid_models = ['all-MiniLM-L6-v2', 'all-mpnet-base-v2', 'multi-qa-mpnet-base-dot-v1']
    valid_dbs = ['chroma', 'qdrant', 'faiss']
    
    device = os.getenv('DEVICE')
    if device not in ['auto', 'cuda', 'cpu']:
        print(f"Warning: Invalid DEVICE value: {device}. Using 'auto'")
        os.environ['DEVICE'] = 'auto'
    
    model = os.getenv('EMBEDDING_MODEL')
    if model not in valid_models:
        print(f"Warning: Invalid EMBEDDING_MODEL: {model}. Using default")
        os.environ['EMBEDDING_MODEL'] = 'all-MiniLM-L6-v2'
    
    db = os.getenv('VECTOR_DB')
    if db not in valid_dbs:
        print(f"Warning: Invalid VECTOR_DB: {db}. Using 'chroma'")
        os.environ['VECTOR_DB'] = 'chroma'

def install_python_dependencies():
    """ติดตั้ง Python dependencies"""
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def install_nextjs_dependencies():
    """ติดตั้ง Next.js dependencies"""
    src_path = Path('src')
    if not (src_path / 'node_modules').exists():
        print("Installing Next.js dependencies...")
        os.chdir(src_path)
        try:
            subprocess.run(['npm', '--version'], capture_output=True, check=True)
            subprocess.run(['npm', 'install'], check=True)
        except subprocess.CalledProcessError:
            print("Error: npm not found. Please install Node.js and npm first.")
            sys.exit(1)
        finally:
            os.chdir('..')
    else:
        print("Next.js dependencies already installed")

def setup_project_structure():
    """สร้างโครงสร้างโปรเจค"""
    directories = [
        'src/uploads',
        'server/services',
        os.getenv('VECTOR_DB_PATH')
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # สร้าง __init__.py files
    init_files = [
        'server/__init__.py',
        'server/services/__init__.py'
    ]
    for init_file in init_files:
        Path(init_file).touch()

def print_config():
    """แสดงค่า configuration ทั้งหมด"""
    print("\n=== Current Configuration ===")
    print(f"Device: {os.getenv('DEVICE')}")
    print(f"Embedding Model: {os.getenv('EMBEDDING_MODEL')}")
    print(f"Vector Database: {os.getenv('VECTOR_DB')}")
    print(f"Vector DB Path: {os.getenv('VECTOR_DB_PATH')}")
    if os.getenv('DEVICE') in ['auto', 'cuda']:
        print(f"CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA Device: {torch.cuda.get_device_name(0)}")
    print("==========================\n")

def main():
    print("Setting up Elliott Wave Pattern Analysis System...")
    
    # สร้างและตรวจสอบ config
    create_env_file()
    load_dotenv()
    validate_config()
    
    # ติดตั้ง dependencies
    print("\nInstalling dependencies...")
    install_python_dependencies()
    install_nextjs_dependencies()
    
    # สร้างโครงสร้างโปรเจค
    print("\nSetting up project structure...")
    setup_project_structure()
    
    # แสดงค่า config
    print_config()
    
    print("\nSetup completed successfully!")
    print("You can now run the application with: python run.py")

if __name__ == "__main__":
    main() 