from PIL import  Image,ImageTk 
import tkinter as tk

scenes = { 
    "start": {
        "image":"forest",
        "text":"Ви прокину в темному лісі.Куди підете?",
        "options" : {
            "Лісовуч":"cave",
            "Праворуч": "Village"

        }

    },
    "cave":{ 
        "image" : "came.png",
        "text": "У печері темно і сташно.Ви знайшли меч!",
        "options" : {
            "Назад" : "start"
        }
    },
    "Village" : {
        "image" : "village",
        "text" : "Ви дістали до села.Тут безпечно.",
        "Options" :{}
    }
}

class RPGame:
    def __init__(self,root):
        self.root = root
        self.root.title('RPG Квест')
        self.canvas = tk.Canvas(root,width=600,height=400)
        self.canvas.pack()

        self.text_labet = tk.Label(root,text="",font=("Arial",14),wraplenght=580)
        self.text_label.pack(pady=10)

        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        self.current_scene = "start"
        self.images = {}
        self.load_images()
        self.show_scene()

