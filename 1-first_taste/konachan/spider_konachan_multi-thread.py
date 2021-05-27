import requests
import os
import time
import threading
import traceback
from bs4 import BeautifulSoup
from queue import Queue

count = 6000
if os.path.exists('konachan') is False:
    os.makedirs('konachan')


def download(url, filename):
    if os.path.exists(filename):
        print('file exists!')
        return
    try:
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return filename
    except KeyboardInterrupt:
        if os.path.exists(filename):
            os.remove(filename)
        raise KeyboardInterrupt
    except Exception:
        traceback.print_exc()
        if os.path.exists(filename):
            os.remove(filename)


class Spider(threading.Thread):
    def __init__(self, name, queue):
        super().__init__()
        self.name = name
        self.queue = queue
    def run(self):
        print('Begin {}'.format(self.name))
        while not self.queue.empty():
            try:
                url = self.queue.get()
                html = requests.get(url).text
                soup = BeautifulSoup(html, 'html.parser')
                for img in soup.find_all('img', class_="preview"):
                    target_url = img['src']
                    filename = os.path.join('konachan', target_url.split('/')[-1])
                    download(target_url, filename)
                global count
                print('count: %d' % count)
                count += 1
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except Exception:
                traceback.print_exc()
        print("Finished {}".format(self.name))

if __name__ == "__main__":
    start = time.time()
    queue = Queue()
    for i in range(6000, 12000):
        target = 'https://konachan.net/post?page=%d&tags=' % i
        queue.put(target)
    
    thread1 = Spider("1", queue)
    thread2 = Spider("2", queue)
    thread3 = Spider("3", queue)
    thread4 = Spider("4", queue)
    
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()

    end = time.time()
    print("Job ended with {} seconds".format(end - start))