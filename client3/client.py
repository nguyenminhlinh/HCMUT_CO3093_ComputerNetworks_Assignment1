import socket
import json
import os
import threading
import shlex
import hashlib
import time
import sys
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
from functools import partial


Main_Server_Flag = True
SERVER_HOST = '192.168.56.1'
SERVER_PORT = 65432
BACKUP_SERVER_PORT = 65431
CLIENT_PORT = 65435

stop_event = threading.Event()
UI_Width = 800
UI_Height = 700
def Clear_Placeholder(Object_Arg,*args):
        if Object_Arg.get() == args[0]:
            Object_Arg.delete(0, tk.END)

def Set_Placeholder(Object_Arg,*args):
        if Object_Arg.get() == "":
            Object_Arg.insert(0, args[0])
class Client_UI():
    def __init__(self ,SSID:str ,PassWord:str ,Client_Port:int , socket) -> None:
        self.SSID_Reference = SSID
        self.Password_Reference = PassWord
        self.Client_Port = Client_Port
        self.Socket = socket
        self.Root = tk.Tk()
        self.Root.title("Computer Network Assignment")
        self.Root.minsize(width=UI_Width,height=UI_Height)
        self.Root.protocol("WM_DELETE_WINDOW", self.Close_UI)
        self.Check_Server()

    def Check_Server(self):
        Response = check_server(sock=self.Socket)
        if Response == "NotResponse" or Response == "Fail":
            answer = messagebox.askyesno("Question", "Server is not responsding. Do you want to connect another server?")
            if answer:
                self.Socket = change_server()
        self.Root.after(30000,self.Check_Server)
    def Start_UI(self):
        # self.Create_Login_Layout()
        self.Create_Login_Layout()
        self.Root.mainloop()
    
    def Close_UI(self):
        answer = messagebox.askyesno("Question", "Do you want to exit?")
        if answer:
            user_input = "exit"
            Command_Handler(user_input=user_input,peers_port=self.Client_Port,sock=self.Socket) 
            sys.exit(0)


    def Create_Login_Layout(self):
        self.Login_Background_Frame = tk.Frame(self.Root,width=UI_Width,height=UI_Height,bg="#a1f7f6")
        self.Login_Background_Frame.pack()
        self.Login_Frame = tk.Frame(self.Login_Background_Frame,bg="white",width=UI_Width-300,height=UI_Height-100)
        self.Login_Frame.place(relx=0.5,rely=0.5,anchor=tk.CENTER)
        tk.Label(self.Login_Frame,text="Login",font=("Arial", 30, "bold"),fg="black", bg="white").place(relx=0.5,rely=0.15, anchor=tk.CENTER)

        # Input SSID area
        self.SSID_Box  = tk.Entry(self.Login_Frame,font=("Arial"))
        self.SSID_Box.insert(0,"Username")
        self.SSID_Box.place(relx=0.5,rely= 0.3,width=UI_Width-500,height=30,anchor=tk.CENTER)
        self.SSID_Box.bind("<FocusIn>", partial(Clear_Placeholder,self.SSID_Box,"Username"))
        self.SSID_Box.bind("<FocusOut>", partial(Set_Placeholder,self.SSID_Box,"Username"))

        # Input password area 
        self.Password_Box  = tk.Entry(self.Login_Frame,font=("Arial"))
        self.Password_Box.insert(0,"Password")
        self.Password_Box.place(relx=0.5,rely= 0.45,width=UI_Width-500,height=30,anchor=tk.CENTER)
        self.Password_Box.bind("<FocusIn>", partial(Clear_Placeholder,self.Password_Box,"Password"))
        self.Password_Box.bind("<FocusOut>", partial(Set_Placeholder,self.Password_Box,"Password"))

        tk.Button(self.Login_Frame,text="Login",bg="#a1f7f6",fg="black",font=("Arial", 15, "bold"),command=self.Login_Handler).place(width=100,relx= 0.5, rely= 0.6, anchor=tk.CENTER)
        
        tk.Button(self.Login_Frame,text="Sign Up",bg="white",fg="black",font=("Arial", 10, "bold"),borderwidth=0,command=self.Change_To_SignUp_Layout).place(relx= 0.5, rely= 0.7, anchor=tk.CENTER)

    def Create_SignUp_Layout(self):
        self.SignUp_Background_Frame = tk.Frame(self.Root,width=UI_Width,height=UI_Height,bg="#a1f7f6")
        self.SignUp_Background_Frame.pack()
        self.SignUp_Frame = tk.Frame(self.SignUp_Background_Frame,bg="white",width=UI_Width-300,height=UI_Height-100)
        self.SignUp_Frame.place(relx=0.5,rely=0.5,anchor=tk.CENTER)
        tk.Label(self.SignUp_Frame,text="Sign Up",font=("Arial", 30, "bold"),fg="black", bg="white").place(relx=0.5,rely=0.15, anchor=tk.CENTER)

        self.SSID_Box  = tk.Entry(self.SignUp_Frame,font=("Arial"))
        self.SSID_Box.insert(0,"Username")
        self.SSID_Box.place(relx=0.5,rely= 0.3,width=UI_Width-500,height=30,anchor=tk.CENTER)
        self.SSID_Box.bind("<FocusIn>", partial(Clear_Placeholder,self.SSID_Box,"Username"))
        self.SSID_Box.bind("<FocusOut>", partial(Set_Placeholder,self.SSID_Box,"Username"))

        self.Password_Box  = tk.Entry(self.SignUp_Frame,font=("Arial"))
        self.Password_Box.insert(0,"Password")
        self.Password_Box.place(relx=0.5,rely= 0.4,width=UI_Width-500,height=30,anchor=tk.CENTER)
        self.Password_Box.bind("<FocusIn>", partial(Clear_Placeholder,self.Password_Box,"Password"))
        self.Password_Box.bind("<FocusOut>", partial(Set_Placeholder,self.Password_Box,"Password"))

        self.Confirm_Password_Box  = tk.Entry(self.SignUp_Frame,font=("Arial"))
        self.Confirm_Password_Box.insert(0,"Confirm Password")
        self.Confirm_Password_Box.place(relx=0.5,rely= 0.5,width=UI_Width-500,height=30,anchor=tk.CENTER)
        self.Confirm_Password_Box.bind("<FocusIn>", partial(Clear_Placeholder,self.Confirm_Password_Box,"Confirm Password"))
        self.Confirm_Password_Box.bind("<FocusOut>", partial(Set_Placeholder,self.Confirm_Password_Box,"Confirm Password"))

        tk.Button(self.SignUp_Frame,text="Sign Up",bg="#a1f7f6",fg="black",font=("Arial", 15, "bold"),command=self.SignUp_Handler).place(width=100,relx= 0.5, rely= 0.65, anchor=tk.CENTER)
        
        tk.Button(self.SignUp_Frame,text="Login",bg="white",fg="black",font=("Arial", 10, "bold"),borderwidth=0,command=self.Change_To_Login_Layout).place(relx= 0.5, rely= 0.75, anchor=tk.CENTER)
    
    def Create_Main_Layout(self):

        self.Main_Background_Frame = tk.Frame(self.Root,width=UI_Width,height=UI_Height,bg="#a1f7f6")
        self.Main_Background_Frame.pack()

        ######################
        self.Client_Information_Frame =  tk.Frame(self.Main_Background_Frame,bg="white")
        self.Client_Information_Frame.place(relx=0,rely=0,relwidth=0.2,relheight=1)

        tk.Label(self.Client_Information_Frame, text = f"User : {self.SSID_Reference}",font=("Arial", 15, "bold"),bg="white",fg="black").place(relx=0,rely=0.1)

        tk.Label(self.Client_Information_Frame, text = f"Port : {self.Client_Port}",font=("Arial", 15, "bold"),bg="white",fg="black").place(relx=0,rely=0.2)
        ######################
        self.Command_Frame = tk.Frame(self.Main_Background_Frame,bg="#a1f7f6")
        self.Command_Frame.place(relx=0.2,rely=0,relwidth=0.8,relheight=0.5)
        
        self.Publish_Button = tk.Button(self.Command_Frame,text="Publish",font=("Arial", 12, "bold"), command = self.Publish_Handler)
        self.Publish_Button.place(relx=0.1,rely= 0.1, relwidth= 0.2, relheight=0.1)
        self.Publish_Text = tk.Entry(self.Command_Frame,font=("Arial", 12, "bold"))
        self.Publish_Text.place(relx= 0.4, rely= 0.1,relwidth= 0.4,relheight=0.1)

        self.Fetch_Button = tk.Button(self.Command_Frame,text="Fetch",font=("Arial", 12, "bold"), command= self.Fetch_Handler)
        self.Fetch_Button.place(relx=0.1,rely= 0.3, relwidth= 0.2, relheight=0.1)
        self.Fetch_Text = tk.Entry(self.Command_Frame,font=("Arial", 12, "bold"))
        self.Fetch_Text.place(relx= 0.4, rely= 0.3,relwidth= 0.4,relheight=0.1)

        self.Exit_Button = tk.Button(self.Command_Frame,text="Exit",font=("Arial", 12, "bold"), command= self.Exit_Handler)
        self.Exit_Button.place(relx=0.5,rely= 0.6, relwidth= 0.2, relheight=0.1,anchor=tk.CENTER)
        ######################
        self.Information_File_Frame = tk.Frame(self.Main_Background_Frame,bg="#a1f7f6")
        self.Information_File_Frame.place(relx=0.2,rely=0.5,relwidth=0.8,relheight=0.5)

        self.Tree = ttk.Treeview(self.Information_File_Frame, columns=("File", "Information"), show="headings")
        self.Tree.place(relx=0,rely=0,relheight=1,relwidth=1)


    def Change_To_Login_Layout(self):
        self.SignUp_Background_Frame.destroy()
        self.Create_Login_Layout()

    def Login_Handler(self):
        SSID = self.SSID_Box.get()
        Password = self.Password_Box.get()
        if (SSID != "" and Password != "") and (SSID != "Username" and Password != "Password"):
            if (SSID == self.SSID_Reference) and (Password == self.Password_Reference):
                self.Change_To_Main_Layout()
            else:
                messagebox.showerror("Error",message="Either the SSID or the Password is not correct")
            # send request to server to authenticate user 
        else:
            messagebox.showerror("Error",message="Please enter username and password")


    def Change_To_SignUp_Layout(self):
        self.Login_Background_Frame.destroy()
        self.Create_SignUp_Layout()

    def SignUp_Handler(self):
        SSID = self.SSID_Box.get()
        Password = self.Password_Box.get()
        Confirm_Password = self.Confirm_Password_Box.get()
        if (SSID == "" or Password == "" or Confirm_Password == "") and (SSID == "Username" or Password == "Password" or Confirm_Password == "Confirm Password"):
            messagebox.showerror("Error",message="Please enter all information")
        elif (Password != Confirm_Password):
            messagebox.showerror("Error",message="Confirm password must be same as password")
        else:
            print(f"User Sign up's Information: {SSID} - {Password}")
            # Send request to server to get authorization
    
    def Change_To_Main_Layout(self):
        self.Login_Background_Frame.destroy()
        self.Create_Main_Layout()

    def Publish_Handler(self):
        self.Tree.heading("File",text="File")
        self.Tree.heading("Information",text="Hash")
        File_Name = self.Publish_Text.get()
        if File_Name == "":
            messagebox.showerror("Error",message="Please enter file")
        else:
            for item in self.Tree.get_children():
                self.Tree.delete(item)
            user_input = f"publish {File_Name}"
            Response = Command_Handler(user_input=user_input,peers_port=self.Client_Port,sock=self.Socket) 
            Message = ""
            for Filename_Publish in Response:
                if Response[Filename_Publish]["Status"] == False:
                    Message += f"{Filename_Publish} is not existence\n"
                else:
                    for piece_file in Response[Filename_Publish]["Information"]["Data"]:
                        piece_hash = Response[Filename_Publish]["Information"]["Data"][piece_file]
                        self.Tree.insert("","end",values=(f"{piece_file}",f"{piece_hash}"))
                    Message += Response[Filename_Publish]["Information"]["Response"]
            messagebox.showinfo(title="Publish Status",message=Message)
            
    def Fetch_Handler(self):
        self.Tree.heading("File",text="File")
        self.Tree.heading("Information",text="Port")
        File_Name = self.Fetch_Text.get()
        if File_Name == "":
            messagebox.showerror("Error",message="Please enter file")
        else:
            for item in self.Tree.get_children():
                self.Tree.delete(item)
            Message = ""
            user_input = f"fetch {File_Name}"
            Reponse = Command_Handler(user_input=user_input,peers_port=self.Client_Port,sock=self.Socket) 
            for filename in Reponse:
                for file_piece in Reponse[filename]["Data"]:
                    ip_port = Reponse[filename]["Data"][file_piece]
                    self.Tree.insert("","end",values=(f"{file_piece}",f"{ip_port}"))
                Response_Message = Reponse[filename]["Response"]
                Message += f"{Response_Message}\n"
            messagebox.showinfo("Fetch Information",message=Message)
                   
        
    def Exit_Handler(self):
        self.Close_UI()

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
    Publish_Information = {"Data":{},"Response":""}
    pieces_hash = create_pieces_string(pieces)
    piece_hash=[]
    num_order_in_file=[]
    print(f"Publishing file {file_name} to server: " )
    for i in pieces:
        index = pieces.index(i)
        num_order_in_file.append(index+1)
        piece_hash.append(pieces_hash[index])
        print (f"{i} : {pieces_hash[index]}")
        Publish_Information["Data"][f"{i}"] = f"{pieces_hash[index]}"
    Response = publish_piece_file(sock,peers_port,file_name,file_size, piece_hash,piece_size,num_order_in_file)
    Publish_Information["Response"] = Response
    return Publish_Information

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
    return response

