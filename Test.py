# VARIABLES DE TEST

# Coordonnées
Paris = 2.3522, 48.8566
Lyon = 4.8357, 45.7640
Cergy = 2.0761, 49.0365
Marseille = 5.3691, 43.3026
Defense = 2.2382, 48.8924
ENSEA = 2.0754, 49.0325
Pointe_a_Pitre = -61.5376, 16.2371
La_Defense = 2.229307, 48.896676

# Coordonnées lieu principal
lon, lat = La_Defense

# Distance en mètre des points d'intérêts
# Distance nulle pour désactiver le critère
distance_sncf = 0
distance_metro = 0
distance_ecole = 0
distance_universite = 0
distance_crous = 0
distance_parc = 0
distance_pharmacie = 0
distance_boulangerie = 0
distance_medecin = 0
distance_bus = 0
distance_supermarche = 0
distance_piscine = 0
distance_sport = 0
distance_cinema = 0

# IMPORTS

import json
import math
import gc
import requests
from shapely.geometry import Point, Polygon, MultiPolygon, shape
from shapely.ops import unary_union
from shapely.affinity import scale

# CHEMINS

communesjson = "./Data/communes.geojson"
regionsjson = "./Data/Recherche/regions.geojson"
sncfjson = "./Data/gares.geojson"
crousjson = "./Data/crous.geojson"
ecolejson = "./Data/ecole.geojson"
universitejson = "./Data/universite.geojson"
regionidfjson = "./Data/regionidf.geojson"
busidfjson = "./Data/bus-idf.geojson"
metroidfjson = "./Data/metro-idf.geojson"

departementjson1, departementjson2 = "./Data/Recherche/regions/", "/departements.geojson"
villejson1, villejson2 = "./Data/Recherche/departements/", "/communes.geojson"


# OUVERTURE DES FICHIER JSON

with open(communesjson, "r") as f:
    datacommunes = json.load(f)

with open(regionsjson, "r") as f:
    dataregions = json.load(f)

with open(regionidfjson, "r") as f:
    dataregionidf = json.load(f)


# FONCTIONS ANNEXES POUR LA RECHERCHE DE LIEUX

def Coordunique(Liste):
    """Enlève les doublons d'une liste de coordonnées"""
    Liste_unique = []
    for coord in Liste:
        if not coord in Liste_unique:
            Liste_unique.append(coord)
    return Liste_unique

def Distance_Haversine(coord1, coord2):
    """Calcul de la distance en mètres entre 2 coordonnées"""
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    R = 6371000  # Rayon moyen de la Terre en mètres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Distance en mètres

def Rayonrecherche(lon, lat, liste_coord_ville):
    """Recherche la distance la plus grande parmis un centre ville et les villes alentours"""
    
    rayon_max = 0
    coordrecherche = [lon, lat]
    
    for geom in liste_coord_ville:
        if isinstance(geom, Polygon):
            coords = geom.exterior.coords
        elif isinstance(geom, MultiPolygon):
            coords = []
            for poly in geom.geoms:
                coords.extend(poly.exterior.coords)
        else:
            continue  # Skip if not a recognized geometry

        for coord in coords:
            distance = Distance_Haversine(coordrecherche, [coord[0], coord[1]])
            if distance > rayon_max:
                rayon_max = distance

    return rayon_max * 1.1

def testidf(ville):
    for feature in dataregionidf["features"]:
        code = feature["properties"]["code"]
        if ville == code: # Ville en Ile de France
            return True
    
    return False # Ville hors de l'ile de france



# RECHERCHE DE LIEUX EN LOCAL

def recherche_sncf(liste_ville):
    """Recherche la liste des gares de train les plus proche à partir des coordonnées de la zone voulue"""
    with open(sncfjson, "r") as f:
        datasncf = json.load(f)

    # A compléter avec la recherche de coordonnées de gare de train
    liste_coord = []

    for feature in datasncf["features"]:
        if feature["properties"]["voyageurs"] == "O":
            coord = feature["properties"]["c_geo"]
            lon, lat = coord["lon"], coord["lat"]
            code = feature["properties"]["code_commune"]
            for ville in liste_ville:
                if ville == code:
                    liste_coord.append([lon,lat])
    
    del datasncf
    gc.collect()
    return Coordunique(liste_coord)

