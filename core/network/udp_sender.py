import socket
import json


class UDPSender:
    def __init__(self, ip: str = "127.0.0.1", port: int = 5005):
        self.server_address = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    def send_dict(self, data: dict):
        try:
            json_data = json.dumps(data).encode('utf-8')
            self.sock.sendto(json_data, self.server_address)
        except Exception as e:
            print(f"[UDP Sender] Ошибка отправки JSON: {e}")