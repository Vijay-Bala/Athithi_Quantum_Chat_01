import socket
import threading
from bb84 import bb84_key_exchange, generate_symmetric_key, decrypt_message, encrypt_message
import numpy as np

clients = {}
keys = {}

def handle_client(client_socket, addr):
    try:
        # Prompt client for custom name
        client_socket.send("Enter your name: ".encode('utf-8'))
        client_name = client_socket.recv(1024).decode('utf-8').strip()
        
        # Generate shared key information using BB84
        alice_bits, alice_bases, bob_bases, _, shared_key = bb84_key_exchange()
        fernet = generate_symmetric_key(shared_key)
        keys[client_name] = fernet
        print(f"Shared key for {addr} ({client_name}): {shared_key}")
        
        # Prepare BB84 information to send to client
        bb84_info = f"{alice_bits.tolist()}|{alice_bases.tolist()}|{bob_bases.tolist()}"
        client_socket.send(bb84_info.encode('utf-8'))
        
        clients[client_name] = client_socket
        
        while True:
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                print(f"No data received from {client_name}")
                break
            
            message = decrypt_message(fernet, encrypted_message)
            print(f"Received message from {client_name}: {message}")
            broadcast(f"{client_name}: {message}", client_name)
            
    except Exception as e:
        print(f"Error handling client {client_name}: {e}")
        del clients[client_name]
        client_socket.close()

def broadcast(message, sender):
    for client_name, client_socket in clients.items():
        if client_name != sender:
            try:
                fernet = keys[client_name]
                encrypted_message = encrypt_message(fernet, message)
                client_socket.send(encrypted_message)
            except Exception as e:
                print(f"Error broadcasting message to {client_name}: {e}")
                client_socket.close()
                del clients[client_name]

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5555))
    server.listen(5)
    print("Server started... Waiting for connections...")
    
    while True:
        try:
            client_socket, addr = server.accept()
            print(f"Connection from {addr}")
            
            threading.Thread(target=handle_client, args=(client_socket, addr)).start()
        
        except KeyboardInterrupt:
            print("\nServer shutting down.")
            break
        except Exception as e:
            print(f"Error accepting connection: {e}")

    server.close()

if __name__ == "__main__":
    start_server()
