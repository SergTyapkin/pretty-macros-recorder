import time
import keyboard
from constants import fileControlsNames
from utils import *


currentConfig = {}
stop = False

recordingState = False
recordTargetName = None
def onKeyboardEvent(event):
    global recordingState, stop, recordTargetName
    if not isinstance(event, keyboard.KeyboardEvent):
        return

    if event.event_type != 'down':
        return

    if not recordingState:
        if event.scan_code == 1:  # Esc
            stop = True
        else:
            idx = -1
            if 2 <= event.scan_code <= 10:  # 2 = key '1'; 10 = key '9'
                idx = event.scan_code - 2
            elif event.scan_code in [30, 48, 46]:  # 'abc'
                idx = 9 + [30, 48, 46].index(event.scan_code)
            else:
                return
            recordTargetName = list(fileControlsNames.keys())[idx]
            print("\nRecord key for \"", recordTargetName, '\" ...', sep='')
            recordingState = True
        return

    hotkeys = handleRecordHotkeys(event)
    if hotkeys is None:
        return

    print("Recorded for ", recordTargetName, ": ")
    print("Hotkeys: ", hotkeys)

    currentConfig[recordTargetName] = hotkeys

    printMenuChangeConfig(currentConfig)

    recordTargetName = None
    recordingState = False


if __name__ == '__main__':
    # --- READ CONFIG ---
    currentConfig = readConfig()
    print(currentConfig)

    # --- PRINT MENU ---
    printMenuChangeConfig(currentConfig)

    # --- START LISTEN ---
    keyboard._listener.add_handler(onKeyboardEvent)
    while not stop:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            stop = True

    # --- EXIT AND WRITE CONFIG ---
    writeConfig(currentConfig)
