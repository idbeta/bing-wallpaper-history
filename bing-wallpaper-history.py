#!/usr/bin/env python
# encoding=utf-8
import requests,re,os,sys,threading,time
import urllib,urllib2
from bs4 import BeautifulSoup

def cur_file_dir():
    return os.path.split(os.path.realpath(__file__))[0]
max_thread = 10
lock = threading.RLock() 
class Downloader(threading.Thread):
    def __init__(self, url, start_size, end_size, fobj, buffer):
        self.url = url
        self.buffer = buffer
        self.start_size = start_size
        self.end_size = end_size
        self.fobj = fobj
        threading.Thread.__init__(self) 
    def run(self):
        with lock:
            print 'starting: %s' % self.getName()
        self._download() 
    def _download(self):
        req = urllib2.Request(self.url)
        req.headers['Range'] = 'bytes=%s-%s' % (self.start_size, self.end_size)
        f = urllib2.urlopen(req)
        offset = self.start_size
        while 1:
            block = f.read(self.buffer)
            if not block:
                with lock:
                    print '%s done.' % self.getName()
                break
            with lock:
                # sys.stdout.write('%s saveing block...' % self.getName())
                self.fobj.seek(offset)
                self.fobj.write(block)
                offset = offset + len(block)
                sys.stdout.write('done.\n')
def down_img(url, thread=3, save_file='', buffer=1024):
    thread = thread if thread <= max_thread else max_thread
    req = urllib2.urlopen(url)
    size = int(req.info().getheaders('Content-Length')[0])
    fobj = open(save_file, 'wb')
    avg_size, pad_size = divmod(size, thread)
    plist = []
    for i in xrange(thread):
        start_size = i*avg_size
        end_size = start_size + avg_size - 1
        if i == thread - 1:
            end_size = end_size + pad_size + 1
        t = Downloader(url, start_size, end_size, fobj, buffer)
        plist.append(t)
 
    for t in plist:
        t.start()

    for t in plist:
        t.join()
 
    fobj.close()
    print 'Download completed!'

def download_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
    }
    data = requests.get(url, headers=headers).content
    return data
def reporthook(blocks_read,block_size,total_size):
    if total_size <0:
        print "source file is not exit!"  % blocks_read
    else:
        print "downloading: %d KB, totalsize: %d KB" % (blocks_read*block_size/1024.0,total_size/1024.0)
class AppURLopener(urllib.FancyURLopener):
    version = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT)";
def geturl():
    urllib._urlopener = AppURLopener();
    today=download_page("http://cn.bing.com")
    content = re.findall('g_img={url: "(.+?)",',today)    
    if not os.path.exists(cur_file_dir()+'\%s'%content[0].split('/')[len(content[0].split('/'))-1]):
        urllib.urlretrieve(content[0],cur_file_dir()+'\%s'%content[0].split('/')[len(content[0].split('/'))-1],reporthook)
    y=range(2009,int(time.strftime('%Y'))+1)
    m=range(1,13)    
    for i in y:
        for j in m:
            urlList = []
            checklist = []
            url = 'http://www.istartedsomething.com/bingimages/?m=%s&y=%s'%(j,i)
            doc = download_page(url)
            rule = re.compile('data-original="resize.php\?i=(.*)&w=100"')
            urls = re.findall(rule,doc) 
            for i in urls:
                if i.split('_')[0] not in checklist:
                    checklist.append(i.split('_')[0])
                    urlList.append(i)
            urlList=map(lambda x: 'http://www.istartedsomething.com/bingimages/cache/'+str(x), urlList)                
            for p in urlList:
                if not os.path.exists(cur_file_dir()+'\%s'%p.split('/')[len(p.split('/'))-1]):
                    # urllib.urlretrieve(fullurl,cur_file_dir()+'\%s'%i,reporthook)
                    down_img(url=p, thread=5, save_file=cur_file_dir()+'\%s'%p.split('/')[len(p.split('/'))-1], buffer=4096)
    # return sorted(list(set(urlList)))##list的中文直接打印会乱码，要用for循环拿出来打印

if __name__ == '__main__':    
    geturl()
