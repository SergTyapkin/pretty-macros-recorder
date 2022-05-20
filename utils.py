import json
from constants import fileControlsNames
import keyboard


_configFilename = 'UserControls.json'
def writeConfig(conf, withPrint=True):
    with open(_configFilename, 'w') as file:
        json.dump(conf, file, indent='\t')
        if withPrint:
            print(f"Config saved to {_configFilename}")

def readConfig(withCreate=True):
    try:
        with open(_configFilename, 'r') as file:
            conf = json.load(file)

            for name in fileControlsNames:
                if conf.get(name) is None:
                    conf[name] = fileControlsNames[name]
            return conf
    except:
        if withCreate:
            with open(_configFilename, 'w') as file:
                file.write("{}\n")
            return readConfig()
        else:
            return None


def printMenu(conf, _withChange=False):
    print(f'{"EVENT NAME":30} _ ({"KEYS":10})')
    print(f'{"-"*30} | ({"-"*10})')
    i = 1
    for name in fileControlsNames:
        print(f'{name:30} = ({conf[name]:10})' + ('. To change press: ' + (str(i) if i < 10 else (chr(ord('a') + i - 10))) if _withChange else ''), sep='')
        i += 1
    print()
def printMenuChangeConfig(conf):
    print("To configure controls press key:")
    print()
    printMenu(conf, True)
    print("save and exit ------- Esc")



_isInRecordingState = False
_hotkeysNames = set()
def handleRecordHotkeys(event):
    global _isInRecordingState
    if not isinstance(event, keyboard.KeyboardEvent):
        return

    if event.event_type != 'down':
        return

    if keyboard.is_modifier(event.scan_code):
        _hotkeysNames.add(event.name)
        return

    _isInRecordingState = False
    _hotkeysNames.add(event.name)

    return keyboard.get_hotkey_name(_hotkeysNames)
