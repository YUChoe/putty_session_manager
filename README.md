# about
* SSH Session Manager for KiTTY, Putty
* [KiTTY](https://www.9bis.net/kitty/)
* [PuTTY](https://www.putty.org/)

# download
* [release](https://github.com/YUChoe/putty_session_manager/releases)

# build
```
(.venv) PS > pip install -r requitements_build.txt
(.venv) PS > python -m nuitka --plugin-enable=tk-inter --mingw64 --windows-disable-console --onefile main.py -o puttysession.exe
```

# license
* MIT
