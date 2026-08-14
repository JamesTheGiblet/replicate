#!/usr/bin/env python3
import socket

def is_port_free(port=8085):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        sock.close()
        return True
    except:
        return False

if __name__ == "__main__":
    if is_port_free():
        print("✅ Port 8085 is free")
    else:
        print("⚠️ Port 8085 in use, but can be freed")
