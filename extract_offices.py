import requests
from bs4 import BeautifulSoup
import json

OFFICE_URLS = [
    "https://c21.com.bo/inmobiliaria/59-century-21-grand-sky-achumani-la-paz-bolivia",
    "https://c21.com.bo/inmobiliaria/58-century-21-realtor-achumani-la-paz-bolivia",
    "https://c21.com.bo/inmobiliaria/43-century-21-imperial-agua-de-castilla-potosi-bolivia",
    # Agrega todos los enlaces restantes aquí
]

def extract_office(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    try:
        office_name = soup.find("h3").text.strip()
        members = soup.select("div.agent-info h5")
        names = [m.text.strip() for m in members]
        return office_name, names
    except Exception as e:
        print(f"Error en {url}: {e}")
        return None, []

def build_mapping():
    mapping = {}
    for url in OFFICE_URLS:
        office, names = extract_office(url)
        for n in names:
            mapping[n] = office
    return mapping

if __name__ == "__main__":
    mapping = build_mapping()
    with open("asesor_oficina.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
