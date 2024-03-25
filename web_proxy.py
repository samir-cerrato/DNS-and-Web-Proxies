#!/usr/bin/python3
#
# Wesleyan University
# COMP 332
# Homework 3: Simple multi-threaded web proxy

# Usage:
#   python3 web_proxy.py <proxy_host> <proxy_port> <requested_url>

# Python modules
import socket
import sys
import threading

# Project modules
import http_constants as const
import http_util


class WebProxy():

    def __init__(self, proxy_host, proxy_port):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_backlog = 1
        self.cache = {}
        self.start()

    def start(self):

        # Initialize server socket on which to listen for connections
        try:
            proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_sock.bind((self.proxy_host, self.proxy_port))
            proxy_sock.listen(self.proxy_backlog)
        except OSError as e:
            print ("Unable to open proxy socket: ", e)
            if proxy_sock:
                proxy_sock.close()
            sys.exit(1)

        # Wait for client connection
        while True:
            conn, addr = proxy_sock.accept()
            print ('Client has connected', addr)
            thread = threading.Thread(target = self.serve_content, args = (conn, addr))
            thread.start()

    def serve_content(self, conn, addr):

        # Receive binary request from client
        bin_req = conn.recv(4096)
        try:
            str_req = bin_req.decode('utf-8')
            print(str_req)
        except ValueError as e:
            print ("Unable to decode request, not utf-8", e)
            conn.close()
            return

        # Extract host and path
        hostname = http_util.get_http_field(str_req, 'Host: ', const.END_LINE)
        pathname = http_util.get_http_field(str_req, 'GET ', ' HTTP/1.1')
        if hostname == -1 or pathname == -1:
            print ("Cannot determine host")
            conn.close()
            return
        elif pathname[0] != '/':
            [hostname, pathname] = http_util.parse_url(pathname)
        str_req = http_util.create_http_req(hostname, pathname)

        # Open connection to host and send binary request
        url = hostname + pathname
        if url in self.cache:
            print(f"Cache hit for URL: {url}")
            cached_response = self.cache[url]
            if 'Last-Modified' in cached_response:
            # Modify the client's GET request to a conditional GET request
                conditional_get_req = f"GET {pathname} HTTP/1.1\r\nHost: {hostname}\r\n"
                conditional_get_req += f"If-Modified-Since: {cached_response['Last-Modified']}\r\n\r\n"
                bin_req = conditional_get_req.encode('utf-8')
                print("Sending conditional GET request to web server:", conditional_get_req)
            else:
                print(f"No Last-Modified date found for cached response. Forwarding cached response to client...")
                # Forward the cached response to the client
                conn.sendall(cached_response['response'])
                conn.close()
                return

        bin_req = str_req.encode('utf-8')
        try:
            web_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            web_sock.connect((hostname, 80))
            print ("Sending request to web server: ", str_req)
            web_sock.sendall(bin_req)
        except OSError as e:
            print ("Unable to open web socket: ", e)
            if web_sock:
                web_sock.close()
            conn.close()
            return

        # Wait for response from web server
        bin_reply = b''
        while True:
            more = web_sock.recv(4096)
            if not more:
                 break
            bin_reply += more
        
        # If the response is 304 Not Modified, forward the cached response to the client
        if "304 Not Modified" in bin_reply.decode('utf-8'):
            print("Received 304 Not Modified response from web server.")
            # Forward the cached response to the client
            conn.sendall(cached_response['response'])
        else:
            # Store response in cache
            self.cache[url] = {'response': bin_reply}
            print(f"Response stored in cache for URL: {url}")
            # Forward web server response to client
            conn.sendall(bin_reply)


        # Send web server response to client
        print('Proxy received from server (showing 1st 300 bytes): ', bin_reply[:300])
        conn.sendall(bin_reply)

        # Close connection to client
        conn.close()

def main():

    print (sys.argv, len(sys.argv))

    proxy_host = 'localhost'
    proxy_port = 50008

    if len(sys.argv) > 1:
        proxy_host = sys.argv[1]
        proxy_port = int(sys.argv[2])

    web_proxy = WebProxy(proxy_host, proxy_port)

if __name__ == '__main__':

    main()