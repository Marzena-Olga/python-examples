from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argparse
import shutil
from os import walk
import os

parser = argparse.ArgumentParser(
        description="Script required params eq: --src_path=/tmp/ --des_path=/temp/ --track_erase=True"
    )
parser.add_argument("--src_path", required=True, type=str)
parser.add_argument("--des_path", required=True, type=str)
parser.add_argument("--track_erase, type=bool)
args = parser.parse_args()

class MyHandler(FileSystemEventHandler):
    def on_start(self):
        src_files = next(walk(args.src_path), (None, None, []))[2]
        des_files = next(walk(args.des_path), (None, None, []))[2]
        for i in src_files:
            if (i in des_files) == False:
                shutil.copy2(args.src_path + '/' + i, args.des_path)

    def on_deleted(self, event):
        r_file = (event.src_path.strip())
        r_file = r_file.replace(args.src_path, args.des_path)
        if args.track_erase is True:
            os.remove(r_file)
	
    def on_created(self, event):
        shutil.copy2(event.src_path.strip(), args.des_path)

event_handler = MyHandler()
event_handler.on_start()
observer = Observer()
observer.schedule(event_handler, path=args.src_path, recursive=False)
observer.start()
observer.join()
