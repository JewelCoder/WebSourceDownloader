# -*-coding:utf-8 -*-

'''
a simple script to download videos from bilibili by using you-get
'''

from logging import info
from requests.api import request
from you_get import common
from you_get.extractors.bilibili import Bilibili
import requests
import json
import os
from typing import List,Dict,Tuple

out_dir = 'D:\Download\迅雷下载\雾山五行\动画'
cookieFile = ""

def GetEspicodes(ep_id:int) -> Tuple:
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://manga.bilibili.com",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
    }
    access_url = 'https://api.bilibili.com/pgc/view/web/season'
    params ={
        'ep_id' : ep_id
    }
    comic_title = ''
    retList = []
    r = requests.get(access_url,params = params)
    if r.status_code == requests.codes.ok:
        jText = json.loads(r.text)
        if 'result' in jText.keys() and 'episodes' in jText['result'].keys():
            episodes = jText['result']['episodes']
            # these episodes should be already sorted
            ordIndex = 1
            for episode in episodes:
                addItem = {
                    'link':episode['link'],
                    'title':episode['long_title']
                }
                # most videos' title is a number
                if episode['title'].isdigit():
                    ord = '{0:0>2d}'.format(int(episode['title']))
                else:
                    ord = '0:0>2d'.format(ordIndex)
                addItem['ord'] = ord
                retList.append(addItem)
                ordIndex += 1
                pass
        if 'result' in jText.keys() and 'title' in jText['result']:
            comic_title = jText['result']['title']
        pass
    else:
        print('failed')
    return (comic_title,retList)

def DownloadAllEspicodes(ep_id:int)->None:
    (comic_title ,espicodes) = GetEspicodes(ep_id)
    if espicodes:
        for espicode in espicodes:
            DownloadEachEspicode(comic_title,espicode)
            pass
    pass

def DownloadEachEspicode(comic_title:str,espicode:Dict)->None:
    videoInfo = GetVideoInfo(espicode)
    if not videoInfo:
        return
    headers = {
        'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
    }
    if 'link' in espicode and espicode['link']:
        headers['Referer'] = espicode['link']
    # only download mp4 type video, so fixed it
    print("Downloading %s %s %s" % (comic_title,espicode['ord'],espicode['title']))
    ext = 'mp4'
    parts = []
    bar = common.SimpleProgressBar(videoInfo['total_size'],len(videoInfo['urls']))
    bar.update()
    for i,url in enumerate(videoInfo['urls']):
        fileName = '%s %s[%02d].%s' %(espicode['ord'],espicode['title'],i,ext)
        filePath = os.path.join(out_dir,fileName)
        bar.update_piece(i + 1)
        parts.append(filePath)
        common.url_save(url = url,filepath = filePath,bar = bar,is_part = True,faker = False,headers = headers)
        pass
    bar.done()
    
    # waiting to merge video and audio

    print()
    # common.download_urls(urls = videoInfo['urls'],title = videoInfo['title'],ext = 'mp4',\
    #     total_size = videoInfo['total_size'],out_dir = out_dir,\
    #         merge=True,headers=headers,av=True)
    pass

def GetVideoInfo(espicode:Dict)->Dict:
    if 'link' in espicode:
        site = Bilibili()
        site.url = espicode['link']
        site.prepare(info_only=True)
        title = site.title
        itags = sorted(site.dash_streams,key=lambda i: -site.dash_streams[i]['size'])
        # choose mp4 type
        itags = list(filter(lambda i:site.dash_streams[i]['container'] == 'mp4',itags))
        if itags:
            format = itags[0]
            stream = site.dash_streams[itags[0]]
        if stream is None:
            return None
        if 'quality' in stream:
            quality = stream['quality']
        if 'size' in stream:
            size = str(round(stream['size'] / 1048576,1)) + 'MB'
            total_size = stream['size']
        if 'src' in stream:
            urls = stream['src']
        return {
            'format' : format,
            'quality' : quality,
            'size' : size,
            'urls' : urls,
            'total_size' : total_size,
            'title':title
        }
    else:
        return None
    pass

if __name__ == '__main__':
    ep_id = None
    # GetEspicodes(ep_id)
    # common.load_cookies(cookiefile = cookieFile)
    DownloadAllEspicodes(ep_id)