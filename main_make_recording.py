import os
import sys
import time
import keyboard
import mouse
from constants import fileControlsNames
from utils import *


recording = []
stop = False
keyboardRecordType = None
recordedKeys = []
recordHotkeyCallback = None
ignoreNextKeyboardEvent = False

mouseButtons = [mouse.LEFT, mouse.MIDDLE, mouse.RIGHT]
mouseButtonSelected = 0
def change_mouse_button():
    global mouseButtonSelected
    mouseButtonSelected = (mouseButtonSelected + 1) % len(mouseButtons)
    print("Active mouse button switched to", mouseButtons[mouseButtonSelected].upper())

lastEventTime = None
def getEventTimeDelta():
    global lastEventTime
    d = 0
    nowTime = time.time()
    if lastEventTime:
        d = nowTime - lastEventTime
    lastEventTime = nowTime
    return d

lastMousePos = (0, 0)
def save_mouse_position():
    global lastMousePos
    lastMousePos = (x, y) = mouse.get_position()

    duration = getEventTimeDelta()
    recording.append({
        'class': 'mouse',
        'type': 'move',
        'x': x, 'y': y,
        'timing-function': 'ease-out',
        'duration': duration,
    })
    print(f'{"Move to":10} {x:4},{y:4}. Time  {duration:f}sec')
def _save_mouse_event(name):
    duration = getEventTimeDelta()
    recording.append({
        'class': 'mouse',
        'type': name,
        'button': mouseButtons[mouseButtonSelected],
        'after': duration,
    })
    print(f'{name.capitalize():7} button {mouseButtons[mouseButtonSelected].upper():5}. After {duration:f}sec')
def save_mouse_click():
    _save_mouse_event("click")
def save_mouse_press():
    _save_mouse_event("hold")
def save_mouse_release():
    _save_mouse_event("release")
def move_mouse_to_last_saved_pos():
    mouse.move(lastMousePos[0], lastMousePos[1])
    print("Mouse moved to las pos:", lastMousePos)

def _save_keyboard_event(name, hotkey):
    duration = getEventTimeDelta()
    recording.append({
        'class': 'keyboard',
        'type': name,
        'after': duration,
        'hotkey': hotkey
    })
    print(f'Key {name.capitalize():7} {hotkey:10}. After {duration:f}sec')
def _set_keyboard_hotkeys_callback(callback):
    global recordHotkeyCallback, ignoreNextKeyboardEvent, keyboardRecordType
    print("Waiting for press any hotkeys...")
    keyboardRecordType = 'single'
    recordHotkeyCallback = callback
    ignoreNextKeyboardEvent = True
def save_keyboard_hit(hotkey=None):
    if hotkey is None:
        _set_keyboard_hotkeys_callback(save_keyboard_hit)
        return
    _save_keyboard_event("hit", hotkey)
def save_keyboard_hold(hotkey=None):
    if hotkey is None:
        _set_keyboard_hotkeys_callback(save_keyboard_hit)
        return
    _save_keyboard_event("hold", hotkey)
def save_keyboard_release(hotkey=None):
    if hotkey is None:
        _set_keyboard_hotkeys_callback(save_keyboard_release)
        return
    _save_keyboard_event("release", hotkey)

textTypeStartedAfter = None
def start_text_typing_recording():
    global keyboardRecordType, recordedKeys, textTypeStartedAfter, ignoreNextKeyboardEvent
    print("Start listening for typing text...")
    keyboardRecordType = 'text'
    textTypeStartedAfter = getEventTimeDelta()
    ignoreNextKeyboardEvent = True
    recordedKeys = []
def stop_text_typing_recording():
    global recordedKeys, textTypeStartedAfter
    duration = getEventTimeDelta()
    recording.append({
        'class': 'keyboard',
        'type': 'text',
        'after': textTypeStartedAfter,
        'duration': duration,
        'text': recordedKeys
    })
    print(f'Type text {recordedKeys}. After {textTypeStartedAfter:f}sec. Duration {duration:f}sec')
    textTypeStartedAfter = None
    recordedKeys = []

def stop_recording():
    global stop
    stop = True

controlsFunctions = {
    "save_mouse_position": save_mouse_position,
    "save_mouse_click": save_mouse_click,
    "save_mouse_hold": save_mouse_press,
    "save_mouse_release": save_mouse_release,
    "move_mouse_to_last_saved_pos": move_mouse_to_last_saved_pos,
    "change_mouse_button": change_mouse_button,

    "save_keyboard_hit": save_keyboard_hit,
    "save_keyboard_hold": save_keyboard_hold,
    "save_keyboard_release": save_keyboard_release,

    "start_text_typing_recording": start_text_typing_recording,
    "stop_text_typing_recording": stop_text_typing_recording,

    "stop_recording": stop_recording,
}

def onKeyboardEvent(event):
    global recordHotkeyCallback, ignoreNextKeyboardEvent
    if not isinstance(event, keyboard.KeyboardEvent):
        return

    if event.event_type != 'down':
        return
    if ignoreNextKeyboardEvent:
        ignoreNextKeyboardEvent = False
        return

    if keyboardRecordType == 'single':
        if recordHotkeyCallback is None:
            return

        hotkeys = handleRecordHotkeys(event)
        if hotkeys is not None:
            recordHotkeyCallback(hotkeys)
            recordHotkeyCallback = None
    elif keyboardRecordType == 'text':
        recordedKeys.append(event.name)


def writeRecording(recording):
    print("Recording ends.")
    if len(recording) == 0:
        print("Recording is empty")
        return

    if not os.path.isdir("recordings"):
        os.mkdir("recordings")

    curTimeStr = time.strftime("%Y-%m-%d-_%H-%M-%S")
    fileName = 'recordings/recording_' + curTimeStr + '.json'
    with open(fileName, 'w') as file:
        json.dump(recording, file, indent='\t')

    print(f"Saved to new file in local folder \"{fileName}\".")


if __name__ == '__main__':
    # --- READ CONFIG ---
    controlsConfig = readConfig(False)
    if controlsConfig is None:
        print("Configure controls using \"main_controls_configure.py\" firstly!")
        sys.exit()

    # --- HANDLE CONTROLS ---
    print("Waiting for actions...")
    for eventName in controlsConfig:
        control = controlsConfig[eventName]
        try:
            function = controlsFunctions[eventName]
            keyboard.add_hotkey(control, function)
        except Exception as e:
            print(e)

    # --- START LISTEN ---
    keyboard._listener.add_handler(onKeyboardEvent)
    while not stop:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            stop = True

    # --- END ---
    writeRecording(recording)
