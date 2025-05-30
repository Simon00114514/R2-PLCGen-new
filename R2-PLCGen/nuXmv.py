# -*- coding: utf-8 -*-
import subprocess
import glob
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import sys
import io
sys.stdout  = io.TextIOWrapper(sys.stdout.buffer,  encoding='utf-8', errors='replace')

def run_nuxmv(file_path):
    """
    running nuXmv checking

    参数:
        file_path (str): 要检查的 SMV 文件路径。
    """
    print(f"running nuXmv checking {file_path}...")
    subprocess.run(['nuXmv', file_path])


class SMVHandler(PatternMatchingEventHandler):
    """
    event handler for smv files
    """
    patterns = ["*.smv"]

    def on_modified(self, event):
        """
        when smv file is modified, run nuXmv check

       reference:
            event:
        """
        run_nuxmv(event.src_path)

    def on_created(self, event):
        """
        when smv file is created, run nuXmv check

        """
        run_nuxmv(event.src_path)


if __name__ == "__main__":
    #  initial checking
    smv_files = glob.glob('*.smv')
    for file in smv_files:
        run_nuxmv(file)

    # 设置文件监测器，监测当前目录下的 .smv 文件变化
    path = '.'  # 当前目录
    event_handler = SMVHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    print("Detecting .smv file changes, press Ctrl+C to stop.")

    # 持续运行，直到用户手动停止
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()