
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import json
import unicodedata
import geopandas as gpd

# 1. Configuracion de la pagina
st.set_page_config(
    page_title="Crecimiento regional del Peru",
    layout="wide"
)

# 2. Carga de datos
RUTA = Path(__file__).resolve().parent / "datos" / "dataset.csv"

@st.cache_data
def cargar_datos():
    datos = pd.read_csv(RUTA, dtype={"ubigeo": str})
    datos["ubigeo"] = datos["ubigeo"].str.zfill(2)
    datos["anio"] = datos["anio"].astype(int)
    return datos

df = cargar_datos()

st.title("Crecimiento economico y mineria en el Peru")
st.caption("Analisis departamental, 2007-2019 | Fuente: INEI")

# 3. Filtros
st.sidebar.header("Filtros")

anio = st.sidebar.selectbox(
    "Selecciona un año",
    options=sorted(df["anio"].unique()),
    index=len(df["anio"].unique()) - 1
)

regiones = st.sidebar.multiselect(
    "Region natural",
    options=sorted(df["region_natural"].unique()),
    default=sorted(df["region_natural"].unique())
)

filtrado = df[df["region_natural"].isin(regiones)].copy()

if filtrado.empty:
    st.warning("Selecciona al menos una region natural.")
    st.stop()

# 4. Comparacion contra 2007
base = filtrado[filtrado["anio"] == 2007][
    ["ubigeo", "vab_pc"]
].rename(columns={"vab_pc": "vab_pc_2007"})

actual = filtrado[filtrado["anio"] == anio].merge(
    base, on="ubigeo", validate="one_to_one"
)

actual["crecimiento_pct"] = (
    (actual["vab_pc"] / actual["vab_pc_2007"] - 1) * 100
)

# 5. Indicadores
vab_agregado = (
    (actual["vab_pc"] * actual["poblacion"]).sum()
    / actual["poblacion"].sum()
)

c1, c2, c3 = st.columns(3)

c1.metric("Departamentos", actual["ubigeo"].nunique())
c2.metric(
    f"Crecimiento mediano desde 2007",
    f"{actual['crecimiento_pct'].median():+.1f}%"
)
c3.metric(
    "VAB real por habitante agregado",
    f"S/ {vab_agregado:,.0f}"
)

# 6. Visualizacion
st.subheader("Crecimiento por departamento")

ordenado = actual.sort_values("crecimiento_pct")
mayor = ordenado.iloc[-1]["departamento"].title()

fig = px.bar(
    ordenado,
    x="crecimiento_pct",
    y="departamento",
    color="region_natural",
    orientation="h",
    title=f"{mayor} lidera el crecimiento en la seleccion",
    labels={
        "crecimiento_pct": "Crecimiento acumulado desde 2007 (%)",
        "departamento": "Departamento",
        "region_natural": "Region natural"
    }
)

fig.update_layout(
    height=max(480, len(actual) * 27 + 150)
)

st.plotly_chart(fig, width="stretch")

# 7. Tabla
st.subheader("Datos departamentales")

st.dataframe(
    actual[
        ["departamento", "anio", "vab_pc",
         "peso_mineria_pct", "crecimiento_pct"]
    ],
    hide_index=True,
    width="stretch"
)

st.caption(
    "El VAB mide produccion economica territorial. "
    "Las comparaciones son descriptivas."
)


# --------------------------------------------------
# ANALISIS DE MINERIA Y CRECIMIENTO ECONOMICO
# --------------------------------------------------

st.divider()
st.subheader("Mineria y crecimiento economico")

st.write(
    "¿Los departamentos con mayor participacion minera "
    "registraron tambien un mayor crecimiento economico?"
)

fig_disp = px.scatter(
    actual,
    x="peso_mineria_pct",
    y="crecimiento_pct",
    color="region_natural",
    hover_name="departamento",
    hover_data={
        "poblacion": ":,",
        "vab_pc": ":,.0f",
        "peso_mineria_pct": ":.1f",
        "crecimiento_pct": ":.1f"
    },
    labels={
        "peso_mineria_pct": "Participacion minera en el VAB (%)",
        "crecimiento_pct": "Crecimiento acumulado (%)",
        "region_natural": "Region natural",
        "poblacion": "Poblacion",
        "vab_pc": "VAB por habitante"
    },
    title=f"Mineria y crecimiento departamental, 2007-{anio}"
)

fig_disp.update_traces(
    marker=dict(size=12, opacity=0.8)
)

fig_disp.add_hline(
    y=0,
    line_dash="dash",
    line_color="gray"
)

fig_disp.update_layout(height=480)

st.plotly_chart(fig_disp, width="stretch")

# Correlacion descriptiva
validos = actual[
    ["peso_mineria_pct", "crecimiento_pct"]
].dropna()

if (
    len(validos) >= 3
    and validos["peso_mineria_pct"].nunique() > 1
    and validos["crecimiento_pct"].nunique() > 1
):
    r = validos["peso_mineria_pct"].corr(
        validos["crecimiento_pct"]
    )

    st.caption(
        f"Correlacion de Pearson: r = {r:.2f}; "
        f"n = {len(validos)} departamentos. "
        "Esta asociacion descriptiva no demuestra causalidad."
    )
else:
    st.info(
        "La seleccion no permite estimar "
        "una correlacion informativa."
    )