def request_file_from_peer(peers_ip, peer_port, file_name, piece_hash, num_order_in_file):
    Fetch_Data = {}
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
        Fetch_Data[f"{file_name}_piece{num_order_in_file}"] = f"{peers_ip}:{peer_port}"
    except Exception as e:
        print(f"An error occurred while connecting to peer at {peers_ip}:{peer_port} - {e}")
    finally:
        peer_sock.close()
    return Fetch_Data

def fetch_file(sock,peers_port,file_name, piece_hash, num_order_in_file):
    Fetch_Information = {"Data":{},"Response":""}
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
                            Fetch_Information["Data"] = request_file_from_peer(peers_info[index]['peers_ip'], peers_info[index]['peers_port'], peers_info[index]['file_name'],peers_info[index]['piece_hash'],peers_info[index]['num_order_in_file'])
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
                        Fetch_Information["Data"] = request_file_from_peer(peers_info[index]['peers_ip'], peers_info[index]['peers_port'], peers_info[index]['file_name'],peers_info[index]['piece_hash'],peers_info[index]['num_order_in_file'])
            
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
                Fetch_Information["Response"] = f"Create file {file_name} successful"
            else:
                print(f"Not enough piece to create file {file_name}")
                Fetch_Information["Response"] = f"Not enough piece to create file {file_name}"
        else:
            print("No hosts have the file.")
            Fetch_Information["Response"] = f"No hosts have the file."
    else:
        print("No peers have the file or you had this file.")
        Fetch_Information["Response"] = f"No peers have the file or you had this file."
    return Fetch_Information

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
        sock.settimeout(1)
        sock.connect((server_host, server_port))
        peers_hostname = socket.gethostname()
        host_service_thread = threading.Thread(target=start_host_service, args=(peers_port, './'))
        host_service_thread.start()
        sock.sendall(json.dumps({'action': 'introduce', 'peers_hostname': peers_hostname, 'peers_port': peers_port}).encode() + b'\n')
        return sock
    except (socket.error, ConnectionRefusedError) as e:
        print(f"Unable to connect to server: {e}")
        return None

