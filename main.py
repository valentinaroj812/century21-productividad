import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os

# ---------- PARTE 1: SCRAPING ----------

OFFICE_URLS = [
    "https://c21.com.bo/inmobiliaria/59-century-21-grand-sky-achumani-la-paz-bolivia",
    "https://c21.com.bo/inmobiliaria/58-century-21-realtor-achumani-la-paz-bolivia",
    "https://c21.com.bo/inmobiliaria/43-century-21-imperial-agua-de-castilla-potosi-bolivia",
    # Puedes agregar todos los links aquí
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

# ---------- PARTE 2: ANÁLISIS ----------

def analyze_excel(mapping):
    file_name = "21 Online (23).xlsx"
    if not os.path.exists(file_name):
        print(f"No se encontró el archivo '{file_name}' en el directorio actual.")
        return

    df = pd.read_excel(file_name, skiprows=1)

    df["Asesor Captador"] = df["Asesor Captador"].astype(str).str.strip()
    df["Asesor Colocador"] = df["Asesor Colocador"].astype(str).str.strip()
    df["Precio de Cierre"] = (
        df["Precio Cierre"]
        .astype(str)
        .str.replace("$", "")
        .str.replace(",", "")
        .str.strip()
        .replace("", "0")
        .astype(float)
    )

    df["Oficina Captador"] = df["Asesor Captador"].map(mapping)
    df["Oficina Colocador"] = df["Asesor Colocador"].map(mapping)
    df["Oficina"] = df["Oficina Captador"].fillna(df["Oficina Colocador"])

    agg = (
        df.groupby("Oficina")
        .agg(Ventas=("Precio de Cierre", "count"),
             Total=("Precio de Cierre", "sum"))
        .sort_values("Total", ascending=False)
    )

    agg.to_excel("productividad_oficinas.xlsx")
    print("Archivo generado: productividad_oficinas.xlsx")
    print(agg)

# ---------- MAIN ----------

if __name__ == "__main__":
    print("Extrayendo asesores desde los sitios web...")
    mapping = build_mapping()
    print("Analizando archivo Excel...")
    analyze_excel(mapping)
