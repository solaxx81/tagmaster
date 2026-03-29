from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

audio = MP3("/mnt/data/python/Music/playlist/3 Doors Down - Here Without You.mp3", ID3=EasyID3)
print(audio.keys())
