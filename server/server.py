import socketserver
import socket
import pickle
from dataclasses import dataclass, field


SERVER_ADDRESS = ("localhost", 9090)
CHATROOMS: dict[str: list] = {}


@dataclass(slots=True, frozen=True, kw_only=True)
class message:
	from_: str = field(default=socket.gethostbyname(socket.gethostname()))
	to_: str
	color: str = field(repr=False)
	symbol: str = field(repr=False)
	message: str


@dataclass(slots=True, frozen=True)
class server_message:
	message: str
	color: str = field(default="red")


@dataclass(slots=True, frozen=True)
class login_message:
	chatroom_ID: str
	client_name: str


class HandleClient(socketserver.BaseRequestHandler):
	
	def handle(self):
		print("new client connected")

		login_details = self.request.recv(1024)
		unpickled_login_details = pickle.loads(login_details)

		if (room:=unpickled_login_details.chatroom_ID) in CHATROOMS:
			CHATROOMS[room].append(self.request)
			print(f"client add to room {room}")
			msg = server_message(message=f"You have joined chatroom {room}")
		else:
			CHATROOMS[room] = []
			CHATROOMS[room].append(self.request)
			msg = server_message(message=f"Room {room} has been created!!")

		pickled_msg = pickle.dumps(msg)
		self.request.send(pickled_msg)

		self.server_broadcast(room, f"new client: {unpickled_login_details.client_name}")
		self.waiting_room(self.request)

	def waiting_room(self, client: "socket object")-> None:
		while True:
			
			msg = pickle.loads(client.recv(1024))
			self.client_broadcast(msg)

	def server_broadcast(self, chatroom_ID: str, message: str)-> None:
		message_to_be_sent = server_message(message=message)
		pickled_message = pickle.dumps(message_to_be_sent)
		
		print(f"server broading message to chatroom {chatroom_ID}")

		for client in CHATROOMS[chatroom_ID]:
			client.send(pickled_message)

	def client_broadcast(self, message_object: bytes)-> None:
		
		repickled_message = pickle.dumps(message_object)
		for client in CHATROOMS[message_object.to_]:
			client.send(repickled_message)


class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass


if __name__ == '__main__':
	server = Server(SERVER_ADDRESS, HandleClient)
	print("server is running")
	server.serve_forever()
