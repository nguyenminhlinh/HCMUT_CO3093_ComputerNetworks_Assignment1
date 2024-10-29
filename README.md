# HCMUT_CO3093_ComputerNetworks_Assignment1
# `Peer-to-Peer File-Sharing Application`

## Overview
Build a Simple Like-torrent application with application protocols defined by each group, using the TCP/IP protocol stack.

All descriptions and reports are included in the documentation
## Requirements 
- Python 3
- PostgreSQL installed on the Server machine 
- How to use PostgreSQL in https://www.w3schools.com/postgresql/ and dowload in https://www.postgresql.org/download/
- Install library `psycopg2` to connect in python
```
python3 -m pip install psycopg2
```
- Press enter until you get to the password, then enter the password as 12345678
![install sql](_img/image.png)
## Installation
Installation from source is straightforward:
```
$ git clone https://github.com/nguyenminhlinh/HCMUT_CO3093_ComputerNetworks_Assignment1.git
$ cd HCMUT_CO3093_ComputerNetworks_Assignment1
```
## Usage
1. Create database with SQL Shell (PostgreSQL) by file server/db.txt 
2. Start the central server:
   - $ cd server
   - Run the `server.py` script to start the central server. Ensure the server is running before proceeding with client actions.

3. Client Setup:
   - $ cd client1
   - $ cd client2
   - Edit the `SERVER_HOST`, `SERVER_PORT`, `CLIENT_PORT` setting in the `client.py` file to configure the IP for the central server. After that run the `client.py` script to start the client and connect to the central server.

## Features

1. The client has a simple command-shell interpreter that is used to accept two kinds of commands.
    - `publish file_name`: A set of local files on the client machine is divided into parts (size of each part is 512kb). Users can select pieces shared content to send information to the server.
    
    - `fetch file_name`: The server sends information about parts of files shared by peers that are not yet available to clients. Clients can choose any part to download. Once all parts are downloaded, they will be merged into one original file.

## Example
### Client1 publish Data.pdf on Server
#### Server side

```
\server> python server.py
2024-04-25 15:51:31,649 - INFO - Server started and is listening for connections.
Server command: 2024-04-25 15:51:35,938 - INFO - Active connections: 2
2024-04-25 15:51:35,938 - INFO - Connection established with linh/192.168.56.1:65433)
2024-04-25 15:51:41,464 - INFO - Active connections: 3
2024-04-25 15:51:41,472 - INFO - Connection established with linh/192.168.56.1:65434)
2024-04-25 15:52:03,987 - INFO - Updating client info in database for hostname: linh/192.168.56.1:65433
2024-04-25 15:52:03,992 - INFO - Database update complete for hostname: linh/192.168.56.1:65433
```

#### Client side
Client 1 push piece 1,2,4,5,6
```
\client1> python client.py
Enter command (publish file_name/ fetch file_name/ exit): publish Data.pdf
File Data.pdf have ['Data.pdf_piece1', 'Data.pdf_piece2', 'Data.pdf_piece3', 'Data.pdf_piece4', 'Data.pdf_piece5', 'Data.pdf_piece6']
 piece: ["b'\\xe1\\xd8\\\\r\\xa2\\t\\xee\\x0c\\xfd91\\x12\\xedkk\\xf1u\\x03\\x9b\\x14'", "b'\\x14\\xab\\x0eC\\xb1mi\\xfb\\x9c\\xcd\\x19\\x90*\\xcez\\xbc\\xe3\\r!\\x1f'", "b'\\xb4\\x9bo\\n\\xbdG|l^\\xd9\\x99\\xa5\\xd0?\\xf8\\xe8\\xabsY|'", "b'\\n\\xb2\\x04Z\\x87\\xd1R\\xb1$\\x13\\xdai\\x1500A\\xeb\\xdbN\\xf1'", "b'1\\xb4\\xe9l\\x9c\\x8cH\\x02\\x91\\xe2\\x1c\\xd6\\xf8{\\x0bX\\xd8#\\xa19'", "b'X\\x94!g\\xa9\\xc6\\xe4S\\x1b\\x89NS\\xe0\\xce\\x03\\xc9\\xed\\xd3x\\x98'"].
Please select num piece in file to publish:1 2 4 5 6
You was selected:
Number 1 : b'\xe1\xd8\\r\xa2\t\xee\x0c\xfd91\x12\xedkk\xf1u\x03\x9b\x14'
Number 2 : b'\x14\xab\x0eC\xb1mi\xfb\x9c\xcd\x19\x90*\xcez\xbc\xe3\r!\x1f'
Number 4 : b'\n\xb2\x04Z\x87\xd1R\xb1$\x13\xdai\x1500A\xeb\xdbN\xf1'
Number 5 : b'1\xb4\xe9l\x9c\x8cH\x02\x91\xe2\x1c\xd6\xf8{\x0bX\xd8#\xa19'
Number 6 : b'X\x94!g\xa9\xc6\xe4S\x1b\x89NS\xe0\xce\x03\xc9\xed\xd3x\x98'
File list updated successfully.
Enter command (publish file_name/ fetch file_name/ exit):
```

