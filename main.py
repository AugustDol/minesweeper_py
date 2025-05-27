import pygetwindow as gw
import time
import mss
from PIL import Image, PyAccess
import pyautogui

area = {
  'left': 690,
  'top': 340,
  'width': 540,
  'height': 485
}


def capture_screenshot() -> PyAccess:
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

def click(x, y, r_click = False):
  pyautogui.moveTo(area['left'] + x*30 + 21, area['top'] + 60 + y*30 + 19)
  if r_click:
    pyautogui.rightClick()
  else:
    pyautogui.click()

def analyse_screenshot(screenshot: PyAccess):
  # 1 -> una bomba vicino
  # 2 -> due bombe vicine
  # 3...
  # 8 -> otto bombe vicine
  # 0 -> nessuna bomba vicina
  # 10 -> bomba
  # -1 -> casella non aperta
  rows, cols = 540, 485
  matrix = [[0 for _ in range(14)] for _ in range(18)]
  unique_colors = set()
  color_positions = {}
  
  for y in range(75, cols, 30):
    for x in range(15, rows, 30):
        pixel = screenshot[x, y]
        matrix_y = (y - 79) // 30
        matrix_x = (x - 21) // 30
        
        
        # Aggiungi il colore all'insieme dei colori unici
        if pixel not in color_positions:
          color_positions[pixel] = []
        color_positions[pixel].append((matrix_x, matrix_y))
        
        
        # Mappatura dei colori come nel tuo codice originale
        if pixel == (185,221,119) or pixel == (170,215,81) or pixel == (162,209,73):
            matrix[matrix_x][matrix_y] = -1
        elif pixel == (215,184,153) or pixel == (229,194,159):
            matrix[matrix_x][matrix_y] = 0
        elif pixel == (25,118,210):
            matrix[matrix_x][matrix_y] = 1
        elif pixel == (56,142,60):
            matrix[matrix_x][matrix_y] = 2
        elif pixel == (211,47,47):
            matrix[matrix_x][matrix_y] = 3
        elif pixel == (123,31,162):
            matrix[matrix_x][matrix_y] = 4
        else:
            # Se il colore non è mappato, assegna un valore speciale (es. 99)
            matrix[matrix_x][matrix_y] = 99
        
  print(f"Casella ({matrix_x}, {matrix_y}): {matrix[matrix_x][matrix_y]} - Colore: {pixel}")

  print("\nPosizioni per ogni colore:")
  for color, positions in color_positions.items():
    print(f"{color}: {positions}")
      

  
  

if __name__ == '__main__':
  screenshot = capture_screenshot()
  click(3, 3)
  analyse_screenshot(screenshot)
  
  rows, cols = 18, 14
  matrix = [[0 for _ in range(cols)] for _ in range(rows)]
    