def recherche_ecole(liste_ville):
    """Recherche la liste des écoles les plus proche à partir des coordonnées de la zone voulue"""
    with open(ecolejson, "r") as f:
        dataecole = json.load(f)

    # A compléter avec la recherche de la position d'une école
    liste_coord = []

    for feature in dataecole["features"]:
        coord = feature["geometry"]
        code = feature["properties"]["code_commune"]
        for ville in liste_ville:
            if feature["geometry"] != None:
                if ville == code:
                    liste_coord.append(coord["coordinates"])
    
    del dataecole
    gc.collect()
    return Coordunique(liste_coord)

def recherche_universite(liste_ville):
    """Recherche la liste des universités proche à partir des coordonnées de la zone voulue"""

    with open(universitejson, "r") as f:
        datauniversite = json.load(f)
    
    # A compléter avec la recherche de la position d'une université
    liste_coord = []

    for feature in datauniversite["features"]:
        coord = feature["geometry"]["coordinates"]
        code = feature["properties"]["com_code"]
        for ville in liste_ville:
            if ville == code:
                liste_coord.append(coord)
    
    del datauniversite
    gc.collect()
    
    return Coordunique(liste_coord)

def recherche_crous(liste_ville):
    """Recherche la liste des crous proche à partir des coordonnées de la zone voulue"""

    with open(crousjson, "r") as f:
        datacrous = json.load(f)

    # A compléter avec la recherche de la position d'un crous
    liste_coord = []

    for feature in datacrous["features"]:
        coord = feature["geometry"]["coordinates"]
        code = feature["properties"]["code_commune"]
        for ville in liste_ville:
            if ville == code:
                    liste_coord.append(coord)
    
    del datacrous
    gc.collect()
    
    return Coordunique(liste_coord)


# RECHERCHE DE LIEUX VIA INTERNET

def Recherchemot(lon,lat,recherche,rayon):
    """Recherche la liste des lieux correspondants au mot utilisé"""
    sortie = []  # Liste pour stocker les résultats

    query = f"""
    [out:json];
    {recherche}(around:{rayon},{lat},{lon});
    out body;
    """

    url = "https://overpass-api.de/api/interpreter"
    response = requests.get(url, params={'data': query})

    if response.status_code == 200:
        data = response.json()

        for place in data.get('elements', []):
            sortie.append([place['lon'], place['lat']])  # Longitude avant latitude

    return sortie  # Retourne la liste des résultats

def recherche_parc(lon, lat, rayon):
    """Recherche la liste des parcs proche à partir des coordonnées de la zone voulue"""

    # A compléter avec la recherche de la position d'un parc
    liste_coord =  []
    liste_coord += Recherchemot(lon, lat, 'node["name"~"Parc",i]', rayon)
    liste_coord += Recherchemot(lon, lat, 'node["name"~"Jardin",i]', rayon)

    return Coordunique(liste_coord)

def recherche_pharmacie(lon, lat, rayon):
    """Recherche la liste des pharmacies proche à partir des coordonnées de la zone voulue"""
    # A compléter avec la recherche de la position d'une pharmacie
    liste_coord =  []
    liste_coord += Recherchemot(lon, lat, 'node["amenity"="pharmacy"]', rayon)
    liste_coord += Recherchemot(lon, lat, 'node["name"~"Pharmacie",i]', rayon)
    return Coordunique(liste_coord)

def recherche_boulangerie(lon, lat, rayon):
    """Recherche la liste des boulangerie proche à partir des coordonnées de la zone voulue"""

    # A compléter avec la recherche de la position d'une boulangerie
    liste_coord = []
    liste_coord += Recherchemot(lon, lat, 'node["shop"="bakery"]', rayon)
    liste_coord += Recherchemot(lon, lat, 'node["name"~"Boulangerie",i]', rayon)

    return Coordunique(liste_coord)

def recherche_medecin(lon, lat, rayon):
    """Recherche la liste des médecin proche à partir des coordonnées de la zone voulue"""

    # A compléter avec la recherche de la position d'un médecin
    liste_coord =  []
    liste_coord += Recherchemot(lon, lat, 'node["amenity"="doctors"]', rayon)
    liste_coord += Recherchemot(lon, lat, 'node["healthcare"="doctor"]', rayon)

    return Coordunique(liste_coord)