def check_server(sock):
    try:
        # Gửi một thông điệp kiểm tra
        command = {
                "action": "check",
            } 
        sock.sendall(json.dumps(command).encode() + b'\n')                    
        response = sock.recv(4096).decode()
        if 'ServerOn' not in response:
            return "NotResponse"
        else:
            return "Okay"
    except socket.error:
        print("\nThe main server is down, if you want to connect to the backup server, enter reconnect.")
        return "Fail"
        
def Command_Handler(user_input:str,peers_port:int,sock):
    
    command_parts = shlex.split(user_input)
    if len(command_parts) >= 2 and command_parts[0].lower() == 'publish':
        command = {
            "action": "check",
        } 
        sock.sendall(json.dumps(command).encode() + b'\n')                    
        sock.recv(4096).decode()
        # sock.sendall("check".encode())                    
        # response = sock.recv(4096).decode()
        Publish_File_Information = {}
        for file_name in command_parts[1:]:
            Publish_File_Information[file_name] = {"Status":True,"Information":{}}
            if check_local_files(file_name):
                Publish_File_Information[file_name]["Status"] = True
                piece_size = 524288  # 524288 byte = 512KB
                file_size = os.path.getsize(file_name)
                pieces = split_file_into_pieces(file_name,piece_size)
                Publish_File_Information[file_name]["Information"] = handle_publish_piece(sock, peers_port, pieces, file_name,file_size,piece_size)

            elif (pieces := check_local_piece_files(file_name)):
                Publish_File_Information[file_name]["Status"] = True
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
                    
                Publish_File_Information[file_name]["Information"] = handle_publish_piece(sock, peers_port, pieces, file_name,file_size,piece_size)
            else:
                Publish_File_Information[file_name]["Status"] = False
                print(f"Local file {file_name}/piece does not exist.")
        return Publish_File_Information
    elif len(command_parts) >= 2 and command_parts[0].lower() == 'fetch':
        command = {
            "action": "check",
        } 
        sock.sendall(json.dumps(command).encode() + b'\n')                    
        sock.recv(4096).decode()
        # sock.sendall("check".encode())                    
        # response = sock.recv(4096).decode()
        Fetch_Response = {}
        for file_name in command_parts[1:]:
            pieces = check_local_piece_files(file_name)
            pieces_hash = [] if not pieces else create_pieces_string(pieces)
            num_order_in_file= [] if not pieces else [item.split("_")[-1][5:] for item in pieces]
            Fetch_Response[file_name] = fetch_file(sock,peers_port,file_name, pieces_hash,num_order_in_file)
        return Fetch_Response

    elif user_input.lower() == 'exit':
        stop_event.set()  # Stop the host service thread
        sock.close()


def change_server():
    if Main_Server_Flag == True:
        Main_Server_Flag == False
        sock = connect_to_server(SERVER_HOST, BACKUP_SERVER_PORT,CLIENT_PORT)
    else:
        Main_Server_Flag == True
        sock = connect_to_server(SERVER_HOST, SERVER_PORT,CLIENT_PORT)
    return sock
if __name__ == "__main__":
    # Replace with your server's IP address and port number
    sock = connect_to_server(SERVER_HOST, SERVER_PORT,CLIENT_PORT)
    if sock==None:
        print("Cannot connect to server")
        messagebox.showerror(title="Error",message="Cannot connect to server")
    else:
        App = Client_UI(SSID = "client3", PassWord="1234",Client_Port=CLIENT_PORT,socket = sock)
        App.Start_UI()
