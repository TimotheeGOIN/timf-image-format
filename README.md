Here is my own image file format : the TIMF. This is not meant to be the next standart but just to try this out and learn more about file formats and how they work. 
I'll learn this by myself and by searching on the net.

- Note that if I need to specify something, I will write it out here and I will try to actualize this file.

- This is an amateur repo, so the code may not be the clearest, not the most efficient and not the most protective neither. It may also contain some weird debug things for myself.
- I try my best to do all of this myself and then I make reasearches on the net, understand what I read and not just copy-paste it.
- About AIs, I try not using them directly because I want to think by myself. But I can use them to, for instance, helping me to understand a concept.
- I'm also kinda new to the github sphere and know about all of its uses and techniques.

Now the project itself :

This is a compressed file format for images named TIMF (the extension is .timf). The compression is meant to be lossless. The data is stored in hexadecimal.
In the repo, there is an 'executable' folder in which there are the final apps that can be used (just the vizualiser.exe right now). The exe files are made with 
the PyInstaller library.

For now I have just done a converter (png to timf and timf to png) and a compressor that is able to compress and uncompress timf data. But eventually the uncompressed timf files will not exist anymore
because timf will be natively compressed (lossless compression)

Those are the next things I want to improve or implement :

- a signature for the timf file format (at the begining of the file)
- eventually just have one file and not separated
- improve the timf vizualizer (resizable window mainly)  

I'm working one the file signature (this texte isn't finished yet)
The signature will include a magic string, the width and length of the image (and maybe if the image contains transparents parts).
