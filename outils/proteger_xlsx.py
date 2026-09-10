"""
Passe les classeurs .xlsx du portfolio en lecture seule, sans les reconstruire.

Un .xlsx est un zip d'XML. On reecrit uniquement xl/workbook.xml et les
xl/worksheets/sheetN.xml ; toutes les autres entrees (graphiques, TCD, styles,
images, tables) sont recopiees octet pour octet. Un aller-retour openpyxl
detruirait les TCD et les graphiques : c'est pour cela qu'on edite le zip.

Trois verrous poses :
  - fileSharing readOnlyRecommended  -> Excel ouvre le fichier en lecture seule
  - workbookProtection lockStructure -> pas d'ajout/suppression/renommage d'onglet
  - sheetProtection (par feuille)    -> cellules et formules non modifiables,
                                        mais selection, tri, filtre, TCD et
                                        redimensionnement restent permis
Aucun mot de passe : le but est d'empecher la modification accidentelle et de
signaler l'intention, pas de chiffrer. Issa peut lever la protection en un clic
(Revision > Oter la protection) pour mettre a jour un classeur.

Le script est idempotent : relance sur un fichier deja protege = meme resultat.
"""

import re
import shutil
import sys
import zipfile

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

FILE_SHARING = '<fileSharing readOnlyRecommended="1"/>'
WORKBOOK_PROTECTION = '<workbookProtection lockStructure="1"/>'

# Rappel de semantique ECMA-376 : pour ces attributs, "1" = action VERROUILLEE,
# "0" = action AUTORISEE. D'ou sort/autoFilter/pivotTables a "0" (on veut que le
# visiteur puisse trier, filtrer et manipuler les TCD) et formatCells a "1".
SHEET_PROTECTION = (
    '<sheetProtection sheet="1" objects="1" scenarios="1"'
    ' formatCells="1" formatColumns="0" formatRows="0"'
    ' insertColumns="1" insertRows="1" insertHyperlinks="1"'
    ' deleteColumns="1" deleteRows="1"'
    ' selectLockedCells="0" selectUnlockedCells="0"'
    ' sort="0" autoFilter="0" pivotTables="0"/>'
)


def _strip(xml: str, tag: str) -> str:
    """Retire un element vide existant, pour que le script reste idempotent."""
    return re.sub(rf"<{tag}\b[^>]*/>", "", xml)


def _insert_before_first(xml: str, snippet: str, candidates: list[str]) -> str:
    """Insere snippet devant le premier des elements candidats presents.

    L'ordre des enfants de <workbook> est impose par le schema
    (fileVersion, fileSharing, workbookPr, workbookProtection, bookViews,
    sheets, ...) : viser le bon successeur suffit a se placer correctement.
    """
    for tag in candidates:
        pos = xml.find(f"<{tag}")
        if pos != -1:
            return xml[:pos] + snippet + xml[pos:]
    raise ValueError(f"aucun point d'insertion parmi {candidates}")


def protect_workbook(xml: str) -> str:
    xml = _strip(_strip(xml, "fileSharing"), "workbookProtection")
    xml = _insert_before_first(xml, FILE_SHARING, ["workbookPr", "bookViews", "sheets"])
    return _insert_before_first(xml, WORKBOOK_PROTECTION, ["bookViews", "sheets"])


def protect_sheet(xml: str) -> str:
    """Insere sheetProtection juste apres sheetData (place imposee par le schema)."""
    xml = _strip(xml, "sheetProtection")

    end = xml.find("</sheetData>")
    pos = end + len("</sheetData>") if end != -1 else -1
    if pos == -1:  # feuille vide : <sheetData/>
        m = re.search(r"<sheetData\b[^>]*/>", xml)
        if not m:
            return xml  # pas une feuille exploitable, on n'y touche pas
        pos = m.end()

    # sheetCalcPr, s'il existe, se place entre sheetData et sheetProtection.
    calc = re.match(r"\s*<sheetCalcPr\b[^>]*/>", xml[pos:])
    if calc:
        pos += calc.end()

    return xml[:pos] + SHEET_PROTECTION + xml[pos:]


def process(path: str) -> None:
    backup = path + ".orig"
    shutil.copy2(path, backup)

    with zipfile.ZipFile(backup) as src:
        infos = src.infolist()
        payloads = {i.filename: src.read(i.filename) for i in infos}

    sheets = 0
    for name, data in payloads.items():
        if name == "xl/workbook.xml":
            payloads[name] = protect_workbook(data.decode("utf-8")).encode("utf-8")
        elif re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name):
            payloads[name] = protect_sheet(data.decode("utf-8")).encode("utf-8")
            sheets += 1

    # Reecriture en preservant l'ordre, l'horodatage et le mode de compression
    # de chaque entree : seules les parties XML ciblees changent.
    with zipfile.ZipFile(path, "w") as out:
        for info in infos:
            new = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            new.compress_type = info.compress_type
            new.external_attr = info.external_attr
            new.internal_attr = info.internal_attr
            new.create_system = info.create_system
            out.writestr(new, payloads[info.filename])

    print(f"  {path} : {sheets} feuille(s) protegee(s)")


if __name__ == "__main__":
    for target in sys.argv[1:]:
        process(target)
