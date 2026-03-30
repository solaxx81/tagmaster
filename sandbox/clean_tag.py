from mutagen.easyid3 import EasyID3

# Attention, ceci supprime TOUT dans le fichier indiqué
audio = EasyID3("/mnt/data/python/Music/playlist/0jym - pas de tag.mp3")
audio.delete()
audio.save()
