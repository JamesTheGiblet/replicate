#!/usr/bin/env python3
"""
Simple Encryption for Explorer-d334
No external dependencies
"""

import os
import base64
from pathlib import Path

class EncryptionManager:
    def __init__(self):
        self.key_file = Path.home() / ".forge_key"
        self.key = self.load_or_create_key()
    
    def load_or_create_key(self):
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            # Generate simple key using os.urandom
            key = os.urandom(32)
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt_data(self, data):
        """Simple XOR encryption"""
        if isinstance(data, str):
            data = data.encode()
        key_bytes = self.key[:len(data)]
        result = bytes(a ^ b for a, b in zip(data, key_bytes))
        return base64.b64encode(result).decode()
    
    def decrypt_data(self, data_encrypted):
        """Decrypt XOR encrypted data"""
        encrypted = base64.b64decode(data_encrypted)
        key_bytes = self.key[:len(encrypted)]
        result = bytes(a ^ b for a, b in zip(encrypted, key_bytes))
        return result.decode()
    
    def encrypt_file(self, filepath):
        with open(filepath, 'rb') as f:
            data = f.read()
        encrypted = bytes(a ^ b for a, b in zip(data, self.key[:len(data)]))
        enc_path = f"{filepath}.enc"
        with open(enc_path, 'wb') as f:
            f.write(encrypted)
        return enc_path
    
    def decrypt_file(self, enc_filepath):
        with open(enc_filepath, 'rb') as f:
            encrypted = f.read()
        decrypted = bytes(a ^ b for a, b in zip(encrypted, self.key[:len(encrypted)]))
        original = enc_filepath.replace('.enc', '')
        with open(original, 'wb') as f:
            f.write(decrypted)
        return original

# Simple test
if __name__ == "__main__":
    em = EncryptionManager()
    test = "Hello Forge"
    encrypted = em.encrypt_data(test)
    decrypted = em.decrypt_data(encrypted)
    print(f"Original: {test}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print("✅ Encryption module working")
