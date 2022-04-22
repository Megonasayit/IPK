#!/usr/bin/env python3
import argparse
import re
import socket
from urllib.parse import urlparse

def copyfile(filename):
    request = "GET " + filename + " FSP/1.0\n" 
    request += "Hostname: " + SURL.netloc + " \n"
    request += "Agent: xhrmor00\n\n"
    sock.send(request.encode())

    if(filename.find('/')):
        filename = ' '.join(filename.split('/')[-1:])

    is_header = True
    with open(filename, 'wb') as f:
        while True:
            data = sock.recv(10000)
            
            if is_header:
                if(data.find(bytes("Not Found", 'UTF-8')) != -1):
                    print("File not found")
                    sock.close()
                    exit(1)

                is_header = False
                continue
                
            if not data:
                break
            
            f.write(data)
    f.close()
    return

def whereIs(address):
    request = "WHEREIS " + SURL.netloc
    sock.sendto(request.encode(), address)
    result, address = sock.recvfrom(1024)
    result = result.decode('UTF-8')
    if(result[0] != 'O') & (result[1] != 'K'):
        print("Connection error")
        sock.close()
        exit(1)
    return result[3:]
try:
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", help = "ip address and port of the server")
    parser.add_argument("-f", help = "SURL of file")
    args = parser.parse_args()

    ip_regex = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{1,5}$")
    SURL_regex = re.compile(r"^fsp://([a-zA-Z._-]+)(/[^/ ]+)+/?$")

    if args.n is None or args.f is None:
        exit(1)
        
    m = re.match(ip_regex,args.n)
    f = re.match(SURL_regex, args.f)

    if m is None:
        print("n is wrong")
        exit(1)
    if f is None:
        print("f is wrong")
        exit(1)

    SURL = urlparse(args.f)
    path = SURL.path[1:]

    ipPort = args.n.split(":")
    address = (ipPort[0], int(ipPort[1]))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(120)
    tcpAddr = whereIs(address)

    tcpAddr = tcpAddr.split(":")
    tcpAddress = (tcpAddr[0], int(tcpAddr[1]))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(tcpAddress)

    if(path == "*"):
        copyfile("index")
        sock.close()

        with open("index") as index:
            for line in index:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(tcpAddress)
                copyfile(line[:-1])
                sock.close()
    else:
        copyfile(path)
        sock.close()
except:
    exit(1)
