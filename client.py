import socket
import threading
from bb84 import generate_symmetric_key, encrypt_message, decrypt_message
import numpy as np

def receive_messages(client_socket, fernet):
    while True:
        try:
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                raise Exception("No data received from server")
            
            message = decrypt_message(fernet, encrypted_message)
            print(message)
        except Exception as e:
            print(f"Error receiving message: {e}")
            client_socket.close()
            break

def send_messages(client_socket, fernet):
    while True:
        try:
            message = input('')  # Prompt for message input
            encrypted_message = encrypt_message(fernet, message)
            client_socket.send(encrypted_message)
        except Exception as e:
            print(f"Error sending message: {e}")
            client_socket.close()
            break

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5555))
    
    try:
        # Prompt user to enter custom name
        client_name = input("Enter your name: ")
        client_socket.send(client_name.encode('utf-8'))
        
        # Receive response from server
        response = client_socket.recv(1024).decode('utf-8')
        if response.startswith("Error"):
            raise Exception(response)
        
        # Receive BB84 information from server
        bb84_info = client_socket.recv(1024).decode('utf-8')
        bb84_data = bb84_info.split('|')
        
        if len(bb84_data) != 3:
            raise Exception("Invalid BB84 information received")
        
        alice_bits_str, alice_bases_str, bob_bases_str = bb84_data
        
        alice_bits = np.array(eval(alice_bits_str))
        alice_bases = np.array(eval(alice_bases_str))
        bob_bases = np.array(eval(bob_bases_str))
        
        # Derive shared key
        bob_measurements = []
        for i in range(len(alice_bits)):
            if alice_bases[i] == bob_bases[i]:
                bob_measurements.append(alice_bits[i])
            else:
                bob_measurements.append(np.random.randint(2))
        
        matching_bases_indices = [i for i in range(len(alice_bits)) if alice_bases[i] == bob_bases[i]]
        shared_key = ''.join(map(str, [alice_bits[i] for i in matching_bases_indices]))
        
        fernet = generate_symmetric_key(shared_key)
        print(f"Shared key: {shared_key}")
        
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket, fernet))
        receive_thread.start()
        
        send_thread = threading.Thread(target=send_messages, args=(client_socket, fernet))
        send_thread.start()
    
    except Exception as e:
        print(f"Error starting client: {e}")
        client_socket.close()

if __name__ == "__main__":
    start_client()
