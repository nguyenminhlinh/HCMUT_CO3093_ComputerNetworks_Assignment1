import logging
import socket
import threading
import json
import psycopg2
import sys
import os
import time
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(dbname="", user="postgres", password="12345678", host="", port="5432")
cur = conn.cursor()

def log_event(message):
    logging.info(message)

def update_client_info(peers_ip,peers_port,peers_hostname,file_name,file_size,piece_hash,piece_size,num_order_in_file):
    # Update the client's file list in the database
    for i in range(len(num_order_in_file)):
        cur.execute(
            "INSERT INTO peers (peers_ip,peers_port,peers_hostname,file_name,file_size,piece_hash,piece_size,num_order_in_file) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (peers_ip,peers_port,peers_hostname,file_name,file_size,piece_hash[i],piece_size,num_order_in_file[i])
        )
    conn.commit()

active_connections = {}  
host_files = {}

def client_handler(conn, addr,Flag_stop):
    peers_port_current=""
    conn.settimeout(5) 
    try:
        while True:
            if Flag_stop[0]!=0: #exit
                break
            try:
                data = conn.recv(4096).decode()
                # log_event(f"Received data from {addr}: {data}")
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
                    # peers_ip,peers_port,peers_hostname,file_name,piece_hash
                    log_event(f"Updating client info in database for hostname: {peers_hostname}/{peers_ip}:{peers_port}")
                    update_client_info(peers_ip,peers_port, peers_hostname,file_name,file_size, piece_hash,piece_size,num_order_in_file)  # addr[0] is the IP address
                    log_event(f"Database update complete for hostname: {peers_hostname}/{peers_ip}:{peers_port}")
                    conn.sendall("File list updated to server successfully.".encode())

                elif command['action'] == 'fetch':
                    # print("fetch",file_name, num_order_in_file, piece_hash)
                    # Query the database for the IP addresses of the clients that have the file
                    cur.execute("SELECT * FROM peers WHERE file_name = %s AND num_order_in_file <> ALL (%s) AND piece_hash <> ALL (%s)", (file_name, num_order_in_file, piece_hash))
                    results = cur.fetchall()
                    if results:
                        # print(active_connections)
                        # Create a list of dictionaries with 'hostname' and 'ip' keys
                        peers_info = [{'peers_ip': peers_ip, 'peers_port': peers_port, 'peers_hostname': peers_hostname, 'file_name':file_name,'file_size':file_size,'piece_hash':piece_hash,'piece_size':piece_size,'num_order_in_file':num_order_in_file } for peers_ip, peers_port, peers_hostname, file_name,file_size, piece_hash,piece_size, num_order_in_file  in results if str(peers_port) in active_connections]
                        conn.sendall(json.dumps({'peers_info': peers_info}).encode())
                    else:
                        conn.sendall(json.dumps({'error': 'File not available'}).encode())
                        
                elif command['action'] == 'info':
                    # print("fetch",file_name, num_order_in_file, piece_hash)
                    # Query the database for the IP addresses of the clients that have the file
                    cur.execute("SELECT * FROM peers WHERE file_name = %s", (file_name,))
                    results = cur.fetchall()
                    if results:
                        # Create a list of dictionaries with 'hostname' and 'ip' keys
                        # print( active_connections)
                        peers_info = [{'peers_ip': peers_ip, 'peers_port': peers_port, 'peers_hostname': peers_hostname, 'file_name':file_name,'file_size':file_size,'piece_hash':piece_hash,'piece_size':piece_size,'num_order_in_file':num_order_in_file } for peers_ip, peers_port, peers_hostname, file_name,file_size, piece_hash,piece_size, num_order_in_file  in results if str(peers_port) in active_connections]
                        conn.sendall(json.dumps({'peers_info': peers_info}).encode())
                    else:
                        conn.sendall(json.dumps({'error': 'File not available'}).encode())

                elif command['action'] == 'file_list':
                    files = command['files']
                    print(f"List of files : {files}")
            except socket.timeout:
                # Khi timeout xảy ra, tiếp tục kiểm tra Flag_stop
                continue

    except Exception as e:
        logging.exception(f"An error occurred while handling client {addr[0]}:{peers_port_current}: {e}")
    finally:
        if peers_port:
            del active_connections[str(peers_port)] 
        conn.close()
        log_event(f"Connection with {addr[0]}:{peers_port_current} has been closed.")

