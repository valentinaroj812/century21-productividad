import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import io

# --- SCRAPING DE OFICINAS ---
@st.cache_data
def obtener_mapeo():
    urls = [
        "https://c21.com.bo/inmobiliaria/59-century-21-grand-sky-achumani-la-paz-bolivia",
        "https://c21.com.bo/inmobiliaria/58-century-21-realtor-achumani-la-paz-bolivia",
        "https://c21.com.bo/inmobiliaria/43-century-21-imperial-agua-de-castilla-potosi-bolivia",
        "https://c21.com.bo/inmobiliaria/82-century-21-boulevard-centro-cochabamba-bolivia",
        "https://c21.com.bo/inmobiliaria/54-century-21-central-top-centro-cochabamba-bolivia",
        # Puedes seguir agregando más URLs si lo deseas
    ]
    mapping = {}
    for url in urls:
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")
            oficina = soup.find("h3").text.strip()
            asesores = soup.select("div.agent-info h5")
            for a in asesores:
                mapping[a.text.strip()] = oficina
        except Exception as e:
            st.error(f"Error con {url}: {e}")
    return mapping

# --- INTERFAZ ---
st.title("🏢 Análisis de Productividad de Oficinas CENTURY 21")

archivo = st.file_uploader("Sube el archivo Excel generado por 21 Online", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo, skiprows=1)
    mapping = obtener_mapeo()

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

    resultado = (
        df.groupby("Oficina")
        .agg(Ventas=("Precio de Cierre", "count"),
             Total=("Precio de Cierre", "sum"))
        .sort_values("Total", ascending=False)
    )

    st.subheader("🏆 Ranking por Oficina")
    st.dataframe(resultado)

    # Descargar resultado
    buffer = io.BytesIO()
    resultado.to_excel(buffer, index=True)
    buffer.seek(0)
    st.download_button("📥 Descargar Excel", buffer, "productividad_oficinas.xlsx")
