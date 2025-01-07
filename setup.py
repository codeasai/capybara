import subprocess
import sys
import os

def install_python_dependencies():
    """ติดตั้ง Python dependencies จาก requirements.txt"""
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def install_nextjs_dependencies():
    """ติดตั้ง Next.js dependencies"""
    if not os.path.exists('src/node_modules'):
        print("Installing Next.js dependencies...")
        current_dir = os.getcwd()
        os.chdir('src')
        try:
            # ตรวจสอบว่ามี npm หรือไม่
            subprocess.run(['npm', '--version'], capture_output=True, check=True)
            # ติดตั้ง dependencies
            subprocess.run(['npm', 'install'], check=True)
        except subprocess.CalledProcessError:
            print("Error: npm not found. Please install Node.js and npm first.")
            sys.exit(1)
        finally:
            os.chdir(current_dir)
    else:
        print("Next.js dependencies already installed")

def setup_project():
    """ตั้งค่าโปรเจคทั้งหมด"""
    # สร้างโฟลเดอร์ที่จำเป็น
    os.makedirs('src/uploads', exist_ok=True)
    os.makedirs('server/services', exist_ok=True)

    # สร้างไฟล์ __init__.py ถ้ายังไม่มี
    init_files = [
        'server/__init__.py',
        'server/services/__init__.py'
    ]
    for init_file in init_files:
        if not os.path.exists(init_file):
            open(init_file, 'a').close()

def main():
    print("Setting up PDF Processing Project...")
    
    # ตั้งค่าโปรเจค
    setup_project()
    
    # ติดตั้ง dependencies
    print("\nInstalling Python dependencies...")
    install_python_dependencies()
    
    print("\nChecking Next.js dependencies...")
    install_nextjs_dependencies()
    
    print("\nSetup completed successfully!")
    print("\nYou can now run the application with:")
    print("python run.py")

if __name__ == "__main__":
    main() 