def request_file_list_from_client(peers_hostname):
    if peers_hostname in active_connections:
        conn = active_connections[peers_hostname]
        print(active_connections[peers_hostname])
        ip_address, _ = conn.getpeername()
        # print(ip_address)
        peer_port = 65433  
        peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_sock.connect((ip_address, peer_port))
        request = {'action': 'request_file_list'}
        peer_sock.sendall(json.dumps(request).encode() + b'\n')
        response = json.loads(peer_sock.recv(4096).decode())
        peer_sock.close()
        if 'files' in response:
            return response['files']
        else:
            return "Error: No file list in response"
    else:
        return "Error: Client not connected"

# Discover Files Function
def discover_files(file_name):
    try:
        # Query the database to find all peers that have the specified file_name
        cur.execute("SELECT peers_ip, peers_port, peers_hostname, num_order_in_file FROM peers WHERE file_name = %s", (file_name,))
        results = cur.fetchall()

        if results:
            # Create a list of dictionaries with details of each peer
            peers_info = [
                {
                    'peers_ip': peers_ip,
                    'peers_port': peers_port,
                    'peers_hostname': peers_hostname,
                    'num_order_in_file': num_order_in_file
                }
                for peers_ip, peers_port, peers_hostname, num_order_in_file in results
            ]
            print(f"Peers sharing file '{file_name}':")
            for peer in peers_info:
                print(f"{file_name}_piece{peer['num_order_in_file']} - {peer['peers_hostname']} ({peer['peers_ip']}:{peer['peers_port']})")
        else:
            print(f"No peers found sharing the file '{file_name}'.")
    except Exception as e:
        print(f"An error occurred while discovering peers for file '{file_name}': {e}")
        
def ping_host(peers_hostname):
    cur.execute("SELECT address FROM client_files WHERE hostname = %s", (peers_hostname,))
    results = cur.fetchone()  
    ip_address = results[0]
    print(ip_address)
    if ip_address:
        peer_port = 65433
        peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_sock.connect((ip_address, peer_port))
        request = {'action': 'ping'}
        peer_sock.sendall(json.dumps(request).encode() + b'\n')
        response = peer_sock.recv(4096).decode()
        peer_sock.close()
        if response:
            print(f"{peers_hostname} is online!")
        else:
            print(f"{peers_hostname} is offline!")
    else:
        print("There is no host with that name")



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
                    Flag_stop[0]=2
                    break
                else:
                    print("Unknown command or incorrect usage.")
    except KeyboardInterrupt:
        Flag_stop[0]=1
        return
def start_server(Flag_stop,host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    log_event("Server started and is listening for connections.")

    try:
        while True:
            if Flag_stop[0]!=0: #exit
                break
            try:
                server_socket.settimeout(1.0)  # Đặt thời gian chờ để kiểm tra cờ thường xuyên
                conn, addr = server_socket.accept()
                thread = threading.Thread(target=client_handler, args=(conn, addr,Flag_stop))
                thread.start()
                log_event(f"Active connections: {threading.active_count() - 2}")
            except socket.timeout:
                continue  # Bỏ qua timeout và tiếp tục kiểm tra Flag_stop
    finally:
        server_socket.close()
        cur.close()

if __name__ == "__main__":
    # SERVER_HOST = '192.168.56.1'
    SERVER_PORT = 65432
    SERVER_HOST='0.0.0.0'
    Flag_stop=[0]
    # Start server in a separate thread
    server_thread = threading.Thread(target=start_server, args=(Flag_stop,SERVER_HOST,SERVER_PORT))
    server_thread.start()

    # Start the server command shell in the main thread
    server_command_shell(Flag_stop)

    # Signal the server to shutdown
    if Flag_stop[0]==1:
        print("The server stopped suddenly and the backup server was running")
        try:
            parent_path = os.path.dirname(os.getcwd())+"\\server_backup\\server.py"
            # keys = list(active_connections.keys())
            # with open("data_client_active.txt", "w") as file:
            #     file.write(str(keys))
            subprocess.Popen(["start", "powershell", "-NoExit", "-Command", f"python '{parent_path}'"], shell=True)
        except Exception as e:
            print(f"An error occurred while running the server: {e}")
       
    elif Flag_stop[0]==2:
        print("The server is stopped with the exit command")
    sys.exit(0)