#coding=utf-8
import os
import sys
import time
import json
import base64
import random
import urllib
import urllib.parse
import urllib.request
import requests

class QQMusic():
    guid = int(random.random() * 2147483647) * int(time.time() * 1000) % 10000000000
    cookie = {
        "Cookie": 'pgv_pvi=6725760000; pgv_si=s4324782080; pgv_pvid=%s; qqmusic_fromtag=66' % guid,
    }

    def search_song(self, key_word, page=1, num=20):
        '''根据关键词查找歌曲'''
        url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'
        url += '?new_json=1&aggr=1&cr=1&flag_qc=0&p=%d&n=%d&w=%s#page=2' \
                % (page, num, urllib.parse.quote(key_word))
        song_list = json.loads(urllib.request.urlopen(url).read()[9:-1])['data']['song']['list']
        return song_list


class QQMusicSong(QQMusic):
    def __init__(self, media_mid, song_mid, title, album, track_id):
        self.filename = "C400%s.m4a" % media_mid
        self.song_mid = song_mid
        self.title = title
        self.vkey = ""
        self.music_url = ""
        self.album = album
        self.track_id = track_id

    # https://github.com/HuberTRoy/MusicPlayer/blob/master/MusicPlayer/apis/qqApi.py
    def get_key(self):
        url = 'http://base.music.qq.com/fcgi-bin/fcg_musicexpress.fcg?'
        url += 'format=json&platform=yqq&cid=205361747&songmid=%s&filename=%s&guid=%s' \
                % (self.song_mid, self.filename, QQMusic.guid)
        self.vkey = json.loads(requests.get(url).text)['key']
        return self.vkey

    def get_vkey(self):
        '''获取指定歌曲的vkey值'''
        url = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?'
        url += 'format=json&platform=yqq&cid=205361747&songmid=%s&filename=%s&guid=%s' \
                % (self.song_mid, self.filename, QQMusic.guid)
        # print(url)
        self.vkey = json.loads(requests.get(url).text)['data']['items'][0]['vkey']
        return self.vkey

    def get_music_url(self):
        '''获取指定歌曲的播放地址'''
        url = 'http://dl.stream.qqmusic.qq.com/%s?' % self.filename
        self.music_url = url + 'vkey=%s&guid=%s&fromtag=30' % (self.vkey, QQMusic.guid)
        return self.music_url

    def get_savepath(self):
        return os.path.join(sys.path[0], self.get_album_title())

    def music_save(self, path=None):
        '''将此歌曲保存至本地'''
        path = self.get_savepath() if path is None else path
        media_data = requests.get(self.music_url, cookies=QQMusic.cookie)
        if media_data.status_code != 200:
            print('歌曲或网络错误')
            return
        music_file = open(os.path.join(path, str(self.track_id) + ' - ' + self.title + '.m4a'), 'wb')
        for chunk in media_data.iter_content(chunk_size=512):
            if chunk:
                music_file.write(chunk)
        music_file.close()
        print('歌曲下载完成')

    def lrc_save(self, path=None):
        path = self.get_savepath() if path is None else path
        headers = {
            "Referer": "https://y.qq.com/portal/player.html",
            "Cookie": "skey=@LVJPZmJUX; p",
        }
        lrc_data = requests.get('https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?g_tk=753738303&songmid=' + self.song_mid, headers=headers)
        if lrc_data.status_code != 200:
            print('歌词不存在或网络错误')
        lrc_dict = json.loads(lrc_data.text[18:-1])
        lrc_data = base64.b64decode(lrc_dict['lyric'])
        lrc_file = open(os.path.join(path, self.title + '.lrc'), 'wb')
        lrc_file.write(lrc_data)
        lrc_file.close()
        #若有翻译歌词
        if lrc_dict['trans'] != "":
            lrc_data = base64.b64decode(lrc_dict['trans'])
            lrc_file = open(os.path.join(path, self.title + '-trans.lrc'), 'w')
            lrc_file.write(lrc_data)
            lrc_file.close()
        print('歌词下载完成')

    def get_album_title(self):
        return self.album['title']

    def get_artwork_url(self):
        url = "https://y.gtimg.cn/music/photo_new/T002R300x300M000{}.jpg".format(self.album['mid'])
        return url

    def save_artwork(self, path=None):
        path = self.get_savepath() if path is None else path
        url = self.get_artwork_url()
        response = requests.get(url)
        if response.status_code != 200:
            print('网络错误')
            return

        with open(os.path.join(path, self.get_album_title() + '.jpg'), 'wb') as album_file:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    album_file.write(chunk)


if __name__ == "__main__":
    key_word = input('Input key word: ')
    qq_music = QQMusic()
    music_list = qq_music.search_song(key_word)
    for num, music in enumerate(music_list):
        print(num, music['title'], music['singer'][0]['title'])
    select_num = int(input('Select num: '))
    song = QQMusicSong(
        music_list[select_num]['file']['media_mid'],
        music_list[select_num]['mid'],
        music_list[select_num]['title'].replace('/', '\\'),
        music_list[select_num]['album']['title'],
    )
    song.get_vkey()
    song.get_music_url()
    song.music_save()
    song.lrc_save()
