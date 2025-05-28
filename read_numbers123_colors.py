from PIL import Image

# This script will print the RGB color at the center of each number in the provided image
# Save the provided image as 'numbers123.png' in your project directory

def main():
    img = Image.open("numbers123.png")
    w, h = img.size
    # Manually measured centers for each number in the image
    # Adjust these if needed
    centers = {
        '1': (w-20, 15),   # top right
        '2': (w//2, h//2-10), # top left
        '3': (w//2+20, h-15), # bottom right
    }
    for label, (x, y) in centers.items():
        rgb = img.getpixel((x, y))
        print(f"Number {label}: RGB = {rgb}")

if __name__ == "__main__":
    main()
