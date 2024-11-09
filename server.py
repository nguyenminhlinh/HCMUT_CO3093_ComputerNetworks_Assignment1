import logging
import socket
import threading
import json
import psycopg2
import sys
import os
import time
import subprocess

# Global active_connections dictionary
active_connections = {}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(dbname="", user="postgres", password="12345678", host="", port="5432")
cur = conn.cursor()

# Function to log events
def log_event(message):
    logging.info(message)

# Function to update client info in the database
def update_client_info(peers_ip, peers_port, peers_hostname, file_name, file_size, piece_hash, piece_size, num_order_in_file):
    for i in range(len(num_order_in_file)):
        cur.execute(
            "INSERT INTO peers (peers_ip, peers_port, peers_hostname, file_name, file_size, piece_hash, piece_size, num_order_in_file) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (peers_ip, peers_port, peers_hostname, file_name, file_size, piece_hash[i], piece_size, num_order_in_file[i])
        )
    conn.commit()

# Ping Host Function
def ping_host(peers_hostname):
    try:
        # Query the database for the IP address of the given peers_hostname
        cur.execute("SELECT address FROM client_files WHERE hostname = %s", (peers_hostname,))
        result = cur.fetchone()

        if result:
            ip_address = result[0]
            # Try to establish a socket connection to the peer (use a predefined port, e.g., 65433)
            peer_port = 65433
            peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_sock.settimeout(5)  # Set a timeout for the connection attempt
            
            try:
                # Attempt to connect to the peer
                peer_sock.connect((ip_address, peer_port))
                peer_sock.sendall(b'ping')  # Optionally, send a "ping" message to the peer
                response = peer_sock.recv(4096).decode()  # Wait for response from peer
                
                # If we receive any response, assume the peer is online
                if response:
                    print(f"{peers_hostname} ({ip_address}) is online!")
                else:
                    print(f"{peers_hostname} is offline (no response).")
            except socket.timeout:
                print(f"{peers_hostname} ({ip_address}) is offline (timeout).")
            except socket.error as e:
                print(f"Error connecting to {peers_hostname} ({ip_address}): {e}")
            finally:
                peer_sock.close()
        else:
            print(f"Hostname {peers_hostname} not found in the database.")
    except Exception as e:
        print(f"An error occurred while pinging {peers_hostname}: {e}")

# Discover Files Function
def discover_files(file_name):
    try:
        # Query the database to find all peers that have the specified file_name
        cur.execute("SELECT peers_ip, peers_port, peers_hostname FROM peers WHERE file_name = %s", (file_name,))
        results = cur.fetchall()

        if results:
            # Create a list of dictionaries with details of each peer
            peers_info = [
                {
                    'peers_ip': peers_ip,
                    'peers_port': peers_port,
                    'peers_hostname': peers_hostname
                }
                for peers_ip, peers_port, peers_hostname in results
            ]
            print(f"Peers sharing file '{file_name}':")
            for peer in peers_info:
                print(f"- {peer['peers_hostname']} ({peer['peers_ip']}:{peer['peers_port']})")
        else:
            print(f"No peers found sharing the file '{file_name}'.")
    except Exception as e:
        print(f"An error occurred while discovering peers for file '{file_name}': {e}")

