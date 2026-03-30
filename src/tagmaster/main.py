from pathlib import Path

from mutagen.easyid3 import EasyID3


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
            if '-' in nom_pur:
                partie_artiste,partie_titre=nom_pur.split(" - ",1)
                artiste=partie_artiste.strip()
                titre=partie_titre.strip()
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
    morceau_a_completer: list[list[str]] = []
    for fichier in dossier.glob("*.mp3"):
        infos = traiter_fichier_mp3(fichier)
        if infos:
            morceau_a_completer.append(infos)

    print(morceau_a_completer)


if __name__ == "__main__":
    main()
