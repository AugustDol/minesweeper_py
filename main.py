import pygetwindow as gw
import time
import mss
from PIL import Image
import pyautogui

cols, rows, width, height  = (None, None, None, None)
grid_area = None

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
    global width, height  # Make width and height global
    pixels = img.load()
    width, height = img.size  # Set global width and height

    # Find top-left cell color
    base_color = pixels[0, 0]

    # Find cell width: count pixels to first color change in row 0
    cell_w = 1
    for dx in range(1, width):
        if pixels[dx, 0] != base_color:
            break
        cell_w += 1

    # Find cell height: count pixels to first color change in column 0
    cell_h = 1
    for dy in range(1, height):
        if pixels[0, dy] != base_color:
            break
        cell_h += 1

    # Calculate columns and rows by dividing total size by cell size
    cols = width // cell_w
    rows = height // cell_h

    return cols, rows

def get_number_from_color(pixel):
    # These RGB values are from numbers123.png (with alpha channel)
    color_map = {
        (109, 147, 184): '1',   # blue (from your new screenshot)
        (56,142,60): '2',  # green (from your new screenshot)
        (211, 47, 47): '3',    # red (from your new screenshot)
    }
    rgb = pixel[:3] if len(pixel) == 4 else pixel  # Ignore alpha if present
    for color, number in color_map.items():
        if all(abs(rgb[i] - color[i]) < 40 for i in range(3)):
            return number
    return 'O'  # Opened or flagged, not a number

def read_grid():
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
                row.append('U')  # Unopened
            elif is_grid_border_color(cell_color):
                row.append('B')  # Border
            else:
                row.append(get_number_from_color(cell_color))
        grid.append(row)
    # Print the grid in a readable format
    print("Current Minesweeper grid:")
    for row in grid:
        print(' '.join(row))
    return grid

if __name__ == '__main__':
    try:
        screenshot = read_screen()
        img = Image.open("screenshot.png")
        cols, rows = detect_grid_size(img)
        
        print(f"Grid size: {cols} columns x {rows} rows")
        click(3, 3, grid_area)
        time.sleep(1)
        capture_screenshot()
        img = Image.open("screenshot.png")
        grid = read_grid()
    except Exception as e:
        print(f"Error: {str(e)}")