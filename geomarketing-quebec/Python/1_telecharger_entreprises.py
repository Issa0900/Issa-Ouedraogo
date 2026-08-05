"""
Téléchargement des données du registre des entreprises du Québec (Registraire des
entreprises, données ouvertes, licence CC-BY-NC-SA 4.0).

Les tableaux ISQ (population, revenu disponible) ne sont pas téléchargeables par script :
la BDSO est une interface JS sans lien CSV stable. Les exporter manuellement depuis
https://statistique.quebec.ca/fr/vitrine/region vers data/population_regions.csv et
data/revenu_regions.csv (voir data/SOURCES.md).

Le fichier des entreprises fait ~225 Mo compressé : prévoir plusieurs minutes selon la
connexion.
"""

from pathlib import Path

import requests

URL_ENTREPRISES = (
    "https://www.registreentreprises.gouv.qc.ca/RQAnonymeGR/GR/GR03/"
    "GR03A2_22A_PIU_RecupDonnPub_PC/FichierDonneesOuvertes.aspx"
)
DEST = Path(__file__).resolve().parent.parent / "data" / "entreprises_raw.zip"


def telecharger(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=60) as reponse:
        reponse.raise_for_status()
        taille_totale = int(reponse.headers.get("content-length", 0))
        recu = 0
        with open(dest, "wb") as f:
            for morceau in reponse.iter_content(chunk_size=1024 * 1024):
                f.write(morceau)
                recu += len(morceau)
                if taille_totale:
                    print(f"\r{recu / 1_048_576:.0f} / {taille_totale / 1_048_576:.0f} Mo", end="")
    print(f"\nTéléchargé : {dest}")


if __name__ == "__main__":
    telecharger(URL_ENTREPRISES, DEST)
