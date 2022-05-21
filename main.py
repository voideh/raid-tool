from time import sleep
from pynput import keyboard
import pytesseract
import pyautogui as pg
import pygetwindow as gw 
import cv2
import re
from tkinter import Tk

def execute():
    raid = gw.getWindowsWithTitle("Raid: Shadow Legends")[0]
    p = re.compile(r"(([A-z][a-z]+)+\s?)+(?:Lvl)")
    if raid:
        r = Tk()
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
        if not raid.isActive:
            raid.minimize()
            raid.restore()
            sleep(2)
        area = (raid.left, raid.top, raid.width, raid.height)
        print(f"[DBG] {area=}")
        
        im = pg.screenshot("test.png", region=area)
        img = cv2.imread("test.png")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18,18))

        dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        im2 = img.copy()

        with open("rec.txt", "w+") as f:
            for cnt in contours:
                x,y,w,h = cv2.boundingRect(cnt)

                rect = cv2.rectangle(im2, (x,y), (x + w, y + h), (0,255,0), 2)
                cropped = im2[y:y + h, x:x + w]

                text = pytesseract.image_to_string(cropped)
                f.write(f"{text}\n")

                baseUrl = "https://hellhades.com/champions/"
                match = p.search(text)
                if match:
                    print(f"[DBG - MATCH] {match.group()=}")
                    name = match.group().lower()
                    trimmed = name[:name.find('lvl')]
                    url = baseUrl + trimmed.replace(" ", "-")[:-1] + "/"
                    print(f"[DBG] {url=}")
                    r.withdraw()
                    r.clipboard_clear()
                    r.clipboard_append(url)

COMBOS = [ 
    {keyboard.Key.shift, keyboard.KeyCode(char='o')},
    {keyboard.Key.shift, keyboard.KeyCode(char='O')}
]

current = set()


TESSERACT_EXE = "C:\Program Files\Tesseract-OCR\\tesseract.exe"

def on_press(key):
    if any([key in COMBO for COMBO in COMBOS]):
        current.add(key)
        if any(all(k in current for k in COMBO) for COMBO in COMBOS):
            execute()

def on_release(key):
    if any([key in COMBO for COMBO in COMBOS]):
        current.remove(key)

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