def recherche_supermarche(lon, lat, rayon):
    """Recherche la liste des supermarchés proche à partir des coordonnées de la zone voulue"""

    # A compléter avec la recherche de la position d'un supermarché
    liste_coord =  []
    liste_coord += Recherchemot(lon, lat, 'node["shop"="supermarket"]', rayon)
    liste_coord += Recherchemot(lon, lat, 'node["shop"="convenience"]', rayon)
    liste_coord += Recherchemot(lon, lat, 'node["name"~"Carrefour",i]', rayon)
    liste_coord += Recherchemot(lon, lat, 'node["name"~"Auchan",i]', rayon)
    liste_coord += Recherchemot(lon, lat, 'node["name"~"Leclerc",i]', rayon)
    liste_coord += Recherchemot(lon, lat, 'node["name"~"Casino",i]', rayon)
    liste_coord += Recherchemot(lon, lat, 'node["name"~"Lidl",i]', rayon)
    liste_coord += Recherchemot(lon, lat, 'node["name"~"Aldi",i]', rayon)

    return Coordunique(liste_coord)

def recherche_piscine(lon, lat, rayon):
    """Recherche la liste des piscine proche à partir des coordonnées de la zone voulue"""

    # A compléter avec la recherche de la position d'une piscine
    liste_coord =  []
    liste_coord += Recherchemot(lon, lat, 'node["sport"="swimming"]', rayon)
    liste_coord += Recherchemot(lon, lat, 'node["name"~"Piscine",i]', rayon)

    return Coordunique(liste_coord)

def recherche_sport(lon, lat, rayon):
    """Recherche la liste des salles de sports proche à partir des coordonnées de la zone voulue"""

    # A compléter avec la recherche de la position d'une salle de sport
    liste_coord =  []
    liste_coord += Recherchemot(lon, lat, 'node["leisure"="fitness_centre"]', rayon)
    liste_coord += Recherchemot(lon, lat, 'node["sport"="fitness"]', rayon)

    return Coordunique(liste_coord)

def recherche_cinema(lon, lat, rayon):
    """Recherche la liste des cinéma proche à partir des coordonnées de la zone voulue"""

    # A compléter avec la recherche de la position d'un cinéma
    liste_coord =  []
    liste_coord += Recherchemot(lon, lat, 'node["amenity"="cinema"]', rayon)
    liste_coord += Recherchemot(lon, lat, 'node["name"~"cinéma",i]', rayon)

    return Coordunique(liste_coord)


# RECHERCHE DE LIEUX VIA INTERNET & EN LOCAL

def recherche_metro(liste_ville_idf, liste_ville_hidf, lon, lat, rayon):
    """Recherche la liste des gares de métro et RER les plus proche à partir des coordonnées de la zone voulue"""
    
    with open(metroidfjson, "r") as f:
        datametroidf = json.load(f)

    # A compléter avec la recherche de la position d'une gare de métro
    liste_coord = []
    if len(liste_ville_idf) > 0:
        for feature in datametroidf["features"]:
            coord = feature["geometry"]["coordinates"]
            code = feature["properties"]["code_commune"]
            for ville in liste_ville_idf:
                if ville == code:
                    liste_coord.append(coord)
    
    del datametroidf
    gc.collect()
    if len(liste_ville_hidf) > 0:
        liste_coord += Recherchemot(lon,lat,'node["railway"="station"]["station"="subway"]',rayon)
        liste_coord += Recherchemot(lon,lat,'node["public_transport"="station"]["station"="subway"]',rayon)
        liste_coord += Recherchemot(lon,lat,'node["name"~"metro",i]',rayon)
    return Coordunique(liste_coord)

def recherche_bus(liste_ville_idf, liste_ville_hidf, lon, lat, rayon):
    """Recherche la liste des arrêt de bus proche à partir des coordonnées de la zone voulue"""

    with open(busidfjson, "r") as f:
        databusidf = json.load(f)

    # A compléter avec la recherche de la position d'un arrêt de bus
    liste_coord = []

    if len(liste_ville_idf) > 0:
        for feature in databusidf["features"]:
            coord = feature["geometry"]["coordinates"]
            code = feature["properties"]["code_insee"]
            for ville in liste_ville_idf:
                if ville == code:
                    liste_coord.append(coord)
    
    del databusidf
    gc.collect()
    
    if len(liste_ville_hidf) > 0:
        liste_coord += Recherchemot(lon, lat, 'node["highway"="bus_stop"]', rayon)
        liste_coord += Recherchemot(lon, lat, 'node["public_transport"="platform"]["bus"="yes"]', rayon)
        liste_coord += Recherchemot(lon, lat, 'node["name"~"bus",i]', rayon)

    return Coordunique(liste_coord)



