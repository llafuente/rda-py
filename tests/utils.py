import logging
import time
from src.automation import Automation
from src.window import Window

language = "es"

def start(automation: Automation, request, process: str, params: str = ""):
    # start notepad.exe process
    automation.ahk.run_script(f'run {process} {params}')
    # TODO change to wait_one
    time.sleep(2.5)
    win = automation.windows().find_one({"process": process})

    def close():
        logging.debug(f"{process}.close()!")
        win.close()

    request.addfinalizer(close)
    logging.debug(win)
    return win

def notepad_selectall(win: Window):
    win.default_background_control = 'RichEditD2DPT1'
    if (language == "es"):
        win.send_keys("{CTRL down}e{CTRL up}")
    else:
        win.send_keys("{CTRL down}a{CTRL up}")