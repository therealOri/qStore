import cv2
import numpy as np
import secrets
import string
import os
import beaupy
from pystyle import Colors, Colorate
from tqdm import tqdm
import shutil
import magic
from Chaeslib import Chaes
import base64
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from PIL import Image
import pyqrcode
import pyzbar.pyzbar as pyzbar
import math
import tempfile
import sqlite3
import wget
import yt_dlp
import subprocess



class Store:
    def __init__(self, workers=None):
        self.chaes = Chaes()
        self.temp_dir = None
        # Number of worker processes/threads to use
        if workers is None:
            self.workers = max(1, os.cpu_count() - 1)
        else:
            self.workers = max(1, workers)

    def banner(self):
        banner = """
                      .d8888b.  888
                     d88P  Y88b 888
                     Y88b.      888
             .d88888  "Y888b.   888888 .d88b.  888d888 .d88b.
            d88" 888     "Y88b. 888   d88""88b 888P"  d8P  Y8b
            888  888       "888 888   888  888 888    88888888
            Y88b 888 Y88b  d88P Y88b. Y88..88P 888    Y8b.
             "Y88888  "Y8888P"   "Y888 "Y88P"  888     "Y8888
                 888
                 888
                 888


        Made by Ori#6338 | @therealOri_ | https://github.com/therealOri

    """
        colored_banner = Colorate.Horizontal(Colors.purple_to_blue, banner, 1)
        return colored_banner

    def clear(self):
        os.system('clear||cls')

    def get_file_type(self, bytes_data):
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(bytes_data)
        return file_type.split('/')[1]


    def generate_filename(self):
        alphabet = string.ascii_letters + string.digits
        filename = ''.join(secrets.choice(alphabet) for _ in range(12)) + ".avi"
        return filename


    def generate_video(self, duration, fps=30, width=1920, height=1080):
        """
        Generate a video with solid color frames.
        """
        output_filename = self.generate_filename()

        # Generates a "random" background color | BGR from left to right
        background_color = tuple(secrets.randbelow(256) for _ in range(3))
        fourcc = cv2.VideoWriter_fourcc(*'FFV1')
        out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

        total_frames = int(fps * duration)

        # Create a single frame template that we'll reuse
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :, :] = background_color

        # Write the same frame multiple times
        for _ in tqdm(range(total_frames), desc="Creating video frames", leave=False):
            out.write(frame)

        out.release()
        cv2.destroyAllWindows()
        self.clear()
        return output_filename


    def init_temp_dir(self):
        """Initialize a temporary directory"""
        if self.temp_dir is None:
            self.temp_dir = tempfile.mkdtemp(prefix="store_")
        return self.temp_dir


    def clean_temp(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
            print("[INFO] Temporary files have been cleaned up.\n")


    def split_string(self, s_str, count=21):
        per_c = math.ceil(len(s_str) / count)
        c_cout = 0
        out_str = ''
        split_list = []
        for s in s_str:
            out_str += s
            c_cout += 1
            if c_cout == per_c:
                split_list.append(out_str)
                out_str = ''
                c_cout = 0
        if c_cout != 0:
            split_list.append(out_str)
        return split_list


    def extract_single_frame(self, args):
        """Extract a single frame from video using args=(video_path, frame_number, output_dir)"""
        video_path, frame_number, output_dir = args
        vidcap = cv2.VideoCapture(video_path)
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        success, image = vidcap.read()
        vidcap.release()

        if success:
            output_path = os.path.join(output_dir, f"{frame_number}.png")
            cv2.imwrite(output_path, image)
            return True
        return False


    def frame_extraction(self, video):
        """
        Extract frames from video with parallel processing
        """
        temp_dir = self.init_temp_dir()
        print(f"[INFO] Temporary directory created at: {temp_dir}")

        vidcap = cv2.VideoCapture(video)
        n_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        vidcap.release()

        # Create task list for parallel execution
        tasks = [(video, frame_number, temp_dir) for frame_number in range(n_frames)]
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            list(tqdm(
                executor.map(self.extract_single_frame, tasks),
                total=len(tasks),
                desc="Extracting frames",
                leave=False
            ))
        return temp_dir


    def resize_and_center_image(self, qr_image_path, background_image_path):
        new_height = 950
        new_width = 950

        qr_image = cv2.imread(qr_image_path)
        resized_qr_image = cv2.resize(qr_image, (new_width, new_height))
        background_image = cv2.imread(background_image_path)

        x = (background_image.shape[1] - resized_qr_image.shape[1]) // 2
        y = (background_image.shape[0] - resized_qr_image.shape[0]) // 2

        result = background_image.copy()
        result[y:y+resized_qr_image.shape[0], x:x+resized_qr_image.shape[1]] = resized_qr_image
        cv2.imwrite(background_image_path, result)


    def process_qr_frame(self, args):
        """Process a single QR code frame with args=(i, data, temp_dir)"""
        i, data, temp_dir = args
        f_name = os.path.join(temp_dir, f"{i}.png")
        qr_code_file_name = os.path.join(temp_dir, f"qr_code{i}.png")

        qr_code = pyqrcode.create(data, error='H', version=40, mode='binary')
        qr_code.png(qr_code_file_name, scale=12)

        self.resize_and_center_image(qr_code_file_name, f_name)
        return i, data


    def encode_video(self, file_name, string_split=51, vid_length=10):
        chaes_ev = Chaes()  # Generate new salt for each encoding
        self.clear()

        key_data = beaupy.prompt("Data for key gen")
        if not key_data:
            self.clear()
            return
        key_data = key_data.encode()

        self.clear()
        eKey = self.chaes.keygen(key_data)
        if not eKey:
            return

        save_me = base64.b64encode(eKey)
        bSalt = base64.b64encode(chaes_ev.salt)
        master_key = f"{save_me.decode()}:{bSalt.decode()}"
        input(f'Save this key so you can decrypt and decode later: {master_key}\n\nPress "enter" to continue...')
        self.clear()

        # Read and encrypt file data
        with open(file_name, 'rb') as rb:
            data = rb.read()
            data_enc = chaes_ev.encrypt(data, eKey)

        split_string_list = self.split_string(data_enc, string_split)
        video_file = self.generate_video(duration=vid_length)
        temp_dir = self.frame_extraction(video_file)
        tasks = [(i, data_chunk, temp_dir) for i, data_chunk in enumerate(split_string_list)]

        # Process QR codes in parallel
        print(f"[INFO] Processing QR codes with {self.workers} workers")
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            results = list(tqdm(
                executor.map(self.process_qr_frame, tasks),
                total=len(tasks),
                desc="Processing QR codes",
                leave=False
            ))

        for i, _ in results:
            print(f"[INFO] frame {i}.png holds part of the encrypted data")


        output_vid = tempfile.mktemp(suffix='.avi')
        subprocess.run([
            "ffmpeg",
            "-framerate", "30",
            "-i", f"{temp_dir}/%d.png",
            "-vcodec", "ffv1",
            "-y",
            output_vid
        ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        self.clean_temp()
        shutil.copy2(output_vid, video_file)
        os.remove(output_vid)
        return True


    def decode_qr_frame(self, frame_path):
        """Decode QR code from a single frame"""
        try:
            img = Image.open(frame_path)
            result = pyzbar.decode(img)
            if result:
                return result[0].data.decode('utf-8')
            return None
        except Exception:
            return None


    def decode_qr_frame_job(self, frame_path):
        """Worker function for parallel QR decoding"""
        try:
            img = Image.open(frame_path)
            result = pyzbar.decode(img)
            if result:
                # Extract frame number from path to maintain order
                frame_number = int(os.path.basename(frame_path).split('.')[0])
                return (frame_number, result[0].data.decode('utf-8'))
            return (None, None)
        except Exception:
            return (None, None)


    def decode_video(self, video, b64_enc_key):
        # Extract frames from the video
        temp_dir = self.frame_extraction(video)

        # Get all frame files
        frame_files = sorted([
            os.path.join(temp_dir, f) for f in os.listdir(temp_dir)
            if f.endswith('.png') and f.split('.')[0].isdigit()
        ], key=lambda x: int(os.path.basename(x).split('.')[0]))

        # Decode QR codes in parallel
        print(f"[INFO] Decoding QR codes with {self.workers} workers")
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            results = list(tqdm(
                executor.map(self.decode_qr_frame_job, frame_files),
                total=len(frame_files),
                desc="Decoding QR codes",
                leave=False
            ))

        # Filter valid results and sort by frame number
        valid_results = [(idx, data) for idx, data in results if idx is not None]
        valid_results.sort(key=lambda x: x[0])

        # Extract data in proper order
        secret = [data for _, data in valid_results]

        print(f"[INFO] Successfully decoded {len(secret)} QR codes from frames")

        # Join all decoded parts
        result = ''.join(secret)

        # Clean up temporary files
        self.clean_temp()

        # Decode the data
        enc_message = self.chaes.hex_to_base64(result)
        json_input = base64.b64decode(enc_message)

        # Parse the key and salt
        key_and_salt = b64_enc_key.split(":")
        salt_1 = key_and_salt[1]
        key_0 = key_and_salt[0]

        salt = base64.b64decode(salt_1)
        key = base64.b64decode(key_0)

        # Decrypt the data
        cha_aes_crypt = self.chaes.decrypt(key, json_input, salt)
        self.clear()
        return cha_aes_crypt















if __name__ == '__main__':
############################### Main Options ###############################
    store = Store(workers=12)
    while True:
        store.clear()
        main_options = ["Embed?", "Extract?", "Download Video?", "Database?", "Exit?"]
        print(f'{store.banner()}\n\nWhat would you like to do?\n-----------------------------------------------------------\n')
        main_option = beaupy.select(main_options, cursor_style="#ffa533")

        if not main_option:
            store.clear()
            exit("Keyboard Interruption Detected!\nGoodbye <3")




        # EMBED OPTION
        if main_options[0] in main_option:
            store.clear()
            file_to_store = beaupy.prompt("File to embed/store. - (Drag & Drop)")
            if not file_to_store:
                store.clear()
                continue
            file_to_store = file_to_store.replace('\\ ', ' ').strip()

            if file_to_store.endswith((".zip", ".gz")):
                # Frame count setting
                frames_to_use = 51  # Default
                if beaupy.confirm("Would you like to increase or decrease the amount of frames to be used for the storing of encrypted data? - (default is at 51)"):
                    frames_input = beaupy.prompt("How many frames?")
                    if not frames_input:
                        store.clear()
                        continue
                    try:
                        frames_to_use = int(frames_input)
                    except Exception:
                        store.clear()
                        continue

                # Video length setting
                vid_length = 10  # Default
                if beaupy.confirm('Would you like to change the length of the video that will be made? - (default is "10" seconds)'):
                    length_input = beaupy.prompt("How long would you like the duration of the video to be?")
                    if not length_input:
                        store.clear()
                        continue
                    try:
                        vid_length = int(length_input)
                    except Exception:
                        store.clear()
                        continue

                store.clear()
                result = store.encode_video(file_to_store, frames_to_use, vid_length)
                if not result:
                    store.clear()
                    continue
                input('\n\nPress "enter" to continue...')
                store.clear()
            else:
                input('Invalid filetype, file must be a .zip or .tar.gz archive.\n\nPress "enter" to continue...')
                store.clear()




        # EXTRACT OPTION
        elif main_options[1] in main_option:
            store.clear()
            vid_that_has_file = beaupy.prompt("Video that has the embedded file in it. - (Drag & Drop)")
            if not vid_that_has_file:
                store.clear()
                continue
            vid_that_has_file = vid_that_has_file.replace('\\ ', ' ').strip()

            dKey = beaupy.prompt("Encryption Key", secure=True)
            if not dKey:
                store.clear()
                continue

            store.clear()
            file_data = store.decode_video(vid_that_has_file, dKey)
            if file_data is None:
                store.clear()
                continue

            file_type = store.get_file_type(file_data)

            if file_type == 'gzip':
                output_file_name = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10)) + ".tar.gz"
                with open(output_file_name, 'wb') as wb:
                    wb.write(file_data)
                input(f'File has been extracted as {output_file_name}.\n\nPress "enter" to continue...')
                store.clear()

            elif file_type == 'zip':
                output_file_name = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10)) + ".zip"
                with open(output_file_name, 'wb') as wb:
                    wb.write(file_data)
                input(f'File has been extracted as {output_file_name}.\n\nPress "enter" to continue...')
                store.clear()

            else:
                input('File is not a supported archive type - (.zip or .tar.gz)\n\nPress "enter" to continue...')
                store.clear()




        # DOWNLOAD VIDEO OPTION
        elif main_options[2] in main_option:
            yt_url = beaupy.prompt("Youtube video url/link.")
            if not yt_url:
                store.clear()
                continue

            store.clear()
            print("Downloading video...")
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]/best[ext=mp4]',
                'outtmpl': '%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'avi'
                }]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([yt_url])

            input('Video has been downloaded.\n\nPress "enter" to continue...')
            store.clear()




        # DATABASE OPTION
        elif main_options[3] in main_option:
            store.clear()
            input("Database functionality not implemented yet.\n\nPress \"enter\" to continue...")
            store.clear()