# FONCTIONS POUR AVOIR LES SURFACES 2D A PARTIR D'UN POINT

def coord_surface(lon, lat, rayon):
    """Renvoie un contour de surface circulaire sous forme de Polygon autour d'un point donné"""
   
    R = 6371000     # Rayon moyen de la Terre en mètres
    coords = []     # Liste des coordonnées du contour 
    n = 32          # Nombre de points du contour de la surface

    for i in range(n):
        angle = 2 * math.pi * i / n  # Divise le cercle en n parts
        lat_offset = (rayon / R) * math.cos(angle)  # Déplacement en radians
        lon_offset = (rayon / (R * math.cos(math.radians(lat)))) * math.sin(angle)

        lat_cercle = lat + math.degrees(lat_offset)
        lon_cercle = lon + math.degrees(lon_offset)

        coords.append((lon_cercle, lat_cercle))  # Tuple pour compatibilité Shapely

    return Polygon(coords)

def liste_surface(liste_coord, rayon):
    """Renvoie la liste des surfaces à partir de la liste de coordonnées et du rayon"""

    liste = [] # Liste des surfaces des zones voulues

    for coord in liste_coord:
        lon, lat = coord[0], coord[1]
        liste.append(coord_surface(lon, lat , rayon))
    
    return liste
    # Renvoie une liste de liste contenant les différentes surfaces associé à chaque coordonnées et rayon

def intersection_zone(zone1, zone2):
    """Détermine la zone d'intersection entre deux zones."""
    # Vérifier si poly1 contient totalement poly2
    if zone1.contains(zone2):  
        return zone2

    # Vérifier si poly2 contient totalement poly1
    if zone2.contains(zone1):  
        return zone1

    # Calculer l'intersection
    intersection = zone1.intersection(zone2)
    
    if intersection.is_empty:
        return None

    # Retourner l'objet Shapely (Polygon ou MultiPolygon)
    if isinstance(intersection, (Polygon, MultiPolygon)):
        return intersection

    return None

def liste_intersection_zone(liste1,liste2):
    """Détermine l'ensemble des intersections entre deux zone"""

    liste_intersection = []

    for zone1 in liste1:
        for zone2 in liste2:
            liste_intersection.append(intersection_zone(zone1,zone2))
    
    return [zone for zone in liste_intersection if zone is not None]

def simplification_coord(liste_intersection):
    """Simplifie les intersections en supprimant les superpositions et en fusionnant les zones adjacentes."""
    polygones = []

    for zone in liste_intersection:
        if isinstance(zone, Polygon):
            polygones.append(zone)

        elif isinstance(zone, MultiPolygon):
            polygones.extend(zone.geoms)

    # Fusionne les polygones qui se touchent ou se chevauchent
    union_polygones = unary_union(polygones)

    # On renvoie une liste de Polygon, même si un seul
    if isinstance(union_polygones, Polygon):
        return [union_polygones]
    elif isinstance(union_polygones, MultiPolygon):
        return list(union_polygones.geoms)

    return []

# FONCTIONS POUR RECHERCHER UNE VILLE A PARTIR DES COORDONNEES

def recherche_region(lon, lat):
    """Renvoie le numéro de la région associé aux coordonnées"""
    
    point = Point(lon, lat)  # Création du point

    for feature in dataregions["features"]:
        geom = shape(feature["geometry"])  # Convertir en objet Shapely (Polygon ou MultiPolygon)

        if geom.contains(point):  # Vérifier si le point est contenu
            return feature['properties']['code']

    return None

def recherche_departement(lon, lat, num):
    """Renvoie le numéro du département associé aux coordonnées"""
    
    if num == None:
        return None

    departementjson = departementjson1 + str(num) + departementjson2
    with open(departementjson, "r") as f:
        datadepartement = json.load(f)

    point = Point(lon, lat)  # Création du point

    for feature in datadepartement["features"]:
        geom = shape(feature["geometry"])  # Convertir en Polygon ou MultiPolygon

        if geom.contains(point):  # Vérifier si le point est contenu dans la zone
            return feature['properties']['code']

    return None  # Valeur par défaut si aucun département trouvé

