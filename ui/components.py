from tkinter import Label, Button


class ComponentFactory:
    @classmethod
    def create_button(cls, master, text, command):
        return Button(master, text=text, command=command)

    @classmethod
    def create_label(cls, master, text=None):
        return Label(master, text=text)
