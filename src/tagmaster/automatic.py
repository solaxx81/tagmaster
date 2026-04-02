from pathlib import Path

import musicbrainzngs
import requests
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.id3._frames import APIC

# Configuration MusicBrainz
musicbrainzngs.set_useragent("TagMaster", "0.3", "mon@email.com")


def traiter_fichier_mp3(chemin_fichier: Path):
    """Analyse les tags et la présence d'une image."""
    try:
        audio_easy = EasyID3(chemin_fichier)
        art_list = audio_easy.get("artist") or ["Artiste Inconnu"]
        tit_list = audio_easy.get("title") or ["Titre Inconnu"]
        alb_list = audio_easy.get("album") or ["Album Inconnu"]

        artiste, titre, album = art_list[0], tit_list[0], alb_list[0]

        a_une_pochette = False
        try:
            audio_id3 = ID3(chemin_fichier)
            if any(key.startswith("APIC") for key in audio_id3.keys()):
                a_une_pochette = True
        except Exception:
            a_une_pochette = False

        if album == "Album Inconnu" or not a_une_pochette:
            return [artiste, titre, album, chemin_fichier, a_une_pochette]
    except Exception:
        return None
    return None


def ajouter_pochette(chemin_fichier: Path, release_id: str):
    """Télécharge la pochette (Tentative Release puis Release-Group)."""
    # Liste des URLs à tester : d'abord l'édition, puis le groupe d'album
    urls = [f"https://coverartarchive.org/release/{release_id}/front-500"]

    try:
        # Récupération de l'ID du groupe d'album pour la roue de secours
        info = musicbrainzngs.get_release_by_id(release_id, includes=["release-groups"])
        rg_id = info["release"]["release-group"]["id"]
        urls.append(f"https://coverartarchive.org/release-group/{rg_id}/front-500")

        for url in urls:
            reponse = requests.get(url, timeout=10)
            if reponse.status_code == 200:
                tags = ID3(chemin_fichier)
                tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Front Cover", data=reponse.content))
                tags.save(chemin_fichier)
                return True
    except Exception:
        pass
    return False


def obtenir_liste_unique(artiste: str, titre: str):
    """Récupère les albums officiels triés par date."""
    resultats = musicbrainzngs.search_recordings(query=titre, artist=artiste)
    albums_vus = set()
    choix_finaux = []
    mots_interdits = ["Compilation", "Live", "Remix", "Soundtrack"]

    recordings = resultats.get("recording-list") or []
    for rec in recordings:
        releases = rec.get("release-list") or []
        for rel in releases:
            group = rel.get("release-group") or {}
            nom_album = rel.get("title")
            sec_types = group.get("secondary-type-list") or []
            if (
                rel.get("status") == "Official"
                and group.get("primary-type") == "Album"
                and not any(m in sec_types for m in mots_interdits)
            ):
                if nom_album not in albums_vus:
                    albums_vus.add(nom_album)
                    choix_finaux.append(rel)

    choix_finaux.sort(key=lambda x: x.get("date", "9999")[:4])
    return choix_finaux


def choisir_album_automatiquement(options):
    """Retourne l'album si un choix unique est évident, sinon None."""
    if len(options) == 1:
        return options[0]
    return None


def main():
    """Fonction principale avec gestion automatique et manuelle."""
    dossier = Path("/mnt/data/python/Music/mp3_tests")
    if not dossier.exists():
        return

    a_traiter = []
    for f in dossier.glob("*.mp3"):
        infos = traiter_fichier_mp3(f)
        if infos:
            a_traiter.append(infos)

    nb_auto = 0
    for art, tit, alb_actuel, chemin, a_poche in a_traiter:
        status_poche = "✅" if a_poche else "❌"
        print(f"\n🔍 Analyse : {art} - {tit}")
        print(f"   [Tag actuel: {alb_actuel} | Pochette: {status_poche}]")

        options = obtenir_liste_unique(art, tit)

        album_selectionne = choisir_album_automatiquement(options)
        rel_id = None

        if album_selectionne:
            print(f"🤖 Auto : '{album_selectionne['title']}' sélectionné.")
            final_alb = album_selectionne["title"]
            final_date = album_selectionne.get("date", "")[:4]
            rel_id = album_selectionne["id"]
            nb_auto += 1
        else:
            if not options:
                print("   ❌ Aucun album trouvé.")
                continue

            for i, opt in enumerate(options, 1):
                print(f"{i}. {opt['title']} ({opt.get('date', '????')[:4]})")

            choix = input("Votre choix (m: manuel, 0: passer, q: quitter) : ")
            if choix.lower() == "q":
                break
            if choix == "0":
                continue
            if choix.lower() == "m":
                final_alb = input("Nom de l'album : ")
                final_date = input("Année : ")
            else:
                sel = options[int(choix) - 1]
                final_alb = sel["title"]
                final_date = sel.get("date", "")[:4]
                rel_id = sel["id"]

        # Sauvegarde
        audio = EasyID3(chemin)
        audio["album"] = final_alb
        if final_date:
            audio["date"] = final_date
        audio.save()

        if rel_id:
            ajouter_pochette(chemin, rel_id)
        print(f"✅ Terminé : {final_alb}")

    print(f"\n--- Fin du traitement. Automatisations réussies : {nb_auto} ---")


if __name__ == "__main__":
    main()
