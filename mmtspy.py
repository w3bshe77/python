#-*- coding=utf-8 -*-
# @Time    : 17-9-4 上午10:07
# @Author  : w3bshe77
# @Site    :
# @File    : 8947987123.py
# @Software: PyCharm Community Edition
import requests
import re
import threading
from bs4 import BeautifulSoup
from json import loads
import random

headers = {'User-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60'}
thread_lock = threading.BoundedSemaphore(value=10)
url = 'https://mm.taobao.com/tstar/search/tstar_model.do?_input_charset=utf-8'

def get_url_list():
    r = requests.post(url,headers =  headers)
    text = r.json()
    #json = loads(r)
    url_dict = text['data']['searchDOList']
    return url_dict
def get_album_id(userid):
    r = requests.post('https://mm.taobao.com/self/album/open_album_list.htm?_charset=utf-8&user_id%20={}'.format(userid),headers=headers)
    #print(r.text)
    # https://mm.taobao.com/self/album/open_album_list.htm?_charset=utf-8&user_id%20=176817195
    reg = r'.*?album_id=.*?(\d+)&'
    albumid = re.findall(reg, r.text)[::9]
    return albumid
    #print(albumid)
def get_pic_num(userid):
    r = requests.post('https://mm.taobao.com/self/album/open_album_list.htm?_charset=utf-8&user_id%20={}'.format(userid),headers=headers)
    reg = r'span class="mm-pic-number">\((.*?\d+)张'
    pic_num = re.findall(reg, r.text)
    #print(num)
    return pic_num
def get_pic_url(userid,albumid,pic_num,page):# 每页只有16条数据
    for i in range(page):
        paGe = i
        if pic_num <= 16:
            for i in range(pic_num):
                r = requests.get(
                    'https://mm.taobao.com/album/json/get_album_photo_list.htm?user_id={}&album_id={}&page={}'.format(
                        userid, albumid, paGe), headers=headers)
                json = r.json()
                url = json['picList'][i]['picUrl']
                print(url)
        elif pic_num > 16:
            n = 0
            x =  pic_num % 16
            if paGe < page:
                for i in range(16):
                    r = requests.get('https://mm.taobao.com/album/json/get_album_photo_list.htm?user_id={}&album_id={}&page={}'.format(userid,albumid,paGe),headers=headers)
                    json = r.json()
                    print(userid,albumid,pic_num)
                    url = json['picList'][i]['picUrl']
                    print(url)
            elif paGe == page:
                for i in range(x) :
                    r = requests.get(
                        'https://mm.taobao.com/album/json/get_album_photo_list.htm?user_id={}&album_id={}&page={}'.format(
                            userid, albumid, paGe), headers=headers)
                    json = r.json()
                    print(userid, albumid, pic_num)
                    url = json['picList'][x]['picUrl']
                    print(url)

def main():
    user_id = get_url_list()
    userid = []
    albumid = []
    pic_num = []
    f = []
    g = {}
    for i in range(len(user_id)):
        userid_foreach = get_url_list()[i]['userId']
        userid.append(userid_foreach)
        get_album_id(userid_foreach)
        albumid.append(get_album_id(userid_foreach))
        pic_num.append(get_pic_num(userid_foreach))
    for i in range(len(albumid)):
        a = albumid[i]
        b = pic_num[i]
        c = {}
        for i in range(len(a)):
            c[a[i]] = b[i]
        subkey = [x for x in a]
        e = []
        for i in subkey:
            j = dict([(i, c[i])])
            e.append(j)
        f.append(e)
    for i in range(len(userid)):
        g[userid[i]] = f[i]
    print(g)
    for i in userid:
        userId = i
        print('userid:{}'.format(userId))
        for i in range(len(g[userId])):
            album_id = g[userId][i]
            for k in album_id.keys():
                albumId = k
            for v in album_id.values():
                picNum = v
                picnum = int(picNum)
                print('picnum:{}'.format(picnum))
                page = picnum // 16
                get_pic_url(userId, albumId, picnum,page)
main()
# def down_pic(url,n):
#     url_addr= ''.join(url)
#     url_list = 'http:' + url_addr
#     thread_lock.release()
