from PIL import  Image,ImageTk 
import tkinter as tk

scenes = { 
    "start": {
        "image":"forest.jpg",
        "text":"Ви прокину в темному лісі.Куди підете?",
        "options" : {
            "Лісовуч":"cave",
            "Праворуч": "Village"

        }

    },
    "cave":{ 
        "image" : "cave.jpg",
        "text": "У печері темно і сташно.Ви знайшли меч!",
        "options" : {
            "Назад" : "start"
        }
    },
    "Village" : {
        "image" : "village.jpg",
        "text" : "Ви дістали до села.Тут безпечно.",
        "options" :{}
    }
}

class RPGame:
    def __init__(self,root):
        self.root = root
        self.root.title('RPG Квест')
        self.canvas = tk.Canvas(root,width=600,height=400)
        self.canvas.pack()

        self.text_label = tk.Label(root,text="",font=("Arial",14),wraplength=580)
        self.text_label.pack(pady=10)

        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        self.current_scene = "start"
        self.images = {}
        self.load_images()
        self.show_scene()


    def load_images(self):
        for scene in scenes.values():
            img = Image.open(scene["image"]).resize((600,400))
            self.images[scene["image"]] = ImageTk.PhotoImage(img)

    def show_scene(self):
        scene = scenes[self.current_scene]
        img = self.images[scene["image"]]
        self.canvas.create_image(0,0,anchor="nw",image=img)
        self.canvas.image=img
        self.text_label.config(text=scene["text"])

        for widget in self.button_frame.winfo_children():
            widget.destroy()

        for option_text,next_scene in scene["options"].items():
            btn=tk.Button(self.button_frame,text=option_text,command=lambda ns=next_scene: self.change_scene(ns))   
            btn.pack (side="left",padx=5)

    def change_scene(self,next_scene):
        self.current_scene = next_scene
        self.show_scene()

root = tk.Tk()
game=RPGame(root)
root.mainloop()