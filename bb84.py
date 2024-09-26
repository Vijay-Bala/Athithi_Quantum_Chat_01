import numpy as np
from cryptography.fernet import Fernet
import base64
import hashlib

def bb84_key_exchange(length=10):
    alice_bits = np.random.randint(2, size=length)
    alice_bases = np.random.choice(['+', 'x'], size=length)
    bob_bases = np.random.choice(['+', 'x'], size=length)
    bob_measurements = []

    for i in range(length):
        if alice_bases[i] == bob_bases[i]:
            bob_measurements.append(alice_bits[i])
        else:
            bob_measurements.append(np.random.randint(2))

    matching_bases_indices = [i for i in range(length) if alice_bases[i] == bob_bases[i]]
    key = [alice_bits[i] for i in matching_bases_indices]
    return alice_bits, alice_bases, bob_bases, bob_measurements, key

def generate_symmetric_key(shared_key):
    key_str = ''.join(map(str, shared_key))
    key_bytes = key_str.encode('utf-8')
    hash_digest = hashlib.sha256(key_bytes).digest()  # Ensure the key is 32 bytes
    symmetric_key = base64.urlsafe_b64encode(hash_digest)  # Encode it to be url-safe
    return Fernet(symmetric_key)

def encrypt_message(fernet, message):
    return fernet.encrypt(message.encode('utf-8'))

def decrypt_message(fernet, encrypted_message):
    return fernet.decrypt(encrypted_message).decode('utf-8')
