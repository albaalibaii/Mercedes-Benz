# Informe final (LaTeX)

Informe de todos los retos de *Clustering the Star* (Mercedes-Benz · III Malackathon 2026).

## Contenido

| Fichero | Qué es |
|---|---|
| `informe.tex` | Documento principal |
| `bibliografia.bib` | Bibliografía (biblatex + biber) |
| `figuras/` | Gráficos exportados de los notebooks de los retos |

## Cómo compilarlo

**Opción 1 · Overleaf (sin instalar nada):** crear un proyecto nuevo, subir esta carpeta entera (o un `.zip` con ella)
y compilar. Overleaf detecta biber automáticamente.

**Opción 2 · En local** (TeX Live o MiKTeX):

```
latexmk -pdf informe.tex
```

o, paso a paso:

```
pdflatex informe.tex
biber informe
pdflatex informe.tex
pdflatex informe.tex
```

## Origen de los datos

Todas las cifras proceden de la ejecución de los notebooks del repositorio. Las fuentes de los datos externos están
detalladas en [`../Fuentes_Datos_Externos.md`](../Fuentes_Datos_Externos.md).
