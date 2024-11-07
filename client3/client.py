import socket
import json
import os
import threading
import shlex
import hashlib
import time

stop_event = threading.Event()

def calculate_piece_hash(piece_data):
    sha1 = hashlib.sha1()
    sha1.update(piece_data)
    return sha1.digest()

def create_pieces_string(pieces):
    hash_pieces = []
    for piece_file_path in pieces:
            with open(piece_file_path, "rb") as piece_file:
                piece_data = piece_file.read()
                piece_hash = calculate_piece_hash(piece_data)
                hash_pieces.append(f"{piece_hash}")
    return hash_pieces

def split_file_into_pieces(file_path, piece_length):
    pieces = []
    with open(file_path, "rb") as file:
        counter = 1
        while True:
            piece_data = file.read(piece_length)
            if not piece_data:
                break
            piece_file_path = f"{file_path}_piece{counter}"
            # piece_file_path = os.path.join("", f"{file_path}_piece{counter}")
            with open(piece_file_path, "wb") as piece_file:
                piece_file.write(piece_data)
            pieces.append(piece_file_path)
            counter += 1
    return pieces

def merge_pieces_into_file(pieces, output_file_path):
    with open(output_file_path, "wb") as output_file:
        for piece_file_path in pieces:
            with open(piece_file_path, "rb") as piece_file:
                piece_data = piece_file.read()
                output_file.write(piece_data)
                

def get_list_local_files(directory='.'):
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        return True
    except Exception as e:
        return f"Error: Unable to list files - {e}"
    
def check_local_files(file_name):
    if not os.path.exists(file_name):
        return False
    else:
        return True
    
def check_local_piece_files(file_name):
    exist_files = []
    directory = os.getcwd()  # Lấy đường dẫn thư mục hiện tại

    for filename in os.listdir(directory):
        if filename.startswith(file_name) and len(filename)>len(file_name):
            exist_files.append(filename)

    if len(exist_files) > 0:
        return exist_files
    else:
        return False

def handle_publish_piece(sock, peers_port, pieces, file_name,file_size,piece_size):
    pieces_hash = create_pieces_string(pieces)
    piece_hash=[]
    num_order_in_file=[]
    print(f"Publishing file {file_name} to server: " )
    for i in pieces:
        index = pieces.index(i)
        num_order_in_file.append(index+1)
        piece_hash.append(pieces_hash[index])
        print (f"{i} : {pieces_hash[index]}")
    publish_piece_file(sock,peers_port,file_name,file_size, piece_hash,piece_size,num_order_in_file)

def publish_piece_file(sock,peers_port,file_name,file_size, piece_hash,piece_size,num_order_in_file):
    peers_hostname = socket.gethostname()
    command = {
        "action": "publish",
        "peers_port": peers_port,
        "peers_hostname":peers_hostname,
        "file_name":file_name,
        "file_size":file_size,
        "piece_hash":piece_hash,
        "piece_size":piece_size,
        "num_order_in_file":num_order_in_file,
    }
    # shared_piece_files_dir.append(command)
    sock.sendall(json.dumps(command).encode() + b'\n')
    response = sock.recv(4096).decode()
    print(response)

def request_file_from_peer(peers_ip, peer_port, file_name, piece_hash, num_order_in_file):
    peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        peer_sock.connect((peers_ip, int(peer_port)))
        peer_sock.sendall(json.dumps({'action': 'send_file', 'file_name': file_name, 'piece_hash':piece_hash, 'num_order_in_file':num_order_in_file}).encode() + b'\n')

        # Peer will send the file in chunks of 4096 bytes
        with open(f"{file_name}_piece{num_order_in_file}", 'wb') as f:
            while True:
                data = peer_sock.recv(4096)
                if not data:
                    break
                f.write(data)

        peer_sock.close()
        print(f"Piece of file: {file_name}_piece{num_order_in_file} has been fetched from peer {peers_ip}:{peer_port}.")
    except Exception as e:
        print(f"An error occurred while connecting to peer at {peers_ip}:{peer_port} - {e}")
    finally:
        peer_sock.close()

