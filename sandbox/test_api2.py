import musicbrainzngs

# Configuration obligatoire
musicbrainzngs.set_useragent("MonAppCode", "0.1", "monemail@exemple.com")


def rechercher_album(artiste, titre):
    """Recherche du duo [titre, artiste] sur musicbrainz"""

    # On lance la recherche
    resultat = musicbrainzngs.search_recordings(query=titre, artist=artiste)

    # On vérifie s'il y a au moins un résultat
    if resultat["recording-count"] > 0:
        premier_enregistrement = resultat["recording-list"][0]
        test = premier_enregistrement["release-list"][0]
        print(test)

        # À tester dans ton code pour comprendre :
        # print("Contenu de resultat :", resultat.keys())

        premier_rec = resultat["recording-list"][0]
        # print("\nContenu d'un enregistrement :", premier_rec.keys())
        # print(premier_rec)

        premiere_rel = premier_rec["release-list"][0]
        # print("\nContenu d'un album :", premiere_rel.keys())
        # print(premiere_rel)

        # On regarde si cet enregistrement est lié à des albums (releases)
        if "release-list" in premier_enregistrement:
            # On prend le titre du premier album de la liste
            nom_album = premier_enregistrement["release-list"][0]["title"]
            return nom_album

    return "Aucun album trouvé"


resultat = rechercher_album("Kryptonite", "3 Doors Down")
print(resultat)
