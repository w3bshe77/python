#/usr/bin/env python3
#-*- coding=utf-8 -*-
# @Time    : 17-9-10 下午2:03
# @Author  : w3bshe77
# @Site    : 
# @File    : mmtspy.py
# @Software: PyCharm Community Edition
'''
                                            本文件仅用于爬淘女郎
'''
import requests
import re
import threading
headers = {'User-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60'}
thread_lock = threading.BoundedSemaphore(value=10)
url = 'https://mm.taobao.com/tstar/search/tstar_model.do?_input_charset=utf-8'

def get_url_list():
    r = requests.post(url,headers =  headers)
    text = r.json()
    url_dict = text['data']['searchDOList']
    return url_dict
def get_album_id(userid):
    r = requests.post('https://mm.taobao.com/self/album/open_album_list.htm?_charset=utf-8&user_id%20={}'.format(userid),headers=headers)
    # https://mm.taobao.com/self/album/open_album_list.htm?_charset=utf-8&user_id%20=176817195
    reg = r'.*?album_id=.*?(\d+)&'
    albumid = re.findall(reg, r.text)[::9]
    return albumid

def get_pic_num(userid):
    r = requests.post('https://mm.taobao.com/self/album/open_album_list.htm?_charset=utf-8&user_id%20={}'.format(userid),headers=headers)
    reg = r'span class="mm-pic-number">\((.*?\d+)张'
    pic_num = re.findall(reg, r.text)
    return pic_num
def get_pic_url(userid,albumid,pic_num,page):# 每页只有16条数据
    urls =  []
    paGe = 0
    if pic_num <= 16:
        for i in range(pic_num):
            r = requests.get('https://mm.taobao.com/album/json/get_album_photo_list.htm?user_id={}&album_id={}&page={}'.format(userid, albumid, paGe), headers=headers)
            json = r.json()
            url = json['picList'][i]['picUrl']
            urls.append(url)
    else:
        x =  pic_num % 16
        while paGe < page - 1:
            for i in range(16):
                r = requests.get('https://mm.taobao.com/album/json/get_album_photo_list.htm?user_id={}&album_id={}&page={}'.format(userid,albumid,paGe),headers=headers)
                json = r.json()
                url = json['picList'][i]['picUrl']
                urls.append(url)
            paGe += 1
            continue
        else:
            for i in range(x) :
                r = requests.get('https://mm.taobao.com/album/json/get_album_photo_list.htm?user_id={}&album_id={}&page={}'.format(userid, albumid, paGe), headers=headers)
                json = r.json()
                url = json['picList'][i]['picUrl']
                urls.append(url)
    return urls
def down_pic(url,n):
    url_addr= ''.join(url)
    url_list = 'http:' + url_addr
    r = requests.get(url_list)
    path = 'img/'+ str(n) + '.jpg'
    with open(path, 'wb') as f:
        f.write(r.content)
    print('正在下载第{}张图片'.format(n))
    thread_lock.release()

def main():
    user_id = get_url_list()
    userid = []
    albumid = []
    pic_num = []
    f = []
    g = {}
    n = 0
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
        for i in range(len(g[userId])):
            album_id = g[userId][i]
            for k,v in album_id.items():
                albumId = k
                picNum = v
                picnum = int(picNum)
                page = picnum // 16 + 1
                urls = get_pic_url(userId, albumId, picnum,page)
                for i in urls:
                    url = i
                    reg = r'(.*?)_290'
                    urlfinnal = re.findall(reg,url)
                    n += 1
                    thread_lock.acquire()  # 上锁
                    t = threading.Thread(target=down_pic, args=(urlfinnal,n))  # 下载
                    t.start()

main()
