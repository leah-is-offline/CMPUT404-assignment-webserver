#  coding: utf-8 


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


import socketserver
from pathlib import Path
import json
import os

class MyWebServer(socketserver.BaseRequestHandler):

    '''
    defines how to handle incoming requests "request comes in, server inspects requestm dispatches request to a designated handler"
    #the most basic handler serves a static file
    #when I go the website (url im hosting on) i want to see the file that i served mself
    '''
 
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        #print("Got request: %s\n" % self.data)
        decoded = self.data.decode('utf-8')
        decoded = decoded.split('\r\n')

        if len(decoded) > 0 :
            request = decoded[0]
            self.parseRequest(request)
        else:
            self.reply("404", "Invalid request", "YOUR REQUEST WAS INVALIIIIIIIIIIIIDDDD")


    def parseRequest(self,request):
        #method to parse get components of request
        #better way of doing this than parsing?
        request = request.split()
        #print(request)
        
        if (len(request) > 2):
            method, requested_path ,scheme = request[0], request[1], request[2]
            if "GET" not in method:
                self.reply("405","Invalid request method", "ONLY GETS ALLOWED")
            else:
                self.genPath(requested_path)
        else:
            self.reply("405", "Method Not Allowed", None)
        
        
   
    def reply(self, status_code, message, body):
        # citation: https://www.w3schools.com/charsets/ref_utf_symbols.asp
        # function that replies to a request
        coffee='&#9749;'
        snowman = '&#9924;'
        smiley = '&#9786;'
        pointing = '&#9758;'
        knight = '&#9822;'

        reply = 'HTTP/1.1 {sc} {m}\r\n\r\n'.format(sc = status_code,m = message)
       

        if status_code == '301':
            icon = '<html><body><center><h1>get out of here{icon}</p></center></body></html>\r\n\r\n'.format(icon = pointing)
        elif status_code == '404':
            icon = '<html><body><center><h1>{icon}and that is ok</p></center></body></html>\r\n\r\n'.format(icon = smiley)
        elif status_code == '405':
            icon = '<html><body><center><h1>{icon}</p></center></body></html>\r\n\r\n'.format(icon = knight)
        else:
            icon = '<html><body><center><h1>{icon}</p></center></body></html>\r\n\r\n'.format(icon = coffee)
        

        if body is not None:
            reply += '<html><body><center><h4>{b}</p></center></body></html>'.format(b = body)
        reply+=icon
       
        encoded_reply = reply.encode('utf-8')
        self.request.sendall(encoded_reply)
            
        
    def genPath(self, req_path):
        # function to decide valid response from provided path
        base = os.path.abspath("www")
        full_path = base + req_path
        #print(full_path)
        
        
        if base not in os.path.abspath(full_path):     
            self.reply("404", "Not Found" ,None)
            return

        if os.path.exists(full_path):            
            if os.path.isdir(full_path):

                if (not req_path.endswith("/")):
                    self.reply("301", "Page Moved", 'Moved To: localhost:8080/{}/'.format(rq = req_path))
                    return

            if req_path[-1] == "/":
                if "html" not in req_path:
                    full_path += "index.html"

            page = self.readFile(full_path)
            mimetype = self.getMimeType(full_path)
            self.respond(mimetype, page)
        else:
            self.reply("404", "Not Found", None)
            return


    def getMimeType(self,full_path):
       # function to set mimetype
        if "css" in full_path:
            mimetype = "text/css"
        else:
            mimetype ="text/html"
        return mimetype
        

    def readFile(self, full_path):
        # function to read and close the appropriate file
        if os.path.exists(full_path):
            f = open(full_path, "r")
            page = f.read()
            f.close()
            return page
        else:
            self.reply("404", "Page Not Found", None)
            

    def respond(self, mimetype, page):
        # function to respond with file contents
        response = 'HTTP/1.1 200 OK\r\n'
        response += 'Allow: GET\r\nContent-Type: {mt}\r\n'.format(mt = mimetype)
        response += 'Connection: close\r\n\r\n{rp}'.format(rp=page)
        self.request.sendall(response.encode('utf-8'))



if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 8080 #TCP addresses are defined by an ip address and a port number

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    
    server = socketserver.TCPServer((HOST, PORT), MyWebServer) #this is a TCP server whi takes a TCP address and a handler

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever() # starts the server and begins listening and responding to incoming requests.
