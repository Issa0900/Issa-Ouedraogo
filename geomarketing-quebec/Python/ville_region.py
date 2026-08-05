# Correspondance ville -> région administrative du Québec (17 régions).
# Construite à partir des ~500 municipalités les plus fréquentes dans le registre des
# entreprises (couvre ~90% des établissements). Approximatif pour les petites localités
# hors de cette liste (non classées).

VILLE_REGION = {}

def _add(region, villes):
    for v in villes:
        VILLE_REGION[v.upper()] = region

_add("Montréal", [
    "Montréal", "Montreal", "Montréal-Est", "Montréal-Ouest", "Verdun", "Lachine",
    "LaSalle", "Anjou", "Pierrefonds", "Saint-Laurent", "Mont-Royal", "Westmount",
    "Hampstead", "Côte-Saint-Luc", "Dorval", "Pointe-Claire", "Kirkland",
    "Dollard-Des Ormeaux", "Beaconsfield", "Sainte-Anne-de-Bellevue", "Baie-D'Urfé",
    "Saint-Léonard", "Montréal                            QC",
])

_add("Capitale-Nationale", [
    "Québec", "Quebec", "L'Ancienne-Lorette", "Saint-Augustin-de-Desmaures",
    "Baie-Saint-Paul", "La Malbaie", "Donnacona", "Pont-Rouge", "Saint-Raymond",
    "Neuville", "Stoneham-et-Tewkesbury", "Lac-Beauport", "Boischatel",
    "Château-Richer", "Beaupré", "Sainte-Anne-de-Beaupré", "Wendake", "Shannon",
    "Sainte-Catherine-de-la-Jacques-Cartier", "Sainte-Brigitte-de-Laval",
    "Saint-Marc-des-Carrières", "L'Île-d'Orléans",
])

_add("Laval", ["Laval"])

_add("Outaouais", [
    "Gatineau", "Val-des-Monts", "Chelsea", "Cantley", "La Pêche", "Maniwaki",
    "Pontiac", "Papineauville", "Saint-André-Avellin",
])

_add("Montérégie", [
    "Longueuil", "Brossard", "Saint-Jean-sur-Richelieu", "Boucherville",
    "Châteauguay", "Sorel-Tracy", "Saint-Bruno-de-Montarville", "Chambly",
    "Beloeil", "La Prairie", "Saint-Lambert", "Varennes", "Saint-Constant",
    "Candiac", "Saint-Lazare", "Mont-Saint-Hilaire", "Sainte-Catherine",
    "Lacolle", "Beauharnois", "Saint-Basile-le-Grand", "Delson", "Mercier",
    "Pincourt", "Napierville", "Carignan", "L'Île-Perrot", "Rigaud",
    "Marieville", "Saint-Amable", "Saint-Rémi", "Contrecoeur", "Saint-Hubert",
    "Sainte-Brigide-d'Iberville", "Acton Vale", "Coteau-du-Lac", "Saint-Zotique",
    "Saint-Mathieu-de-Beloeil", "Verchères", "Sainte-Martine", "Otterburn Park",
    "McMasterville", "Hemmingford", "Huntingdon", "Richelieu", "Ormstown",
    "Les Coteaux", "Les Cèdres", "Granby", "Waterloo", "Roxton Pond",
    "Saint-Pie", "Saint-Césaire", "Farnham", "Cowansville", "Bromont",
    "Sutton", "Dunham", "Bedford", "Vaudreuil-Dorion", "Hudson",
    "Notre-Dame-de-l'Île-Perrot", "Saint-Isidore", "Saint-Philippe",
    "Saint-Alexandre", "Shefford",
])

_add("Estrie", [
    "Sherbrooke", "Magog", "Coaticook", "Lac-Mégantic", "Windsor", "Danville",
    "Richmond", "Cookshire-Eaton", "Stanstead", "Orford", "Val-des-Sources",
])

_add("Centre-du-Québec", [
    "Drummondville", "Victoriaville", "Bécancour", "Nicolet", "Plessisville",
    "Princeville", "Warwick", "Saint-Germain-de-Grantham",
    "Saint-Cyrille-de-Wendover",
])

_add("Mauricie", [
    "Trois-Rivières", "Shawinigan", "La Tuque", "Louiseville", "Saint-Tite",
])

_add("Chaudière-Appalaches", [
    "Lévis", "Saint-Georges", "Sainte-Marie", "Thetford Mines", "Montmagny",
    "Lac-Etchemin", "Saint-Joseph-de-Beauce", "Saint-Anselme", "Sainte-Claire",
    "Saint-Lambert-de-Lauzon", "Saint-Apollinaire", "Saint-Henri", "Beauceville",
    "Disraeli", "Saint-Jean-Port-Joli", "Lac-Etchemin",
])

_add("Lanaudière", [
    "Terrebonne", "Repentigny", "Mascouche", "Joliette", "L'Assomption",
    "Saint-Lin--Laurentides", "Rawdon", "Lavaltrie", "Saint-Charles-Borromée",
    "Sainte-Julienne", "Notre-Dame-des-Prairies", "Saint-Félix-de-Valois",
    "Berthierville", "Saint-Calixte", "Saint-Jean-de-Matha",
    "Saint-Roch-de-l'Achigan", "Saint-Jacques", "Saint-Ambroise-de-Kildare",
    "L'Épiphanie", "Chertsey", "Saint-Côme", "Lanoraie",
])

_add("Laurentides", [
    "Saint-Jérôme", "Mirabel", "Blainville", "Boisbriand", "Sainte-Adèle",
    "Sainte-Thérèse", "Sainte-Sophie", "Sainte-Agathe-des-Monts", "Prévost",
    "Sainte-Marthe-sur-le-Lac", "Saint-Colomban", "Deux-Montagnes",
    "Saint-Joseph-du-Lac", "Rosemère", "Mont-Tremblant", "Lachute", "Val-David",
    "Saint-Hippolyte", "Saint-Eustache", "Mont-Laurier", "Rivière-Rouge",
    "Morin-Heights", "Lorraine", "Bois-des-Filion", "Sainte-Anne-des-Plaines",
    "Piedmont", "Oka", "Brownsburg-Chatham", "Saint-Sauveur", "Mont-Blanc",
])

_add("Bas-Saint-Laurent", [
    "Rimouski", "Rivière-du-Loup", "Matane", "Amqui", "Témiscouata-sur-le-Lac",
    "Trois-Pistoles", "Saint-Pascal", "La Pocatière", "Mont-Joli",
])

_add("Saguenay–Lac-Saint-Jean", [
    "Saguenay", "Alma", "Roberval", "Dolbeau-Mistassini", "Saint-Félicien",
    "Hébertville", "Chicoutimi", "Jonquière",
])

_add("Abitibi-Témiscamingue", [
    "Rouyn-Noranda", "Val-d'Or", "Amos", "La Sarre", "Ville-Marie",
])

_add("Côte-Nord", [
    "Sept-Îles", "Baie-Comeau", "Port-Cartier", "Havre-Saint-Pierre",
])

_add("Nord-du-Québec", ["Chibougamau", "Chapais", "Lebel-sur-Quévillon"])

_add("Gaspésie–Îles-de-la-Madeleine", [
    "Gaspé", "Chandler", "New Richmond", "Carleton-sur-Mer",
    "Sainte-Anne-des-Monts", "Les Îles-de-la-Madeleine",
])
