import os
import sys
import time
import keyboard
import mouse
from constants import fileControlsNames
from utils import *
from math import exp

recording = []
stop = False

FPS = 60
FRAME_TIME = 1 / FPS

movingFuncs = {
    "linear": lambda x: x,
    "ease-out": lambda x: ((-exp(-x*5)) + 1) * 1.007,
    "ease-out-light": lambda x: pow(x, 1/2),
}
def readRecording(fileName):
    try:
        with open(fileName, 'r') as file:
            try:
                return json.load(file)
            except Exception as e:
                print("Error while parsing json:", e)
    except:
        print("File not exists")
        sys.exit()


def getLatestFileNameFrom(path):
    import os
    files = os.listdir(path)
    files = [os.path.join(path, file) for file in files]
    files = [file for file in files if os.path.isfile(file)]
    if len(files) == 0:
        return None
    return max(files, key=os.path.getctime)


if __name__ == '__main__':
    # --- READ RECORDING ---
    print("Enter recording filename. To use latest hit 'enter'... ")
    filename = input('recordings/')
    if not filename:
        filename = getLatestFileNameFrom('recordings')
        if filename is None:
            print("Folder is empty!")
            sys.exit()
    else:
        filename = 'recordings/' + filename
    print(f'Reading \"{filename}\"...')
    recording = readRecording(filename)
    if recording is None:
        sys.exit()

    # --- HANDLE CONTROLS ---
    print()
    print("To stop playing hit 'Escape'")
    def stopFoo(_):
        global stop
        stop = True
    keyboard.on_press_key('esc', stopFoo)

    # --- START LISTEN ---
    print("PLAYING STARTS")
    for event in recording:
        eClass = event['class']
        eType = event['type']
        eDuration = event.get('duration')
        eAfter = event.get('after')
        if eAfter:
            time.sleep(eAfter)

        if eClass == 'mouse':
            eX = event.get('x')
            eY = event.get('y')
            eTimingFunc = event.get('timing-function')
            eButton = event.get('button')
            eDelta = event.get('delta')

            mouseX, mouseY = mouse.get_position()
            if eType == 'move':
                timeStart = time.time()
                allDx = eX - mouseX
                allDy = eY - mouseY
                progress = 0
                movingFunc = movingFuncs[eTimingFunc]
                while progress < 1 and not stop:
                    modifier = movingFunc(progress)
                    mouse.move(mouseX + allDx * modifier, mouseY + allDy * modifier)
                    newProgress = 1 if eDuration == 0 else (time.time() - timeStart) / eDuration
                    progressDelta = newProgress - progress
                    progress = newProgress
                    time.sleep(FRAME_TIME)
                mouse.move(eX, eY)

            elif eType == 'click':
                mouse.click(eButton)
            elif eType == 'hold':
                mouse.press(eButton)
            elif eType == 'release':
                mouse.release(eButton)
            elif eType == 'scroll':
                frames = eDuration * FPS
                wheelD = eDelta if eDuration == 0 else eDelta / frames
                i = 0
                while i < frames and not stop:
                    mouse.wheel(wheelD)
                    time.sleep(FRAME_TIME)
                    i += 1

        elif eClass == 'keyboard':
            eText = event.get('text')
            eHotkey = event.get('hotkey')

            if eType == 'hit':
                keyboard.send(eHotkey)
            elif eType == 'hold':
                keyboard.press(eHotkey)
            elif eType == 'release':
                keyboard.release(eHotkey)
            elif eType == 'text':
                timeDelta = 0 if len(eText) == 0 else eDuration / len(eText)
                i = 0
                while i < len(eText) and not stop:
                    keyboard.send(eText[i])
                    i += 1
                    time.sleep(timeDelta)

        if stop:
            break

    # --- END ---
    print("PLAYING ENDS")
