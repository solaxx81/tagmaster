from pathlib import Path

import musicbrainzngs
import requests
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.id3._frames import APIC

# Configuration obligatoire pour que MusicBrainz réponde
musicbrainzngs.set_useragent("MonTestMusic", "0.1", "mon@email.com")


def traiter_fichier_mp3(chemin_fichier: Path):
    """S'occupe de la lecture des tags d'un seul fichier."""

    try:
        # Vérification des tags textes avec EasyID3 (artiste, titre, album)
        audio_easy = EasyID3(chemin_fichier)

        # Tags forment un dictionnaire auquel on accède par .get()
        liste_artiste = audio_easy.get("artist", [])
        liste_titre = audio_easy.get("title", [])
        liste_album = audio_easy.get("album", [])

        artiste = liste_artiste[0] if liste_artiste else "Artiste Inconnu"
        titre = liste_titre[0] if liste_titre else "Titre Inconnu"
        album = liste_album[0] if liste_album else "Album Inconnu"

        # Vérification de la présence d'une pochette avec ID3 complet
        a_une_pochette = False

        try:
            audio_ID3 = ID3(chemin_fichier)
            if any(key.startswith("APIC") for key in audio_ID3.keys()):
                a_une_pochette = True
        except Exception:
            a_une_pochette = False

        besoin_reparation = (
            album == "Album Inconnu" or artiste == "Artiste Inconnu" or titre == "Titre Inconnu" or not a_une_pochette
        )

        if besoin_reparation:
            return [artiste, titre, album, chemin_fichier, a_une_pochette]

    except Exception:
        # Fichier mal formé ou vérolé
        return None


def obtenir_liste_unique(artiste, titre):
    """Nettoie la liste d'albums potentiels de tous les albums
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
        return date_brute[:4]  # Que les 4 premiers caractères qui contiennent l'année

    # Tri de la liste 'choix_finaux' sur l'année
    choix_finaux.sort(key=extraire_annee)

    return choix_finaux


def ajouter_pochette(chemin_fichier, release_id):
    """Télécharge la pochette depuis Cover Art Archive et l'insère dans le MP3."""
    url = f"https://coverartarchive.org/release/{release_id}/front-500"

    try:
        reponse = requests.get(url, timeout=10)
        if reponse.status_code == 200:
            try:
                tags = ID3(chemin_fichier)
            except Exception:
                tags = ID3()

            tags.add(
                APIC(
                    encoding=3,  # UTF-8
                    mime="image/jpeg",  # format standard
                    type=3,  # 3 = pochette avant
                    desc="Front Cover",
                    data=reponse.content,
                )
            )
            tags.save(chemin_fichier)
            return True
    except Exception as e:
        print(f"      ⚠️ Erreur pochette : {e}")

    return False


def main():
    """Point d'entrée principal du programme."""

    dossier = Path("/mnt/data/python/Music/mp3_tests")

    print(f"--- Analyse du dossier : {dossier} ---")

    if not dossier.exists():
        print(f"Erreur : Le dossier {dossier} est introuvable.")
        return

    # Boucle sur les fichiers
    morceaux_a_completer: list[list[str]] = []
    for fichier in dossier.glob("*.mp3"):
        infos = traiter_fichier_mp3(fichier)
        # Crée une liste des fichiers où le tag album n'est pas renseigné
        if infos:
            morceaux_a_completer.append(infos)

    for artiste, titre, album_actuel, chemin, a_pochette in morceaux_a_completer:
        statut_poche = "✅" if a_pochette else "❌ Sans pochette"
        print(f"\n--- Analyse de : {artiste} - {titre} ---")
        print(f"   Album actuel dans le tag : {album_actuel}")
        print(f"   Pochette : {statut_poche}")

        options = obtenir_liste_unique(artiste, titre)

        if not options:
            print("Désolé, aucun album trouvé sur MusicBrainz.")
            continue

        # Affiche les options numérotées
        for i, album_data in enumerate(options, 1):
            nom = album_data.get("title")
            annee = album_data.get("date", "????")
            print(f"{i}. {nom} ({annee})")

        print("m. Saisir le nom de l'album")
        print("0. Passer ce morceau")
        print("q. Quitter le programme")
        reponse = input("Votre choix : ")

        if reponse == "0":
            continue
        if reponse.lower() == "q":
            break

        if reponse.lower() == "m":
            album_final = input("Entrez le nom de l'album : ")
            annee_finale = input("Entrez l'année (laisser vide si inconnu) : ")
        else:
            # Indice pour récupérer l'album choisi :
            index = int(reponse) - 1
            album_choisi = options[index]
            album_final = album_choisi["title"]
            annee_finale = album_choisi.get("date", "")[:4]

        print(f"👉 Validation : {album_final}")

        audio = EasyID3(chemin)
        audio["album"] = album_final
        if annee_finale:
            audio["date"] = annee_finale[:4]  # Seule l'année est conservée en cas de date yyyy-mm-dd

        audio.save()

        if reponse.lower() != "m":
            release_id = album_choisi.get("id")
            if release_id:
                print("   🔍 Recherche d'une pochette sur MusicBrainz...")
                succes = ajouter_pochette(chemin, release_id)
                if succes:
                    print("   🎨 Pochette intégrée avec succès !")
                else:
                    print("   ℹ️ Pas de pochette trouvée pour cet album.")

        print("✅ Tags texte mis à jour !")


if __name__ == "__main__":
    main()