def fetch_file(sock,peers_port,file_name, piece_hash, num_order_in_file):
    peers_hostname = socket.gethostname()
    command = {
        "action": "fetch",
        "peers_port": peers_port,
        "peers_hostname":peers_hostname,
        "file_name":file_name,
        "piece_hash":piece_hash,
        "num_order_in_file":num_order_in_file,
    } 
    # command = {"action": "fetch", "fname": fname}
    sock.sendall(json.dumps(command).encode() + b'\n')
    response = json.loads(sock.recv(4096).decode())
    if 'peers_info' in response:
        peers_info = response['peers_info']
        # host_info_str = "\n".join([f"Number: {peer_info['num_order_in_file'] } {peer_info['peers_hostname']}/{peer_info['peers_ip']}:{peer_info['peers_port']} piece_hash: {peer_info['piece_hash']  } num_order_in_file: {peer_info['num_order_in_file'] }" for peer_info in peers_info])
        # print(f"Hosts with the file {file_name}:\n{host_info_str}")
        if len(peers_info) >= 1:
            num_of_piece=int(int(peers_info[0]['file_size'])/524288)+1
            # print(num_of_piece)
            list_piece_dont_have=[]
            num_order_in_file_int = [int(x) for x in num_order_in_file]
            for i in range (1,num_of_piece+1):
                if i not in num_order_in_file_int:
                    list_piece_dont_have.append(i)

            dict_list_piece_dont_have=dict.fromkeys(list_piece_dont_have,0)
            # dict_list_client_ip={}
            dict_list_client_port={}

            for peer_info in peers_info:
                # print(dict_list_piece_dont_have[1])
                # print(dict_list_piece_dont_have['1'])
                dict_list_piece_dont_have[int(peer_info['num_order_in_file'])]=dict_list_piece_dont_have[int(peer_info['num_order_in_file'])]+1
                # dict_list_client_ip[peer_info['peers_ip']]=0
                dict_list_client_port[peer_info['peers_port']]=0

            dict_list_piece_dont_have=dict(sorted(dict_list_piece_dont_have.items(),key=lambda x:x[1]))
            list_piece_id_download=[]
            
            for num_piece in dict_list_piece_dont_have:
                min_count=100 #max
                # ip_min_count=""
                port_min_count=""
                hash_min_count=""
                flag_one_client_have=True
                for peer_info in peers_info:
                    if int(peer_info['num_order_in_file'])==int(num_piece) and dict_list_piece_dont_have[int(num_piece)]==1 :
                        # dict_list_client_ip[peer_info['peers_ip']]=dict_list_client_ip[peer_info['peers_ip']]+1
                        dict_list_client_port[peer_info['peers_port']]=dict_list_client_port[peer_info['peers_port']]+1
                        # ip=peer_info['peers_ip']
                        port=peer_info['peers_port']
                        hash=peer_info['piece_hash']

                        # index = next((j for j, peer_info in enumerate(peers_info) if peer_info.get('peers_ip') == ip), None)
                        index = next((j for j, peer_info in enumerate(peers_info) if peer_info.get('peers_port') == port and str(peer_info.get('piece_hash'))==str(hash)) , None)
                    
                        if index is not None:
                            request_file_from_peer(peers_info[index]['peers_ip'], peers_info[index]['peers_port'], peers_info[index]['file_name'],peers_info[index]['piece_hash'],peers_info[index]['num_order_in_file'])
                            list_piece_id_download.append(int(num_piece))
                            continue
                    elif int(peer_info['num_order_in_file'])==num_piece:
                        # if min_count>dict_list_client_ip[peer_info['peers_ip']]:
                        #     min_count=dict_list_client_ip[peer_info['peers_ip']]
                        #     ip_min_count=peer_info['peers_ip']
                        #     flag_one_client_have=False 
                        if min_count>dict_list_client_port[peer_info['peers_port']]:
                            min_count=dict_list_client_port[peer_info['peers_port']]
                            port_min_count=peer_info['peers_port']
                            hash_min_count=peer_info['piece_hash']
                            flag_one_client_have=False 
                if not flag_one_client_have:      
                    index = next((j for j, peer_info in enumerate(peers_info) if peer_info.get('peers_port') == port_min_count and str(peer_info.get('piece_hash'))==str(hash_min_count)), None)
                    if index is not None:
                        dict_list_client_port[peers_info[index]['peers_port']]=dict_list_client_port[peers_info[index]['peers_port']]+1
                        list_piece_id_download.append(int(num_piece))
                        request_file_from_peer(peers_info[index]['peers_ip'], peers_info[index]['peers_port'], peers_info[index]['file_name'],peers_info[index]['piece_hash'],peers_info[index]['num_order_in_file'])
            
            list_piece_name_download=[]
            for i in list_piece_id_download:
                list_piece_name_download.append(file_name+"_piece"+str(i))
            piece_hash = create_pieces_string(list_piece_name_download)
            
            for i in range(len(piece_hash)):
                if not any(piece_hash[i] in str(value) for peer in peers_info for value in peer.values()):
                    print(f"File {list_piece_name_download[i]} have hash {list_piece_name_download[i]} is incorrect")
                    list_piece_name_download.pop(i)
                    list_piece_id_download.pop(i)
                    piece_hash.pop(i)     
                    
            publish_piece_file(sock,peers_port,file_name,peers_info[0]['file_size'], piece_hash,peers_info[0]['piece_size'],list_piece_id_download)
            # print(list_piece_name_download)
            # print(piece_hash)
            if num_of_piece == len((pieces := sorted(check_local_piece_files(file_name)))):
                merge_pieces_into_file(pieces,file_name)
                print(f"Create file {file_name} successful")
            else:
                print(f"Not enough piece to create file {file_name}")
        else:
            print("No hosts have the file.")
    else:
        print("No peers have the file or you had this file.")

