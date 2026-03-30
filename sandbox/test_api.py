import musicbrainzngs

musicbrainzngs.set_useragent("MonSuperGestionnaireMP3", "0.1", "ton@email.com")

resultat = musicbrainzngs.search_recordings(artist="The Offspring", recording="Pretty Fly")

print(resultat["recording-list"][0]["release-list"][0]["title"])
