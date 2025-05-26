# -*- coding: GBK -*-
import subprocess
import glob
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import sys
import io
sys.stdout  = io.TextIOWrapper(sys.stdout.buffer,  encoding='gbk', errors='replace')

def run_nuxmv(file_path):
    """
    运行 nuXmv 检查指定的 SMV 文件。

    参数:
        file_path (str): 要检查的 SMV 文件路径。
    """
    print(f"正在运行 nuXmv 检查 {file_path}...")
    subprocess.run(['nuXmv', file_path])


class SMVHandler(PatternMatchingEventHandler):
    """
    文件事件处理器，专门处理 .smv 文件的事件。
    """
    patterns = ["*.smv"]

    def on_modified(self, event):
        """
        当 .smv 文件被修改时调用，运行 nuXmv 检查。

        参数:
            event: 文件修改事件对象。
        """
        run_nuxmv(event.src_path)

    def on_created(self, event):
        """
        当 .smv 文件被创建时调用，运行 nuXmv 检查。

        参数:
            event: 文件创建事件对象。
        """
        run_nuxmv(event.src_path)


if __name__ == "__main__":
    # 初始检查：对当前目录下所有 .smv 文件运行 nuXmv
    smv_files = glob.glob('*.smv')
    for file in smv_files:
        run_nuxmv(file)

    # 设置文件监测器，监测当前目录下的 .smv 文件变化
    path = '.'  # 当前目录
    event_handler = SMVHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    print("正在监测 .smv 文件的变化，按 Ctrl+C 停止。")

    # 持续运行，直到用户手动停止
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()