import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import Label, Button
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import os
import threading

# --- Theme Colors ---
LIGHT_THEME = {
    "bg": "#f0f8ff",
    "fg": "#2e7d32",
    "btn_bg": "#2e7d32",
    "btn_fg": "white",
    "btn2_bg": "#0288d1",
    "btn2_fg": "white",
    "panel_bg": "#f0f8ff",
    "title_fg": "#2e7d32"
}
DARK_THEME = {
    "bg": "#181a20",
    "fg": "#f5f5f5",
    "btn_bg": "#23272e",
    "btn_fg": "#f5f5f5",
    "btn2_bg": "#1976d2",
    "btn2_fg": "#f5f5f5",
    "panel_bg": "#23272e",
    "title_fg": "#90caf9"
}

current_theme = LIGHT_THEME

def create_light_bg(size):
    w, h = size
    img = Image.new("RGB", size, "#aeefff")
    draw = ImageDraw.Draw(img)
    for y in range(h):
        color = int(174 + (255-174) * y / h)
        draw.line([(0, y), (w, y)], fill=(color, color, 255))
    sun_center = (int(w*0.8), int(h*0.18))
    sun_radius = 60
    draw.ellipse([sun_center[0]-sun_radius, sun_center[1]-sun_radius,
                  sun_center[0]+sun_radius, sun_center[1]+sun_radius],
                 fill="#fffde4", outline="#ffe066")
    for angle in range(0, 360, 20):
        x1 = sun_center[0] + int(sun_radius * 0.7 * np.cos(np.radians(angle)))
        y1 = sun_center[1] + int(sun_radius * 0.7 * np.sin(np.radians(angle)))
        x2 = sun_center[0] + int(sun_radius * 1.3 * np.cos(np.radians(angle)))
        y2 = sun_center[1] + int(sun_radius * 1.3 * np.sin(np.radians(angle)))
        draw.line([x1, y1, x2, y2], fill="#ffe066", width=4)
    for cx, cy in [(120, 120), (200, 80), (320, 140)]:
        draw.ellipse([cx, cy, cx+60, cy+30], fill="#ffffff", outline="#e0f7fa")
        draw.ellipse([cx+20, cy-10, cx+70, cy+20], fill="#ffffff", outline="#e0f7fa")
    draw.pieslice([0, h-180, w, h+120], 0, 180, fill="#b2e672", outline="#b2e672")
    draw.pieslice([-100, h-100, w-200, h+180], 0, 180, fill="#7ed957", outline="#7ed957")
    return img

def create_dark_bg(size):
    w, h = size
    img = Image.new("RGB", size, "#181a20")
    draw = ImageDraw.Draw(img)
    for y in range(h):
        r = int(24 + (10-24) * y / h)
        g = int(26 + (10-26) * y / h)
        b = int(48 + (30-48) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    for _ in range(60):
        x = np.random.randint(0, w)
        y = np.random.randint(0, int(h*0.7))
        r = np.random.randint(1, 3)
        draw.ellipse([x, y, x+r, y+r], fill="#f5f5f5")
    return img

def get_bg_img(theme, size):
    if theme == DARK_THEME:
        return ImageTk.PhotoImage(create_dark_bg(size))
    else:
        return ImageTk.PhotoImage(create_light_bg(size))

def update_background():
    global bg_img
    bg_img = get_bg_img(current_theme, (bg_width, bg_height))
    canvas.itemconfig(bg_canvas_img, image=bg_img)

def apply_theme(theme):
    title_label.config(bg=theme["bg"], fg=theme["title_fg"])
    upload_btn.config(bg=theme["btn_bg"], fg=theme["btn_fg"], activebackground=theme["btn_bg"], activeforeground=theme["btn_fg"])
    save_btn.config(bg=theme["btn2_bg"], fg=theme["btn2_fg"], activebackground=theme["btn2_bg"], activeforeground=theme["btn2_fg"])
    panel.config(bg=theme["panel_bg"], fg=theme["fg"])
    toggle_btn.config(bg=theme["btn_bg"], fg=theme["btn_fg"], activebackground=theme["btn_bg"], activeforeground=theme["btn_fg"])
    style = ttk.Style()
    style.theme_use('default')
    if theme == DARK_THEME:
        style.configure("TProgressbar", background="#90caf9", troughcolor=theme["panel_bg"])
    else:
        style.configure("TProgressbar", background="#0288d1", troughcolor=theme["panel_bg"])
    update_background()

def toggle_theme():
    global current_theme
    if current_theme == LIGHT_THEME:
        current_theme = DARK_THEME
        toggle_btn.config(text="Switch to Light Mode")
    else:
        current_theme = LIGHT_THEME
        toggle_btn.config(text="Switch to Dark Mode")
    apply_theme(current_theme)

def cartoonify_image(img_path):
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError("Could not read image file.")
    img = cv2.resize(img, (500, 500))
    smoothed = img.copy()
    for _ in range(5):
        smoothed = cv2.bilateralFilter(smoothed, d=9, sigmaColor=50, sigmaSpace=50)
    div = 36
    quantized = smoothed // div * div + div // 2
    blur = cv2.GaussianBlur(quantized, (0, 0), sigmaX=1.5)
    sharpened = cv2.addWeighted(quantized, 1.5, blur, -0.5, 0)
    hsv = cv2.cvtColor(sharpened, cv2.COLOR_BGR2HSV)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.2, 0, 255)
    vibrant = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return vibrant

