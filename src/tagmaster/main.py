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
        liste_date = audio.get("date", [])
        artiste = liste_artiste[0] if liste_artiste else "Artiste Inconnu"
        titre = liste_titre[0] if liste_titre else "Titre Inconnu"
        album = liste_album[0] if liste_album else "Album Inconnu"
        date = liste_date[0] if liste_date else "Date Inconnue"

        print(f"'{chemin_fichier.name}' - [{artiste}] - {titre} (Album: {album} - Année: {date})")
    except Exception as e:
        print(f"Erreur : Aucun tag dans le fichier {chemin_fichier.name} ({e})")


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
    for fichier in dossier.glob("*.mp3"):
        traiter_fichier_mp3(fichier)

        # 3. Essayer de lire les tags avec EasyID3
        # Aide : utilise un bloc "try...except" au cas où le fichier n'a aucun tag
        # Aide : EasyID3 se comporte comme un dictionnaire Python


if __name__ == "__main__":
    main()
