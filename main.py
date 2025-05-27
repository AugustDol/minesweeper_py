import pygetwindow as gw
import time
import mss
from PIL import Image
import pyautogui

area = {
  'left': 685,
  'top': 335,
  'width': 550,
  'height': 490
}


def capture_screenshot():
  print("In attesa che la finestra di Chrome diventi attiva...")
  # Loop finché la finestra di Chrome non è attiva
  while True:
      chrome_windows = [win for win in gw.getWindowsWithTitle('minesweeper - Cerca con Google') if not win.isMinimized]
      if chrome_windows and chrome_windows[0] == gw.getActiveWindow():
          print("Finestra di Chrome attiva!")
          break
      time.sleep(1)  # Aspetta un secondo prima di controllare di nuovo


  # Cattura lo screenshot
  with mss.mss() as screen:
      screenshot = screen.grab(area)
  # Converte lo screenshot in un'immagine e lo salva
  image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
  image.save("screenshot.png")
  print("Screenshot salvato come screenshot.png")
  return image.load()

def click(x, y):
  # un quadrato è 550/14 = 30, 490/18 = 30
  
  pyautogui.moveTo(area['left'], area['top'] + 60)

    
if __name__ == '__main__':
  screenshot = capture_screenshot()
  
    # 1 -> una bomba vicino
    # 2 -> due bombe vicine
    # 3...
    # 8 -> otto bombe vicine
    # 0 -> nessuna bomba vicina
    # 10 -> bomba
    # -1 -> casella non aperta
    
    
    
  rows, cols = 18, 14
  matrix = [[0 for _ in range(cols)] for _ in range(rows)]
