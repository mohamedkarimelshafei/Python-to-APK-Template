import socket
import select

REMOTE_IP = "mytv2.duckdns.org"
REMOTE_PORT = 9000

LOCAL_IP = "127.0.0.1"
LOCAL_PORT = 19999

BUF_SIZE = 4096

def main():
    # --- TCP socket ---
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setblocking(False)
    try:
        tcp_sock.connect((REMOTE_IP, REMOTE_PORT))
    except BlockingIOError:
        # Non-blocking connect in progress
        pass
    print(f"TCP connecting to {REMOTE_IP}:{REMOTE_PORT}")

    # --- UDP socket ---
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setblocking(False)
    local_addr = (LOCAL_IP, LOCAL_PORT)
    print(f"UDP will send to {LOCAL_IP}:{LOCAL_PORT}")

    while True:
        rlist = [tcp_sock, udp_sock]
        readable, _, _ = select.select(rlist, [], [], 0.001)  # 1ms timeout

        for s in readable:
            # TCP → UDP
            if s is tcp_sock:
                try:
                    data = tcp_sock.recv(BUF_SIZE)
                    if not data:
                        print("TCP closed")
                        tcp_sock.close()
                        return
                    udp_sock.sendto(data, local_addr)
                except BlockingIOError:
                    pass
                except Exception as e:
                    print("TCP error:", e)
                    tcp_sock.close()
                    return

            # UDP → TCP
            elif s is udp_sock:
                try:
                    data, addr = udp_sock.recvfrom(BUF_SIZE)
                    if data:
                        tcp_sock.sendall(data)
                except BlockingIOError:
                    pass
                except Exception as e:
                    print("UDP error:", e)

if __name__ == "__main__":
    main()
