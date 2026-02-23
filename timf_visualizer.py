
import os, sys
import pygame

pygame.init()

# en realité le fichier .exe sera exécuté en console comme ceci :C:\chemin\vers\timf_visualizer.exe "C:\chemin\vers\image.timf"
# sys.argv est la liste des éléments de la commande donc :
# sys.argv[0] = "C:\chemin\vers\timf_visualizer.exe"
# sys.argv[1] = "C:\chemin\vers\image.timf"

if len(sys.argv) > 1 :
    file_to_show = sys.argv[1]
else:
    print("No file path provided. Please provide a .timf file path as a command line argument.")
    sys.exit(1)

def get_timf_size(timf_path: str) -> tuple[int, int] | None:
    """ This function gets the size of a .timf image. It returns a tuple (width, height) or None if the file doesn't exist. """
    if not os.path.exists(timf_path):
        return None # the timf file doesn't exist
    
    with open(timf_path, "r") as file:
        timf_file_data = file.read()

    rows = timf_file_data.split("00000000")

    width = len(rows[0]) // 8 # each pixel is represented by 8 characters in hex (rrggbbaa)
    height = len(rows)

    return (width, height)

window = pygame.display.set_mode(get_timf_size(file_to_show))

def draw_pixel(x: int, y: int, color: tuple[int, int, int, int]):
   
    if not (0 <= x < window.get_width() and 0 <= y < window.get_height()):
        return # pixel out of bounds
    
    window.set_at((x, y), pygame.Color(*color))


def hex_to_rgba(hex_color: str) -> tuple[int, int, int, int]:
    """ Convert HEX color to RGBA format. """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        hex_color += 'ff'  # Add full opacity if alpha is not provided

    rgba = (int(hex_color[0:2], 16), 
            int(hex_color[2:4], 16), 
            int(hex_color[4:6], 16), 
            int(hex_color[6:8], 16))
    
    return rgba


def get_rgb_from_timf(timf_path: str) -> bool:
    """ This function converts a .timf image to a .png image.
    - Returns True if the conversion was successful, False otherwise.
    """
    # check if the file exists
    if not os.path.exists(timf_path):
        return False # the timf file doesn't exist
    
    rgba_values = []
    
    # get the timf data
    with open(timf_path, "r") as file:
        timf_file_data = file.read()

    # split the data into rows using the end-line character "00000000" (make the "00000000" disappear in the process)
    rows = timf_file_data.split("00000000")

    # get the width and height of the image
    width = len(rows[0]) // 8 # each pixel is represented by 8 characters in hex (rrggbbaa)
    height = len(rows)

    # cycling through each row and converting it to RGBA values to put them in the new image
    for y, row in enumerate(rows):
        for x in range(width):
            
            # get the hex color of the pixel at (x, y) (grabs 8 by 8 characters in the row)
            hex_color = row[x*8:(x+1)*8]
            # convert it to RGBA
            rgba = hex_to_rgba(hex_color)
            # put the pixel in the new image
            rgba_values.append(rgba)

        rgba_values.append(False) # end of line

    return rgba_values


def draw_image(rgba_values: list[tuple[int, int, int, int] | bool]):
    """ Draw the image represented by the list of RGBA values. """
    x = 0
    y = 0
    for color in rgba_values:
        if color is False: # end of line
            y += 1
            x = 0
        else:
            draw_pixel(x, y, color)
            x += 1

run = True

draw_image(get_rgb_from_timf(file_to_show))

while run:
    # quitting loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    pygame.display.flip()

pygame.quit()