def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        progress_bar.place(relx=0.5, rely=0.92, anchor="center")
        progress_bar.start(10)
        root.update_idletasks()
        threading.Thread(target=process_image, args=(file_path,)).start()

def process_image(file_path):
    try:
        cartoon = cartoonify_image(file_path)
    except Exception as e:
        progress_bar.stop()
        progress_bar.place_forget()
        messagebox.showerror("Error", str(e))
        return
    bgr_img = cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(bgr_img)
    img_tk = ImageTk.PhotoImage(img_pil)
    def update_panel():
        panel.config(image=img_tk)
        panel.image = img_tk
        panel.cartoon_img = cartoon
        panel.original_path = file_path
        save_btn.config(state="normal")
        progress_bar.stop()
        progress_bar.place_forget()
    root.after(0, update_panel)

def save_image():
    if hasattr(panel, 'cartoon_img'):
        original_name = os.path.splitext(os.path.basename(panel.original_path))[0]
        suggested_name = f"{original_name}_anime.png"
        save_path = filedialog.asksaveasfilename(initialfile=suggested_name,
                                                 defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"),
                                                            ("JPEG files", "*.jpg")])
        if save_path:
            cv2.imwrite(save_path, panel.cartoon_img)
            messagebox.showinfo("Saved", f"Image saved to:\n{save_path}")
    else:
        messagebox.showwarning("No image", "Please upload and cartoonify an image first.")

# GUI setup
root = tk.Tk()
root.title("✨Cartoonify Image")
root.geometry("700x700")
root.resizable(False, False)

# --- Background ---
bg_width, bg_height = 700, 700
bg_img = get_bg_img(current_theme, (bg_width, bg_height))
canvas = tk.Canvas(root, width=bg_width, height=bg_height, highlightthickness=0)
canvas.pack(fill="both", expand=True)
bg_canvas_img = canvas.create_image(0, 0, anchor="nw", image=bg_img)

# --- Title Label ---
title_label = Label(root, text="✨Cartoonify Image", font=("Comic Sans MS", 30, "bold"),
                    bg=current_theme["bg"], fg=current_theme["title_fg"])
title_label.place(relx=0.5, rely=0.05, anchor="center")

# --- Buttons & Panel ---
upload_btn = Button(root, text="Upload Image", command=upload_image, font=("Arial", 14, "bold"),
                    bg=current_theme["btn_bg"], fg=current_theme["btn_fg"], padx=10, pady=5, bd=0)
upload_btn.place(relx=0.5, rely=0.14, anchor="center")

save_btn = Button(root, text="Save Anime Image", command=save_image, font=("Arial", 14, "bold"),
                  bg=current_theme["btn2_bg"], fg=current_theme["btn2_fg"], padx=10, pady=5, bd=0, state="disabled")
save_btn.place(relx=0.5, rely=0.21, anchor="center")

panel = Label(root, bg=current_theme["panel_bg"], fg=current_theme["fg"], bd=2, relief="ridge")
panel.place(relx=0.5, rely=0.57, anchor="center", width=400, height=400)

toggle_btn = Button(root, text="Switch to Dark Mode", command=toggle_theme, font=("Arial", 12, "bold"),
                    bg=current_theme["btn_bg"], fg=current_theme["btn_fg"], padx=8, pady=4, bd=0)
toggle_btn.place(relx=0.5, rely=0.87, anchor="center")

# --- Progress Bar ---
progress_bar = ttk.Progressbar(root, mode='indeterminate', length=300)
apply_theme(current_theme)

root.mainloop()