
import os
from PIL import Image
from utils import *

"""
- The end-line character in .timf files is "00000000", so this value is not allowed in the image data.
"""

image_file_path = "C:/Users/timot/Desktop/MyOwnExtension/images/screen_lambda.png"


# in first those 2 functions are the compression and the uncompression ones
def compress_timf_data(timf_data: str, debug_prints: bool = False) -> tuple[bool, str]:
    """
    This function compresses raw .timf data and returns it. Also returns a boolean indicating if
    the compression was successful. If not, it returns False and the raw data is returned.
    Here, the compression is simple, if there are 3 or more repeated values in a rox, it just
    replaces them with the number of repetitions and the repeated value. For example, if
    the value 1f2e3d4c is repeated 27 times, this will be replaced with x000001b1f2e3d4c (1b in hex is 27 in decimal).
    The compression is better explained in the README.md file on the GitHub repository.
    :param timf_data: this is the .timf that will be compressed
    :param debug_prints: enables debug prints in the console
    :return: returns the success of the compression and the compressed data
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

    return compressed_data