def recherche_ville(lon, lat, num):
    """Renvoie le code commune INSEE de la ville associée aux coordonnées"""

    if num == None:
        return None, None, None

    villejson = villejson1 + str(num) + villejson2

    with open(villejson, "r") as f:
        datavilles = json.load(f)

    point = Point(lon, lat)  # Création du point

    for feature in datavilles["features"]:
        geom = shape(feature["geometry"])  # Convertir en Polygon ou MultiPolygon

        if geom.contains(point):
            return feature['properties']['code'], geom, feature['properties']['nom']
        
    return None, None, None
    
def recherche_liste_ville(lon,lat):
    region = recherche_region(lon,lat)
    departement = recherche_departement(lon,lat,region)
    code, coord, nom = recherche_ville(lon,lat,departement)
    liste_ville = [code]
    liste_coord = [coord]
    liste_nom = [nom]
    centroid = coord.centroid
    coordcontour = scale(coord, xfact=1.05, yfact=1.05, origin=centroid)

    # Extraire les points du contour extérieur
    if isinstance(coordcontour, Polygon):
        points = list(coordcontour.exterior.coords)
    elif isinstance(coordcontour, MultiPolygon):
        # On peut aussi ne prendre que le plus grand polygone si besoin
        points = []
        for poly in coordcontour.geoms:
            points.extend(poly.exterior.coords)
    else:
        return [], [], []

    # Boucle de recherche des villes via les points
    for lon, lat in points:
        region2 = recherche_region(lon, lat)
        departement2 = recherche_departement(lon, lat, region2)
        code2, coord2, nom2 = recherche_ville(lon, lat, departement2)
        if code2 != None:
            if code2 not in liste_ville and len(code2) > 1:
                liste_ville.append(code2)
                liste_coord.append(coord2)
                liste_nom.append(nom2)

    return liste_ville, liste_coord, liste_nom

def shapely_vers_liste(zone):
    """
    Transforme une liste de Polygons/MultiPolygons Shapely 
    en une liste de listes de coordonnées [ [lon, lat], ... ]
    """
    liste_coord = []

    if isinstance(zone, Polygon):
        coords = list(zone.exterior.coords)[:-1]  # Retirer le point de fermeture si nécessaire
        liste_coord.append([[lon, lat] for lon, lat in coords])

    elif isinstance(zone, MultiPolygon):
        for sub_poly in zone.geoms:
            coords = list(sub_poly.exterior.coords)[:-1]
            liste_coord.append([[lon, lat] for lon, lat in coords])

    return liste_coord

# PRIX ET COULEUR

def recherche_prix(liste_code):
    """Renvoie le prix moyen associé au code communale de la ville"""
    
    liste_prix = []

    for code in liste_code:
        test = True
        for feature in datacommunes["features"]:
            if feature['properties']['code'] == code:
                liste_prix.append(feature['properties']['prixm2'])
                test = False
        if test:
            liste_prix.append(-1)

    return liste_prix

def prix_couleur(prix):
    """Renvoie la couleure associé au prix"""
    if prix == -1:
        return "#1F1F1F"
    if prix >= 0 and prix <= 1000:
        return "#030565"
    elif prix > 1000 and prix <= 1250:
        return "#1135F8"
    elif prix > 1250 and prix <= 1600:
        return "#12C8EF"
    elif prix > 1600 and prix <= 2500:
        return "#22C219"
    elif prix > 2500 and prix <= 4000:
        return "#E0D618"
    elif prix > 4000 and prix <= 6500:
        return "#F55906"
    elif prix > 6500 and prix <= 10000:
        return "#A90101"
    elif prix > 10000:
        return "#4E0000"
    