### Client2 publish Data.pdf on Server
#### Server side

```
\server> python server.py
2024-04-25 15:51:31,649 - INFO - Server started and is listening for connections.
Server command: 2024-04-25 15:51:35,938 - INFO - Active connections: 2
2024-04-25 15:51:35,938 - INFO - Connection established with linh/192.168.56.1:65433)
2024-04-25 15:51:41,464 - INFO - Active connections: 3
2024-04-25 15:51:41,472 - INFO - Connection established with linh/192.168.56.1:65434)
2024-04-25 15:52:03,987 - INFO - Updating client info in database for hostname: linh/192.168.56.1:65433
2024-04-25 15:52:03,992 - INFO - Database update complete for hostname: linh/192.168.56.1:65433
```

#### Client side
Client 2 push piece 1,3,4,5,6
```
\client1> python client.py
Enter command (publish file_name/ fetch file_name/ exit): publish Data.pdf
File Data.pdf have ['Data.pdf_piece1', 'Data.pdf_piece2', 'Data.pdf_piece3', 'Data.pdf_piece4', 'Data.pdf_piece5', 'Data.pdf_piece6']
 piece: ["b'\\xe1\\xd8\\\\r\\xa2\\t\\xee\\x0c\\xfd91\\x12\\xedkk\\xf1u\\x03\\x9b\\x14'", "b'\\x14\\xab\\x0eC\\xb1mi\\xfb\\x9c\\xcd\\x19\\x90*\\xcez\\xbc\\xe3\\r!\\x1f'", "b'\\xb4\\x9bo\\n\\xbdG|l^\\xd9\\x99\\xa5\\xd0?\\xf8\\xe8\\xabsY|'", "b'\\n\\xb2\\x04Z\\x87\\xd1R\\xb1$\\x13\\xdai\\x1500A\\xeb\\xdbN\\xf1'", "b'1\\xb4\\xe9l\\x9c\\x8cH\\x02\\x91\\xe2\\x1c\\xd6\\xf8{\\x0bX\\xd8#\\xa19'", "b'X\\x94!g\\xa9\\xc6\\xe4S\\x1b\\x89NS\\xe0\\xce\\x03\\xc9\\xed\\xd3x\\x98'"].
Please select num piece in file to publish:1 3 4 5 6
You was selected:
Number 1 : b'\xe1\xd8\\r\xa2\t\xee\x0c\xfd91\x12\xedkk\xf1u\x03\x9b\x14'
Number 3 : b'\xb4\x9bo\n\xbdG|l^\xd9\x99\xa5\xd0?\xf8\xe8\xabsY|'
Number 4 : b'\n\xb2\x04Z\x87\xd1R\xb1$\x13\xdai\x1500A\xeb\xdbN\xf1'
Number 5 : b'1\xb4\xe9l\x9c\x8cH\x02\x91\xe2\x1c\xd6\xf8{\x0bX\xd8#\xa19'
Number 6 : b'X\x94!g\xa9\xc6\xe4S\x1b\x89NS\xe0\xce\x03\xc9\xed\xd3x\x98'
File list updated successfully.
Enter command (publish file_name/ fetch file_name/ exit):
```

### Client3 fetch Data.pdf 
#### Server side

