import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import json, os, subprocess

# ================= STORAGE =================
FILE = "os_data.json"
if not os.path.exists(FILE):
    with open(FILE, "w") as f:
        json.dump({"users": {}, "notes": {}, "desktop": {}, "apps": {}, "chat": []}, f)

def load(): 
    with open(FILE) as f: 
        return json.load(f)
def save(d):
    with open(FILE, "w") as f: 
        json.dump(d, f)

data = load()
current_user = None
desktop_icons = {}

# ================= ROOT =================
root = tk.Tk()
root.title("Python OS")
root.configure(bg="#1e1e1e")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.destroy())  # Only exit with Escape

# ================= CLEAR =================
def clear():
    for w in root.winfo_children():
        w.destroy()

# ================= LOGIN =================
def login_screen():
    clear()
    f = tk.Frame(root, bg="#1e1e1e")
    f.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(f, text="Python OS Login", font=("Consolas", 28), fg="white", bg="#1e1e1e").pack(pady=10)
    u = tk.Entry(f); u.pack(pady=5)
    p = tk.Entry(f, show="*"); p.pack(pady=5)
    msg = tk.Label(f, fg="red", bg="#1e1e1e"); msg.pack()

    def do_login():
        global current_user, data
        data = load()
        username = u.get()
        password = p.get()
        if username in data["users"] and data["users"][username] == password:
            current_user = username
            if current_user not in data.get("desktop", {}):
                data["desktop"][current_user] = []
            save(data)
            desktop()
        else:
            msg.config(text="Wrong login")

    def create():
        global data
        data = load()
        username = u.get()
        password = p.get()
        if username not in data["users"]:
            data["users"][username] = password
            data["notes"][username] = ""
            if "desktop" not in data:
                data["desktop"] = {}
            data["desktop"][username] = []
            save(data)
            msg.config(text="Account created")
        else:
            msg.config(text="Username exists")

    tk.Button(f, text="Login", command=do_login).pack(pady=5)
    tk.Button(f, text="Create", command=create).pack(pady=5)

# ================= APPS =================
def calculator():
    w = tk.Toplevel(root); w.title("Calculator")
    e = tk.Entry(w, font=("Consolas", 18)); e.pack()
    def calc():
        try: e.insert("end", "=" + str(eval(e.get())))
        except: e.delete(0,"end"); e.insert(0,"Error")
    tk.Button(w, text="=", command=calc).pack()

def notes():
    d = load()
    w = tk.Toplevel(root); w.title("Notes")
    t = tk.Text(w); t.pack(fill="both", expand=True)
    t.insert("1.0", d["notes"].get(current_user,""))
    def save_note():
        d["notes"][current_user] = t.get("1.0","end-1c"); save(d)
    tk.Button(w, text="Save", command=save_note).pack()

def snake():
    w = tk.Toplevel(root); w.title("Snake")
    c = tk.Canvas(w, width=400, height=400, bg="black"); c.pack()
    x,y=200,200; dx,dy=20,0
    snake=[c.create_rectangle(x,y,x+20,y+20, fill="lime")]
    food=c.create_oval(100,100,120,120, fill="red")
    def move():
        nonlocal x,y
        x+=dx; y+=dy
        c.coords(snake[0],x,y,x+20,y+20)
        w.after(150, move)
    def key(e):
        nonlocal dx,dy
        if e.keysym=="Up": dx,dy=0,-20
        if e.keysym=="Down": dx,dy=0,20
        if e.keysym=="Left": dx,dy=-20,0
        if e.keysym=="Right": dx,dy=20,0
    w.bind("<Key>", key)
    move()

def terminal():
    w = tk.Toplevel(root); w.title("Terminal")
    t = tk.Text(w,bg="black",fg="lime"); t.pack(fill="both",expand=True)
    e = tk.Entry(w); e.pack(fill="x")
    t.insert("end","Safe Terminal\nCommands: dir, pwd, shutdown\n\n")
    def run(ev=None):
        cmd=e.get(); e.delete(0,"end")
        if cmd in ["dir","pwd","ls"]:
            out=subprocess.getoutput(cmd)
            t.insert("end", out+"\n")
        elif cmd=="shutdown":
            root.destroy()
        else: t.insert("end","Blocked\n")
    e.bind("<Return>", run)

