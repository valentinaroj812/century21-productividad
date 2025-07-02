import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io

# --- SCRAPING DE OFICINAS ---
@st.cache_data
def obtener_mapeo():
    urls = [
        "https://c21.com.bo/inmobiliaria/59-century-21-grand-sky-achumani-la-paz-bolivia",
        "https://c21.com.bo/inmobiliaria/58-century-21-realtor-achumani-la-paz-bolivia",
        "https://c21.com.bo/inmobiliaria/43-century-21-imperial-agua-de-castilla-potosi-bolivia",
        "https://c21.com.bo/inmobiliaria/82-century-21-boulevard-centro-cochabamba-bolivia",
        "https://c21.com.bo/inmobiliaria/54-century-21-central-top-centro-cochabamba-bolivia"
    ]
    mapping = {}
    for url in urls:
        try:
            st.info(f"Procesando: {url}")
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")
            oficina = soup.find("h3").text.strip()
            asesores = soup.select("div.agent-info h5")
            for a in asesores:
                mapping[a.text.strip()] = oficina
        except Exception as e:
            st.error(f"❌ Error con {url}: {e}")
    return mapping

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Análisis CENTURY 21", layout="centered")
st.title("🏢 Análisis de Productividad de Oficinas CENTURY 21")
st.markdown("Sube un archivo de Excel exportado de 21 Online para calcular qué oficina ha sido más productiva.")

archivo = st.file_uploader("📤 Subir archivo Excel (.xlsx)", type=["xlsx"])

if archivo:
    try:
        df = pd.read_excel(archivo, skiprows=1)
        st.success("✅ Excel cargado correctamente.")
        with st.spinner("🔍 Cargando asesores desde las oficinas..."):
            mapping = obtener_mapeo()
        st.success("✅ Mapeo de asesores completado.")

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

        buffer = io.BytesIO()
        resultado.to_excel(buffer, index=True)
        buffer.seek(0)
        st.download_button("📥 Descargar Excel de Resultados", buffer, "productividad_oficinas.xlsx")

        st.success("✅ Análisis completado con éxito.")

    except Exception as e:
        st.error(f"⚠️ Error procesando el archivo: {e}")
else:
    st.info("Por favor, sube un archivo Excel para comenzar el análisis.")
