# Assignment 3 – ¿Qué regiones del Perú crecieron más entre 2007 y 2019, y tuvo que ver la minería?

**Grupo 9** · Fundamentos de Python · Diplomado PUCP 2026

**Dashboard:** https://grupo9-crecimiento-regional.streamlit.app/

## Qué muestra el dashboard

En la barra lateral se elige el **año** (2007–2019) y las **regiones naturales** (Costa, Sierra,
Selva). El crecimiento se mide desde 2007 hasta el año elegido. Con esos filtros cambian:

- **Métricas:** número de departamentos, crecimiento mediano desde 2007 y VAB real por habitante
  agregado (ponderado por población).
- **Barras:** crecimiento acumulado de cada departamento, con el que más creció en el título.
- **Dispersión:** peso de la minería vs. crecimiento, con el nombre del departamento al pasar el cursor
  y la correlación de Pearson.
- **Línea:** evolución del VAB por habitante de cada región natural.
- **Mapa interactivo:** crecimiento por departamento, con verificación del cruce por ubigeo.
- **Tabla** con los datos de los departamentos seleccionados.

## Pregunta

Entre 2007 y 2019 el Perú creció, pero no todas sus regiones lo hicieron al mismo ritmo.
Queremos saber **qué departamentos aumentaron más su producción por habitante** y si ese
crecimiento **coincide con el peso de la minería** en su economía.

## Datos

`datos/dataset.csv`: 24 departamentos × 13 años (2007–2019) = 312 filas.

| Columna | Qué es |
|---|---|
| `ubigeo` | Código INEI del departamento, **texto de 2 dígitos** (`'01'` … `'25'`) |
| `departamento` | Nombre del departamento |
| `anio` | Año |
| `region_natural` | Costa, Sierra o Selva (clasificación del INEI) |
| `poblacion` | Población al 30 de junio |
| `vab_pc` | Valor Agregado Bruto real por habitante, en soles de 2007 |
| `peso_mineria_pct` | % del VAB que viene de "extracción de petróleo, gas y minerales" |
| `peso_agricultura_pct` | % del VAB que viene de agricultura, ganadería, caza y silvicultura |
| `peso_manufactura_pct` | % del VAB que viene de manufactura |

**Fuentes:**
- INEI, Producto Bruto Interno por departamentos: VAB a precios constantes de 2007, total y por actividad económica.
- INEI, estimaciones y proyecciones de población por departamento (Boletín Especial N.° 25).
- Límites departamentales: `datos/departamentos_peru.geojson`, de la sesión 7 del curso
  (`fetch_data.py 07-mapas`). No trae ubigeo; en `mapas.ipynb` se le agrega el código INEI
  y el Callao se une con Lima (`'15'`).

**Decisiones sobre los datos:**
- **Lima y Callao aparecen juntos** (`ubigeo = '15'`). El INEI publica el VAB de Lima con la
  producción del Callao incluida, pero la población del Callao por separado. Si se dividiera el
  VAB de Lima solo entre la población de Lima, el VAB por habitante saldría ~11 % inflado.
- **"Minería" incluye petróleo y gas**, porque así lo agrupa el INEI.
- El `ubigeo` siempre se lee como texto (`dtype={"ubigeo": str}`) para no perder el cero de la izquierda.

## Hallazgos

1. **Apurímac es el caso extremo.** Su VAB por habitante casi se cuadruplicó (+298 % entre 2007 y
   2019), y casi todo el salto ocurre en 2016, cuando la minería pasa de 10 % a 61 % de su economía,
   el año en que inicia la producción de Las Bambas.
2. **Solo dos departamentos retrocedieron: Madre de Dios (−23 %) y Moquegua (−3 %).** En Madre de
   Dios la caída va de la mano con la pérdida de peso de la minería (de 53 % a 25 % de su VAB).
3. **En el mapa, los que más crecieron son vecinos.** Apurímac, Huánuco, Ayacucho, Cusco y
   Huancavelica forman un bloque en la sierra centro y sur, todos con más de 75 %. La mediana de la
   sierra (+75 %) casi duplica la de la costa (+42 %) y triplica la de la selva (+22 %).

## Limitaciones

- El VAB mide **lo que se produce** dentro del departamento, no el ingreso de quienes viven ahí:
  parte de las ganancias mineras sale de la región.
- Las relaciones que mostramos son **asociaciones, no causas**. Que Apurímac crezca a la vez que
  su minería no prueba que una cause la otra.
- El INEI no publica el VAB del Callao por separado, así que no se puede analizar solo.
- Son datos departamentales: esconden diferencias grandes entre provincias y distritos.

## Contenido de la carpeta

| Archivo | Qué hace |
|---|---|
| `visualizacion.ipynb` | Parte 1: gráficos con Plotly (barras, dispersión y línea) |
| `grafico.html` | Gráfico de barras exportado, interactivo |
| `mapas.ipynb` | Parte 2: mapas con Geopandas y Folium |
| `app.py` | Parte 3: dashboard en Streamlit |
| `requirements.txt` | Librerías que necesita el dashboard |
| `datos/dataset.csv` | Datos usados en las tres partes |
| `datos/departamentos_peru.geojson` | Límites departamentales para los mapas y el dashboard |

## Cómo correr el dashboard en local

Desde la carpeta `assignment_3/`:

```bash
uv run --with-requirements requirements.txt streamlit run app.py
```

O, con pip:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Integrantes

- Jhanela Luz Carhuaz Fuster – Parte 1: Visualización
- Amanda Gomez Flores – Parte 2: Mapas
- Victor Roman Lazarte – Parte 3: Dashboard