# RECHERCHE FINALE
import time
def recherche_globale(lon, lat, distance_sncf=0, distance_metro=0, distance_ecole=0,
                                distance_universite=0, distance_crous=0, distance_parc=0,
                                distance_pharmacie=0, distance_boulangerie=0, distance_medecin=0,
                                distance_bus=0, distance_supermarche=0, distance_piscine=0,
                                distance_sport=0, distance_cinema=0):
    """Fonction finale"""
    liste_ville, liste_coord_ville, liste_nom_ville = recherche_liste_ville(lon, lat) # Recherche les villes à partir de l'entrée utilisateur
    liste_ville_idf, liste_ville_hidf = [], [] # Sépare la liste des ville en 2
    for ville in liste_ville:
        if testidf(ville):
            liste_ville_idf.append(ville) # Liste des villes en Ile de France
        else:
            liste_ville_hidf.append(ville) # Liste des villes hors Ile de France
    liste_coord_sortie = liste_coord_ville

    Rayon = Rayonrecherche(lon,lat, liste_coord_ville)
    if distance_sncf > 0:
        liste_sncf = recherche_sncf(liste_ville)
        if len(liste_sncf) > 0:
            liste_surface_sncf = liste_surface(liste_sncf,distance_sncf)
            liste_coord_sortie = liste_intersection_zone(liste_surface_sncf, liste_coord_sortie)
            liste_coord_sortie = simplification_coord(liste_coord_sortie)

    if distance_metro > 0:
        liste_metro = recherche_metro(liste_ville_idf, liste_ville_hidf, lon, lat, Rayon)
        if len(liste_metro) > 0:
            liste_surface_metro = liste_surface(liste_metro,distance_metro)
            liste_coord_sortie = liste_intersection_zone(liste_surface_metro, liste_coord_sortie)
            liste_coord_sortie = simplification_coord(liste_coord_sortie)   

    if distance_ecole != 0:
        liste_ecole = recherche_ecole(liste_ville)
        if len(liste_ecole) > 0:
            liste_surface_ecole = liste_surface(liste_ecole,distance_ecole)
            liste_coord_sortie = liste_intersection_zone(liste_surface_ecole, liste_coord_sortie)
            liste_coord_sortie = simplification_coord(liste_coord_sortie)

    if len(liste_coord_sortie) == 0:
        return []       # Pas de résultat renvoie une liste nulle et ne calcul pas les autres critères

    if distance_universite > 0:
        liste_universite = recherche_universite(liste_ville)
        if len(liste_universite) > 0:
            liste_surface_universite = liste_surface(liste_universite,distance_universite)
            liste_coord_sortie = liste_intersection_zone(liste_surface_universite, liste_coord_sortie)
            liste_coord_sortie = simplification_coord(liste_coord_sortie)

    if distance_crous > 0:
        liste_crous = recherche_crous(liste_ville)
        if len(liste_crous) > 0:
            liste_surface_crous = liste_surface(liste_crous,distance_crous)
            liste_coord_sortie = liste_intersection_zone(liste_surface_crous, liste_coord_sortie)
            liste_coord_sortie = simplification_coord(liste_coord_sortie)

    if distance_parc > 0:
        liste_parc = recherche_parc(lon, lat, Rayon)
        if len(liste_parc) > 0:
            liste_surface_parc = liste_surface(liste_parc,distance_parc)
            liste_coord_sortie = liste_intersection_zone(liste_surface_parc, liste_coord_sortie)
            liste_coord_sortie = simplification_coord(liste_coord_sortie)

    if len(liste_coord_sortie) == 0:
        return []       # Pas de résultat renvoie une liste nulle et ne calcul pas les autres critères

    if distance_pharmacie > 0:
        liste_pharmacie = recherche_pharmacie(lon, lat, Rayon)
        if len(liste_pharmacie) > 0:
            liste_surface_pharmacie = liste_surface(liste_pharmacie,distance_pharmacie)
            liste_coord_sortie = liste_intersection_zone(liste_surface_pharmacie, liste_coord_sortie)
            liste_coord_sortie = simplification_coord(liste_coord_sortie)

    if distance_boulangerie > 0:
        liste_boulangerie = recherche_boulangerie(lon, lat, Rayon)
        if len(liste_boulangerie) > 0:
            liste_surface_boulangerie = liste_surface(liste_boulangerie,distance_boulangerie)
            liste_coord_sortie = liste_intersection_zone(liste_surface_boulangerie, liste_coord_sortie)
            liste_coord_sortie = simplification_coord(liste_coord_sortie)

    if distance_medecin > 0:
        liste_medecin = recherche_medecin(lon, lat, Rayon)
        if len(liste_medecin) > 0:
            liste_surface_medecin = liste_surface(liste_medecin,distance_medecin)
            liste_coord_sortie = liste_intersection_zone(liste_surface_medecin, liste_coord_sortie)
            liste_coord_sortie = simplification_coord(liste_coord_sortie)
    
    if len(liste_coord_sortie) == 0:
        return []       # Pas de résultat renvoie une liste nulle et ne calcul pas les autres critères

    if distance_bus > 0:
        liste_bus = recherche_bus(liste_ville_idf, liste_ville_hidf, lon, lat, Rayon)
        if len(liste_bus) > 0:
            liste_surface_bus = liste_surface(liste_bus,distance_bus)
            liste_coord_sortie = liste_intersection_zone(liste_surface_bus, liste_coord_sortie)
            liste_coord_sortie = simplification_coord(liste_coord_sortie)
    
    if distance_supermarche > 0:
        liste_supermarche = recherche_supermarche(lon, lat, Rayon)
        if len(liste_supermarche) > 0:
            liste_surface_supermarche = liste_surface(liste_supermarche,distance_supermarche)
            liste_coord_sortie = liste_intersection_zone(liste_surface_supermarche, liste_coord_sortie)
            liste_coord_sortie = simplification_coord(liste_coord_sortie)
   
    if distance_piscine > 0:
        liste_piscine = recherche_piscine(lon, lat, Rayon)
        if len(liste_piscine) > 0:
            liste_surface_piscine = liste_surface(liste_piscine,distance_piscine)
            liste_coord_sortie = liste_intersection_zone(liste_surface_piscine, liste_coord_sortie)
            liste_coord_sortie = simplification_coord(liste_coord_sortie)

    if len(liste_coord_sortie) == 0:
        return []       # Pas de résultat renvoie une liste nulle et ne calcul pas les autres critères

    if distance_sport > 0:
        liste_sport = recherche_sport(lon, lat, Rayon)
        if len(liste_sport) > 0:
            liste_surface_sport = liste_surface(liste_sport,distance_sport)
            liste_coord_sortie = liste_intersection_zone(liste_surface_sport, liste_coord_sortie)
            liste_coord_sortie = simplification_coord(liste_coord_sortie)
    
    if distance_cinema > 0:
        liste_cinema = recherche_cinema(lon, lat, Rayon)
        if len(liste_cinema) > 0:
            liste_surface_cinema = liste_surface(liste_cinema,distance_cinema)
            liste_coord_sortie = liste_intersection_zone(liste_surface_cinema, liste_coord_sortie)
            liste_coord_sortie = simplification_coord(liste_coord_sortie)

    liste_coord_sortie = liste_intersection_zone(liste_coord_ville, liste_coord_sortie)

    liste_finale = []
    
    liste_sortie = []

    for zone_shape in liste_coord_sortie:
        liste_sortie.extend( shapely_vers_liste(zone_shape) )

    liste_prix = recherche_prix(liste_ville)

    for zone in liste_sortie:
        lon_moyenne = sum(coord[0] for coord in zone) / len(zone)
        lat_moyenne = sum(coord[1] for coord in zone) / len(zone)
        prix = -1
        for i in range(len(liste_ville)):
            if liste_coord_ville[i].covers(Point(lon_moyenne, lat_moyenne)):
                prix = liste_prix[i]
                nom_ville = liste_nom_ville[i]
        liste_finale.append( [prix_couleur(prix), zone, prix, nom_ville] )

    return liste_finale # Renvoie la liste voulue