# Client Handler Function (This is your existing function)
def client_handler(conn, addr, Flag_stop):
    peers_port_current = ""
    conn.settimeout(5)
    try:
        while True:
            if Flag_stop[0] != 0:  # Exit condition
                break
            try:
                data = conn.recv(4096).decode()
                if not data:
                    break

                command = json.loads(data)

                peers_ip = addr[0]
                if command.get('action') != 'check':
                    peers_port = command['peers_port']
                    peers_port_current = command['peers_port']
                peers_hostname = command['peers_hostname'] if 'peers_hostname' in command else ""
                file_name = command['file_name'] if 'file_name' in command else ""
                file_size = command['file_size'] if 'file_size' in command else ""
                piece_hash = command['piece_hash'] if 'piece_hash' in command else ""
                piece_size = command['piece_size'] if 'piece_size' in command else ""
                num_order_in_file = command['num_order_in_file'] if 'num_order_in_file' in command else ""

                if command.get('action') == 'check':
                    conn.sendall("ServerOn".encode())

                elif command.get('action') == 'introduce':
                    client_peers_hostname = command.get('peers_hostname')
                    active_connections[str(peers_port)] = conn
                    log_event(f"Connection established with {client_peers_hostname}/{peers_ip}:{peers_port})")

                elif command['action'] == 'publish':
                    log_event(f"Updating client info in database for hostname: {peers_hostname}/{peers_ip}:{peers_port}")
                    update_client_info(peers_ip, peers_port, peers_hostname, file_name, file_size, piece_hash, piece_size, num_order_in_file)
                    log_event(f"Database update complete for hostname: {peers_hostname}/{peers_ip}:{peers_port}")
                    conn.sendall("File list updated to server successfully.".encode())

                elif command['action'] == 'fetch':
                    cur.execute("SELECT * FROM peers WHERE file_name = %s AND num_order_in_file <> ALL (%s) AND piece_hash <> ALL (%s)", (file_name, num_order_in_file, piece_hash))
                    results = cur.fetchall()
                    if results:
                        peers_info = [{'peers_ip': peers_ip, 'peers_port': peers_port, 'peers_hostname': peers_hostname, 'file_name': file_name, 'file_size': file_size, 'piece_hash': piece_hash, 'piece_size': piece_size, 'num_order_in_file': num_order_in_file} for peers_ip, peers_port, peers_hostname, file_name, file_size, piece_hash, piece_size, num_order_in_file in results if str(peers_port) in active_connections]
                        conn.sendall(json.dumps({'peers_info': peers_info}).encode())
                    else:
                        conn.sendall(json.dumps({'error': 'File not available'}).encode())

                elif command['action'] == 'info':
                    cur.execute("SELECT * FROM peers WHERE file_name = %s", (file_name,))
                    results = cur.fetchall()
                    if results:
                        peers_info = [{'peers_ip': peers_ip, 'peers_port': peers_port, 'peers_hostname': peers_hostname, 'file_name': file_name, 'file_size': file_size, 'piece_hash': piece_hash, 'piece_size': piece_size, 'num_order_in_file': num_order_in_file} for peers_ip, peers_port, peers_hostname, file_name, file_size, piece_hash, piece_size, num_order_in_file in results if str(peers_port) in active_connections]
                        conn.sendall(json.dumps({'peers_info': peers_info}).encode())
                    else:
                        conn.sendall(json.dumps({'error': 'File not available'}).encode())

                elif command['action'] == 'file_list':
                    files = command['files']
                    print(f"List of files : {files}")
            except socket.timeout:
                continue
    except Exception as e:
        logging.exception(f"An error occurred while handling client {addr[0]}:{peers_port_current}: {e}")
    finally:
        if peers_port:
            del active_connections[str(peers_port)]
        conn.close()
        log_event(f"Connection with {addr[0]}:{peers_port_current} has been closed.")

# Server Command Shell Function
def server_command_shell(Flag_stop):
    try:
        while True:
            cmd_input = input("Server command:\n")
            cmd_parts = cmd_input.split()
            if cmd_parts:
                action = cmd_parts[0]
                if action == "discover" and len(cmd_parts) == 2:
                    hostname = cmd_parts[1]
                    thread = threading.Thread(target=discover_files, args=(hostname,))
                    thread.start()
                elif action == "ping" and len(cmd_parts) == 2:
                    hostname = cmd_parts[1]
                    thread = threading.Thread(target=ping_host, args=(hostname,))
                    thread.start()
                elif action == "exit":
                    Flag_stop[0] = 2
                    break
                else:
                    print("Unknown command or incorrect usage.")
    except KeyboardInterrupt:
        Flag_stop[0] = 1
        return
    except Exception as e:
        print(f"Error in server command shell: {e}")

# Start the Server
def start_server():
    Flag_stop = [0]
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 65432))
    server_socket.listen(5)

    log_event("Server started and listening for connections...")
    
    # Start the server command shell in a separate thread
    command_thread = threading.Thread(target=server_command_shell, args=(Flag_stop,))
    command_thread.start()

    while Flag_stop[0] == 0:
        try:
            conn, addr = server_socket.accept()
            log_event(f"Accepted connection from {addr[0]}:{addr[1]}")
            client_thread = threading.Thread(target=client_handler, args=(conn, addr, Flag_stop))
            client_thread.start()
        except Exception as e:
            logging.exception(f"Error while accepting connection: {e}")
            break

    # Close server socket when done
    server_socket.close()
    sys.exit(0)  # Gracefully exit the server

# Start the server
if __name__ == '__main__':
    start_server()
