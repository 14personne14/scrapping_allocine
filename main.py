import requests
from bs4 import BeautifulSoup
import re

url = str(input("🔶 Enter the Allociné URL of the film or series: \n"))

response = requests.get(url)

if response.status_code == 200:

    soup = BeautifulSoup(response.content, "html.parser")

    film = soup.find("div", class_="meta-body")
    film_title = soup.find("div", class_="titlebar-title")

    # ! CASE 1 : Année, Durée, Genre, Type

    infos = [child for child in film.children if child.name][0].text.split()

    # * Genre
    genre = []
    i = 0
    for element in infos:
        if element == "|":
            i += 1
        elif i > 1:
            genre.append(element)

    # * Type
    categorie = "Inconnu"
    if "film" in url:
        categorie = "Film"
    elif "serie" in url and "Animation" in genre:
        categorie = "Animé"
    elif "serie" in url:
        categorie = "Série"

    if "Animation" in genre:
        genre.remove("Animation")

    #* Date
    date = [element for element in infos if re.search(r'\d{4}', element)]

    #* Duration
    duration = [element for element in infos if re.search(r'\d+[h|min]', element)]
    if len(duration) == 0:
        duration_in_minutes = 0
        i = 0
        for element in infos:
            if element == "|":
                i += 1
            elif 0 < i < 2 and element != "|":
                duration.append(element)
        duration_in_minutes = int(duration[0])
    else:
        duration_in_minutes = int(duration[0].replace('h', '')) * 60 + int(duration[1].replace('min', ''))

    # ! CASE 2 : Realisateur

    infos = [child for child in film.children if child.name][1].text.split()

    # * Réalisateur
    if categorie == "Film":
        realisateur = infos[1:]
    else:
        realisateur = infos[2:]

    # ! CASE 3 & 4 : IGNORE

    # infos = [child for child in film.children if child.name][2].text.split()
    # infos = [child for child in film.children if child.name][3].text.split()

    # ! CASE 5 : Acteurs

    if categorie == "Film":
        infos = [child for child in film.children if child.name][4].text.split(',')
    else:
        infos = [child for child in film.children if child.name][2].text.split(',')

    # * Acteurs
    acteurs = [info.replace('\n', '').replace('Avec', '') for info in infos]

    # ! CASE 6 : Synopsis

    synopsis = soup.find("section", id="synopsis-details").find("div", class_="content-txt")
    synopsis = [child.text.strip() for child in synopsis.children if child.name]
    synopsis_text = "\n".join(synopsis)

    # ! CASE 7 : Photos

    if categorie == "Film":
        url_photo = url.replace("fichefilm_gen_cfilm=", "fichefilm-").replace(".html", "") + "/photos/"
    else:
        url_photo = url.replace("ficheserie_gen_cserie=", "ficheserie-").replace(".html", "") + "/photos/"
    response_photo = requests.get(url_photo)

    photos_ids = []
    photos_url = []
    if response_photo.status_code == 200:
        soup_photo = BeautifulSoup(response_photo.content, "html.parser")
        if categorie == "Film":
            photos = soup_photo.find("section", class_="section-movie-photo").find_all("a")
        else:
            photos = list(soup_photo.find_all("section", class_="section-season-photo"))[-1].find_all("a")

        for photo in photos:
            photos_ids.append(re.sub(r'.*=(\d+)', r'\1', photo.get('href')))

    if len(photos_ids) > 0:
        for photo_id in photos_ids:
            url_photo_detail = url_photo + "detail/?cmediafile=" + photo_id
            response_photo_detail = requests.get(url_photo_detail)

            if response_photo_detail.status_code == 200:
                soup_photo_detail = BeautifulSoup(response_photo_detail.content, "html.parser")
                photos_src = soup_photo_detail.find_all("img", class_="photo")
                photos_url.append(photos_src[0].get('src'))

    if len(photos_url) == 0:
        photos_url = ["Inconnu"]

    # ! PRINT
    #     print(f"""
    # ----------------------------
    # | Titre:       {film_title.text}
    # |
    # | Lien:        ###
    # | Synopsis:    {len(' '.join(synopsis))} caractères
    # | Réalisateur: {' '.join(realisateur)}
    # | Casting:     {', '.join(acteurs)}
    # | Année:       {date[0]}
    # | Durée (min): {duration_in_minutes}
    # | Type:        {type}
    # | Genre:       {' '.join(genre)}
    # |
    # | Photos:     ({len(photos_url)})""")
    #     for photo in photos_url:
    #         print(f"| 🔵 ###")
    #     print("----------------------------")
    print("✔ file generated successfully!")

    # ! WRITE
    with open('resultat.txt', 'w', encoding='utf-8') as file:
        file.write(f"""----------------------------
| Titre:       {film_title.text}
|
| Lien:        {url}
| Synopsis:    {len(' '.join(synopsis))} caractères
\"\"\"
{synopsis_text}
\"\"\"
| Réalisateur: {' '.join(realisateur)}
| Casting:     {', '.join(acteurs)}
| Année:       {date[0]}
| Durée (min): {duration_in_minutes} 
| Type:        {categorie}
| Genre:       {' '.join(genre)}
|
| Photos:     ({len(photos_url)})""")
        for photo in photos_url:
            file.write(f"\n| 🔵 {photo}")
        file.write("\n----------------------------")

else:
    print("The request failed.")
