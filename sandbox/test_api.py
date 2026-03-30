import musicbrainzngs

# Configuration (obligatoire pour que MusicBrainz nous réponde)
musicbrainzngs.set_useragent("MonTestMusic", "0.1", "ton@email.com")


def lister_albums_officiels(artiste, titre):
    """Extrait la liste de tous les albums"""
    # 1. On lance la recherche
    print(f"Recherche de : {artiste} - {titre}...")
    reponse = musicbrainzngs.search_recordings(query=titre, artist=artiste)

    # 2. On vérifie s'il y a des résultats dans 'recording-list'
    if not reponse.get("recording-list"):
        print("Aucun enregistrement trouvé.")
        return

    # 3. On boucle sur TOUS les enregistrements trouvés (souvent 25 par défaut)
    # car 'Kryptonite' peut apparaître plusieurs fois (version live, acoustique, etc.)
    for enregistrement in reponse["recording-list"]:
        # 4. Pour chaque enregistrement, on regarde sa liste d'albums ('release-list')
        if "release-list" in enregistrement:
            for album in enregistrement["release-list"]:
                # --- C'EST ICI QU'ON FILTRE LE BAZAR ---

                # On récupère le statut (Official, Bootleg, etc.)
                statut = album.get("status", "Inconnu")

                # On va chercher le type dans 'release-group'
                groupe = album.get("release-group", {})
                type_album = groupe.get("primary-type", "Inconnu")

                # On ne garde que ce qui est "Official" et "Album"
                if statut == "Official" and type_album == "Album":
                    nom_album = album.get("title")
                    date = album.get("date", "Année inconnue")
                    print(f"-> Trouvé : {nom_album} | Date: {date}")


def obtenir_liste_unique(artiste, titre):
    """
    Nettoie la liste d'albums potentiels de tous les albums
    non-officiels, live, bootleg, compilation, etc
    """
    resultats = musicbrainzngs.search_recordings(query=titre, artist=artiste)
    albums_vus = set()  # Pour stocker les noms d'albums déjà affichés
    choix_finaux = []
    mots_interdits = ["Compilation", "Live", "Remix", "Soundtrack"]

    for rec in resultats.get("recording-list", []):
        for rel in rec.get("release-list", []):
            group = rel.get("release-group", {})

            nom_album = rel.get("title")
            statut = rel.get("status")
            type_principal = group.get("primary-type")
            types_secondaires = set(group.get("secondary-type-list", []))

            # Liste des mots "interdits" pour un album studio propre

            # C'est ici que ça se joue :
            types_secondaires = group.get("secondary-type-list", [])
            est_indesirable = any(mot in types_secondaires for mot in mots_interdits)

            if statut == "Official" and type_principal == "Album" and not est_indesirable:
                if nom_album not in albums_vus:
                    albums_vus.add(nom_album)
                    choix_finaux.append(nom_album)

    return choix_finaux


# Test avec ton exemple
# lister_albums_officiels("3 Doors Down", "Kryptonite")
print(obtenir_liste_unique("The Offspring", "Pretty Fly (For A White Guy)"))
print(obtenir_liste_unique("4 Non Blondes", "What's Up"))
