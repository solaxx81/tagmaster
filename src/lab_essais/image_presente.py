from pathlib import Path

from mutagen.id3 import ID3


def verifier_pochette(chemin_fichier: Path):
    """Test existence d'une pochette dans le MP3."""
    try:
        audio = ID3(chemin_fichier)

        # Le tag pour les images est "APIC"
        # On utilise .getall pour voir s'il y en a au moins une
        pochettes = audio.getall("APIC")

        if pochettes:
            pochette = pochettes[0]
            print(f"✅ Image trouvée : {pochette.mime} ({len(pochette.data)} octets)")
        else:
            print("❌ Aucune image dans ce fichier.")

    except Exception as e:
        print(f"Erreur ID3 : {e}")


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
        verifier_pochette(fichier)


if __name__ == "__main__":
    main()