st.caption(
    "La participacion minera corresponde al año seleccionado; "
    "el crecimiento se mide desde 2007 hasta ese año. "
    "Ambas variables no establecen una secuencia causal."
)


# --------------------------------------------------
# EVOLUCION TEMPORAL DEL VAB POR HABITANTE
# --------------------------------------------------

st.divider()
st.subheader("Evolucion economica regional")

historico = filtrado[
    filtrado["anio"] <= anio
].copy()

historico["vab_total_estimado"] = (
    historico["vab_pc"] * historico["poblacion"]
)

serie = (
    historico.groupby(
        ["anio", "region_natural"],
        as_index=False
    )
    .agg(
        vab_total=("vab_total_estimado", "sum"),
        poblacion=("poblacion", "sum")
    )
)

serie["vab_pc_ponderado"] = (
    serie["vab_total"] / serie["poblacion"]
)

fig_serie = px.line(
    serie,
    x="anio",
    y="vab_pc_ponderado",
    color="region_natural",
    markers=True,
    title=f"Evolucion del VAB real por habitante, 2007-{anio}",
    labels={
        "anio": "Año",
        "vab_pc_ponderado": "Soles constantes de 2007",
        "region_natural": "Region natural"
    }
)

fig_serie.update_xaxes(dtick=1)
fig_serie.update_layout(height=450)

st.plotly_chart(fig_serie, width="stretch")

st.caption(
    "VAB real por habitante agregado mediante ponderacion "
    "por poblacion de los departamentos de cada region "
    "natural. Fuente: INEI."
)


# --------------------------------------------------
# 8. MAPA INTERACTIVO DEL PERU
# --------------------------------------------------

st.divider()
st.subheader("Distribucion geografica del crecimiento")

@st.cache_data
def preparar_mapa():

    ruta_mapa = (
        Path(__file__).resolve().parent
        / "datos"
        / "departamentos_peru.geojson"
    )

    geo = gpd.read_file(ruta_mapa)

    # Normalizar nombres para evitar problemas
    # con tildes y diferencias de escritura.
    def normalizar(nombre):
        texto = str(nombre).strip().upper()
        return "".join(
            caracter
            for caracter in unicodedata.normalize("NFD", texto)
            if unicodedata.category(caracter) != "Mn"
        )

    geo["clave"] = geo["departamento"].map(normalizar)

    # El dataset considera Lima y Callao una sola unidad.
    geo["clave"] = geo["clave"].replace({
        "LIMA": "LIMA Y CALLAO",
        "CALLAO": "LIMA Y CALLAO"
    })

    # Crear correspondencia con los codigos INEI
    codigos = df[
        ["departamento", "ubigeo"]
    ].drop_duplicates().copy()

    codigos["clave"] = codigos["departamento"].map(
        normalizar
    )

    geo = geo.merge(
        codigos[["clave", "ubigeo"]],
        on="clave",
        how="left",
        validate="many_to_one"
    )

    # Registrar las geometrías sin correspondencia.
    sin_codigo = geo.loc[
        geo["ubigeo"].isna(), "departamento"
    ].tolist()

    # Unir las geometrias de Lima y Callao.
    geo = geo.dropna(subset=["ubigeo"])
    geo = geo.dissolve(by="ubigeo", as_index=False)

    geojson = json.loads(
        geo[["ubigeo", "geometry"]].to_json()
    )

    return geojson, geo["ubigeo"].tolist(), sin_codigo


geojson, ubigeos_mapa, sin_codigo = preparar_mapa()

# Verificacion del cruce geográfico
sin_mapa = sorted(
    set(actual["ubigeo"]) - set(ubigeos_mapa)
)

if sin_codigo:
    st.warning(
        f"Geometrias sin codigo: {sin_codigo}"
    )

if sin_mapa:
    st.error(
        f"Departamentos sin geometria: {sin_mapa}"
    )
else:
    st.success(
        f"Cruce geografico correcto: "
        f"{actual['ubigeo'].nunique()} departamentos "
        f"seleccionados con geometria disponible."
    )

# Crear mapa interactivo
fig_mapa = px.choropleth(
    actual,
    geojson=geojson,
    locations="ubigeo",
    featureidkey="properties.ubigeo",
    color="crecimiento_pct",
    hover_name="departamento",
    hover_data={
        "ubigeo": False,
        "crecimiento_pct": ":.1f",
        "vab_pc": ":,.0f",
        "peso_mineria_pct": ":.1f"
    },
    color_continuous_scale="RdYlGn",
    color_continuous_midpoint=0,
    labels={
        "crecimiento_pct": "Crecimiento (%)",
        "vab_pc": "VAB por habitante",
        "peso_mineria_pct": "Actividad extractiva (%)"
    },
    title=f"Crecimiento acumulado departamental, 2007-{anio}"
)

fig_mapa.update_geos(
    fitbounds="locations",
    visible=False
)

fig_mapa.update_layout(
    height=600,
    margin=dict(l=0, r=0, t=60, b=0)
)

st.plotly_chart(fig_mapa, width="stretch")

st.caption(
    "Fuente: INEI. Lima y Callao se presentan como "
    "una unidad economica. El mapa muestra "
    "variaciones descriptivas, no efectos causales."
)
