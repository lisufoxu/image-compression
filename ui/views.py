import os
from pathlib import Path

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Frame, Canvas, Scrollbar, HORIZONTAL, VERTICAL
from tkinter.filedialog import askopenfilename, asksaveasfilename

from ui.components import ComponentFactory
from callbacks import MainWindowActionHandler, MainViewActionHandler
from resources import EnglishTranslations


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.attributes('-zoomed', True)
        self.lang = EnglishTranslations
        self.handler = MainWindowActionHandler(self)
        self.title(self.lang.title)

        self.config(padx=5, pady=5)
        self.grid_rowconfigure(0, weight=1, uniform='MainWindow')
        self.grid_columnconfigure(0, weight=1, uniform='MainWindow')

        self.view = MainView(self)
        self.view.grid(row=0, column=0, sticky='nsew')

        self.protocol("WM_DELETE_WINDOW", self.handler.quit)


class MainView(Frame):
    def __init__(self, outer):
        super().__init__(outer, borderwidth=5)
        self.outer = outer
        self.lang = EnglishTranslations
        self.handler = MainViewActionHandler(self)
        self.image = None
        self.resized_image = None

        self.grid_columnconfigure(0, weight=1, uniform='MainView')
        self.grid_columnconfigure(1, weight=1, uniform='MainView')
        self.grid_rowconfigure(0, weight=1, uniform='MainView')

        self.image_load_view = ImageLoadView(self)
        self.image_load_view.grid(row=0, column=0, sticky='nsew')
        self.image_compression_view = ImageCompressionView(self)
        self.image_compression_view.grid(row=0, column=1, sticky='nsew')

    def destroy(self):
        if self.image:
            self.image.close()
        if self.resized_image:
            self.resized_image.close()
        super().destroy()

    def open_new_image(self):
        if self.image:
            self.image.close()
            self.image = None
        filepath = askopenfilename(
            filetypes=[(self.lang.images, "*.jpg"), (self.lang.all_files, "*.*")]
        )
        if filepath:
            try:
                self.image = Image.open(filepath)
            except Exception as e:
                raise e

        self.image_load_view.set_image(self.image)
        self.image_compression_view.set_image(None)

    def save_new_image(self):
        if not self.resized_image:
            return
        filepath = Path(self.image.filename)
        stem = filepath.stem  # filename
        suffix = filepath.suffix  # .jpg
        new_filename = f'{stem}-{self.lang.compressions[self.resized_image.compression_method]}{suffix}'
        filename = asksaveasfilename(initialfile=f'{new_filename}')
        if filename:
            self.resized_image.save(filename, quality=98)

    def resize_image(self, method):
        if not self.image:
            return
        if self.resized_image:
            self.resized_image.close()
        width, height = self.image.size
        ratio = .4
        self.resized_image = self.image.resize((int(width * ratio), int(height * ratio)), method)
        self.resized_image.compression_method = method
        self.image_compression_view.set_image(self.resized_image)


class PreviewPane(Frame):
    def __init__(self, outer):
        super().__init__(outer)
        self.outer = outer
        self.grid_rowconfigure(0, weight=1, uniform='ImageLoadView_preview_layout')
        self.grid_columnconfigure(0, weight=1, uniform='ImageLoadView_preview_layout')

        self.image_container = None
        self.image_tk = None

        h = Scrollbar(self, orient=HORIZONTAL)
        v = Scrollbar(self, orient=VERTICAL)
        self.image_canvas = Canvas(self, yscrollcommand=v.set, xscrollcommand=h.set)
        h['command'] = self.image_canvas.xview
        v['command'] = self.image_canvas.yview

        self.image_canvas.grid(row=0, column=0, sticky='nsew')
        h.grid(column=0, row=1, sticky='ew')
        v.grid(column=1, row=0, sticky='ns')
        self.image_canvas.configure(
            scrollregion=(1, 1, self.winfo_width(), self.winfo_height()))

    def set_pane(self, image_obj):
        self.image_canvas.delete('all')
        if image_obj:
            self.image_tk = ImageTk.PhotoImage(image_obj)
            self.image_canvas.create_image(0, 0, anchor='nw', image=self.image_tk)


class ImageLoadView(Frame):
    def __init__(self, outer):
        super().__init__(outer)
        self.outer = outer
        self.lang = EnglishTranslations

        self.config(padx=5, pady=5)
        self.grid_rowconfigure(1, weight=1, uniform='ImageLoadView')
        self.grid_columnconfigure(0, weight=1, uniform='ImageLoadView')

        self.actions_layout = Frame(self)
        self.actions_layout.grid(column=0, row=0, sticky='nw')
        self.preview_pane = PreviewPane(self)
        self.preview_pane.grid(column=0, row=1, sticky='nsew')

        ComponentFactory\
            .create_button(self.actions_layout, self.lang.open_btn_lbl, self.outer.handler.open_new_image)\
            .grid(column=0, row=0)
        self.uploaded_image_name_lbl = ComponentFactory.create_label(self.actions_layout, '')
        self.uploaded_image_name_lbl.grid(column=1, row=0)

    def set_image(self, image_obj):
        text = os.path.basename(image_obj.filename) if image_obj else ''
        self.uploaded_image_name_lbl.config(text=text)
        self.preview_pane.set_pane(image_obj)


class ImageCompressionView(Frame):
    def __init__(self, outer):
        super().__init__(outer)
        self.outer = outer
        self.lang = EnglishTranslations

        self.config(padx=5, pady=5)
        self.grid_rowconfigure(1, weight=1, uniform='ImageCompressionView')
        self.grid_columnconfigure(0, weight=1, uniform='ImageCompressionView')

        self.actions_layout = Frame(self)
        self.actions_layout.grid(column=0, row=0, sticky='nsew')
        self.preview_pane = PreviewPane(self)
        self.preview_pane.grid(column=0, row=1, sticky='nsew')

        for index, compression in enumerate(self.outer.lang.compressions.items()):
            self.actions_layout.grid_columnconfigure(index, weight=1, uniform='ImageCompressionView_actions_layout')
            ComponentFactory\
                .create_button(self.actions_layout, compression[1],
                               command=lambda compression=compression: self.outer.handler.resize_image(compression[0]))\
                .grid(column=index, row=0, sticky='ew')

        self.download_btn = ComponentFactory \
            .create_button(self, self.lang.download_lbl, command=self.outer.handler.download_resized_image)
        self.download_btn.grid(column=0, row=2, sticky='nw')

    def set_image(self, image_obj):
        self.preview_pane.set_pane(image_obj)
        new_text = f'{self.lang.download_lbl} - {self.lang.compressions[image_obj.compression_method]}' if image_obj else self.lang.download_lbl
        self.download_btn.config(text=new_text)
