#  coding: utf-8
import socketserver,os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        method,url = self.parseRequest(self.data.decode('utf-8'))

        if method!="GET":
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n\r\n405 Method Not Allowed",'utf-8'))
            return

        self.functions(method,url)

    def functions(self,method, url):
        split = url.split('/')
        level = 0

        for i in split:
            if i == "..":
                level = level -1
            else:
                level += 1
            if level < 0:
                self.request.sendall(bytearray(f"HTTP/1.1 404 Not Found\r\n\r\n404 Not Found",'utf-8'))
                return

        path = "./www"+ url
        print("path", path)

        if url[-1] != "/":
            if os.path.isdir(path):
                self.request.sendall(bytearray(f"HTTP/1.1 301 Moved Permanently\r\nLocation:{url+'/'}\r\n\r\n301 Moved Permanently",'utf-8'))
                return

        if not os.path.isfile(path):
                # The webserver can return index.html from directories (paths that end in /)
                if path[-1] == '/':
                    path += "index.html"
                else:  # The webserver can server 404 errors for paths not found
                    self.request.sendall(bytearray(f"HTTP/1.1 404 Not Found\r\n\r\n404 Not Found",'utf-8'))
                    return

        if os.path.exists(path):

            try:
                with open(path, 'r') as file:
                    content = file.read()
            except:
                self.request.sendall(bytearray(f"HTTP/1.1 404 Not Found\r\n\r\n404 Not Found",'utf-8'))
                return

            response = "HTTP/1.1 200 OK\r\n"
            response += "cache-control: no-cache\r\n"
            if ".css" in url:
                response += "content-type: {};charset=UTF-8\r\n".format("text/css")
            else:
                response += "content-type: {};charset=UTF-8\r\n".format("text/html")
            length = len(content)
            response += "content-length: {}\r\n\n".format(length)
            self.request.sendall(response.encode())
            return


        else:
            self.request.sendall(bytearray(f"HTTP/1.1 404 Not Found\r\n\r\n404 Not Found",'utf-8'))
            return



    def parseRequest(self, request):
        request = request.strip().split('\n')
        requestHTTP = request[0]  # GET / HTTP/1.1
        element = requestHTTP.split(' ')

        return (element[0], element[1])


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