def send_piece_to_client(conn, piece):
    with open(piece, 'rb') as f:
        while True:
            bytes_read = f.read(4096)
            if not bytes_read:
                break
            conn.sendall(bytes_read)

def handle_file_request(conn, shared_files_dir):
    try:
        data = conn.recv(4096).decode()
        command = json.loads(data)
        if command['action'] == 'send_file':
            file_name = command['file_name']
            num_order_in_file = command['num_order_in_file']
            file_path = os.path.join(shared_files_dir, f"{file_name}_piece{num_order_in_file}")
            send_piece_to_client(conn, file_path)
    finally:
        conn.close()

def start_host_service(port, shared_files_dir):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('0.0.0.0', port))
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.listen()

    while not stop_event.is_set():
        try:
            server_sock.settimeout(1) 
            conn, addr = server_sock.accept()
            thread = threading.Thread(target=handle_file_request, args=(conn, shared_files_dir))
            thread.start()
        except socket.timeout:
            continue
        except Exception as e:
            break

    server_sock.close()

def connect_to_server(server_host, server_port, peers_port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_host, server_port))
        peers_hostname = socket.gethostname()
        host_service_thread = threading.Thread(target=start_host_service, args=(peers_port, './'))
        host_service_thread.start()
        sock.sendall(json.dumps({'action': 'introduce', 'peers_hostname': peers_hostname, 'peers_port': peers_port}).encode() + b'\n')
        return sock,host_service_thread
    except (socket.error, ConnectionRefusedError) as e:
        print(f"Unable to connect to server: {e}")
        return None,None

def check_server(sock,flag_exit):
    while True:
        time.sleep(5)  # Kiểm tra mỗi 5 giây
        try:
            # Gửi một thông điệp kiểm tra
            command = {
                    "action": "check",
                } 
            sock.sendall(json.dumps(command).encode() + b'\n')                    
            response = sock.recv(4096).decode()
            if 'ServerOn' not in response:
                print("Server is not responding.")
                break
        except socket.error:
            if not flag_exit[0]:
                print("\nThe main server is down, if you want to connect to the backup server, enter reconnect.")
            break
        
