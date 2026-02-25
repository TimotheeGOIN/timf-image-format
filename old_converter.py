
import os
from PIL import Image

"""
- The end-line character in .timf files is "00000000", so this value is not allowed in the image data.
"""

image_file_path = "C:/Users/timot/Desktop/MyOwnExtension/images/screen_lambda.png"

def rgba_to_hex(rgba: tuple[int, int, int, int]) -> str:
    """ Convert RGBA color to HEX format. 
    Explanation of {:02x}:
    - the ':' indicates the start of the format specifier.
    - the '0' means to pad with zeros if the number is less than 2 digits.
    - the '2' means to use at least 2 digits.
    - the 'x' means to format the number as hexadecimal. 
    Returns ex: #rrggbb and if alpha is not 255, #rrggbbaa
    So #rrggbb means #rrggbbaa with aa = ff (full opacity)
    """
    hex_color = "#{:02x}{:02x}{:02x}".format(rgba[0], rgba[1], rgba[2])

    if rgba[3] != 255: # If alpha is not fully opaque, include it in the hex 
        hex_color += "{:02x}".format(rgba[3])

    return hex_color

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

def format_hex_for_timf(hex: str) -> str: # find a name for my file format
    """ This format an hex value to the format used in .timf files. This consists in removing the # and explicit the alpha value.
    For example: #rrggbb becomes rrggbbaa.
    """

    formatted_hex = hex.lstrip('#')
    # explicit the alpha value if not already in (fully opaque)
    if len(formatted_hex) == 6:
        formatted_hex += "ff"

    if formatted_hex == "00000000": # "00000000" is the end-line character in .timf files, so in not allowed
        formatted_hex = "00000100"  # and replace with "00000100" that an human eye can't distinguish from "00000000"

    return formatted_hex

def get_filename_wo_enxtension(path: str) -> str:
    """ This function extracts the filename from a given file path. 
    For example, if the input is "C:/Users/Timot/Desktop/image.png", the output will be "image.png". """ 
    return os.path.basename(path)



# function that converts a .png image to a .timf image
def convert_png_to_timf(png_path: str, overwrite: bool=False, debug_prints: bool=False) -> bool:
    """ This function converts a .png image to a .timf image.
    - Returns True if the conversion was successful, False otherwise.
    """
    # check if the file exists
    if not os.path.exists(png_path):
        return False # the png file doesn't exist
    
    timf_file_data = ""
    png_img = Image.open(png_path).convert("RGBA")

    if debug_prints : print("Starting conversion...")

    # cycling through each pixel of the image and converting it to the .timf format
    for y in range(png_img.height): 
        for x in range(png_img.width): 
            
            # get the RGBA value of the pixel at (x, y)
            rgba = png_img.getpixel((x, y))

            # then convert it to hex, format it for .timf and add it to the timf_file_data string
            timf_file_data += format_hex_for_timf(rgba_to_hex(rgba))

        # when a row is finished add the new-line character (but not if this is the last line of the image)
        if y != png_img.height - 1:
            timf_file_data += "00000000" 

        if debug_prints : print(f"Row {y+1}/{png_img.height} converted. That's {(y+1)/png_img.height*100:.2f}%.")

    if debug_prints : print("Conversion finished.")

    # create the .timf file path
    folder_path = os.path.dirname(png_path)
    png_file_name = os.path.splitext(os.path.basename(png_path))[0] # get the filename and then get it without extension
    timf_file_path = folder_path + "/" + png_file_name + ".timf"

    if debug_prints : print(f"Writing .timf data to {timf_file_path}...")

    # when conversion is done, write .timf data in a .timf file
    try:
        with open(timf_file_path, "x") as file:
            file.write(timf_file_data)

    except FileExistsError:
        # if the file already exists, raise error if overwrite isn't allowed, othrwise overwrite the file with the same name
        if not overwrite:
            print(f"Error: The file {timf_file_path} already exists.")
            return False
        
        else:
            with open(timf_file_path, "w") as file:
                file.write(timf_file_data)
    
    if debug_prints : print("Done !")
    return True


def convert_timf_to_png(timf_path: str, overwrite: bool=False, debug_prints: bool=False) -> bool:
    """ This function converts a .timf image to a .png image.
    - Returns True if the conversion was successful, False otherwise.
    """
    # check if the file exists
    if not os.path.exists(timf_path):
        return False # the timf file doesn't exist
    
    with open(timf_path, "r") as file:
        timf_file_data = file.read()

    # split the data into rows using the end-line character "00000000" (make the "00000000" disappear in the process)
    rows = timf_file_data.split("00000000")

    # get the width and height of the image
    width = len(rows[0]) // 8 # each pixel is represented by 8 characters in hex (rrggbbaa)
    height = len(rows)

    if debug_prints : print(f"Image dimensions: {width}x{height}")

    # create a new image with the same dimensions as the original image
    png_img = Image.new("RGBA", (width, height))

    # cycling through each row and converting it to RGBA values to put them in the new image
    for y, row in enumerate(rows):
        for x in range(width):
            
            # get the hex color of the pixel at (x, y) (grabs 8 by 8 characters in the row)
            hex_color = row[x*8:(x+1)*8]
            # convert it to RGBA
            rgba = hex_to_rgba(hex_color)
            # put the pixel in the new image
            png_img.putpixel((x, y), rgba)

        if debug_prints : print(f"Row {y+1}/{height} converted. That's {(y+1)/height*100:.2f}%.")

    if debug_prints : print("Conversion finished.")

    # create the .png file path
    folder_path = os.path.dirname(timf_path)
    timf_file_name = os.path.splitext(os.path.basename(timf_path))[0] # get the filename and then get it without extension
    png_file_path = folder_path + "/" + timf_file_name + ".png"

    if debug_prints : print(f"Saving .png image to {png_file_path})...")

    png_img.save(png_file_path)

    return True 


result = convert_png_to_timf(image_file_path, overwrite=True, debug_prints=True)

#result = convert_timf_to_png("C:/Users/timot/Desktop/MyOwnExtension/images/image.timf", overwrite=True, debug_prints=True)

print(f"Conversion result: {result}")
