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

    def __init__(self) -> None:
        self.load_config()
        self.root = tk.Tk()
        self.root.title("SSH(PuTTY/KiTTY) Session Manager")
        # root.eval("tk::PlaceWindow . center")
        self.root.geometry(self.config['geometry'])
        self.root.resizable(False, False)

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
        cnt = 0
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
            # C:\Users\yucho\Documents\apps\kitty-bin-0.76.0.8\kitty.exe -load "**OracleVM0"
            btn.bind("<Button-1>", lambda event, session=sess_name: self.run_session(event, session))
            cnt += 1
            # __LAST_ELEMENT_NAME = f"{idx}{sess_name}"
        # set_element_count(cnt)

    def get_sub_registry(self, REG_PATHS):
        i = 0
        for REG_PATH in REG_PATHS:
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
            while True:
                try:
                    name = winreg.EnumKey(registry_key, i)
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



def onWindowConfig(event, tkapproot):
    # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/event-handlers.html
    global __LAST_ELEMENT_NAME
    global __NEW_HEIGHT
    if str(event.widget) != '.':
        # widget_name = event.widget.cget("text")
        # if __LAST_ELEMENT_NAME and __LAST_ELEMENT_NAME == widget_name:
        #     tkapproot.geometry(f'200x{event.y + event.height}')
        # tkapproot.unbind("<Configure>")
        # w, h, x, y = get_geometry(tkapproot)
        if __NEW_HEIGHT <= (event.y + event.height):
            print(f'changed to {__NEW_HEIGHT} > {event.y + event.height}')
            tkapproot.geometry(f'200x{event.y + event.height}')
            __NEW_HEIGHT = event.y + event.height

if __name__ == '__main__':
    app = App()
    app.run()
    exit()
    # https://stackoverflow.com/a/32289245
    # root.bind("<Configure>", lambda event, tkapproot=root: onWindowConfig(event, tkapproot))

"""
python -m nuitka --plugin-enable=tk-inter --mingw64 --windows-disable-console --onefile main.py -o puttysession.exe
# Nuitka-Onefile:WARNING: Onefile mode cannot compress without 'zstandard' module installed.
"""
