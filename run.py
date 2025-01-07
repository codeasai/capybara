import uvicorn
import subprocess
import sys
import os
import socket
import requests
import time
from typing import Tuple
from pathlib import Path
from threading import Thread

def is_port_in_use(port: int) -> bool:
    """ตรวจสอบว่า port กำลังถูกใช้งานอยู่หรือไม่"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def check_servers() -> Tuple[bool, bool]:
    """ตรวจสอบว่า FastAPI และ Next.js กำลังทำงานอยู่หรือไม่"""
    fastapi_running = False
    nextjs_running = False
    
    if is_port_in_use(8000):
        try:
            response = requests.get('http://127.0.0.1:8000/api/health')
            fastapi_running = response.status_code == 200
        except:
            pass
    
    if is_port_in_use(3000):
        try:
            response = requests.get('http://localhost:3000')
            nextjs_running = response.status_code == 200
        except:
            pass
            
    return fastapi_running, nextjs_running

def kill_process_on_port(port: int):
    """ฆ่า process ที่ใช้ port ที่ระบุ"""
    if sys.platform == 'win32':
        try:
            # ใช้ findstr เพื่อหา PID ที่ใช้ port นั้น
            cmd = f'for /f "tokens=5" %a in (\'netstat -aon ^| findstr :{port} ^| findstr LISTENING\') do @echo %a'
            result = subprocess.check_output(cmd, shell=True).decode().strip()
            
            if result and result != "0":
                # ฆ่า process ด้วย PID ที่ได้
                subprocess.run(f'taskkill /F /PID {result}', shell=True)
                time.sleep(1)  # รอให้ process ถูกฆ่า
        except subprocess.CalledProcessError:
            pass  # ไม่มี process ที่ใช้ port นี้
    else:
        try:
            subprocess.run(f'lsof -ti:{port} | xargs kill -9', shell=True)
        except:
            pass

def run_nextjs():
    """รัน Next.js development server"""
    src_path = Path('src').absolute()
    if not src_path.exists():
        print(f"Error: Could not find Next.js project at {src_path}")
        sys.exit(1)
        
    os.chdir(src_path)
    
    # ใช้ start cmd เพื่อเปิด terminal ใหม่สำหรับ Next.js
    if sys.platform == 'win32':
        subprocess.Popen('start cmd /k "npm run dev"', shell=True)
    else:
        subprocess.Popen('npm run dev', shell=True)

def run_fastapi():
    """รัน FastAPI server"""
    root_dir = Path(__file__).parent.absolute()
    os.chdir(root_dir)  # กลับไปที่ root directory
    
    if sys.platform == 'win32':
        # รัน FastAPI ใน terminal ใหม่
        cmd = 'start cmd /k "uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload"'
        subprocess.Popen(cmd, shell=True)
    else:
        # สำหรับ Unix-like systems
        subprocess.Popen('uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload', shell=True)

def wait_for_servers():
    """รอจนกว่า servers จะพร้อมใช้งาน"""
    print("Waiting for servers to start...")
    max_attempts = 30
    interval = 1

    for _ in range(max_attempts):
        fastapi_ready = False
        nextjs_ready = False

        try:
            # ตรวจสอบ FastAPI
            response = requests.get('http://127.0.0.1:8000/api/health')
            if response.status_code == 200:
                fastapi_ready = True
                print("FastAPI server is ready!")

            # ตรวจสอบ Next.js
            response = requests.get('http://localhost:3000')
            if response.status_code == 200:
                nextjs_ready = True
                print("Next.js server is ready!")

        except:
            pass

        if fastapi_ready and nextjs_ready:
            print("All servers are running!")
            return True

        time.sleep(interval)

    print("Timeout waiting for servers to start")
    return False

if __name__ == "__main__":
    try:
        # ตรวจสอบโครงสร้างโปรเจค
        root_dir = Path(__file__).parent.absolute()
        required_paths = [
            root_dir / 'src',
            root_dir / 'server',
            root_dir / 'server' / 'services',
        ]
        
        for path in required_paths:
            if not path.exists():
                print(f"Error: Required directory not found: {path}")
                sys.exit(1)
                
        # ตรวจสอบว่า servers กำลังทำงานอยู่หรือไม่
        fastapi_running, nextjs_running = check_servers()
        
        if fastapi_running or nextjs_running:
            print("Detected running servers. Stopping them...")
            if fastapi_running:
                kill_process_on_port(8000)
            if nextjs_running:
                kill_process_on_port(3000)
            time.sleep(2)  # รอให้ port ว่าง

        print("Starting servers...")
        print("FastAPI will run on http://127.0.0.1:8000")
        print("Next.js will run on http://localhost:3000")

        # รัน Next.js
        run_nextjs()
        
        # รัน FastAPI
        run_fastapi()

        # รอให้ servers พร้อมใช้งาน
        if not wait_for_servers():
            print("Failed to start servers")
            kill_process_on_port(8000)
            kill_process_on_port(3000)
            sys.exit(1)

        print("\nServers are running!")
        print("Press Ctrl+C to stop all servers")

        # รอจนกว่าจะกด Ctrl+C
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down servers...")
        kill_process_on_port(8000)
        kill_process_on_port(3000)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        kill_process_on_port(8000)
        kill_process_on_port(3000)
        sys.exit(1) 