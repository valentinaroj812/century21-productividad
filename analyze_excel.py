import pandas as pd
import json

# Carga el archivo Excel (ajusta nombre si es necesario)
df = pd.read_excel("21 Online (23).xlsx", skiprows=1)

# Carga el mapeo de asesores a oficinas
with open("asesor_oficina.json", encoding="utf-8") as f:
    mapping = json.load(f)

# Normaliza nombres y oficinas
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

# Mapea oficinas
df["Oficina Captador"] = df["Asesor Captador"].map(mapping)
df["Oficina Colocador"] = df["Asesor Colocador"].map(mapping)
df["Oficina"] = df["Oficina Captador"].fillna(df["Oficina Colocador"])

# Agrupa por oficina
agg = (
    df.groupby("Oficina")
    .agg(Ventas=("Precio de Cierre", "count"),
         Total=("Precio de Cierre", "sum"))
    .sort_values("Total", ascending=False)
)

agg.to_excel("productividad_oficinas.xlsx")
print(agg)