```
\server> python server.py
2024-04-25 15:51:31,649 - INFO - Server started and is listening for connections.
Server command: 2024-04-25 15:51:35,938 - INFO - Active connections: 2
2024-04-25 15:51:35,938 - INFO - Connection established with linh/192.168.56.1:65433)
2024-04-25 15:51:41,464 - INFO - Active connections: 3
2024-04-25 15:51:41,472 - INFO - Connection established with linh/192.168.56.1:65434)
2024-04-25 15:52:03,987 - INFO - Updating client info in database for hostname: linh/192.168.56.1:65433
2024-04-25 15:52:03,992 - INFO - Database update complete for hostname: linh/192.168.56.1:65433
```

#### Client side
Client3 fetch file Data.pdf. It select pieces between client 1 and client 2 follow algorithm I define myself:
   - Piece of file: Data.pdf_piece2 has been fetched from peer192.168.56.1:65433.
   - Piece of file: Data.pdf_piece3 has been fetched from peer192.168.56.1:65434.
   - Piece of file: Data.pdf_piece4 has been fetched from peer192.168.56.1:65433.
   - Piece of file: Data.pdf_piece5 has been fetched from peer192.168.56.1:65434.
   - Piece of file: Data.pdf_piece6 has been fetched from peer192.168.56.1:65433.
   - Create file Data.pdf successful
```
Enter command (publish file_name/ fetch file_name/ exit): fetch Data.pdf
No peers have the file or the response format is incorrect.
Enter command (publish file_name/ fetch file_name/ exit): exit
PS D:\OneDrive - zb87w\STUDY\Ki6\Mang_may_tinh\2024\ass1\HCMUT_CO3093_ComputerNetworks_Assignment1\client3> python client.py
Enter command (publish file_name/ fetch file_name/ exit): fetch Data.pdf
Hosts with the file Data.pdf:
Number: 2 linh/192.168.56.1:65433 piece_hash: b'\x14\xab\x0eC\xb1mi\xfb\x9c\xcd\x19\x90*\xcez\xbc\xe3\r!\x1f' num_order_in_file: 2
Number: 4 linh/192.168.56.1:65433 piece_hash: b'\n\xb2\x04Z\x87\xd1R\xb1$\x13\xdai\x1500A\xeb\xdbN\xf1' num_order_in_file: 4
Number: 5 linh/192.168.56.1:65433 piece_hash: b'1\xb4\xe9l\x9c\x8cH\x02\x91\xe2\x1c\xd6\xf8{\x0bX\xd8#\xa19' num_order_in_file: 5
Number: 6 linh/192.168.56.1:65433 piece_hash: b'X\x94!g\xa9\xc6\xe4S\x1b\x89NS\xe0\xce\x03\xc9\xed\xd3x\x98' num_order_in_file: 6
Number: 3 linh/192.168.56.1:65434 piece_hash: b'\xb4\x9bo\n\xbdG|l^\xd9\x99\xa5\xd0?\xf8\xe8\xabsY|' num_order_in_file: 3
Number: 4 linh/192.168.56.1:65434 piece_hash: b'\n\xb2\x04Z\x87\xd1R\xb1$\x13\xdai\x1500A\xeb\xdbN\xf1' num_order_in_file: 4
Number: 5 linh/192.168.56.1:65434 piece_hash: b'1\xb4\xe9l\x9c\x8cH\x02\x91\xe2\x1c\xd6\xf8{\x0bX\xd8#\xa19' num_order_in_file: 5
Number: 6 linh/192.168.56.1:65434 piece_hash: b'X\x94!g\xa9\xc6\xe4S\x1b\x89NS\xe0\xce\x03\xc9\xed\xd3x\x98' num_order_in_file: 6
6
Piece of file: Data.pdf_piece2 has been fetched from peer192.168.56.1:65433.
Piece of file: Data.pdf_piece3 has been fetched from peer192.168.56.1:65434.
Piece of file: Data.pdf_piece4 has been fetched from peer192.168.56.1:65433.
Piece of file: Data.pdf_piece5 has been fetched from peer192.168.56.1:65434.
Piece of file: Data.pdf_piece6 has been fetched from peer192.168.56.1:65433.
Create file Data.pdf successful
Enter command (publish file_name/ fetch file_name/ exit):
```