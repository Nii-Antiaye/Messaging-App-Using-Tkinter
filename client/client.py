import socket
import pickle
from dataclasses import dataclass, field
from tkinter import messagebox, PhotoImage, Frame, Canvas
import customtkinter
import emoji
from threading import Thread
import PIL


customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("green")
SERVER_ADDRESS = ("localhost", 9090)


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
	color: str


@dataclass(slots=True, frozen=True)
class login_message:
	chatroom_ID: str
	client_name: str


def server_connect(details: tuple[str])-> "socket object":
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(SERVER_ADDRESS)

	login_details = login_message(chatroom_ID=details[-1], client_name=details[0])
	pickled_login_details = pickle.dumps(login_details)

	sock.send(pickled_login_details)
	
	server_message = sock.recv(1024)
	server_message = pickle.loads(server_message)

	messagebox.showinfo(title="Chatroom", message=server_message.message)
	return (*details, sock)


def connecting_server()-> tuple[str]:

	returned_tuple = []
	def connect()-> None:
		
		if name_entry.get()=="" or chatroom_ID_entry.get()=="":
			messagebox.showerror(title="Connecting Error", message="Kindly fill all the fields")
			return

		returned_tuple.append(name_entry.get())
		returned_tuple.append(color_entry.get())
		returned_tuple.append(symbol_entry.get())
		returned_tuple.append(chatroom_ID_entry.get())
		connect_window.destroy() 
	

	connect_window = customtkinter.CTk()
	connect_window.title("Message App")
	connect_window.geometry("380x420")
	connect_window.resizable(False, False)
	connect_window.columnconfigure(0, weight=1)

	welcome_lbl = customtkinter.CTkLabel(connect_window, text="Welcome", font=("normal", 20))
	welcome_lbl.grid(row=0, column=0, columnspan=2, sticky="we", pady=10)

	name_lbl = customtkinter.CTkLabel(connect_window, text="Client Name")
	name_lbl.grid(row=1, column=0, sticky="we")
	name_entry = customtkinter.CTkEntry(connect_window, width=220)
	name_entry.grid(row=1, column=1, pady=20, padx=20, sticky="we")

	color_lbl = customtkinter.CTkLabel(connect_window, text="Color")
	color_lbl.grid(row=2, column=0, sticky="we")
	colors = ["yellow", "green", "blue", "orange"]
	color_entry = customtkinter.CTkOptionMenu(connect_window, values=colors, width=220)
	color_entry.grid(row=2, column=1, pady=20)

	symbol_lbl = customtkinter.CTkLabel(connect_window, text="Symbol")
	symbol_lbl.grid(row=3, column=0, sticky="we")
	emoji_unicode_dict = list(emoji.get_emoji_unicode_dict("en"))[:60]
	symbol = [emoji.emojize(sym, language="alias") for sym in emoji_unicode_dict]
	symbol_entry = customtkinter.CTkOptionMenu(connect_window, values=symbol, width=220, text_color="yellow")
	symbol_entry.grid(row=3, column=1, pady=20)

	chatroom_ID_lbl = customtkinter.CTkLabel(connect_window, text="Chatroom ID")
	chatroom_ID_lbl.grid(row=4, column=0, sticky="we")
	chatroom_ID_entry = customtkinter.CTkEntry(connect_window, width=220)
	chatroom_ID_entry.grid(row=4, column=1, pady=20, padx=20, sticky="we")

	connect_btn = customtkinter.CTkButton(connect_window, text="Connect", cursor="hand2", command=connect)
	connect_btn.grid(row=5, column=0, columnspan=2, pady=20)

	connect_window.mainloop()
	return tuple(returned_tuple)


