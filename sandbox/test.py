def extraire_infos_fichier(nom_fichier):
    """On retire l'extension .mp3 et on sépare au niveau du ' - '"""
    nom_sans_extension = nom_fichier.replace(".mp3", "")

    if " - " in nom_sans_extension:
        artiste, titre = nom_sans_extension.split(" - ", 1)
        return artiste.strip(), titre.strip()
    return None, None


# Test rapide
fichier = "Daft Punk - Get Lucky.mp3"
artiste, titre = extraire_infos_fichier(fichier)
print(f"Artiste : {artiste} | Titre : {titre}")
