class MainWindowActionHandler:
    def __init__(self, window):
        self.window = window

    def quit(self):
        self.window.destroy()


class MainViewActionHandler:
    def __init__(self, view):
        self.view = view

    def open_new_image(self):
        self.view.open_new_image()

    def resize_image(self, method):
        self.view.resize_image(method)

    def download_resized_image(self):
        self.view.save_new_image()