import customtkinter as ctk
import uuid
import json
import os
import threading
import time

from brain import Brain

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CAI_UI(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Creative AI")
        self.geometry("1250x780")

        self.brain = Brain()

        self.mode = "fast"

        self.chat_file = "chats.json"
        self.chats = {}
        self.current_chat = None

        self.load_chats()
        self.build_ui()

        if not self.chats:
            self.create_chat()
        else:
            first = list(self.chats.keys())[0]
            self.load_chat(first)

        self.startup_animation()

    # ------------------------
    # CHAT STORAGE
    # ------------------------

    def load_chats(self):

        if os.path.exists(self.chat_file):
            try:
                with open(self.chat_file, "r") as f:
                    self.chats = json.load(f)
            except:
                self.chats = {}

    def save_chats(self):

        with open(self.chat_file, "w") as f:
            json.dump(self.chats, f, indent=2)

    # ------------------------
    # UI
    # ------------------------

    def build_ui(self):

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=260, fg_color="#1e1e1e")
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.logo = ctk.CTkLabel(
            self.sidebar,
            text="Creative AI",
            font=("Segoe UI", 24, "bold")
        )
        self.logo.pack(pady=20)

        self.search = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="Search chats..."
        )
        self.search.pack(fill="x", padx=10, pady=5)
        self.search.bind("<KeyRelease>", self.search_chat)

        self.new_btn = ctk.CTkButton(
            self.sidebar,
            text="+ New Chat",
            command=self.create_chat
        )
        self.new_btn.pack(fill="x", padx=10, pady=4)

        self.rename_btn = ctk.CTkButton(
            self.sidebar,
            text="Rename",
            command=self.rename_chat
        )
        self.rename_btn.pack(fill="x", padx=10, pady=4)

        self.delete_btn = ctk.CTkButton(
            self.sidebar,
            text="Delete",
            command=self.delete_chat,
            fg_color="#b91c1c"
        )
        self.delete_btn.pack(fill="x", padx=10, pady=4)

        self.chat_list = ctk.CTkScrollableFrame(self.sidebar)
        self.chat_list.pack(fill="both", expand=True, padx=10, pady=10)

        # Chat area
        self.chat_area = ctk.CTkFrame(self)
        self.chat_area.grid(row=0, column=1, sticky="nsew")

        self.chat_area.grid_rowconfigure(0, weight=1)
        self.chat_area.grid_columnconfigure(0, weight=1)

        self.chat_scroll = ctk.CTkScrollableFrame(self.chat_area)
        self.chat_scroll.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        # MODE BAR
        self.mode_bar = ctk.CTkFrame(self.chat_area)
        self.mode_bar.grid(row=1, column=0, sticky="ew", padx=10)

        ctk.CTkLabel(
            self.mode_bar,
            text="Mode:",
            font=("Segoe UI", 14)
        ).pack(side="left", padx=10)

        self.mode_select = ctk.CTkOptionMenu(
            self.mode_bar,
            values=[
                "⚡ Fast",
                "🧠 Balanced",
                "💻 Coding",
                "🔬 Thinking"
            ],
            command=self.change_mode
        )

        self.mode_select.set("⚡ Fast")
        self.mode_select.pack(side="left", padx=10)

        # INPUT
        self.input_frame = ctk.CTkFrame(self.chat_area)
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=15)

        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(
            self.input_frame,
            height=45,
            font=("Segoe UI", 14),
            placeholder_text="Ask Creative AI anything..."
        )

        self.entry.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.entry.bind("<Return>", self.send_message)

        self.send_btn = ctk.CTkButton(
            self.input_frame,
            text="➤",
            width=60,
            height=40,
            command=self.send_message
        )

        self.send_btn.grid(row=0, column=1, padx=10)

        self.refresh_sidebar()

    # ------------------------
    # STARTUP ANIMATION
    # ------------------------

    def startup_animation(self):

        for i in range(0, 101, 5):
            self.logo.configure(text=f"Creative AI {i}%")
            self.update()
            time.sleep(0.01)

        self.logo.configure(text="Creative AI")

    # ------------------------
    # MODE
    # ------------------------

    def change_mode(self, value):

        if "Fast" in value:
            self.mode = "fast"
        elif "Balanced" in value:
            self.mode = "balanced"
        elif "Coding" in value:
            self.mode = "coding"
        else:
            self.mode = "thinking"

        self.brain.set_mode(self.mode)

    # ------------------------
    # CHAT MANAGEMENT
    # ------------------------

    def create_chat(self):

        cid = str(uuid.uuid4())[:8]

        self.chats[cid] = {
            "name": f"Chat {len(self.chats)+1}",
            "messages": []
        }

        self.current_chat = cid

        self.save_chats()
        self.refresh_sidebar()
        self.clear_chat()

    def rename_chat(self):

        if not self.current_chat:
            return

        dialog = ctk.CTkInputDialog(text="Rename chat", title="Rename")
        name = dialog.get_input()

        if name:
            self.chats[self.current_chat]["name"] = name
            self.save_chats()
            self.refresh_sidebar()

    def delete_chat(self):

        if not self.current_chat:
            return

        del self.chats[self.current_chat]

        self.save_chats()

        if self.chats:
            self.load_chat(list(self.chats.keys())[0])
        else:
            self.create_chat()

        self.refresh_sidebar()

    def refresh_sidebar(self):

        for widget in self.chat_list.winfo_children():
            widget.destroy()

        for cid, chat in self.chats.items():

            btn = ctk.CTkButton(
                self.chat_list,
                text=chat["name"],
                anchor="w",
                command=lambda c=cid: self.load_chat(c)
            )

            btn.pack(fill="x", pady=3)

    def load_chat(self, cid):

        self.current_chat = cid
        self.clear_chat()

        for role, msg in self.chats[cid]["messages"]:
            self.add_message(role, msg)

    def search_chat(self, event):

        term = self.search.get().lower()

        for widget in self.chat_list.winfo_children():
            widget.destroy()

        for cid, chat in self.chats.items():

            if term in chat["name"].lower():

                btn = ctk.CTkButton(
                    self.chat_list,
                    text=chat["name"],
                    anchor="w",
                    command=lambda c=cid: self.load_chat(c)
                )

                btn.pack(fill="x", pady=3)

    # ------------------------
    # CHAT UI
    # ------------------------

    def clear_chat(self):

        for widget in self.chat_scroll.winfo_children():
            widget.destroy()

    def add_message(self, role, text):

        frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        frame.pack(fill="x", pady=5)

        if role == "user":

            bubble = ctk.CTkLabel(
                frame,
                text=text,
                fg_color="#2563eb",
                text_color="white",
                corner_radius=12,
                wraplength=650,
                padx=12,
                pady=8
            )

            bubble.pack(anchor="e", padx=10)

        else:

            bubble = ctk.CTkLabel(
                frame,
                text=text,
                fg_color="#3a3a3a",
                text_color="white",
                corner_radius=12,
                wraplength=650,
                padx=12,
                pady=8
            )

            bubble.pack(anchor="w", padx=10)

        self.update_idletasks()
        self.chat_scroll._parent_canvas.yview_moveto(1)

    # ------------------------
    # THINKING
    # ------------------------

    def animate_thinking(self, label):

        dots = ["", ".", "..", "..."]

        def loop(i=0):
            try:
                label.configure(text="Thinking" + dots[i % 4])
                self.after(400, lambda: loop(i + 1))
            except:
                pass

        loop()

    def add_thinking(self):

        frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        frame.pack(fill="x", pady=5)

        label = ctk.CTkLabel(
            frame,
            text="Thinking",
            fg_color="#3a3a3a",
            text_color="white",
            corner_radius=12,
            padx=10,
            pady=8
        )

        label.pack(anchor="w", padx=10)

        self.animate_thinking(label)

        self.update_idletasks()
        self.chat_scroll._parent_canvas.yview_moveto(1)

        return label

    # ------------------------
    # MESSAGE FLOW
    # ------------------------

    def send_message(self, event=None):

        text = self.entry.get().strip()

        if not text:
            return

        self.entry.delete(0, "end")

        self.add_message("user", text)

        self.chats[self.current_chat]["messages"].append(("user", text))
        self.save_chats()

        thinking = self.add_thinking()

        threading.Thread(
            target=self.generate_ai,
            args=(text, thinking),
            daemon=True
        ).start()

    # ------------------------
    # AI GENERATION
    # ------------------------

    def generate_ai(self, text, thinking_label):

        full = ""
        destroyed = False

        frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        frame.pack(fill="x", pady=5)

        bubble = ctk.CTkLabel(
            frame,
            text="",
            fg_color="#3a3a3a",
            text_color="white",
            corner_radius=12,
            wraplength=650,
            padx=12,
            pady=8
        )

        bubble.pack(anchor="w", padx=10)

        def stream(chunk):

            nonlocal full, destroyed
            full += chunk

            if not destroyed:
                self.after(0, thinking_label.destroy)
                destroyed = True

            self.after(0, lambda: bubble.configure(text=full))
            self.after(0, lambda: self.chat_scroll._parent_canvas.yview_moveto(1))

        try:
            self.brain.process(text, stream, self.mode)
        except Exception as e:
            full = f"Error: {e}"
            self.after(0, lambda: bubble.configure(text=full))

        self.chats[self.current_chat]["messages"].append(("assistant", full))
        self.save_chats()


if __name__ == "__main__":
    app = CAI_UI()
    app.mainloop()