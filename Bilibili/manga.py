# -*- coding:utf-8 -*-
'''
 this is a simple python script to download bilibili manga
'''
import requests
import json
from typing import List,Dict
import os

saveDirPath = '.'

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://manga.bilibili.com",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
    'cookie':""
}

def GetAllEspicodes(comic_id:int) -> List:
    url = "https://manga.bilibili.com/twirp/comic.v1.Comic/ComicDetail?device=pc&platform=web"
    payload = {'comic_id':comic_id}
    r = requests.post(url,data=json.dumps(payload),headers = headers)
    retList = []
    if(r.status_code == requests.codes.ok):
        jsonR = json.loads(r.text)
        # print('type of jsonR：%s' % type(jsonR))
        if('data' in jsonR.keys() and 'ep_list' in jsonR['data'].keys()):
            # print("type of jsonR['data']['ep_list']：%s" % type(jsonR['data']['ep_list']))
            # print("type obj in jsonR['data']['ep_list']：%s" % type(jsonR['data']['ep_list'][0]))
            ep_list = sorted(jsonR['data']['ep_list'],key=lambda ep:ep['ord'])
            for ep in ep_list:
                item = {'ep_id':ep['id'],'title':ep['title'],'short_title':ep['short_title']}
                retList.append(item)
            # print(retList)
    else:
        print('fail')
    return retList
    pass
    
def DownloadAllEspicodes(espicodes:List) -> None:
    for ep in espicodes:
        DownloadDesignatedEspicode(ep)
    pass
    
def DownloadDesignatedEspicode(espicode:Dict) -> None:
    # print('ep_id:%s,title:%s,sub_title:%s' %(espicode['ep_id'],espicode['title'],espicode['short_title']))
    # access url to get images' paths
    url = "https://manga.bilibili.com/twirp/comic.v1.Comic/GetImageIndex?device=pc&platform=web"
    payload = {
        'ep_id':espicode['ep_id']
    }
    # create sub directory named like 'order name'
    print(espicode)
    dirName = espicode['short_title'] + ' ' + espicode['title']
    fullpath = os.path.join(saveDirPath,dirName)
    if not os.path.exists(fullpath):
      os.mkdir(fullpath)
    else:
      # this could be removed
      return
    r = requests.post(url,data=json.dumps(payload),headers = headers)
    if(r.ok):
        images = r.json()['data']['images']
        imageUrl = "https://manga.bilibili.com/twirp/comic.v1.Comic/ImageToken?device=pc&platform=web"
        imageIndex = 1
        for image in images:
            imagePath = []
            imagePath.append(image['path'])
            imagePayload = {
                "urls":json.dumps(imagePath)
            }
            # print("imagePayload %s:" % imagePayload)
            imageR = requests.post(imageUrl,data = json.dumps(imagePayload),headers = headers)
            if(imageR.ok):
                # print('Path: %s is OK' %image['path'])
                imageInfos = imageR.json()['data']
                # Get this image
                for imageInfo in imageInfos:
                    DownloadImageByInfo(imageInfo['url'],imageInfo['token'],fullpath,imageIndex,espicode)
                    pass
            else:
                print('Path:%s is failed' % image['path'])
            imageIndex = imageIndex + 1
    else:
        print('fail')
    pass
    
def DownloadImageByInfo(imageUrl:str,token:str,imagePath:str,index:int,espicode:Dict) -> None:
    '''
    save this image directly
    '''
    actualUrl = imageUrl + '?token=' + token
    r = requests.get(actualUrl)
    fileName = '{0:0>2d}'.format(index) + '.jpeg'
    filePath = os.path.join(imagePath,fileName)
    with open(filePath,'wb') as f:
        f.write(r.content)
    pass


if __name__ == '__main__':
    espicodes = GetAllEspicodes(26551)
    DownloadAllEspicodes(espicodes)
    # DownloadDesignatedEspicode({'ep_id':316882,'title':'清凝','short_title':'001'})
    pass