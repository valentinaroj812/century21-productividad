import pandas as pd
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import process

# --- CONFIGURACIÓN ---
EXCEL_PATH = "21 Online (23).xlsx"
LINKS_PATH = "all_office_links.txt"
OUTPUT_PATH = "equivalencias_nombres_sugeridas.csv"

# --- 1. Cargar nombres del Excel ---
df = pd.read_excel(EXCEL_PATH, skiprows=1)
captadores = df["Asesor Captador"].dropna().astype(str).str.strip()
colocadores = df["Asesor Colocador"].dropna().astype(str).str.strip()
nombres_excel = pd.Series(pd.concat([captadores, colocadores]).unique())

# --- 2. Scraping de asesores desde los sitios web ---
def obtener_asesores_de_web(links):
    asesores_web = set()
    for url in links:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.content, "html.parser")
            asesores = soup.select("div.agent-info h5")
            for a in asesores:
                nombre = a.text.strip()
                if nombre:
                    asesores_web.add(nombre)
        except Exception as e:
            print(f"Error en {url}: {e}")
    return list(asesores_web)

with open(LINKS_PATH, encoding="utf-8") as f:
    links = [line.strip() for line in f if line.strip()]

nombres_web = obtener_asesores_de_web(links)

# --- 3. Fuzzy Matching ---
sugerencias = []
for nombre_excel in nombres_excel:
    match, score = process.extractOne(nombre_excel, nombres_web)
    sugerencias.append([nombre_excel, match if score >= 80 else ""])

# --- 4. Guardar archivo CSV ---
df_sugerencias = pd.DataFrame(sugerencias, columns=["Nombre en Excel", "Nombre en Web"])
df_sugerencias.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print(f"✅ Archivo generado: {OUTPUT_PATH}")
