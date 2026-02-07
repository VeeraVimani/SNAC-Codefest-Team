import os
import customtkinter as ctk
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def clear(w):
    for i in w.winfo_children():
        i.destroy()


def add_hover_zoom(btn, width, height, zoom=1.2):
    def on_enter(_e):
        btn.configure(width=int(width * zoom), height=int(height * zoom))

    def on_leave(_e):
        btn.configure(width=width, height=height)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


def image_path(name):
    return os.path.join(BASE_DIR, name)


def image_button(app, image_path_value, size, command, zoom=1.12): # the image button with zoom effect
    base_img = Image.open(image_path_value).resize(size)
    zoom_size = (int(size[0] * zoom), int(size[1] * zoom))
    zoom_img = Image.open(image_path_value).resize(zoom_size)

    base_photo = ImageTk.PhotoImage(base_img)
    zoom_photo = ImageTk.PhotoImage(zoom_img)

    btn = ctk.CTkButton(
        app,
        image=base_photo,
        text="",
        command=command,
        width=size[0],
        height=size[1],
        fg_color="transparent",
        hover=False,
        border_width=0,
        corner_radius=0,
    )

    btn.image = base_photo
    btn._hover_image = zoom_photo

    def on_enter(_e):
        btn.configure(image=btn._hover_image, width=zoom_size[0], height=zoom_size[1])

    def on_leave(_e):
        btn.configure(image=btn.image, width=size[0], height=size[1])

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn
