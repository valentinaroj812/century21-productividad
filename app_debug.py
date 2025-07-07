import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io

st.set_page_config(page_title="Productividad Oficinas", layout="wide")
st.title("🏢 Análisis de Productividad de Oficinas CENTURY 21")

# --- FUNCIONES ---
@st.cache_data(show_spinner=False)
def obtener_mapeo():
    mapping = {}
    try:
        with open("all_office_links.txt", "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'all_office_links.txt'.")
        return mapping

    for url in urls:
        st.write(f"🔎 Procesando: [{url}]({url})")
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")
            oficina = soup.find("h3").text.strip()
            asesores = soup.select("div.agent-info h5")
            for a in asesores:
                nombre = a.text.strip()
                if nombre:
                    mapping[nombre] = oficina
        except Exception as e:
            st.warning(f"⚠️ Error al procesar {url}: {e}")
    return mapping

def analizar_excel(df, mapping):
    df["Asesor Captador"] = df["Asesor Captador"].astype(str).str.strip()
    df["Asesor Colocador"] = df["Asesor Colocador"].astype(str).str.strip()
    df["Precio de Cierre"] = (
        pd.to_numeric(
            df["Precio Cierre"]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip(),
            errors="coerce",
        )
        .fillna(0.0)
    )

    df["Oficina Captador"] = df["Asesor Captador"].map(mapping)
    df["Oficina Colocador"] = df["Asesor Colocador"].map(mapping)
    df["Oficina"] = df["Oficina Captador"].fillna(df["Oficina Colocador"])

    return df

# --- UI ---
archivo = st.file_uploader("📤 Sube el archivo Excel generado por 21 Online", type=["xlsx"])

if archivo:
    try:
        with st.spinner("⏳ Cargando archivo..."):
            df = pd.read_excel(archivo, skiprows=1)
        st.success("✅ Archivo cargado correctamente.")
        st.write("Vista previa de los datos:")
        st.dataframe(df.head())

        with st.spinner("🔍 Obteniendo asesores desde las oficinas..."):
            mapping = obtener_mapeo()

        st.success(f"✅ {len(mapping)} asesores cargados desde la web.")

        with st.spinner("📊 Procesando datos..."):
            df = analizar_excel(df, mapping)

        st.info(f"📌 Total de propiedades en el archivo: {len(df)}")
        asignadas = df["Oficina"].notna().sum()
        no_asignadas = len(df) - asignadas
        st.info(f"🏢 Propiedades con oficina asignada: {asignadas}")
        st.warning(f"❌ Propiedades sin oficina asignada: {no_asignadas}")

        if no_asignadas > 0:
            st.subheader("❗ Propiedades sin oficina asignada")
            st.dataframe(df[df["Oficina"].isna()][["Asesor Captador", "Asesor Colocador", "Precio de Cierre"]])

        resultado = (
            df[df["Oficina"].notna()]
            .groupby("Oficina")
            .agg(Ventas=("Precio de Cierre", "count"),
                 Total=("Precio de Cierre", "sum"))
            .sort_values("Total", ascending=False)
        )

        st.subheader("🏆 Ranking por Oficina")
        st.dataframe(resultado)

        buffer = io.BytesIO()
        resultado.to_excel(buffer, index=True)
        buffer.seek(0)
        st.download_button("📥 Descargar Excel", buffer, "productividad_oficinas.xlsx")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo Excel (.xlsx) para comenzar.")
