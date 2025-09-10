import json
import socket

class QtClient:
    _req_id = 1
    def __init__(self, host="127.0.0.1", port=5555, timeout=10000):
       self._sock = socket.create_connection((host, port), timeout)
       self._sock.settimeout(5)
    
    def __del__(self):
       self._sock.close()
        
    def _send_frame(self, obj):
      payload = json.dumps(obj, separators=(',', ':')).encode()
      frame = str(len(payload)).encode() + b'\n' + payload
      self._sock.sendall(frame)
      self._req_id += 1
    
    def _get_response(self, raise_on_timeout=True):
      header = b''
      try:
        while not header.endswith(b'\n'):
            header += self._sock.recv(1)
        length = int(header.strip())
        data = self._sock.recv(length)
        return data
      except TimeoutError as e:
        if raise_on_timeout:
           raise e
        return None

    def ping(self):
        self._send_frame({"id": self._req_id, "method": "ping"})
        return self._get_response(raise_on_timeout=False) is not None

    def roots(self):
        self._send_frame({"id": self._req_id, "method": "elements.roots"})
        return self._get_response()
  
    def app_info(self):
        self._send_frame({"id": self._req_id, "method": "app.info"})
        return self._get_response()
    
    def children(self, id):
        self._send_frame({"id": self._req_id, "method": "elements.children", "params": {"id": id}})
        return self._get_response()
      
    def element_info(self, id):
        self._send_frame({"id": self._req_id, "method": "elements.info", "params": {"id": id}})
        return self._get_response()
    
    def click(self, id):
        self._send_frame({"id": self._req_id, "method": "elements.click", "params": {"id": id}})
        if not json.loads(self._get_response())["result"]["ok"]:
          raise Exception

    def set_text(self, id, text):
        self._send_frame({"id": self._req_id, "method": "elements.setText", "params": {"id": id, "text": f"{text}"}})
        if not json.loads(self._get_response())["result"]["ok"]:
          raise Exception