def game_creator():
    w = tk.Toplevel(root)
    tk.Label(w,text="Game Creator (Click Test)",font=("Consolas",20)).pack()
    name=tk.Entry(w); name.pack(pady=5); name.insert(0,"My Click Game")
    def create_game():
        g=tk.Toplevel(root); score=0
        lbl=tk.Label(g,text=f"{name.get()}\nScore: 0",font=("Consolas",20)); lbl.pack(pady=20)
        def click(): nonlocal score; score+=1; lbl.config(text=f"{name.get()}\nScore: {score}")
        tk.Button(g,text="CLICK",command=click).pack()
    tk.Button(w,text="Create Game",command=create_game).pack(pady=10)

def global_chat():
    d = load()
    w = tk.Toplevel(root); w.title("Global Chat")
    chat=tk.Text(w,height=20); chat.pack()
    entry=tk.Entry(w); entry.pack(fill="x")
    def send(ev=None):
        msg = entry.get(); entry.delete(0,"end")
        if "chat" not in d: d["chat"]=[]
        d["chat"].append(f"{current_user}: {msg}"); save(d)
        refresh()
    def refresh():
        chat.delete("1.0","end")
        for line in d.get("chat",[]): chat.insert("end", line+"\n")
    tk.Button(w,text="Send",command=send).pack()
    entry.bind("<Return>",send)
    refresh()

def file_explorer(load_desktop):
    d = load()
    w = tk.Toplevel(root); w.title("File Explorer")
    def add_file():
        f = filedialog.askopenfilename()
        if f:
            if current_user not in d["desktop"]: d["desktop"][current_user] = []
            if f not in d["desktop"][current_user]:
                d["desktop"][current_user].append(f)
            save(d)
            load_desktop()  # refresh desktop icons
    tk.Button(w,text="Add File",command=add_file).pack()

# ================= DESKTOP =================
def desktop():
    clear()
    tk.Label(root,text=f"Python OS - {current_user}", fg="white", bg="#1e1e1e", font=("Consolas",20)).pack(pady=5)
    desktop_frame=tk.Frame(root,bg="#1e1e1e"); desktop_frame.pack(fill="both",expand=True)

    app_list = {
        "Calculator": calculator,
        "Notes": notes,
        "Snake": snake,
        "Terminal": terminal,
        "Game Creator": game_creator,
        "Global Chat": global_chat,
        "File Explorer": lambda: file_explorer(load_desktop)
    }

    # Desktop icons
    def load_desktop():
        for b in desktop_icons.values(): b.destroy()
        desktop_icons.clear()
        for idx, app in enumerate(data.get("desktop",{}).get(current_user,[])):
            name=os.path.basename(app) if os.path.isfile(app) else app
            btn=tk.Button(desktop_frame,text=name,width=12,height=3,command=lambda a=app: open_app(a))
            btn.place(x=20+((idx%8)*110), y=50+((idx//8)*100))
            desktop_icons[app]=btn
            btn.bind("<Button-3>", lambda e,a=app: delete_icon(a))
            # Enable drag
            def start_drag(event, b=btn):
                b.startX = event.x; b.startY = event.y
            def do_drag(event, b=btn):
                x = b.winfo_x() + event.x - b.startX
                y = b.winfo_y() + event.y - b.startY
                b.place(x=x, y=y)
            btn.bind("<Button-1>", start_drag)
            btn.bind("<B1-Motion>", do_drag)

    def delete_icon(app):
        desktop_icons[app].destroy(); desktop_icons.pop(app)
        data["desktop"][current_user].remove(app); save(data)

    def open_app(app_name):
        if app_name in app_list: app_list[app_name]()
        elif os.path.isfile(app_name):
            if app_name.endswith(".py"): os.system(f'python "{app_name}"')
            else: os.startfile(app_name)

    load_desktop()
    
    # Start Menu
    def start_menu():
        menu=tk.Toplevel(root); menu.title("Start Menu"); menu.geometry("200x400")
        for app_name in app_list:
            tk.Button(menu,text=app_name,width=20,command=lambda a=app_name: open_app(a)).pack()
    tk.Button(root,text="Start",command=start_menu).pack(side="left")
    tk.Button(root,text="Logout",command=login_screen).pack(side="right")

# ================= START =================
login_screen()
root.mainloop()
