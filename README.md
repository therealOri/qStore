# qStore
A proof of concept for using youtube as file storage.
__ __

<br>
<br>

# About
So, I got inspired by DvorakDwarf's [Infinite-Storage-Glitch](https://github.com/DvorakDwarf/Infinite-Storage-Glitch) and wanted to try it out myself but in python and the file data would be encrypted using GCMlib. (AES-GCM).

The issue and difference with my project here is that the encrypted data is being stored in a QR code instead of actually in the images/video itself. I have tried LSB, RGB, DCT, and Spacial Domain steganography and ALL have failed when I upload to youtube and then download the video. The compression is just to strong and kills any hope I have. I am also unsure how to use the "Binary" option "ISG" uses in python as I can't really find any documentation or libraries that'd help. I would like help to move away from the QR codes, so anything provided in terms of steganography is very appreciated.

On a good note, I did manage to get all of the other methods mentioned to work with hiding the encrypted data of a .zip/.tar.gz archive in a video file and then reveal/retrieve the data, etc. But I just couldn't get it to work/get past youtube's compression.
__ __

<br>
<br>

# How-to
- Archive the files you want to store.
- Upload to qStore.
- Add record to database to keep track.
- Upload video to youtube account specifically for these kinds of videos.
- Download the video via url/link and then provide to qStore.
- It will extract the data and give you the .zip or .tar.gz file with a "random" name.
__ __

<br>
<br>

# Demo
> To be added...

Menu provided by: [Beaupy](https://github.com/petereon/beaupy)
__ __


<br>
<br>
<br>

# Support  |  Buy me a coffee <3
(God knows I need one xD)

Donate to me here:
> - Don't have Cashapp? [Sign Up](https://cash.app/app/TKWGCRT)

![image](https://user-images.githubusercontent.com/45724082/158000721-33c00c3e-68bb-4ee3-a2ae-aefa549cfb33.png)
