
import os, sys
import pygame

pygame.init()

# en réalité le fichier .exe sera exécuté en console comme ceci :C:\chemin\vers\timf_visualizer.exe "C:\chemin\vers\image.timf"
# sys.argv est la liste des éléments de la commande donc :
# sys.argv[0] = "C:\chemin\vers\timf_visualizer.exe"
# sys.argv[1] = "C:\chemin\vers\image.timf"

"""if len(sys.argv) > 1 :
    file_to_show = sys.argv[1]
else:
    print("No file path provided. Please provide a .timf file path as a command line argument.")
    sys.exit(1)"""

file_to_show = "C:/Users/timot/Desktop/MyOwnExtension/test_images/sot_ref_image_2.timf"


# utils
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


def extract_info_from_timf_header(header: str) -> tuple[str, int, int]:
    """
    This function extracts and returns the information contained in the timf header passed.
    The timf header contains the magic number, the width and height of the image
    :param header: The header we want to get the information
    :return: Returns a tuple containing in this order: magic number, width, height.
    """

    # extracting the magic number
    magic_number_hex = header[:20]
    magic_number_bytes = []
    reconstructed_magic_number = ""

    # get each byte (chars two by two in hexa) and convert each byte from hexa to decimal
    for i in range(0, len(magic_number_hex), 2):
        magic_number_bytes.append(int(magic_number_hex[i:i + 2], 16))

    # finally convert these bytes in a string
    for byte in magic_number_bytes:
        reconstructed_magic_number += chr(byte)

    # then extracting the width and height
    width = int(header[20:28], 16) # 20th to 27th chars are the width
    height = int(header[28:36], 16)# 28th to 35th chars are the height

    # return the extracted info in a tuple
    return (reconstructed_magic_number,
            width,
            height)


def uncompress_timf_data(compressed_timf_data: str, debug_prints: bool = False) -> tuple[bool, str]:
    """
    This function uncompresses compressed .timf data and returns it. Also returns a boolean indicating if
    the decompression was successful. If not, it returns False and the compressed data is returned.
    If the decompression fails, it returns the compressed data instead of the uncompressed.

    :param compressed_timf_data: This is the compressed .timf that will be uncompressed
    :param debug_prints: Enables debug prints in the console
    :return: Returns the success of the decompression and the decompressed data (or compressed if fail)
    """

    uncompressed_data = ""
    sequence_lenght = 0

    if debug_prints: print("Starting decompression...")

    # cycle through the row 8 chars by 8 chars
    for i in range(len(compressed_timf_data) // 8):

        # get the value of each item (pixel color) in the row
        hex_value = compressed_timf_data[i * 8:(i + 1) * 8]

        # if the hex value starts with x, it's a compressed sequence, and we need to uncompress it
        if hex_value.startswith("x"):
            # keep the compression factor (sequence lenght) in memory to uncompress in the next loop
            sequence_lenght = int(hex_value[1:8])  # get the lenght of the sequence (value in the xFFFFFFF hex)

        elif sequence_lenght > 0:  # actually sequence lenght can't be under 3
            # if there's a compression factor in memory, we have to expand the sequence with the current hex value
            uncompressed_data += str(hex_value) * sequence_lenght
            sequence_lenght = 0  # reset the compression factor

        else:
            # if it isn't, just add the value to the uncompressed row
            uncompressed_data += hex_value

        # show progress
        if debug_prints: print(
            f"It's {i / (len(compressed_timf_data) // 8) * 100:.2f}% of the image that have been uncompressed.")

    if debug_prints: print("Decompression finished.")

    # return uncompressed data if everything went right
    return True, uncompressed_data


def draw_pixel(surface: pygame.Surface, x: int, y: int, color: tuple[int, int, int, int]):
    if not (0 <= x < surface.get_width() and 0 <= y < surface.get_height()):
        return  # pixel out of bounds

    surface.set_at((x, y), pygame.Color(*color))


def draw_image(surface: pygame.Surface, size: tuple[int, int], rgba_values: list[tuple[int, int, int, int]]):
    """ Draw the image represented by the list of RGBA values. """

    width, height = size
    i = 0

    for y in range(height):
        for x in range(width):

            draw_pixel(surface, x, y, rgba_values[i])
            i += 1


def get_rgb_from_timf_data(raw_timf_data: str) -> list[tuple[int, int, int, int]]:
    """
    Extracts rgba values of pixels from the timf data. Returns it in a list of tuple (each tuple is a pixel).
    :param raw_timf_data: The timf data we want to extract the pixel values.
    :return: A list of tuple containing integers
    """

    rgba_values = []

    # cycle through raw timf data 8 by 8 characters and converting it to RGBA values to put them in the new image
    for i in range(len(raw_timf_data)//8):

        pixel_hex = raw_timf_data[i*8:(i+1)*8]

        rgba_values.append(hex_to_rgba(pixel_hex))

    return rgba_values


def visualize_timf_image(timf_path: str) -> None:

    # check if the file exists
    if not os.path.exists(timf_path):
        raise FileNotFoundError(f"The {timf_path} file doesn't exist.")  # the timf file doesn't exist

    # get the timf data
    with open(timf_path, "r") as file:
        timf_file_data = file.read()

    # separate the header from the data
    header = timf_file_data[:36]  # header is the 36 first chars (0 to 35th)
    compressed_timf_data = timf_file_data[36:]

    # extract information from the timf header
    reconstructed_magic_number, width, height = extract_info_from_timf_header(header)

    # uncompressing the data to be able to use it
    raw_timf_data = uncompress_timf_data(compressed_timf_data)[1]

    # create the visualizer window surface
    window = pygame.display.set_mode((width, height))

    # draw the image
    draw_image(window, (width, height), get_rgb_from_timf_data(raw_timf_data))

    run = True
    while run:
        # quitting loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.flip()
    pygame.quit()


path = "C:/Users/timot/Desktop/MyOwnExtension/test_images/sot_ref_image.timf"
visualize_timf_image(path)