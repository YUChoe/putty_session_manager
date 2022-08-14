import tkinter as tk
import winreg  # pip install pywin32
import subprocess
from urllib.parse import unquote
import json
import os
from typing import Dict


class App():

    config_filename: str = "ssh_session_config.json"
    config: Dict = {}
    __NEW_HEIGHT = 0

    def __init__(self) -> None:
        self.load_config()
        self.root = tk.Tk()
        self.root.title("SSH(PuTTY/KiTTY) Session Manager")
        # root.eval("tk::PlaceWindow . center")
        self.root.geometry(self.config['geometry'])
        self.root.resizable(False, False)
        # https://stackoverflow.com/a/32289245
        self.root.bind("<Configure>", lambda event, tkapproot=self.root: self.onWindowConfig(event, tkapproot))
        self.draw_frame()

    def run(self):
        self.root.mainloop()

    def load_config(self):

        self.config = {}
        if not os.path.isfile(self.config_filename):
            self.make_config()
        with open(self.config_filename) as fp:
            self.config = json.load(fp)

        self.config['geometry'] = f"{self.config['width']}x200+{self.config['x']}+{self.config['y']}"

        print('DEB', self.config)

    def make_config(self):
        self.config = {}
        self.config['width'] = 230
        self.config['x'] = 1
        self.config['y'] = 1
        self.config['putty'] = r".\kitty-0.76.0.10.exe"

        with open(self.config_filename, 'w') as fp:
            json.dump(self.config, fp)

    def draw_frame(self):
        frame = self.root
        tk.Grid.rowconfigure(frame, 0, weight=1)

        tk.Grid.columnconfigure(frame, 0, weight=1)
        btn = tk.Button(frame)
        btn.grid(sticky='we')

        REG_PATHS = [r"Software\9bis.com\KiTTY\Sessions", r'Software\SimonTatham\PuTTY\Sessions']
        # cnt = 0
        for idx, sess_name in self.get_sub_registry(REG_PATHS):
            if sess_name == 'Default%20Settings': continue
            # SESS_PATH = f"{REG_PATH}\{sess_name}"
            tk.Grid.columnconfigure(frame, idx, weight=1)
            sess_name = unquote(sess_name, encoding="cp949")
            btn = tk.Button(
                frame,
                text=sess_name, font=("Cascadia Code Light", 9),
                anchor="w",
                bg="#28393a", fg="white",
                cursor="hand2",
                activebackground="#badee2", activeforeground="black",
            )
            btn.grid(sticky='we')
            btn.bind("<Button-1>", lambda event, session=sess_name: self.run_session(event, session))
            # cnt += 1

    def get_sub_registry(self, REG_PATHS):
        i = 0
        for REG_PATH in REG_PATHS:
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
            while True:
                try:
                    name = winreg.EnumKey(registry_key, i)
                    print(f"{REG_PATH}/{name}")
                    yield i, name
                    i += 1
                except OSError as e:
                    if e.errno != 22:
                        print(e)
                    break

    def run_session(self, event, session):
        # kitty = r"C:\Users\yucho\Documents\apps\kitty-bin-0.76.0.8\kitty.exe"
        cmd = f'{self.config["putty"]} -load "{session}"'
        print(cmd)
        subprocess.Popen(cmd)  # detached

    def onWindowConfig(self, event, tkapproot):
        # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/event-handlers.html
        # widget_name = event.widget.cget("text")
        if str(event.widget) == '.': return
        this_height = event.y + event.height
        if self.__NEW_HEIGHT <= this_height:
            print(f'changed to {self.__NEW_HEIGHT} > {this_height}')
            tkapproot.geometry(f'{self.config["width"]}x{this_height}')
            self.__NEW_HEIGHT = this_height


if __name__ == '__main__':
    app = App()
    app.run()
