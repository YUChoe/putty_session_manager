import tkinter as tk
import winreg  # pip install pywin32
import subprocess
from urllib.parse import unquote
import json
import os
from typing import Dict
import pystray
from PIL import Image, ImageDraw


__title = "SSH(PuTTY/KiTTY) Session Manager"
__version = "0.1"


class App():

    config_filename: str = "ssh_session_config.json"
    config: Dict = {}
    __NEW_HEIGHT = 0
    __show = True

    def __init__(self, title) -> None:
        self.load_config()
        self.root = tk.Tk()
        self.root.title(title)
        # root.eval("tk::PlaceWindow . center")
        self.root.geometry(self.config['geometry'])
        self.root.resizable(False, False)
        # https://stackoverflow.com/a/32289245
        self.root.bind("<Configure>", lambda event, tkapproot=self.root: self.onWindowConfig(event, tkapproot))
        self.root.protocol("WM_DELETE_WINDOW", self.toggle)
        self.draw_frame()

    def run(self):
        self.root.mainloop()

    def quit(self):
        self.root.withdraw()  # hide
        self.root.quit()
        try:
            self.root.destroy()
        except RuntimeError as e:
            print(e)

    def toggle(self):
        self.__show = not self.__show
        if self.__show:
            self.root.deiconify()
        else:
            self.root.withdraw()

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


def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image


def on_clicked(icon, app):
    icon.visible = False
    icon.stop()
    app.quit()


def on_show(icon, app):
    app.toggle()


if __name__ == '__main__':
    app = App(__title)

    icon = pystray.Icon(__title)
    icon.icon = create_image(64, 64, 'black', 'white')

    icon.menu = pystray.Menu(
        pystray.MenuItem('Show', lambda: on_show(icon, app), default=True, visible=False),
        pystray.MenuItem('Quit', lambda: on_clicked(icon, app))
    )

    icon.run_detached()
    app.run()

    print('here again')
    exit()