############################### Database Options & functions ###############################

        def add_item(link, description, enc_key):
            conn = sqlite3.connect('qS_links.db')
            c = conn.cursor()
            c.execute(f"INSERT INTO items (link, description, enc_key) VALUES ('{link}', '{description}', '{enc_key}')")
            conn.commit()
            conn.close()


        def remove_item():
            conn = sqlite3.connect('qS_links.db')
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM items")
            count = c.fetchone()[0]
            if count == 0:
                input('There are no records to remove...\n\nPress "enter" to continue.')
                conn.close()
                return None

            print(f"Available options:\n---------------------------------------------------------------------------------------\n")
            for row in c.execute("SELECT id, link, description, enc_key FROM items"):
                print(row)

            delete_ids = beaupy.prompt("\n\nEnter the ID(s) of the item(s) you want to delete (separated by commas): ")
            delete_ids = delete_ids.split(",")
            for delete_id in delete_ids:
                c.execute(f"DELETE FROM items WHERE id = '{delete_id.strip()}'")
            conn.commit()
            conn.close()
            return True



        class PageSchema:
            def __init__(self, page_size):
                self.page_size = page_size

            def get_page(self, items, page_number):
                start_index = (page_number - 1) * self.page_size
                end_index = start_index + self.page_size
                return items[start_index:end_index]

            def get_page_count(self, items):
                return int((len(items) + self.page_size - 1) / self.page_size)


        #headache...but worth it.
        def view_items(page_size=15):
            conn = sqlite3.connect('qS_links.db')
            c = conn.cursor()
            items = []
            for row in c.execute("SELECT id, link, description, enc_key FROM items"):
                items.append(row)

            c.execute("SELECT COUNT(*) FROM items")
            count = c.fetchone()[0]
            if count == 0:
                input('There are no records to view...\n\nPress "enter" to continue.')
                conn.close()
                return None

            page_schema = PageSchema(page_size=page_size)
            page_count = page_schema.get_page_count(items)
            page_number = 1

            while True:
                # Get current page
                page_items = page_schema.get_page(items, page_number)
                clear()
                print("Available items (Page {}/{}):\n".format(page_number, page_count))
                print("{:<5} {:<50} {:<50} {:<50}".format("ID", "Link", "Description", "Encryption Key"))
                print("-" * 150)
                for item in page_items:
                    print("{:<5} {:<50} {:<50} {:<50}".format(item[0], item[1], item[2], item[3]))

                # Prompt user to go to next/previous page or exit
                print("\n")
                if page_number == 1 and page_count > 1:
                    print("Press 'p' to go to the last page.")
                elif page_number == page_count and page_count > 1:
                    print("Press 'n' to go to the first page.")
                    print("Press 'p' to go to the previous page.")
                elif page_number > 1:
                    print("Press 'p' to go to the previous page.")
                if page_number < page_count:
                    print("Press 'n' to go to the next page.")
                print("Press 'q' to exit.")


                choice = input("\n>_ ")
                if choice == 'p':
                    if page_number > 1:
                        page_number -= 1
                    else:
                        page_number = page_count
                elif choice == 'n':
                    if page_number < page_count:
                        page_number += 1
                    else:
                        page_number = 1
                elif choice == 'q':
                    return None

            conn.close()



        # Locking and unlocking files.
        def lock(file_path, key):
            with open(file_path, 'rb') as fr:
                data = fr.read()

            enc_data = chaes.encrypt(data, key)

            with open(f'{file_path}', 'w') as fw:
                fw.write(enc_data)
            os.rename(file_path, file_path.replace(file_path, f'{file_path}.locked'))


        def unlock(file_path, dKey):
            with open(file_path, 'r') as fr:
                data = fr.read()

            enc_message = chaes.hex_to_base64(data)
            json_input = base64.b64decode(enc_message)
            key_and_salt = dKey.split(":")
            salt_1 = key_and_salt[1]
            key_0 = key_and_salt[0]

            salt = base64.b64decode(salt_1)
            key = base64.b64decode(key_0)

            cha_aes_crypt = chaes.decrypt(key, json_input, salt)

            with open(file_path, 'wb') as fw:
                fw.write(cha_aes_crypt)
            os.rename(file_path, file_path.replace('.locked', ''))




        if main_options[3] in main_option:
            clear()
            while True:
                db_options = ["Add record?", "Remove record?", "View records?", "Lock?", "Unlock?", "Back?"]
                print(f'{banner()}\n\nWhat would you like to do?\n-----------------------------------------------------------\n')
                db_option = beaupy.select(db_options, cursor_style="#ffa533")


                if not db_option:
                    clear()
                    break


                if db_options[0] in db_option:
                    if os.path.isfile('qS_links.db') or os.path.isfile('qS_links.db.locked'):
                        if os.path.isfile('qS_links.db.locked'):
                            clear()
                            print("Database file already encrypted...")
                            input('\n\nPress "enter" to continue...')
                            clear()
                        else:
                            clear()
                            link = beaupy.prompt("Url/Link of the video that has your file embedded in it.")
                            if not link or link.lower() == 'q':
                                clear()
                                continue

                            description = beaupy.prompt("Description of what the file is/contains so you can distinguish what is what.")
                            if not description or description.lower() == 'q':
                                clear()
                                continue

                            enc_key0 = beaupy.prompt("The key that was used to encrypt the file that is stroed in the video file.")
                            if not enc_key0 or enc_key0.lower() == 'q':
                                clear()
                                continue
                            clear()
                            add_item(link, description, enc_key0)
                            input('[INFO] Database has been updated!\n\nPress "enter" to continue...')
                            clear()
                    else:
                        clear()
                        print("qS_links.db not found, downloading from the repository...")
                        wget.download("https://github.com/therealOri/qStore/blob/main/qS_links.db?raw=true")
                        clear()
                        link = beaupy.prompt("Url/Link of the video that has your file embedded in it.")
                        if not link or link.lower() == 'q':
                            clear()
                            continue

                        description = beaupy.prompt("Description of what the file is/contains so you can distinguish what is what.")
                        if not description or description.lower() == 'q':
                            clear()
                            continue

                        enc_key0 = beaupy.prompt("The key that was used to encrypt the file that is stroed in the video file.")
                        if not enc_key0 or enc_key0.lower() == 'q':
                            clear()
                            continue
                        clear()
                        add_item(link, description, enc_key0)
                        input('[INFO] Database has been updated!\n\nPress "enter" to continue...')
                        clear()



                if db_options[1] in db_option:
                    if os.path.isfile('qS_links.db') or os.path.isfile('qS_links.db.locked'):
                        if os.path.isfile('qS_links.db.locked'):
                            clear()
                            print("Database file already encrypted...")
                            input('\n\nPress "enter" to continue...')
                            clear()
                        else:
                            clear()
                            check = remove_item()
                            if not check:
                                clear()
                                continue
                            
                            clear()
                            input('[INFO] Database has been updated!\n\nPress "enter" to continue...')
                            clear()
                    else:
                        clear()
                        print("qS_links.db not found, downloading from the repository...")
                        wget.download("https://github.com/therealOri/qStore/blob/main/qS_links.db?raw=true")
                        input('\n\nDatabse is empty, nothing to remove.\n\nPress "enter" to continue...')
                        clear()
                        continue



                if db_options[2] in db_option:
                    if os.path.isfile('qS_links.db') or os.path.isfile('qS_links.db.locked'):
                        if os.path.isfile('qS_links.db.locked'):
                            clear()
                            print("Database file already encrypted...")
                            input('\n\nPress "enter" to continue...')
                            clear()
                        else:
                            clear()
                            check = view_items()
                            if not check:
                                clear()
                                continue

                            input('Press "enter" to continue...')
                            clear()
                    else:
                        clear()
                        print("qS_links.db not found, downloading from the repository...")
                        wget.download("https://github.com/therealOri/qStore/blob/main/qS_links.db?raw=true")
                        input('\n\nDatabse is empty, nothing to view.\n\nPress "enter" to continue...')
                        clear()
                        continue


                #Lock Database
                if db_options[3] in db_option:
                    if os.path.isfile('qS_links.db') or os.path.isfile('qS_links.db.locked'):
                        if os.path.isfile('qS_links.db.locked'):
                            clear()
                            print("Database file already encrypted...")
                            input('\n\nPress "enter" to continue...')
                            clear()
                        else:
                            clear()
                            print('Please provide credentials to lock the database.\nPress "q" to go back/quit.\n\n')
                            file_path = beaupy.prompt("File path? - (Drag & drop): ")
                            if not file_path or file_path.lower() == 'q':
                                clear()
                                continue
                            file_path = file_path.replace('\\ ', ' ').strip()


                            # Each time we lock the database, a new key will get made.
                            chaes2 = Chaes()
                            clear()
                            key_data = beaupy.prompt("Data for key generation. - (100+ characters)")
                            if not key_data:
                                clear()
                                continue
                            key_data = key_data.encode()

                            clear()
                            eKey = chaes2.keygen(key_data)
                            if not eKey:
                                clear()
                                continue

                            save_me = base64.b64encode(eKey)
                            bSalt = base64.b64encode(chaes2.salt)
                            master_key = f"{save_me.decode()}:{bSalt.decode()}"
                            input(f'Save this key so you can decrypt and decode later: {master_key}\n\nPress "enter" to contine...')
                            clear()

                            lock(file_path, eKey)
                            clear()
                            input('Your file has been succesfully locked!\n\nPress "enter" to continue...')
                            clear()
                            continue
                    else:
                        clear()
                        print("qS_links.db not found, downloading from the repository...")
                        wget.download("https://github.com/therealOri/qStore/blob/main/qS_links.db?raw=true")
                        input('\n\nDatabse is empty, skipping on locking the database.\n\nPress "enter" to continue...')
                        clear()
                        continue



                #unlock Database
                if db_options[4] in db_option:
                    if os.path.isfile('qS_links.db') or os.path.isfile('qS_links.db.locked'):
                        if os.path.isfile('qS_links.db.locked'):
                            clear()
                            print('Please provide the correct credentials to unlock the database.\nPress "q" to go back/quit.\n\n')
                            file_path2 = beaupy.prompt("File path? - (Drag & drop): ")
                            if not file_path2 or file_path2.lower() == 'q':
                                clear()
                            file_path2 = file_path2.replace('\\ ', ' ').strip()
                            enc_key2 = beaupy.prompt("Encryption Key: ")

                            try:
                                enc_key_check = enc_key2
                                enc_key_check = base64.b64decode(enc_key_check)
                            except Exception:
                                clear()
                                print("Provided key isn't base64 encoded...\n\n")
                                input('Press "enter" to continue...')
                                clear()
                                continue

                            try:
                                enc_key_check = enc_key2.split(':')
                            except Exception:
                                clear()
                                print("Provided key isn't a valid chaeslib key...\n\n")
                                input('Press "enter" to continue...')
                                clear()
                                continue

                            unlock(file_path2, enc_key2)
                            clear()
                            input('Your file has been succesfully unlocked!\n\nPress "enter" to continue...')
                            clear()
                        else:
                            clear()
                            print("Database file is not encrypted/locked...")
                            input('\n\nPress "enter" to continue...')
                            clear()
                    else:
                        clear()
                        print("qS_links.db not found, downloading from the repository...")
                        wget.download("https://github.com/therealOri/qStore/blob/main/qS_links.db?raw=true")
                        input('\n\nDatabse is empty and not locked, skipping on unlocking the database.\n\nPress "enter" to continue...')
                        clear()



                if db_options[5] in db_option:
                    clear()
                    break
############################### Database Options & functions ###############################






        # EXIT OPTION
        elif main_options[4] in main_option:
            store.clear()
            store.clean_temp()
            exit("Goodbye <3")
############################### Main Options ###############################

