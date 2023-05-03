import Auto_Chess
import time
import random
from PIL import ImageGrab
import pyautogui
from pyclick import HumanClicker
import pytweening
from pyclick.humancurve import HumanCurve

import os


"""
Settings:
Chess.com:
Pieces: Classic
Board: Green
Animation Type: None
Highlight Moves: off

"""


def checkColor(x, y):
    bbox = (x, y, x + 1, y + 1)
    im = ImageGrab.grab(bbox=bbox)
    rgbim = im.convert('RGB')
    r, g, b = rgbim.getpixel((0, 0))
    return r, g, b


def CheckWhite():
    if checkColor(343, 922) == (255, 255, 255) and checkColor(343, 221) == (0, 0, 0):
        return True
    return False


def CheckBlack():
    if checkColor(343, 922) == (0, 0, 0) and checkColor(343, 221) == (255, 255, 255):
        return True
    return False


def GameOver():
    if checkColor(1171, 665) == (127, 166, 80): # One side won
        return True
    if checkColor(693, 519) == (216, 225, 206): # Abort
        return True
    return False


def main(legitt):
    while (1):

        if CheckWhite():
            who = "w"
            Auto_Chess.main(legitt, who)
        elif CheckBlack():
            who = "b"
            Auto_Chess.main(legitt, who)
        else:
            print("INVALID SIDE")

        if True:
            os.system('cls')
            print("game over.")
            time.sleep(random.randint(1, 35) / 10)
            hc = HumanClicker()
            x, y = (1254, 948)
            curve = HumanCurve(pyautogui.position(), (
                x - random.randint(-13, 13),
                y - random.randint(-13, 13)),
                               distortionFrequency=0, tweening=pytweening.easeInOutQuad,
                               offsetBoundaryY=8, offsetBoundaryX=8, targetPoints=random.randint(30, 40))
            hc.move((x, y), duration=0.02, humanCurve=curve)

            pyautogui.press("f5")
            time.sleep(10)

            pyautogui.click()
            time.sleep(0.1)
            pyautogui.click()

            while (GameOver()):
                time.sleep(1)
            time.sleep(3)
            continue


if __name__ == "__main__":
    while 1:
        legit = input("Do you want legit mode? (y/n): ")
        if legit != "y" and legit != "n":
            print("Please type y or n.")
            continue
        break

    main(legit)
