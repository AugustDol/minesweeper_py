import pygetwindow as gw
import time
import mss
from PIL import Image
import pyautogui

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
    """Detect Minesweeper grid location and calculate size based on borders"""
    # Capture entire window
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

def capture_screenshot():
    """Capture Minesweeper grid screenshot with auto-detection"""
    print("Finding Minesweeper window...")
    minesweeper_window = None
    
    # Try to find browser window with Minesweeper
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
    with mss.mss() as sct:
        screenshot = sct.grab(grid_area)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        img.save("screenshot.png")
        print("Screenshot saved as screenshot.png")
    
    return img.load(), grid_area

def click(x, y, grid_area, r_click=False):
    """Click on a grid cell"""
    # Calculate click position (center of cell)
    px_x = grid_area['left'] + x * 30 + 15
    px_y = grid_area['top'] + y * 30 + 15
    pyautogui.moveTo(px_x, px_y)
    pyautogui.rightClick() if r_click else pyautogui.click()

# Rest of your analysis code would go here...

if __name__ == '__main__':
    try:
        screenshot, grid_area = capture_screenshot()
        # Example: click on center cell
        click(8, 8, grid_area)
        # analyse_screenshot(screenshot)  # Your analysis function
    except Exception as e:
        print(f"Error: {str(e)}")