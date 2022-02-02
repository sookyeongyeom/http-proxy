import os
import sys
import socket
import argparse
import selectors

sel = selectors.DefaultSelector()
conn_list = []


def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    conn_list.append(conn)
    print(f">> [Socket {conn_list.index(conn)}] Connected! : {conn}\n")
    print(f"* * * Connection List * * *")
    for index, c in enumerate(conn_list):
        print(f"[Socket {index}] {c}")
    print("* * * * * * * * * * * * * *\n")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)


def read(conn, mask):
    req = conn.recv(65535)
    if req:
        req = req.decode()  # 요청 패킷 가져와서 디코딩

        # telnet에서 엔터쳤을 때 IndexError방지
        try:
            msg = req.split()[0]  # 메소드
            url = req.split()[1]  # url
        except:
            info = "[!] Send some Request!\n"
            info = info.encode()
            conn.send(info)
            return

        try:
            index = '/'.join(url.split("/")[3:])  # 파일경로
            root = url.split("/")[2]  # IP/도메인
        except:
            index = ''
            root = url.split("/")[2]

        if(msg != "GET"):  # GET이 아닌 경우
            if(msg in http):
                info = "[!] Not Implemented(501)!\n"
            else:
                info = "[!] Bad Request(400)!\n"
            print(f"[Socket {conn_list.index(conn)}] {info}")
            info = info.encode()
            conn.send(info)
            print(">> Keep going...\n")
            return
        else:  # GET인 경우
            print(f"* * * Request From [Socket {conn_list.index(conn)}] * * *")
            print(req)
            print("* * * * * * * * * * * * * * * * * *\n")

            #root + index
            target = root+"/"+index

            # Cache가 있는 경우
            if(target in cache):
                get = cache[target]
                get = get.replace("$$$", ":")
                get = get.replace("###", "{")
                get = get.replace("@@@", ",")
                get = get.encode()
                conn.sendall(get)
                print(f">> [Socket {conn_list.index(conn)}] Cache Sent!\n")
                return

            # 절대경로 -> 상대경로
            new_req = f"GET /{index} HTTP/1.1\r\nHost: {root}\r\nConnection: close\r\n\r\n"
            new_req = new_req.encode()

            # 오리진 서버와 연결하기 위한 소켓 생성
            s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                host = socket.gethostbyname(f"{root}")
            except:
                info = "[!] There's no such Host!\n"
                print(info)
                info = info.encode()
                conn.send(info)
                print(">> Keep going...\n")
                return
            host_port = 80
            s2.connect((host, host_port))

            # 오리진 서버에 요청 패킷 전송
            s2.sendall(new_req)
            value = ""  # 응답 패킷 내용을 저장할 빈 문자열
            bad = False

            while True:
                res = s2.recv(65535)  # 응답 가져오기
                if not res:
                    break
                # 응답 패킷을 Cache 사전에 저장하기 위해 디코딩
                deco = res.decode()
                deco = deco.replace(":", "$$$")
                deco = deco.replace("{", "###")
                deco = deco.replace(",", "@@@")
                value += deco  # 문자열에 패킷 내용 저장
                if(deco.split()[1] == "400"):
                    info = "[!] Bad Request(400)!\n"
                    print(f"[Socket {conn_list.index(conn)}] {info}")
                    info = info.encode()
                    conn.send(info)
                    bad = True
                    break
                # 응답 패킷을 사용자에게 전송
                conn.sendall(res)
            print(f">> [Socket {conn_list.index(conn)}] Send Success!\n")

            if(bad):
                print(">> Keep going...\n")
                return

            # Cache 저장
            cache[target] = value
            print(">> New Cache Written!\n")
            print("* * * Cache List * * *")
            for index, key in enumerate(cache.keys()):
                print(f"{index+1}. {key}")
            print("* * * * * * * * * * *")
            print("\n>> Keep going...\n")

    else:
        print(f">> [Socket {conn_list.index(conn)}] Socket Closed! : {conn}\n")
        conn_list[conn_list.index(conn)] = "Closed"
        print(f"* * * Connection List * * *")
        for index, c in enumerate(conn_list):
            print(f"[Socket {index}] {c}")
        print("* * * * * * * * * * * * * *\n")
        sel.unregister(conn)
        conn.close()


# 커맨드로부터 포트번호 받기
parser = argparse.ArgumentParser()
parser.add_argument('-p', type=int, help="port number")
args = parser.parse_args()
my_port = args.p
if(my_port):
    pass
else:
    print("")
    print("[!] python <file.py> -p <port> 형식으로 접속해주세요!")
    sys.exit()

# 터미널창 비우기
os.system('cls')
print("Proxy Started\n")

# Cache 사전
cache = {}
# HTTP 메소드 종류
http = ["GET", "POST", "DELETE", "PUT", "PATCH", "HEAD", "OPTION", "TRACE"]

# 사용자와 연결하기 위한 소켓 생성
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', my_port))
sock.listen(10)  # 리슨
print(f">> [Port {my_port}] Listening...\n")
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)
