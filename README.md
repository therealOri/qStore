# qStore
A proof of concept for using youtube as file storage.
> Please feel free to star this project if you like what I have done! <3
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

# Extra context
When calling the "`encode_video()`" function, it prompts you to provide "`data for keygen`". This is basically any 100+ random characters you can put together. I personally just press all of the buttons of my keyboard in a satisfying way to get a lot of randomly pressed letters, symbols, and numbers. You could also use [Genter](https://github.com/therealOri/Genter) to generate 100+ characters if you want something with a lot more variety than your keyboard.
__ __

<br>
<br>

# Updates
5/31/23

Updated:

- Made the way you control how long a video is and how many frames get used to put a QR code in more convenient.
__ __


5/30/23

Updated:

- Youtube compression fix. You should now be able to download the video from youtube and have it extract properly now. 🤞
- We are using yt_dlp for downloading videos now.
__ __

5/29/23

Updated:

- Encryption method now uses [Chaeslib](https://github.com/therealOri/Chaeslib) instead of only gcm/GCMlib.

- When encoding a file into a video, it will now split the resulting encrypted data into segements. And for each segment that it gets split into, a QR code will be made. The segmented data will then be put into a qr code, and the qr code will be pasted into a frame of the video.

- Updated some if checks for more key verification.

- Fixed some typos and updated some wording.
__ __


<br>
<br>

# How-to
- Archive the files you want to store. (.zip or .tar.gz)
- Upload to qStore and encode a video.
- Upload video to youtube account specifically for these kinds of videos.
- Add record to database to keep track. (if you want)
- Download the video via url/link and then provide to qStore.
- It will extract the data and give you the .zip or .tar.gz file with a "random" name.

> If you are using Ubuntu (linux), you may need to install an additional package `sudo apt-get install zbar-tools` in order for the qr codes to be read. This has happened only 1 time so far so just in case, I'm going to put this little note here.
__ __

<br>
<br>

# Result
> Github isn't a fan of me embedding the video...

https://www.youtube.com/watch?v=hMS30w23zkQ
__ __

<br>
<br>

# Installation
```
git clone https://github.com/therealOri/qStore.git
cd qStore
virtualenv qstrENV
source qstrENV
pip install -r requirements.txt
```
> If you don't have `virtualenv` you can install it via "pip", `pip install virtualenv`.
__ __

<br>
<br>
<br>

# Support  |  Buy me a coffee <3
(God knows I need one xD)

Donate to me here:
> - Don't have Cashapp? [Sign Up](https://cash.app/app/TKWGCRT)

![image](https://user-images.githubusercontent.com/45724082/158000721-33c00c3e-68bb-4ee3-a2ae-aefa549cfb33.png)
