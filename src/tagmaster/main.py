from pathlib import Path

import musicbrainzngs
from mutagen.easyid3 import EasyID3

# Configuration (obligatoire pour que MusicBrainz nous réponde)
musicbrainzngs.set_useragent("MonTestMusic", "0.1", "ton@email.com")


def traiter_fichier_mp3(chemin_fichier: Path):
    """S'occupe de la lecture des tags d'un seul fichier."""

    try:
        audio = EasyID3(chemin_fichier)

        # On accède aux tags comme à un dictionnaire
        # .get() est plus sûr : si le tag n'existe pas, il renverra "Inconnu" au lieu de planter
        liste_artiste = audio.get("artist", [])
        liste_titre = audio.get("title", [])
        liste_album = audio.get("album", [])
        # liste_date = audio.get("date", [])
        artiste = liste_artiste[0] if liste_artiste else "Artiste Inconnu"
        titre = liste_titre[0] if liste_titre else "Titre Inconnu"
        album = liste_album[0] if liste_album else "Album Inconnu"
        # date = liste_date[0] if liste_date else "Date Inconnue"

        if artiste == "Artiste Inconnu" or titre == "Titre Inconnu":
            nom_pur = chemin_fichier.stem
            if "-" in nom_pur:
                partie_artiste, partie_titre = nom_pur.split(" - ", 1)
                artiste = partie_artiste.strip()
                titre = partie_titre.strip()
            else:
                # A voir plus tard, mais fichier mal nommé dès le départ. pas traité pour l'instant
                return None

        if album == "Album Inconnu":
            return [artiste, titre]
        else:
            return None

    except Exception:
        # Fichier mal formé ou vérolé
        return None


def obtenir_liste_unique(artiste, titre):
    """
    Nettoie la liste d'albums potentiels de tous les albums
    non-officiels, live, bootleg, compilation, etc
    """

    resultats = musicbrainzngs.search_recordings(query=titre, artist=artiste)
    albums_vus = set()  # Pour stocker les noms d'albums déjà affichés
    choix_finaux = []
    # Liste des "types secondaires" d'albums qui ne conviennent pas
    mots_interdits = ["Compilation", "Live", "Remix", "Soundtrack"]

    for rec in resultats.get("recording-list", []):
        for rel in rec.get("release-list", []):
            group = rel.get("release-group", {})

            nom_album = rel.get("title")
            statut = rel.get("status")
            type_principal = group.get("primary-type")
            types_secondaires = set(group.get("secondary-type-list", []))

            est_indesirable = any(mot in types_secondaires for mot in mots_interdits)

            if statut == "Official" and type_principal == "Album" and not est_indesirable:
                if nom_album not in albums_vus:
                    albums_vus.add(nom_album)
                    choix_finaux.append(rel)

    def extraire_annee(album):
        date_brute = album.get("date", "9999")  # 9999 si inconnu pour le mettre à la fin
        return date_brute[:4]  # On ne prend que les 4 premiers caractères

    # On trie la liste 'choix_finaux' en place
    choix_finaux.sort(key=extraire_annee)

    return choix_finaux


def main():
    """Point d'entrée principal du programme."""
    # 1. Définir le dossier (plus tard, on pourra passer ça en argument)
    dossier = Path("/mnt/data/python/Music/mp3_tests")

    print(f"--- Analyse du dossier : {dossier} ---")

    # 2. Vérifier si le dossier existe
    if not dossier.exists():
        print(f"Erreur : Le dossier {dossier} est introuvable.")
        return

    # 3. Boucle sur les fichiers
    morceaux_a_completer: list[list[str]] = []
    for fichier in dossier.glob("*.mp3"):
        infos = traiter_fichier_mp3(fichier)
        # Crée une liste des fichiers où le tag album n'est pas renseigné
        if infos:
            morceaux_a_completer.append(infos)

    for artiste, titre in morceaux_a_completer:
        print(f"\nRecherche pour : {artiste} - {titre}")

        options = obtenir_liste_unique(artiste, titre)

        if not options:
            print("Désolé, aucun album trouvé sur MusicBrainz.")
            continue

        # 1. Affiche les options numérotées
        for i, album_data in enumerate(options, 1):
            nom = album_data.get("title")
            annee = album_data.get("date", "????")
            print(f"{i}. {nom} ({annee})")

        print("0. Passer ce morceau")

        # 2. Demande le choix à l'utilisateur
        reponse = input("Votre choix : ")

        # 3. Logique de sélection (à toi de jouer !)
        if reponse == "0":
            continue

        # Indice pour récupérer l'album choisi :
        index = int(reponse) - 1
        album_choisi = options[index]

        print(f"Vous avez choisi : {album_choisi['title']}")


if __name__ == "__main__":
    main()
