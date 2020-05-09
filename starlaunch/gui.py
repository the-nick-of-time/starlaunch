import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from typing import Callable

import lib


class Application:
    def __init__(self, model: lib.Application):
        self.window = tk.Tk()
        self.window.title('StarLaunch')
        self.window.wm_protocol('WM_DELETE_WINDOW', self.quit)
        self.model = model
        self.instancesWrapper = ttk.Frame(self.window)
        self.instances = [InstanceView(self.instancesWrapper, inst, self.launch) for inst in
                          self.model.instances]
        self.menu = SettingsMenu(self.window, self.model.settings)
        self.window.config(menu=self.menu.menubar)
        self.newButton = ttk.Button(self.window, text='New', command=self.new)
        self.__draw()

    def __draw(self):
        for i, inst in enumerate(self.instances):
            inst.grid(i, 0)
        self.instancesWrapper.grid(row=0, column=0)
        self.newButton.grid(row=1, column=0, sticky='nsew')

    def run(self):
        self.window.mainloop()

    def hide(self):
        self.window.withdraw()

    def show(self):
        self.window.deiconify()

    def new(self):
        # def make_new(inst):
        #     view = InstanceView(self.window, inst, self.launch)
        #     self.instances.append(view)
        #     view.grid(len(self.instances), 0)
        # fresh = lib.Instance()
        # InstanceEdit(None, make_new)
        pass

    def launch(self, instance: lib.Instance):
        self.hide()
        try:
            instance.launch()
        finally:
            self.show()

    def quit(self):
        self.model.write()
        self.window.destroy()


class Section:
    def __init__(self, container, **kwargs):
        self.f = tk.Frame(container, **kwargs)

    def grid(self, row, column, **opts):
        self.f.grid(row=row, column=column, **opts)


class LabeledEntry(Section):
    def __init__(self, container, label, **kwargs):
        super().__init__(container, **kwargs)
        self.label = ttk.Label(self.f, text=label)
        self.entry = ttk.Entry(self.f)
        self.__draw()

    def __draw(self):
        self.label.grid(row=0, column=0)
        self.entry.grid(row=0, column=1)

    @property
    def value(self):
        return self.entry.get()

    @value.setter
    def value(self, new: str):
        self.entry.delete(0, 'end')
        self.entry.insert(0, new)


class PathSelector(Section):
    def __init__(self, container, label: str, suffix: str, **kwargs):
        super().__init__(container, **kwargs)
        self.var = tk.StringVar(value='inst:' + suffix)
        self.label = ttk.Label(self.f, text=label)
        self.instance = ttk.Radiobutton(self.f, text='Instance', variable=self.var,
                                        value='inst:' + suffix, command=self.hide_custom)
        self.main = ttk.Radiobutton(self.f, text='Main install', variable=self.var,
                                    value='sb:' + suffix, command=self.hide_custom)
        self.custom = ttk.Radiobutton(self.f, text='Custom location', variable=self.var,
                                      value='custom', command=self.show_custom)
        self.browser = ttk.Button(self.f, text='Select location...', command=self.ask_directory)
        self.suffix = suffix
        self.__draw()

    def __draw(self):
        self.label.grid(row=0, column=0)
        self.instance.grid(row=1, column=0, sticky='w')
        self.main.grid(row=2, column=0, sticky='w')
        self.custom.grid(row=3, column=0, sticky='w')

    def ask_directory(self):
        directory = filedialog.askdirectory()
        self.browser['name'] = directory
        self.var.set(directory)

    def show_custom(self):
        self.browser.grid(row=4, column=0)

    def hide_custom(self):
        self.browser.grid_remove()

    @property
    def value(self):
        return self.var.get()

    @value.setter
    def value(self, new: str):
        self.var.set(new)


class InstanceView(Section):
    def __init__(self, container, instance: lib.Instance,
                 launch: Callable[[lib.Instance], None], **kwargs):
        super().__init__(container, **kwargs)
        self.instance = instance
        self.launch_command = launch
        self.launch = ttk.Button(self.f, text=self.instance.name, command=self.launch_game)
        self.edit = ttk.Button(self.f, text='✎', command=self.edit_instance, width=2)
        self.__draw()

    def __draw(self):
        self.launch.grid(row=0, column=0, sticky='nsew')
        self.edit.grid(row=0, column=1, sticky='e')

    def launch_game(self):
        self.launch_command(self.instance)

    def edit_instance(self):
        def update():
            self.launch['text'] = self.instance.name

        InstanceEdit(self.instance, lambda i: update())


class InstanceEdit:
    def __init__(self, instance: lib.Instance,
                 callback: Callable[[lib.Instance], None]):
        self.callback = callback
        self.window = tk.Toplevel()
        self.window.wm_protocol('WM_DELETE_WINDOW', self.save)
        self.instance = instance
        self.name = LabeledEntry(self.window, 'Instance name')
        self.storage = PathSelector(self.window, 'Storage location', 'storage')
        self.mods = PathSelector(self.window, 'Mods location', 'mods')
        self.__draw()

    def __draw(self):
        self.name.value = self.instance.name
        self.name.grid(0, 0)
        self.storage.value = str(self.instance.storage)
        self.storage.grid(1, 0)
        self.mods.value = str(self.instance.mods)
        self.mods.grid(2, 0)

    def save(self):
        self.instance.set_storage(self.storage.value)
        self.instance.set_mods(self.mods.value)
        self.instance.set_name(self.name.value)
        self.callback(self.instance)
        self.window.destroy()


class SettingsMenu:
    def __init__(self, window, settings: lib.ApplicationSettings):
        self.menubar = tk.Menu(window)
        self.menu = tk.Menu(self.menubar, tearoff=False)
        self.settings = settings
        self.menu.add_command(label='Set Starbound directory',
                              command=lambda: self.select_directory(self.settings.starbound_dir,
                                                                    self.settings.set_starbound_dir))
        self.menu.add_command(label='Set instances root directory',
                              command=lambda: self.select_directory(self.settings.instances_dir,
                                                                    self.settings.set_instances_dir))
        self.menubar.add_cascade(menu=self.menu, label='Settings')

    def select_directory(self, starting, setter: Callable[[str], None]):
        directory = filedialog.askdirectory(initialdir=starting)
        setter(directory)