#print( recherche_globale(2.0608,49.0354,distance_sncf=2000,distance_universite=2000,distance_crous=2000,distance_bus=2000,distance_ecole=2000,distance_metro=2000, distance_boulangerie=2000, distance_cinema=2000, distance_medecin=2000, distance_sport=2000, distance_piscine=2000, distance_pharmacie=2000) )

import folium

#Centre de la carte (exemple : Paris)
centre_carte = [lat, lon]

# Création de la carte Folium
m = folium.Map(location=centre_carte, zoom_start=13)

polygones = recherche_globale(lon, lat, distance_sncf, distance_metro, distance_ecole,
                                distance_universite, distance_crous, distance_parc,
                                distance_pharmacie, distance_boulangerie, distance_medecin,
                                distance_bus, distance_supermarche, distance_piscine,
                                distance_sport, distance_cinema)

for couleur, points, prix, nom in polygones:
    # Conversion des coordonnées en format Leaflet (latitude, longitude)
    coords = [[lat, lon] for lon, lat in points]
    
    if prix == -1:
        prix = "Ø"

    # Ajouter le polygone sur la carte
    folium.Polygon(
        locations=coords, 
        color=couleur, 
        fill=True, 
        fill_color=couleur, 
        fill_opacity=0.6,
        opacity=1.0,
        weight=5,
        popup=folium.Popup(f"{nom} : {prix} €/m²", max_width=200)
    ).add_to(m)

# Afficher la carte
m

m.save("./carte.html")

import webbrowser
import os

webbrowser.open('file://' + os.path.realpath("./carte.html"))
