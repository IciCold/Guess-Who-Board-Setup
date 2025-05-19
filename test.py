import os
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')

class ImageBox(Frame):
    def __init__(self, master, img_path, *args, **kwargs):
        super().__init__(master, relief=SOLID, borderwidth=1, padx=5, pady=5, *args, **kwargs)
        self.img_path = img_path
        self.hidden = False

        pil_img = Image.open(img_path)
        pil_img.thumbnail((150, 150))
        self.tk_img = ImageTk.PhotoImage(pil_img)

        self.img_label = Label(self, image=self.tk_img)
        self.img_label.grid(row=0, column=0)

        name = os.path.splitext(os.path.basename(img_path))[0]
        self.name_label = Label(self, text=name)
        self.name_label.grid(row=1, column=0)

        self.button = Button(self, text="Hide", command=self.toggle)
        self.button.grid(row=2, column=0, pady=(4, 0))

    def toggle(self):
        self.hidden = not self.hidden
        if self.hidden:
            self.img_label.grid_remove()
            self.button.config(text="Unhide")
        else:
            self.img_label.grid(row=0, column=0)
            self.button.config(text="Hide")


class ImageOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Organizer")

        top_frame = Frame(root, bg="#1F1F1F", bd=0, highlightthickness=0)
        top_frame.pack(fill=X, padx=10, pady=5)

        self.add_btn = Button(top_frame, text="Add Folder", command=self.add_folder)
        self.add_btn.pack(side=LEFT)

        # New label "Choosing:" to the left
        self.choose_label = Label(top_frame, text="Choosing:", bg="#1F1F1F", fg="white", font=("Arial", 10))
        self.choose_label.pack(side=LEFT, padx=(20, 5))

        # Selected image name stringvar
        self.selected_image_name = StringVar()
        self.selected_image_name.set("Select Image")

        # Custom dropdown button + menu
        self.dropdown_btn = Button(top_frame, textvariable=self.selected_image_name, relief=RAISED, width=20,
                                   command=self.show_dropdown_menu)
        self.dropdown_btn.pack(side=LEFT)

        # Menu for dropdown
        self.dropdown_menu = Menu(root, tearoff=0)

        # Canvas and scrolling
        self.canvas = Canvas(root, bg="#00ADB5", bd=0, highlightthickness=0)
        self.scroll_frame = Frame(self.canvas, bg='#00ADB5', bd=0, highlightthickness=0)
        self.scroll_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.v_scroll = Scrollbar(root, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.v_scroll.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.scroll_frame.bind("<Configure>", self.on_frame_configure)
        self.root.bind("<Configure>", self.refresh_grid)

        self.image_boxes = []

        # Mouse wheel bindings for scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_mousewheel_linux(event):
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.bind_all("<Button-4>", _on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", _on_mousewheel_linux)

    def show_dropdown_menu(self):
        # Rebuild menu with only visible images
        self.dropdown_menu.delete(0, END)

        visible_boxes = [box for box in self.image_boxes if not box.hidden]
        names = [os.path.splitext(os.path.basename(box.img_path))[0] for box in visible_boxes]

        if not names:
            self.dropdown_menu.add_command(label="No visible images", state=DISABLED)
        else:
            for name in names:
                self.dropdown_menu.add_command(label=name, command=lambda v=name: self.select_image(v))

        # Calculate position to anchor top-right of button
        x = self.dropdown_btn.winfo_rootx()
        y = self.dropdown_btn.winfo_rooty() + self.dropdown_btn.winfo_height()

        # Width of the menu in pixels (approximate)
        menu_width = 150  # You can adjust this if needed

        # Post menu so its top-right corner aligns with button's top-right corner
        self.dropdown_menu.post(x + self.dropdown_btn.winfo_width() - menu_width, y)

    def select_image(self, value):
        self.selected_image_name.set(value)
        self.dropdown_menu.unpost()

    def add_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            for filename in os.listdir(folder):
                if filename.lower().endswith(SUPPORTED_FORMATS):
                    full_path = os.path.join(folder, filename)
                    box = ImageBox(self.scroll_frame, full_path)
                    self.image_boxes.append(box)
            self.refresh_grid()

    def refresh_grid(self, event=None):
        for widget in self.scroll_frame.winfo_children():
            widget.grid_forget()

        width = self.root.winfo_width()
        box_width = 180  # Width per image box (including margins)

        cols = max(1, width // box_width)

        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(cols + 1, weight=1)

        for i, box in enumerate(self.image_boxes):
            row = i // cols
            col = i % cols
            box.grid(row=row, column=col + 1, padx=10, pady=10, sticky='n')

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


if __name__ == "__main__":
    root = Tk()
    root.geometry("800x600")
    root.configure(bg="#1F1F1F")
    app = ImageOrganizerApp(root)
    root.mainloop()
