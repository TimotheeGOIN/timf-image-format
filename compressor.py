
import os

timf_file_path = "C:/Users/timot/Desktop/MyOwnExtension/images/screen_lambda.timf"
comp_timf_file_path = "C:/Users/timot/Desktop/MyOwnExtension/images/screen_lambda_compressed.timf"


def compress_timf(timf_path: str, save: bool=False, overwrite: bool=False, debug_prints: bool=False) -> str | bool:
    """ This function compresses a .timf image.
    - Returns True if the compression was successful, False otherwise.
    """
    # check if the file exists
    if not os.path.exists(timf_path):
        print("bruhhhhhhhhh")
        return False # the timf file doesn't exist
    
    with open(timf_path, "r") as file:
        timf_file_data = file.read()

    # initiate the hex value to be able to compare the first pixel to it
    sequence_start_value = 00000000
    sequence_lenght = 0

    compressed_data = ""
    
    # analyse the row to find sequences of repeated pixels and replace them with a compressed format
    # a marker to indicate the start of a compressed sequence is of the form : xnnnnnnn where n is the number of reps (if n isn't that long then it's 0-padded)

    if debug_prints : print("Starting compression...")

    # cycle trough the row 8 chars by 8 chars
    for i in range(len(timf_file_data)//8):

        # get the value of each item (pixel color) in the row
        hex_value = timf_file_data[i*8:(i+1)*8]

        # if the hex value is the same as the last value, increase the sequence lenght by 1
        if sequence_start_value == hex_value:
            sequence_lenght += 1
        else:
            # if the hex value is different from the last value, Eend the sequence and compress it if long enough
            if sequence_lenght >= 3:
                # if it is, replace the sequence with the compressed format
                compressed_sequence = f"x{sequence_lenght:07d}{sequence_start_value}"
                compressed_data += compressed_sequence # add the compressed sequence to the compressed row

            else:
                # if it isn't, just add the sequence to the compressed row without compressing it
                compressed_data += str(sequence_start_value) * sequence_lenght

            # reset the sequence start value and lenght
            sequence_start_value = hex_value
            sequence_lenght = 1

            # show progress
            if debug_prints : print(f"It's {i/(len(timf_file_data)//8)*100:.2f}% of the image that have been compressed.")

    if debug_prints : print("Compression finished.")

    if not save:
        # then just return the timf data
        return compressed_data
    
    else:

        # create the .timf file path
        folder_path = os.path.dirname(timf_path)
        file_name = os.path.splitext(os.path.basename(timf_path))[0] # get the filename and then get it without extension
        compressed_timf_path = folder_path + "/" + file_name + "_compressed" + ".timf"

        # when conversion is done, write .timf data in a .timf file
        try:
            with open(compressed_timf_path, "x") as file:
                file.write(compressed_data)

        except FileExistsError:
            # if the file already exists, raise error if overwrite isn't allowed, othrwise overwrite the file with the same name
            if not overwrite:
                print(f"Error: The file {compressed_timf_path} already exists.")
                return False
            
            else:
                with open(compressed_timf_path, "w") as file:
                    file.write(compressed_data)

        return True
    

def uncompress_timf(timf_path: str, save: bool=False, overwrite: bool=False, debug_prints: bool=False) -> str | bool:
    """ This function uncompresses a .timf image that was compressed with the compress_timf function.
    - Returns True if the uncompression was successful, False otherwise.
    """

    # check if the file exists
    if not os.path.exists(timf_path):
        return False # the timf file doesn't exist
    
    with open(timf_path, "r") as file:
        timf_file_data = file.read()

    uncompressed_data = ""
    sequence_lenght = 0

    if debug_prints : print("Starting compression...")
    
    # cycle trough the row 8 chars by 8 chars
    for i in range(len(timf_file_data)//8):

        # get the value of each item (pixel color) in the row
        hex_value = timf_file_data[i*8:(i+1)*8]

        # if the hex value starts with x, it's a compressed sequence and we need to uncompress it
        if hex_value.startswith("x"):
            # keep the compression factor (sequence lenght) in memory to uncompress in the next loop
            sequence_lenght = int(hex_value[1:8]) # get the lenght of the sequence

        elif sequence_lenght > 0: # actually sequence lenght can't be under 3
            # if there's a compression factor in memory, we have to expand the sequence with the current hex value
            uncompressed_data += str(hex_value) * sequence_lenght
            sequence_lenght = 0 # reset the compression factor

        else:
            # if it isn't, just add the value to the uncompressed row
            uncompressed_data += hex_value

        # show progress
        if debug_prints : print(f"It's {i/(len(timf_file_data)//8)*100:.2f}% of the image that have been uncompressed.")

    if debug_prints : print("Compression finished.")

    if not save:
        return uncompressed_data
    
    else:

        # create the .timf file path
        folder_path = os.path.dirname(timf_path)
        file_name = os.path.splitext(os.path.basename(timf_path))[0] # get the filename and then get it without extension
        uncompressed_timf_path = folder_path + "/" + file_name + "_uncompressed" + ".timf"

        # when conversion is done, write .timf data in a .timf file
        try:
            with open(uncompressed_timf_path, "x") as file:
                file.write(uncompressed_data)

        except FileExistsError:
            # if the file already exists, raise error if overwrite isn't allowed, othrwise overwrite the file with the same name
            if not overwrite:
                print(f"Error: The file {uncompressed_timf_path} already exists.")
                return False
            
            else:
                with open(uncompressed_timf_path, "w") as file:
                    file.write(uncompressed_data)

        return True

#compress_timf(timf_file_path, save=True, overwrite=True, debug_prints=True)

uncompress_timf(comp_timf_file_path, save=True, overwrite=True, debug_prints=True)








        
    