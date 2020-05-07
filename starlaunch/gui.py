import tkinter as tk
import tkinter.ttk as ttk
from typing import Callable

import lib


class Application:
    def __init__(self):
        self.window = tk.Tk()

    def run(self):
        self.window.mainloop()


class Section:
    def __init__(self, container, **kwargs):
        self.f = tk.Frame(container, **kwargs)

    def grid(self, row, column):
        self.f.grid(row=row, column=column)


class LabeledEntry(Section):
    def __init__(self, container, label, **kwargs):
        super().__init__(container, **kwargs)
        self.label = ttk.Label(self.f, text=label)
        self.entry = ttk.Entry(self.f)
        self.__draw()

    def __draw(self):
        self.label.grid(row=0, column=0)
        self.label.grid(row=0, column=1)

    @property
    def value(self):
        return self.entry.get()


class PathSelector(Section):
    def __init__(self, container, **kwargs):
        super().__init__(container, **kwargs)


class InstanceView(Section):
    def __init__(self, container, instance: lib.Instance, **kwargs):
        super().__init__(container, **kwargs)
        self.instance = instance
        self.launch = ttk.Button(self.f, text=self.instance.name, command=self.launch_game)
        self.edit = ttk.Button(self.f, text='\u270E', command=self.edit_instance)
        self.__draw()

    def __draw(self):
        self.launch.grid(row=0, column=0)
        self.edit.grid(row=0, column=1)

    def launch_game(self):
        pass

    def edit_instance(self):
        pass


class InstanceEdit:
    def __init__(self, instance: lib.Instance, callback: Callable[[lib.Instance], None]):
        self.callback = callback
        self.window = tk.Toplevel()
        self.instance = instance
        self.name = LabeledEntry(self.window, 'Instance name')
        # instead do radiobutton: instance/main/custom
        # also custom will have a file selector
        self.storage = LabeledEntry(self.window, 'Storage location')
        self.mods = LabeledEntry(self.window, 'Mods location')
        self.__draw()

    def __draw(self):
        self.name.grid(0, 0)
        self.storage.grid(1, 0)
        self.mods.grid(2, 0)

    def save(self):
        self.callback(self.instance)
        self.window.destroy()
