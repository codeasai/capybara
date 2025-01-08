import os
import shutil
from pathlib import Path
import subprocess
import sys

def clean_environment():
    """ล้าง virtual environments ทั้งหมด"""
    print("Cleaning virtual environments...")
    
    # ลบ venv directories
    venv_dirs = ['venv', '.venv']
    for venv in venv_dirs:
        if os.path.exists(venv):
            print(f"Removing {venv}...")
            shutil.rmtree(venv)

def clean_cache():
    """ล้าง cache files"""
    print("Cleaning cache files...")
    
    # ลบ Python cache
    for root, dirs, files in os.walk('.'):
        # ข้าม node_modules
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
            
        # ลบ __pycache__ directories
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            print(f"Removing {pycache_path}")
            shutil.rmtree(pycache_path)
            dirs.remove('__pycache__')
            
        # ลบ .pyc files
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                print(f"Removing {pyc_path}")
                os.remove(pyc_path)

def clean_database():
    """ล้าง vector database"""
    print("Cleaning vector database...")
    db_path = os.getenv('VECTOR_DB_PATH', 'db')
    if os.path.exists(db_path):
        print(f"Removing {db_path}...")
        shutil.rmtree(db_path)

def clean_uploads():
    """ล้างไฟล์ที่อัพโหลด"""
    print("Cleaning uploaded files...")
    uploads_dir = 'src/uploads'
    if os.path.exists(uploads_dir):
        for file in os.listdir(uploads_dir):
            if file != '.gitkeep':  # เก็บ .gitkeep ไว้
                file_path = os.path.join(uploads_dir, file)
                print(f"Removing {file_path}")
                os.remove(file_path)

def clean_env_file():
    """ลบไฟล์ .env"""
    print("Removing .env file...")
    if os.path.exists('.env'):
        os.remove('.env')

def setup_new_environment():
    """สร้าง virtual environment ใหม่"""
    print("\nSetting up new virtual environment...")
    
    # สร้าง venv ใหม่
    subprocess.run([sys.executable, '-m', 'venv', 'venv'])
    
    # activate venv
    if sys.platform == 'win32':
        activate_script = os.path.join('venv', 'Scripts', 'activate.bat')
        activate_cmd = f'call {activate_script}'
    else:
        activate_script = os.path.join('venv', 'bin', 'activate')
        activate_cmd = f'source {activate_script}'
    
    # รัน setup.py
    setup_cmd = f'{activate_cmd} && python setup.py'
    
    if sys.platform == 'win32':
        subprocess.run(setup_cmd, shell=True)
    else:
        subprocess.run(['bash', '-c', setup_cmd])

def main():
    try:
        # ถามยืนยันก่อนล้างระบบ
        response = input("This will remove all virtual environments, cache, and uploaded files. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return
        
        # ล้างระบบทั้งหมด
        clean_environment()
        clean_cache()
        clean_database()
        clean_uploads()
        clean_env_file()
        
        print("\nAll cleaned successfully!")
        
        # ถามว่าต้องการติดตั้งใหม่หรือไม่
        response = input("\nDo you want to setup a new environment? (y/N): ")
        if response.lower() == 'y':
            setup_new_environment()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 