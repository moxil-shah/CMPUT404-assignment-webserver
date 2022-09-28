#  coding: utf-8
import socketserver

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
        self.data = self.data.decode("utf-8")  # decode from binary
        self.data = self.data.split(" ")  # make array from spaces
        # print(self.data)
        if self.data[0] == 'GET':  # only supported method is GET; all else status code 405
            self.handleGET()
            self.request.sendall(bytearray("OK", 'utf-8'))
        else:
            self.request.sendall(
                bytearray("HTTP/1.1 405 Method Not Allowed\r\n", 'utf-8'))

    def handleGET(self):
        # if last char is '/', then path is .../index.html
        if self.data[1][-1] == '/':
            path = './www'+self.data[1]+'/index.html' # default to index.html
            # print(path)
            contentType = "text/html"
        # if last 4 chars is 'html', then path is the path
        elif self.data[1][-4:] == "html":
            path = './www'+self.data[1]
            contentType = "text/html"
        # if last 3 chars is 'css', then path is the path
        elif self.data[1][-3:] == "css":
            path = './www'+self.data[1]
            contentType = "text/css"
         # invalid path; add '/' after path
        else:
            header301 = "HTTP/1.1 301 Moved Permanently\r\n"
            new_location = "Location: " + \
                self.data[1] + "/\r\n"  # notice the extra '/'
            self.request.sendall(bytearray(header301 + new_location, 'utf-8'))
            return

        # serve path

        # make sure path is actually legit
        try:
            f = open(path)
            content = f.read()
            f.close()

        # if not, then 404 status code
        except:
            thingsToSend = "HTTP/1.1 404 Not Found\r\n"

        # if yes, then serve it
        else:
            header200 = "HTTP/1.1 200 OK\r\n"
            fileType = "Content-Type: " + contentType + "\r\n"
            contentLen = "Content-Length: " + str(len(content)) + "\r\n\r\n"
            thingsToSend = header200 + fileType + contentLen + content
        # send it all
        finally:
            self.request.sendall(bytearray(thingsToSend, 'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
