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
    ���� nuXmv ���ָ���� SMV �ļ���

    ����:
        file_path (str): Ҫ���� SMV �ļ�·����
    """
    print(f"�������� nuXmv ��� {file_path}...")
    subprocess.run(['nuXmv', file_path])


class SMVHandler(PatternMatchingEventHandler):
    """
    �ļ��¼���������ר�Ŵ��� .smv �ļ����¼���
    """
    patterns = ["*.smv"]

    def on_modified(self, event):
        """
        �� .smv �ļ����޸�ʱ���ã����� nuXmv ��顣

        ����:
            event: �ļ��޸��¼�����
        """
        run_nuxmv(event.src_path)

    def on_created(self, event):
        """
        �� .smv �ļ�������ʱ���ã����� nuXmv ��顣

        ����:
            event: �ļ������¼�����
        """
        run_nuxmv(event.src_path)


if __name__ == "__main__":
    # ��ʼ��飺�Ե�ǰĿ¼������ .smv �ļ����� nuXmv
    smv_files = glob.glob('*.smv')
    for file in smv_files:
        run_nuxmv(file)

    # �����ļ����������⵱ǰĿ¼�µ� .smv �ļ��仯
    path = '.'  # ��ǰĿ¼
    event_handler = SMVHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    print("���ڼ�� .smv �ļ��ı仯���� Ctrl+C ֹͣ��")

    # �������У�ֱ���û��ֶ�ֹͣ
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()