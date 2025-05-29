import random
import pygetwindow as gw
import time
import mss
from PIL import Image
import pyautogui
import keyboard 
import sys

cols, rows, width, height  = (None, None, None, None)
grid_area = None
grid = None

def is_grid_border_color(pixel, tolerance=1):
    """Check if pixel matches grid border color (gray) with tolerance"""
    r, g, b = pixel
    return (abs(r - 198) <= tolerance and 
            abs(g - 198) <= tolerance and 
            abs(b - 198) <= tolerance)

def is_unopened_cell_color(pixel, tolerance=5):
    """Check if pixel matches unopened cell color (green) with tolerance"""
    r, g, b = pixel
    return ((abs(r - 185) <= tolerance and abs(g - 221) <= tolerance and abs(b - 119) <= tolerance) or
            (abs(r - 170) <= tolerance and abs(g - 215) <= tolerance and abs(b - 81) <= tolerance) or
            (abs(r - 162) <= tolerance and abs(g - 209) <= tolerance and abs(b - 73) <= tolerance))

def find_grid_area(window):
    with mss.mss() as sct:
        win_area = {
            'left': window.left,
            'top': window.top,
            'width': window.width,
            'height': window.height
        }
        screenshot = sct.grab(win_area)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        pixels = img.load()

    width = win_area['width']
    height = win_area['height']
    
    # Find top-left unopened cell
    start_x = start_y = None
    for y in range(height):
        for x in range(width):
            if is_unopened_cell_color(pixels[x, y]):
                start_x, start_y = x, y
                break
        if start_x is not None:
            break

    if start_x is None or start_y is None:
        return None  # No cell found
    

    # Find bottom-left border (same column, going downward)
    end_y = None
    for y in range(start_y, height):
        if not is_unopened_cell_color(pixels[start_x, y]):
            end_y = y
            break
    if end_y is None:
        end_y = height

    # Find top-right border (same row, going right)
    end_x = None
    for x in range(start_x, width):
        if not is_unopened_cell_color(pixels[x, start_y]):
            end_x = x
            break
    if end_x is None:
        end_x = width

    grid_area = {
        'left': window.left + start_x,
        'top': window.top + start_y,
        'width': end_x - start_x,
        'height': end_y - start_y
    }

    return grid_area

def read_screen():
    """Capture Minesweeper grid screenshot with auto-detection"""
    global grid_area
    print("Finding Minesweeper window...")
    minesweeper_window = None
    
    while True:
      chrome_windows = [win for win in gw.getWindowsWithTitle('minesweeper - Cerca con Google') if not win.isMinimized]
      if chrome_windows and chrome_windows[0] == gw.getActiveWindow():
        print("Finestra di Chrome attiva!")
        minesweeper_window = chrome_windows[0]
        break
      time.sleep(1)
    
    if not minesweeper_window:
      raise Exception("Minesweeper window not found")
    
    print(f"Found window: {minesweeper_window.title}")
    minesweeper_window.activate()
    time.sleep(0.5)  # Wait for window activation
    
    # Detect grid location
    grid_area = find_grid_area(minesweeper_window)
    if not grid_area:
        raise Exception("Could not detect Minesweeper grid")
    
    print(f"Grid detected at: {grid_area}")
    
    # Capture screenshot    
    return capture_screenshot()

def capture_screenshot():
    global grid_area
    with mss.mss() as sct:
        screenshot = sct.grab(grid_area)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        img.save("screenshot.png")
        print("Screenshot saved as screenshot.png")
    
    return img.load()

def click(x, y, grid_area, r_click=False):
    """Click on a grid cell"""
    px_x = grid_area['left'] + x * width // cols + width // (2 * cols)
    px_y = grid_area['top'] + y * height // rows + height // (2 * rows)
    pyautogui.moveTo(px_x, px_y)
    pyautogui.rightClick() if r_click else pyautogui.click()

def detect_grid_size(img):
    global width, height 
    pixels = img.load()
    width, height = img.size 

    base_color = pixels[0, 0]

    cell_w = 1
    for dx in range(1, width):
        if pixels[dx, 0] != base_color:
            break
        cell_w += 1

    cell_h = 1
    for dy in range(1, height):
        if pixels[0, dy] != base_color:
            break
        cell_h += 1

    cols = width // cell_w
    rows = height // cell_h

    return cols, rows

def get_neighboring_cells(x, y, cols, rows):
    neighbors = []
    offsets = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1),         (0, 1),
               (1, -1), (1, 0), (1, 1)]  # All directions

    for dx, dy in offsets:
        nx, ny = x + dx, y + dy  # Neighbor coordinates
        if 0 <= nx < cols and 0 <= ny < rows:  # Check bounds
            neighbors.append((nx, ny))  # Append valid coordinates

    return neighbors

def get_number_from_color(pixel, tolerance=100):

    color_map = {
        (25, 118, 210): '1',
        (56, 142, 60): '2',
        (211, 47, 47): '3',
        (123,31,162): '4',
    }
    rgb = pixel[:3] if len(pixel) == 4 else pixel 
    for color, number in color_map.items():
        if all(abs(rgb[i] - color[i]) <= tolerance for i in range(3)):
            return number
    return '□'

def read_grid(flagged_positions=None):
    """Read the Minesweeper grid from the screenshot and detect numbers by color"""
    img = Image.open("screenshot.png")
    pixels = img.load()
    cols, rows = detect_grid_size(img)
    
    grid = []
    for y in range(rows):
        row = []
        for x in range(cols):
            cell_color = pixels[x * width // cols + width // (2 * cols), 
                                y * height // rows + height // (2 * rows)]
            if is_unopened_cell_color(cell_color):
                row.append('■')
            else:
                row.append(get_number_from_color(cell_color))
        grid.append(row)
    
    if flagged_positions:
        for x, y in flagged_positions:
            grid[y][x] = 'B'
    
    print("Current Minesweeper grid:")
    for row in grid:
        print(' '.join(row))
    return grid

def read_all_numbers():
    numbers = []
    for y in range(rows):
        for x in range(cols):
            if grid[y][x].isdigit():
                numbers.append((x, y))

    for x, y in numbers:
        if grid[y][x].isdigit():
            neighboring_cells = get_neighboring_cells(x, y, cols, rows)
            # print(f"Neighboring cells for position ({x}, {y}): {[(nx, ny, grid[ny][nx]) for nx, ny in neighboring_cells]}")

            

if __name__ == '__main__':

    screenshot = read_screen()
    img = Image.open("screenshot.png")
    cols, rows = detect_grid_size(img)
    
    print(f"Grid size: {cols} columns x {rows} rows")
    
    click(random.randint(0, cols-1), random.randint(0, rows-1), grid_area)
    time.sleep(1) 
    
    flagged_positions = set()
            
    capture_screenshot()
    img = Image.open("screenshot.png")
    grid = read_grid(flagged_positions)
    
    read_all_numbers()