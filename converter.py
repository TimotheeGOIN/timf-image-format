
import os
from PIL import Image
from utils import *

"""
- The end-line character in .timf files is "00000000", so this value is not allowed in the image data.
"""

image_file_path = "C:/Users/timot/Desktop/MyOwnExtension/images/screen_lambda.png"
magic_number = "bestformat" # obviously not
# [98, 101, 115, 116, 102, 111, 114, 109, 97, 116] in bytes


def get_timf_data_from_timf_file(timf_file_path: str) -> str | None:
    """
    This function loads the data in a .timf file and returns it. Return None if the function failed.
    :param timf_file_path: String that contains path to the .timf file we want the data from
    :return: Return the data got in the .timf file, or None if it failed
    """

    # check if the file exists
    if not os.path.exists(timf_file_path):
        return None # the timf file doesn't exist

    try:
        with open(timf_file_path, "r") as file:
            timf_file_data = file.read()

    except Exception as e:
        print(e)
        return None

    # return the data we got
    return timf_file_data


def get_pixels_from_png(png_path: str) -> list[tuple[int, ...]] | None:
    """
    This function simply extracts the pixels and their values from a png file and returns it
    in a list of tuples.
    :param png_path: The path to the png image we want to get the pixel values from;
    :return: Returns a list of tuples (list of pixels values)
    """

    # check if the file exists
    if not os.path.exists(png_path):
        return None  # the timf file doesn't exist

    pixels_list = []

    png_img = Image.open(png_path).convert("RGBA")

    for y in range(png_img.height): # MAY BE IMPROVED by converting in hex directly in this loop
        for x in range(png_img.width): # instead of cycling again after

            pixels_list.append(png_img.getpixel((x, y)))

    return pixels_list


def create_timf_header(png_path: str) -> str:

    png_img = Image.open(png_path).convert("RGBA")

    width_hex, height_hex = hex(png_img.width)[2:], hex(png_img.height)[2:] # [2:] to get rid of the 0x

    # then 0-padding these values to ensure they are 8 chars-long
    width_hex, height_hex = width_hex.zfill(8), height_hex.zfill(8)

    magic_number_hex = ""  # the magic number converted in hexadecimal

    # get the magic number (word actually) in bytes
    magic_number_bytes = list(magic_number.encode())

    for byte in magic_number_bytes:
        magic_number_hex += hex(byte)[2:] # adding [2:] to get rid of the 0x in front of the hex value








# these 2 functions are the compression and the uncompression ones
def compress_timf_data(timf_data: str, debug_prints: bool = False) -> tuple[bool, str]:
    """
    This function compresses raw .timf data and returns it. Also returns a boolean indicating if
    the compression was successful. If not, it returns False and the raw data is returned.
    If the compression fails, it returns the raw data instead of the compressed.

    Here, the compression is straightforward, if there are 3 or more repeated values in a rox, it just
    replaces them with the number of repetitions and the repeated value. For example, if
    the value 1f2e3d4c is repeated 27 times, this will be replaced with x000001b1f2e3d4c (1b in hex is 27 in decimal).
    The compression is better explained in the README.md file in the GitHub repository.
    :param timf_data: This is the .timf that will be compressed
    :param debug_prints: Enables debug prints in the console
    :return: Returns the success of the compression and the compressed data (or raw if fail)
    """

    # initiate the hex value to be able to compare the first pixel to it
    sequence_first_value = ""
    sequence_lenght = 0

    compressed_data = ""

    # analyze the row to find sequences of repeated pixels
    # a marker to indicate the start of a compressed sequence is of the form: xnnnnnnn where n is the number of reps (if n isn't that long, then it's 0-padded)

    if debug_prints: print("Starting compression...")

    # cycle through the data 8 chars by 8 chars (32 bits by 32 bits)
    for i in range(len(timf_data) // 8):

        # get the value of each unit (here a pixel color)
        hex_value = timf_data[i * 8:(i+1) * 8]

        # if the current hex value is the same as the last value (and so same as the first value in the current sequence)
        if sequence_first_value == hex_value:
            sequence_lenght += 1 # increase the sequence length by 1

        # if the hex value is different from the last value, end the sequence and compress it if long enough
        else:
            # if it is, replace the sequence with the compressed format
            if sequence_lenght >= 3:
                # the ":07d" is to 0-padding the number of repetitions
                compressed_data += f"x{sequence_lenght:07d}{sequence_first_value}"  # add the compressed sequence to the compressed row

            # if it isn't, just add the sequence to the compressed row without compressing it
            else:
                compressed_data += str(sequence_first_value) * sequence_lenght

            # the sequence has ended, so reset the sequence first value and length
            sequence_first_value = hex_value
            sequence_lenght = 1

            # show progress
            if debug_prints: print(
                f"It's {i / (len(timf_data) // 8) * 100:.2f}% of the image that have been compressed.")


    if debug_prints: print("Compression finished.")

    # return compressed data if everything went right
    return True, compressed_data


def uncompress_timf_data(timf_data: str, debug_prints: bool = False) -> tuple[bool, str]:
    """
    This function uncompresses compressed .timf data and returns it. Also returns a boolean indicating if
    the decompression was successful. If not, it returns False and the compressed data is returned.
    If the decompression fails, it returns the compressed data instead of the uncompressed.

    :param timf_data: This is the compressed .timf that will be uncompressed
    :param debug_prints: Enables debug prints in the console
    :return: Returns the success of the decompression and the decompressed data (or compressed if fail)
    """

    uncompressed_data = ""
    sequence_lenght = 0

    if debug_prints: print("Starting decompression...")

    # cycle through the row 8 chars by 8 chars
    for i in range(len(timf_data) // 8):

        # get the value of each item (pixel color) in the row
        hex_value = timf_data[i * 8:(i + 1) * 8]

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
            f"It's {i / (len(timf_data) // 8) * 100:.2f}% of the image that have been uncompressed.")

    if debug_prints: print("Decompression finished.")

    # return uncompressed data if everything went right
    return True, uncompressed_data


def convert_png_to_timf(png_path: str, debug_prints: bool=False) -> bool:
    """
    This function converts a png file to the timf format. It directly writes out the file in a folder,
    which can be specified otherwise it's in the same folder as the png file.
    :param png_path: The png file that will be converted into a timf file.
    :param debug_prints: Enables debug prints in the console
    :return: Returns a boolean indicating the success or not of this convertion.
    """

    # get pixels values from the png
    image_pixels = get_pixels_from_png(png_path)

    # convert these pixels into .timf raw data
    raw_timf_data = ""
    for pixel in image_pixels:

        hex_pixel = rgba_to_hex(pixel)
        hex_pixel = format_hex_for_timf(hex_pixel)

        raw_timf_data += hex_pixel

    # compress the .timf raw data
    compressed_timf_data = compress_timf_data(raw_timf_data)

    # create the .timf file header



    # merge the header with the .timf data (compressed)


    # finish up the file and write it on disk

a = int("1100001", base=2)
print(a)
print(bin(97))

b = "bestformat".encode("utf-8")
print(b)
print(list(b))




