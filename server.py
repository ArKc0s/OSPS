import os

def send_command(shared_mem, pipe, command, ping):
    shared_mem.seek(0)
    shared_mem.write((command + '\x00' * (100 - len(command))).encode('utf-8'))
    os.write(pipe, b"ping" if ping else b"pong")

def read_command(shared_mem):
    shared_mem.seek(0)
    return shared_mem.read(100).decode('utf-8').rstrip('\x00')