def main(server_host, server_port, peers_port,flag_re_connect):
    # Connect to the server
    
    sock,host_service_thread = connect_to_server(server_host, server_port,peers_port)
    if sock==None:
        return

    flag_exit=[False]
    if not flag_re_connect[0]:
        check_server_thread = threading.Thread(target=check_server, args=(sock,flag_exit,))
        check_server_thread.start()
    
    
    
    try:
        while True:
            user_input = input("Enter command (publish file_name file_name2 / fetch file_name file_name2/ exit): ")#addr[0],peers_port, peers_hostname,file_name, piece_hash,num_order_in_file
            
            command_parts = shlex.split(user_input)
            if len(command_parts) >= 2 and command_parts[0].lower() == 'publish':
                command = {
                    "action": "check",
                } 
                sock.sendall(json.dumps(command).encode() + b'\n')                    
                sock.recv(4096).decode()
                # sock.sendall("check".encode())                    
                # response = sock.recv(4096).decode()
                for file_name in command_parts[1:]:
                    if check_local_files(file_name):
                        piece_size = 524288  # 524288 byte = 512KB
                        file_size = os.path.getsize(file_name)
                        pieces = split_file_into_pieces(file_name,piece_size)
                        handle_publish_piece(sock, peers_port, pieces, file_name,file_size,piece_size)
                    elif (pieces := check_local_piece_files(file_name)):
                        piece_size = 524288  # 524288 byte = 512KB
                        peers_hostname = socket.gethostname()
                        
                        command = {
                            "action": "info",
                            "peers_port": peers_port,
                            "peers_hostname":peers_hostname,
                            "file_name":file_name,
                        } 
                        sock.sendall(json.dumps(command).encode() + b'\n')                    
                        response = json.loads(sock.recv(4096).decode())
                        
                        if 'peers_info' in response:
                            peers_info = response['peers_info']
                            if len(peers_info)>0:
                                file_size=int(peers_info[0]['file_size'])
                            else:
                                file_size=0  
                        else:
                            file_size=0  
                            
                        handle_publish_piece(sock, peers_port, pieces, file_name,file_size,piece_size)
                    else:
                        print(f"Local file {file_name}/piece does not exist.")
            elif len(command_parts) >= 2 and command_parts[0].lower() == 'fetch':
                command = {
                    "action": "check",
                } 
                sock.sendall(json.dumps(command).encode() + b'\n')                    
                sock.recv(4096).decode()
                # sock.sendall("check".encode())                    
                # response = sock.recv(4096).decode()
                for file_name in command_parts[1:]:
                    pieces = check_local_piece_files(file_name)
                    pieces_hash = [] if not pieces else create_pieces_string(pieces)
                    num_order_in_file= [] if not pieces else [item.split("_")[-1][5:] for item in pieces]
                    fetch_file(sock,peers_port,file_name, pieces_hash,num_order_in_file)
            elif user_input.lower() == 'exit':
                stop_event.set()  # Stop the host service thread
                sock.close()
                flag_exit[0]=True
                break
            elif user_input.lower() == 'reconnect':
                stop_event.set()  # Stop the host service thread
                sock.close()
                flag_re_connect[0]=True
                break
            else:
                print("Invalid command.")
    except socket.error :
        print("The server is not online")
    finally:
            sock.close()
            stop_event.set()
            host_service_thread.join()


if __name__ == "__main__":
    # Replace with your server's IP address and port number
    SERVER_HOST = '192.168.56.1'
    SERVER_PORT = 65432
    BACKUP_SERVER_PORT = 65431
    CLIENT_PORT = 65435
    FLAG_RE_CONNECT=[False]
    main(SERVER_HOST, SERVER_PORT,CLIENT_PORT,FLAG_RE_CONNECT)
    if FLAG_RE_CONNECT[0]:
        main(SERVER_HOST, BACKUP_SERVER_PORT,CLIENT_PORT,FLAG_RE_CONNECT)
