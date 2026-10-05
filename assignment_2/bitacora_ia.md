# Bitácora de IA – Assignment 2

**Grupo 9** · Temporada 2022 · Herramienta usada: **Claude (Claude Code)**

Registramos los momentos en que la IA nos dio algo incorrecto, incompleto o que no funcionó, cómo nos dimos cuenta y cómo lo corregimos.

---

## Entrada 1 – Parte 1: la espera de Selenium se colgaba cuando no había resultados

**1. ¿Qué le pedimos a la IA?**
Una función para abrir la búsqueda de gob.pe de un mes con Selenium, esperar con `WebDriverWait` a que cargaran los resultados y leer el número "N Resultados".

**2. ¿Qué nos respondió?**
Primero sugirió esperar a que aparecieran los `<article>`, y luego a que apareciera el texto "N Resultados":

```python
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "article")))
...
m = re.search(r"(\d+)\s+Resultados?", driver.find_element(By.TAG_NAME, "body").text)
total = int(m.group(1))
```

**3. ¿Qué estaba mal y cómo nos dimos cuenta?**
El código asumía que siempre hay resultados. Nos dimos cuenta al probar la búsqueda con otro término (`lluvias`) para verificar que no se nos escapaban decretos. El script se cayó con:

```
AttributeError: 'NoneType' object has no attribute 'group'
```

Abrimos esa página y vimos que, cuando no hay resultados, gob.pe **no muestra "0 Resultados"** sino *"No se encontraron resultados para "lluvias""*, y tampoco hay ningún `<article>`. Con la primera versión, `WebDriverWait` hubiera esperado hasta el timeout y fallado. En 2022 todos los meses tenían resultados, así que con el término original no lo habríamos notado.

**4. ¿Cómo lo corregimos?**
Hicimos que `leer_total()` devuelva `0` si la página dice "No se encontraron resultados". Además, la función solo espera los `<article>` cuando el total es mayor que 0:

```python
if "No se encontraron resultados" in texto:
    return 0
...
espera.until(lambda d: leer_total(d) is not None)
if leer_total(driver) > 0:
    espera.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
```

---

## Entrada 2 – Parte 1: el conteo por departamento fallaba con `explode` + `crosstab`

**1. ¿Qué le pedimos a la IA?**
Contar, para cada departamento, cuántas declaratorias y prórrogas tiene, partiendo de una columna con la lista de departamentos de cada decreto, y que aparecieran los 25 departamentos aunque tuvieran 0.

**2. ¿Qué nos respondió?**

```python
por_dep = lluvias.explode("departamentos").rename(columns={"departamentos": "departamento"})
conteo = pd.crosstab(por_dep["departamento"], por_dep["tipo"])
decretos_por_departamento = conteo.reindex(departamentos, fill_value=0) ...
```

**3. ¿Qué estaba mal y cómo nos dimos cuenta?**
Al ejecutar el notebook la celda dio error:

```
ValueError: cannot reindex on an axis with duplicate labels
```

Revisamos la tabla intermedia y vimos la causa. `explode` convierte el decreto de Amazonas, Ayacucho y Piura en 3 filas, pero las 3 **conservan el mismo índice** (0, 0, 0). Después `crosstab` intenta alinear las dos columnas por ese índice repetido y falla (usamos pandas 3.0). La IA no lo previó.

**4. ¿Cómo lo corregimos?**
Agregamos `.reset_index(drop=True)` después de `explode`, para que cada fila tenga un índice único. También dejamos un comentario en el código explicando por qué:

```python
por_dep = (lluvias.explode("departamentos")
           .rename(columns={"departamentos": "departamento"})
           .reset_index(drop=True))
```

Comprobamos que la tabla final tiene 25 filas, con 1 declaratoria en Amazonas, Ayacucho y Piura y 0 en el resto.

---

## Entrada 3 – Parte 2: la IA sugirió buscar la tabla de Wikipedia de una forma que elegía tablas equivocadas

**1. ¿Qué le pedimos a la IA?**
Cómo encontrar, entre todas las tablas que devuelve `pd.read_html`, la tabla de departamentos y capitales de Wikipedia.

**2. ¿Qué nos respondió?**

> "Busquen la que tiene una columna 'Capital': `[t for t in tablas if "Capital" in str(t.columns)]`"

**3. ¿Qué estaba mal y cómo nos dimos cuenta?**
Imprimimos la forma y las columnas de cada tabla (`for i, t in enumerate(tablas): print(i, t.shape, list(t.columns))`) y vimos que **cuatro tablas** tienen una columna "Capital":

| tabla | filas | qué es |
|---|---|---|
| 1 | 24 | departamentos actuales ✔ |
| 2 | 8 | **departamentos que ya no existen** (con columnas "Creación", "Desaparición", "Causa") |
| 3 | 2 | provincias de régimen especial (Callao y Lima) |
| 4 | 6 | provincias que ya no existen |

Con la sugerencia de la IA obteníamos una lista de 4 tablas. Si tomábamos una sin revisar, podíamos terminar con la tabla de departamentos desaparecidos. Además, ninguna de esas tablas tiene 25 filas: el **Callao no está en la tabla de departamentos** sino en la de régimen especial, y su nombre trae una nota pegada (`Callao[nota 6]`).

**4. ¿Cómo lo corregimos?**
Elegimos la tabla que tiene **a la vez** las columnas `Departamento` y `Capital` y al menos 20 filas. Agregamos el Callao desde la tabla de régimen especial, limpiando la nota con una expresión regular. Por último, verificamos con `assert len(capitales) == 25`:

```python
tabla_dep = next(t for t in tablas if "Departamento" in t.columns and "Capital" in t.columns and len(t) >= 20)
callao["departamento"] = callao["departamento"].str.replace(r"\[.*?\]", "", regex=True).str.strip()
```

---

## Entrada 4 – Parte 3: la IA escribió una explicación que no coincidía con el resultado

**1. ¿Qué le pedimos a la IA?**
Mostrar la diferencia entre leer `ubigeos.csv` con y sin `dtype={"ubigeo": str}`, y explicar por qué importa.

**2. ¿Qué nos respondió?**
Un código que compara cuántos ubigeos tienen en común las dos lecturas, convirtiendo los números a texto, y esta explicación:

> "Como muestra la celda de arriba, las dos lecturas no tienen ni un solo ubigeo en común."

**3. ¿Qué estaba mal y cómo nos dimos cuenta?**
Revisamos qué hacía realmente el código. Si `1` se convierte en `"1"`, no coincide con `"01"`, pero **`10` sí se convierte en `"10"`** y coincide. Al ejecutarlo, el resultado fue **16 de 25 ubigeos en común**, no 0. La explicación de la IA afirmaba algo que su propio código contradecía.

**4. ¿Cómo lo corregimos?**
Cambiamos la celda para que muestre dos cosas reales:
1. Que `merge` entre texto y número **da error** (`You are trying to merge on str and int64 columns`).
2. Que, al convertir sin cuidado, se pierden justo los departamentos **01 a 09** (Amazonas a Huancavelica).

Reescribimos la explicación según lo que imprime la celda. Aprendimos a no copiar un texto de conclusión sin antes comprobarlo con la salida del código.
