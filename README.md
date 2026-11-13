# Análisis estadístico y gráfico — Balanceados S.A.S.

Aplicación Streamlit para explorar los 50 registros de la matriz cuantitativa P1–P12.

## Archivos
- `app.py`: aplicación interactiva.
- `datos_balanceados_anonimizados.csv`: datos de análisis sin nombres, documentos ni cargos.
- `requirements.txt`: dependencias.

## Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar
1. Crea un repositorio nuevo en GitHub.
2. Sube estos tres archivos a la raíz del repositorio.
3. Entra a https://share.streamlit.io/ e inicia sesión con GitHub.
4. Selecciona el repositorio, la rama `main` y el archivo `app.py`.
5. Pulsa Deploy.

## Nota sobre privacidad y metodología
No subir el Excel original ni el acta PDF al repositorio público: contienen datos personales. La app usa una copia anonimizada. Las correlaciones se presentan como exploratorias y no como evidencia causal. Los promedios de P1–P10 se reportan sin asumir el sentido de la escala, ya que la codificación detallada no aparece en los archivos entregados.