class ScrollableFrame(Frame, customtkinter.CTk):

	def __init__(self, parent, *args, **kwargs):
		super().__init__(parent, *args, **kwargs)

		self.canvas = Canvas(self, bg="#2e2e2e", highlightbackground="#2e2e2e")
		self.frame = customtkinter.CTkFrame(self.canvas, bg_color="#2e2e2e", corner_radius=10)
		# self.scrollbar = customtkinter.CTkScrollbar(self, orientation="vertical",
													# width=8, corner_radius=10, border_spacing=1)

		# self.canvas.configure(yscrollcommand=self.scrollbar.set)
		# self.scrollbar.configure(command=self.canvas.yview)
		self.canvas.pack(side="left", fill="both", expand=True)
		self.frame.pack(fill="both", side="right")
		# self.scrollbar.pack(side="right", fill="y")

		# create a frame ID that can be called
		self.frameID = self.canvas.create_window((0, 0), anchor="nw", window=self.frame)

		# create scroll binding between frame, canvas and scrollbar
		self.frame.bind("<Configure>", self.onFrameConfigure)
		self.canvas.bind("<Configure>", self.onCanvasConfigure)
		self.canvas.bind("<Enter>", self.__bound_mousewheel)
		self.canvas.bind("<Leave>", self.__unbound_mousewheel)


	def onFrameConfigure(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))

	def onCanvasConfigure(self, event):
		width = event.width # getting the width of the canvas
		self.canvas.itemconfigure(self.frameID, width=self.canvas.winfo_width())

	def __bound_mousewheel(self, event):
		self.canvas.bind_all("<MouseWheel>", self._move)

	def __unbound_mousewheel(self, event):
		self.canvas.unbind_all("<MouseWheel>")

	def _move(self, event):
		self.canvas.yview_scroll(int(-1 *(event.delta/120)), "units")


class Window:

	def __init__(self, client_object: tuple[str])-> None:
		self.client_object = client_object

		self.window = customtkinter.CTk()
		self.window.title("Messager App")
		self.window.geometry("380x460")
		self.window.minsize(380, 450)
		self.window.maxsize(400, 480)

		self.room_ID = customtkinter.CTkLabel(self.window, text=f"Room ID: {client_object[3]}")
		self.room_ID.pack(pady=10)

		self.scrollable_frame = ScrollableFrame(self.window)
		self.scrollable_frame.pack(pady=10, fill="both", padx=10)

		self.message_entry = customtkinter.CTkEntry(self.window)
		self.message_entry.pack(pady=10, fill="x", padx=10)

		send_image = customtkinter.CTkImage(PIL.Image.open(r"assets/send.png"))
		self.send_button = customtkinter.CTkButton(self.window, image=send_image, text="Send", command=self.send_message)
		self.send_button.pack(pady=10)

		receiving_thread = Thread(target=self.receive_message, daemon=True)
		receiving_thread.start()

		self.window.mainloop()


	def receive_message(self):
		while True:
			message_ = self.client_object[-1].recv(1024)
			unpickled_message = pickle.loads(message_)

			if isinstance(unpickled_message, server_message):
				random_label = customtkinter.CTkLabel(self.scrollable_frame.frame, text=emoji.emojize(f"{unpickled_message.message}"), bg_color=unpickled_message.color)
				random_label.pack(anchor="nw", fill="x", expand=True)
			elif isinstance(unpickled_message, message):
				if unpickled_message.from_ == self.client_object[0]:
					random_label = customtkinter.CTkLabel(self.scrollable_frame.frame, text=emoji.emojize(f"{unpickled_message.symbol}: {unpickled_message.message}"), bg_color=unpickled_message.color)
					random_label.pack(anchor="w")
				else:
					random_label = customtkinter.CTkLabel(self.scrollable_frame.frame, text=emoji.emojize(f"{unpickled_message.symbol}: {unpickled_message.message}"), bg_color=unpickled_message.color)
					random_label.pack(anchor="e")


	def send_message(self):
		msg = self.message_entry.get()
		message_to_be_sent = message(from_=self.client_object[0], to_=self.client_object[3], message=msg, color=self.client_object[1], symbol=self.client_object[2])

		pickled_message = pickle.dumps(message_to_be_sent)
		self.client_object[4].send(pickled_message)


if __name__ == '__main__':
	# connecting to the server first
	
	client_values = connecting_server()
	client_object = server_connect(client_values)

	Window(client_object)

	
