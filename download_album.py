import os
import sys
from QQMusic import *

# Reference
# https://github.com/LIU9293/musicAPI/blob/master/src/qq.js
# https://github.com/HuberTRoy/MusicPlayer

if __name__ == "__main__":
    qq_music = QQMusic()
    album_title = sys.argv[1]
    artist = sys.argv[2]
    music_list = qq_music.search_song(' '.join([album_title, artist]), num=100)
    filtered_list = list(filter(
        lambda music: music['album']['title'].lower() == album_title and
                      music['singer'][0]['title'].lower() == artist,
                music_list))

    # if filter does not work, fallback to the original list
    if len(filtered_list) == 0:
        filtered_list = music_list

    album_list = sorted(filtered_list, key=lambda music: (music['album']['title'], music['index_album']))
    for num, music in enumerate(album_list):
        print(num,
              '[' + music['album']['title'] + ']',
              music['index_album'],
              music['title'],
              '/',
              music['singer'][0]['title'])


    answer = input('Look good? (Y/N) ')
    artwork_downloaded = False
    if answer.lower() == 'y':
        for song in album_list:
            qq_song = QQMusicSong(
                song['file']['media_mid'],
                song['mid'],
                song['title'].replace('/', '\\'),
                song['album'],
                song['index_album'],
            )
            os.makedirs(qq_song.get_savepath(), exist_ok=True)
            vkey = qq_song.get_key()
            # print(vkey)
            url = qq_song.get_music_url()
            # print(url)
            print('Downloading', qq_song.title)
            qq_song.music_save()
            if not artwork_downloaded:
                qq_song.save_artwork()
                artwork_downloaded = True
            # qq_song.lrc_save()
