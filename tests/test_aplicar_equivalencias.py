import pandas as pd
from io import StringIO
from app import aplicar_equivalencias

def test_aplicar_equivalencias_replaces_names():
    df = pd.DataFrame({
        "Asesor Captador": ["Juan Perez", "Ana Gomez"],
        "Asesor Colocador": ["Pedro Lopez", "Juan Perez"],
    })

    csv_data = StringIO("original,replacement\nJuan Perez,JP\nPedro Lopez,PL\n")
    result = aplicar_equivalencias(df.copy(), csv_data)

    assert result["Asesor Captador"].tolist() == ["JP", "Ana Gomez"]
    assert result["Asesor Colocador"].tolist() == ["PL", "JP"]
