import time
import sys
import os
import datetime
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


def get_work_dir(folder):
    """
    Gets working directory is correct format depending on used operating system.
    :param folder: Folder name to get full path to (e.g Desktop, Downloads)
    :return: str: Full path to specified folder
    """
    work_dir = None
    if os.name == 'posix':
        work_dir = os.path.join(os.path.join(os.path.expanduser('~')), folder)
    elif os.name == 'nt':
        work_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), folder)
    else:
        print('App will not run on this OS. Sorry. Exiting')
    return work_dir


def get_file_attr(f_src):
    """
    Gets files attributes (name, extension (type), source path) from full path.
    :param f_src: Full path to file
    :return: list, str. File name and extension; Full path to file
    """
    return f_src.split("\\")[-1].split(".")[-2:], f_src


def move_to_folder(f_name_ext, f_src, folder):
    """
    Main task: moves new file from observed path to specified folder in Documents
    Following sequence:
    1. Checks if specified folder is created in Documents. If not create it.
    2. Checks if file with the same name exists in specified folder. If exists add
    full today's date to new file (e.g file_2019_08_22_12_42_11).
    3. Move file to specified folder.
    :param f_name_ext: list containing file name and file type
    :param f_src: str full path to file
    :param folder: str folder name to move file to
    :return: nothing
    """

    f_current_src = f_src
    f_path = f'{get_work_dir("Documents")}/{folder}'
    if not os.path.exists(f_path):
        os.mkdir(f_path)
    if os.path.exists(f'{f_path}/{".".join(f_name_ext)}'):
        f_new_src = f'{f_path}/{f_name_ext[0]}_{datetime.datetime.now().strftime("%Y_%m_%d_%H_%m_%S")}.{f_name_ext[1]}'
    else:
        f_new_src = f'{f_path}/{".".join(f_name_ext)}'
    print(f'Moving file {".".join(f_name_ext)} to {folder}')
    os.rename(f_current_src, f_new_src)


class DesktopHandler(PatternMatchingEventHandler):
    """
    DesktopHandler inherits from on of the existing handlers - PatterMatchingEventHandler.
    """

    def process(self, event):
        """
        Process incoming events occurring in observing directory. If event is directory created
        processing is skipped. If even is a file created then file is moved to specified folder by type.
        Available types:
        images (jpg, png, gif, ..), documents (doc, docx, pdf, odt), video (mp4, avi, ..)
        sound (mp3, flac, ..), other if not falls into any categories
        :param event: object with 3 attributes (type, is_directory, src_path)
        :return: nothing
        """
        if event.is_directory:
            print('Directory is created. Skipping processing!')
            return
        f_name_ext, f_src = get_file_attr(event.src_path)
        dic_of_type = {'IMAGES': ['jpg', 'png', 'gif'],
                       'DOCUMENTS': ['doc', 'docx', 'pdf', 'odt', 'txt'],
                       'VIDEO': ['mp4', 'mov', 'avi'],
                       'SOUND': ['mp3', 'flac']}

        for folder, list_of_formats in dic_of_type.items():
            if f_name_ext[1] in list_of_formats:
                print(f'Moving file {".".join(f_name_ext)} to {folder}')
                time.sleep(1)
                return move_to_folder(f_name_ext, f_src, folder)
        return move_to_folder(f_name_ext, f_src, 'OTHER')

    def on_created(self, event):
        """
        Method is executed when a file or directory is created. Then method
        calls process method which process occurring event.
        :param event: object indicating event
        :return: nothing
        """
        self.process(event)


if __name__ == '__main__':
    print('----------------------------------------------------------------------')
    print('You can specify directory to which to clean by providing an argument')
    print('e.g python main.py /home/my_secret_folder')
    print('Otherwise it will use Desktop directory for Windows and Linux')
    print('----------------------------------------------------------------------')
    args = sys.argv[1:]
    watch_dir = None
    if args:
        watch_dir = args[0]
    else:
        watch_dir = get_work_dir('Desktop')
    print(f'Observing directory: {watch_dir}')
    """
    Observer class will watch for any change (in our case on_created), and then dispatch 
    the event to specified handled. In our case - DesktopHandler()
    """
    observer = Observer()
    observer.schedule(DesktopHandler(), path=watch_dir if watch_dir else sys.exit(1))
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
