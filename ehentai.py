#!/usr/bin/env python
# coding: utf-8

import requests
import lxml.etree
import sys
import codecs
import re
import time
import os
import zipfile
import getopt
import shutil

# ファイルをダウンロードし、zipファイルを作成する作業ディレクトリ
TMPPATH='/tmp'

HTTP_CLIENT_CHUNK_SIZE=10240

req = requests.session()
req.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
}


def downloadImageFile(dir, imgurl):
    filename = dir + '/' + imgurl.split('/')[-1]
    print "Download Image File=", filename

    for retry in range(1, 10):
        try:
            r = req.get(imgurl, stream=True, timeout=(10.0, 10.0))

            # print 'status_code:' + str(r.status_code)
            length = int(r.headers['Content-Length'])

            if (os.path.exists(filename)) and (os.stat(filename).st_size == length):
                print 'Used exists file:'
            else:
                # ファイルが存在しない、または、ファイルサイズとダウンロードサイズが異なる。
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=4096):
                        if chunk: # filter out keep-alive new chunks
                            f.write(chunk)
                            f.flush()
                    f.close()

            info = os.stat(filename)
            # print 'file size:' + str(info.st_size)
            if info.st_size == length:
                return filename
            else:
                print 'Download size mismatch file size:' + str(info.st_size) + ' Content-Length:' + length
                continue

        except requests.exceptions.ConnectionError:
            print 'ConnectionError:' + imgurl
            continue
        except requests.exceptions.Timeout:
            print 'Timeout:' + imgurl
            continue
        except requests.exceptions.ReadTimeout:
            print 'Timeout:' + imgurl
            continue

    # リトライ回数をオーバーで終了
    sys.exit()
#
#

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

#
#

def zip_dir(dirname,zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else :
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))
    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        zf.write(tar,arcname)
    zf.close()

#
#

def download_pics(url):
    if ('http://' in url) or ('https://' in url):
        basedir = TMPPATH + '/' + url.split("/")[-2] + '_' + url.split("/")[-1]
        index = lxml.etree.HTML(req.get(url).text)
    else:
        basedir = TMPPATH + '/' + '123456'
        index = lxml.etree.HTML(codecs.open(url, 'r', 'UTF-8').read())

    title = index.xpath('//h1[@id="gj"]/text()')
    if not title:
        # 日本語のタイトルが無い場合
        title = index.xpath('//h1[@id="gn"]/text()')
        if not title:
            title = [time.time()]
    title = title[0]
    print(title)
    basename = cleanPath(title)
    print(basedir + '/' + basename)
    mkdir(basedir + '/' + basename)

    all_subURL = index.xpath('//div[@class="gdtm"]/div/a')
    nexturl = all_subURL[0].attrib['href']
    picurl = None
    print('nexturl:' + nexturl)
    download = False

    while True:
        picurl = nexturl

        if ('http://' in picurl) or ('https://' in picurl):
            retry = 0;
            while True:
                try:
                    text = req.get(picurl).text
                except requests.exceptions.ConnectionError:
                    print 'ConnectionError:' + picurl
                    if retry != 10:
                        retry = retry + 1
                        continue
                    else:
                        sys.exit()
                break;
        else:
            text = codecs.open(picurl, 'r', 'UTF-8').read()

        page = lxml.etree.HTML(text)
        img = page.xpath('//*[@id="img"]')
        next = page.xpath('//div[@id="i3"]/a')
        nl = page.xpath('//a[@id="loadfail"]')

        imgurl = img[0].attrib['src']
        nexturl = next[0].attrib['href']
        nlid = nl[0].attrib['onclick'].split("'")[1]

#        print('imgurl=' + imgurl)
#        print('picurl=' + picurl)
#        print('nexturl=' + nexturl)

        if '/g/509.gif' in imgurl:
            # ダウンロードの上限まで達した 3600秒待って
            print '509 BRNDWIDTH EXCEEDED:' + url
            time.sleep(3600)
            nexturl = picurl
            continue

        if 'keystamp=' in imgurl:
            if not 'nl=' in picurl:
                nexturl = picurl + '?nl=' + nlid
        else:
            # 有効なイメージURL 5秒待ってダウンロード
            time.sleep(3)
            downloadImageFile(basedir + '/' + basename, imgurl)
            if picurl.split('?')[0] == nexturl:
                download = True
                break

    zip_dir(basedir + '/' + basename, basename+'.zip')

    shutil.rmtree(basedir)
    return True

#
#

def cleanPath(path):
    path = path.strip()  # 文字列の前後の空白を削除
    path = path.replace('|', '')
    path = path.replace(':', '')
    path = path.replace('/', '')
    return path

#
#

if __name__ == '__main__':
    for url in sys.argv[1:]:
        if url[-1] == '/':
            download_pics(url[:-1])
        else:
            download_pics(url)
