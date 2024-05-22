import socket
import re
import select

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 8000

# Please put your code in this file
print("Serving HTTP on port 8000")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

server.bind((SERVER_ADDRESS, SERVER_PORT))

server.listen()

def connect_clients():
    current = []
    new_connections_to_read,w,e = select.select([server] , [], [],0.0)
    for connection in new_connections_to_read:
        socket_connection,address_and_port = server.accept()

        current.append(socket_connection)

    return current


#returns encoded html response
def handle_html_response(response,file_path,http_response_code):
    with open(file_path,'r') as file:
        data = file.read()

    data = data.encode("utf-8")

    response+= f'{http_response_code}\r\n'
    response += 'Content-Type: text/html; charset=utf-8\r\n'
    response += 'Content-Length: {}\r\n'.format(len(data))
    #response+= 'Connection: keep-alive\r\n'
    #response+= 'Keep-Alive: timeout=3, max=100\r\n'
    response += '\r\n'

    data = data.decode("utf-8")
    response += data

    response = response.encode("utf-8")

    return response

clients = []

while True:

    # Accept a connection
    clients.extend(connect_clients())
    rdlist, wrlist, exlist = select.select(clients, clients,[],0.0)
    for client_socket in rdlist:

    # Receive the request data

        request_data = client_socket.recv(1000000)
        print(f'Request data:\n{request_data.decode("utf-8")}')

        request_data = request_data.decode("utf-8")

        lines = request_data.split('\r\n')



        status_line = lines[0]

        method,uri,http_version = status_line.split(" ")
        
        response = "HTTP/1.1 "

    
        body = ""

        if method=="GET":
            if uri =="/" or uri.endswith("html"):
                
                data = ""

                try:
                    file_path = './data{}'.format(uri)
                    
                    if uri =="/":
                        file_path = './data/index.html'

                    response = handle_html_response(response,file_path,"200 OK")

                except FileNotFoundError: 
                    response =  handle_html_response(response,"./data/404.html","404 Not Found")
                

                finally:
                    client_socket.send(response)

            #handle jpeg files
            elif uri.endswith("jpeg") or uri.endswith("jpg"):
                data = ""

                try:
                    with open('./data{}'.format(uri),'rb') as file:
                        data = file.read()

                    response+= '200 OK\r\n'
                    response += 'Content-Type: image/jpeg; charset=utf-8\r\n'
                    response += 'Content-Length: {}\r\n'.format(len(data))
                    #response+= 'Connection: keep-alive\r\n'
                    #response+= 'Keep-Alive: timeout=3, max=100\r\n'
                    response += '\r\n'

                    response = response.encode("utf-8")
                    client_socket.send(response)
                    client_socket.send(data)


                except FileNotFoundError:
                    response = handle_html_response(response,"./data/404.html","404 Not Found")
                    client_socket.send(response)
    

            #invalid URI return error
            else:
                response = handle_html_response(response,"./data/404.html","404 Not Found")
                client_socket.send(response)

        
        

        elif method=="POST":
            if "/data" in uri:

                params = request_data[request_data.find("description"):]

                desc,url = params.split("&")

                title,desc= desc.split("=")

                title,url = url.split("=")

                url = url.replace("%2F","/")


                #params are empty
                if len(desc) == 0 or len(url) ==0:

                    response = handle_html_response(response,"./data/400.html","400 Bad Request")

                    client_socket.send(response)

                #change conetens of personal_cats with post data
                else:

                    with open("./data/personal_cats.html","r") as file:
                        content = file.read()

                    match = r'(<img\s+[^>]*src =")([^"]*)("[^>]*>)'
                    replace = r'\1' + url + r'\3'

                    content = re.sub(match,replace,content)


                    with open("./data/personal_cats.html","w") as file:
                        file.write(content)

                    response = handle_html_response(response,"./data/success.html","201 Created")
                    client_socket.send(response)


            else:
                response = handle_html_response(response,"./data/404.html","404 Not Found")
                client_socket.send(response)
                
