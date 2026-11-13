
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ==================================================
# CONFIGURACIÓN GENERAL
# ==================================================

st.set_page_config(
    page_title="Análisis Balanceados S.A.S.",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Análisis Estadístico y Operativo")
st.subheader("Balanceados S.A.S. — Planta Berástegui")
st.markdown(
    "Análisis de los resultados de la encuesta aplicada "
    "a 50 participantes para identificar oportunidades "
    "de mejoramiento operativo y productivo."
)

# ==================================================
# CARGA DE DATOS
# ==================================================

ARCHIVO = Path(__file__).parent / "datos_balanceados_anonimizados.csv"

columnas = [
    "encuestado",
    "P1_planificacion_turnos",
    "P2_mantenimiento_no_programado",
    "P3_mermas_materia_prima",
    "P4_calidad_insumos",
    "P5_inspeccion_proceso",
    "P6_capacitacion_tecnica",
    "P7_repuestos_herramientas",
    "P8_coordinacion_interdepartamental",
    "P9_protocolos_SSOMA",
    "P10_eficiencia_OEE_tecnologia",
    "P11_eficiencia_operativa_1_10",
    "P12_horas_semanales_cuellos_botella"
]

labels = {
    "P1_planificacion_turnos": "P1. Retrasos en la planificación de turnos",
    "P2_mantenimiento_no_programado": "P2. Tiempos muertos por mantenimiento no programado",
    "P3_mermas_materia_prima": "P3. Mermas y desperdicio de materia prima",
    "P4_calidad_insumos": "P4. Calidad y estandarización de insumos",
    "P5_inspeccion_proceso": "P5. Control e inspección en línea de proceso",
    "P6_capacitacion_tecnica": "P6. Capacitación técnica del personal",
    "P7_repuestos_herramientas": "P7. Disponibilidad de repuestos y herramientas",
    "P8_coordinacion_interdepartamental": "P8. Coordinación y comunicación entre áreas",
    "P9_protocolos_SSOMA": "P9. Cumplimiento de protocolos de seguridad",
    "P10_eficiencia_OEE_tecnologia": "P10. Eficiencia global del equipo (OEE / Tecnología)",
    "P11_eficiencia_operativa_1_10": "P11. Nivel general de eficiencia operativa",
    "P12_horas_semanales_cuellos_botella": "P12. Horas semanales perdidas por cuellos de botella"
}

variables_escala = list(labels.keys())[:10]
p11 = "P11_eficiencia_operativa_1_10"
p12 = "P12_horas_semanales_cuellos_botella"

@st.cache_data
def cargar_datos():
    datos = pd.read_csv(ARCHIVO)

    faltantes = [col for col in columnas if col not in datos.columns]

    if faltantes:
        raise ValueError(
            "Faltan columnas en el archivo CSV: " + ", ".join(faltantes)
        )

    datos = datos[columnas].copy()

    for col in variables_escala + [p11, p12]:
        datos[col] = pd.to_numeric(datos[col], errors="coerce")

    return datos


try:
    df = cargar_datos()
except Exception as e:
    st.error(f"No fue posible cargar la base de datos: {e}")
    st.info(
        "Verifica que datos_balanceados_anonimizados.csv "
        "esté guardado en el mismo repositorio que app.py."
    )
    st.stop()

# ==================================================
# VALIDACIONES Y VARIABLES
# ==================================================

total_encuestados = len(df)

# ==================================================
# PESTAÑAS
# ==================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📌 Resumen",
    "📊 Distribución de respuestas",
    "🔗 Relaciones entre variables",
    "📁 Datos y metodología",
    "🔎 Diagnóstico y oportunidades"
])

# ==================================================
# TAB 1: RESUMEN
# ==================================================

with tab1:

    st.header("Resumen general del estudio")

    st.write(
        "Esta sección presenta los principales indicadores "
        "obtenidos a partir de la información recolectada."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Participantes",
        total_encuestados
    )

    col2.metric(
        "Variables analizadas",
        12
    )

    col3.metric(
        "Eficiencia operativa",
        f"{df[p11].mean():.2f}/10"
    )

    col4.metric(
        "Horas perdidas por semana",
        f"{df[p12].mean():.2f} h"
    )

    st.divider()

    st.subheader("Promedio de las dimensiones operativas")

    promedios = df[variables_escala].mean().reset_index()
    promedios.columns = ["Variable", "Promedio"]
    promedios["Nombre"] = promedios["Variable"].map(labels)

    fig = px.bar(
        promedios,
        x="Nombre",
        y="Promedio",
        text="Promedio",
        title="Promedio de las respuestas P1 a P10",
        range_y=[0, 5]
    )

    fig.update_layout(
        xaxis_title="Dimensiones evaluadas",
        yaxis_title="Promedio (escala de 1 a 5)",
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Escala: 1 = Nunca, 2 = Casi nunca, 3 = Algunas veces, "
        "4 = Casi siempre y 5 = Siempre. P1, P2 y P3 miden "
        "situaciones desfavorables; P4 a P10 se interpretan "
        "como prácticas positivas, de acuerdo con la redacción "
        "de los enunciados."
    )

    st.subheader("Indicadores principales")

    resumen = pd.DataFrame({
        "Indicador": [
            "Promedio de eficiencia operativa",
            "Mediana de eficiencia operativa",
            "Promedio de horas perdidas por semana",
            "Mediana de horas perdidas por semana"
        ],
        "Resultado": [
            round(df[p11].mean(), 2),
            round(df[p11].median(), 2),
            round(df[p12].mean(), 2),
            round(df[p12].median(), 2)
        ]
    })

    st.dataframe(resumen, hide_index=True, use_container_width=True)

# ==================================================
# TAB 2: DISTRIBUCIÓN DE RESPUESTAS
# ==================================================

with tab2:

    st.header("Distribución de respuestas")

    st.write(
        "En esta sección se observa cómo se distribuyen "
        "las respuestas de los participantes en cada variable."
    )

    variable_seleccionada = st.selectbox(
        "Selecciona una variable para analizar:",
        variables_escala,
        format_func=lambda x: labels[x]
    )

    frecuencias = (
        df[variable_seleccionada]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    frecuencias.columns = ["Respuesta", "Cantidad"]

    fig = px.bar(
        frecuencias,
        x="Respuesta",
        y="Cantidad",
        text="Cantidad",
        title=f"Distribución: {labels[variable_seleccionada]}",
        color="Respuesta"
    )

    fig.update_layout(
        xaxis_title="Valor de respuesta (1 a 5)",
        yaxis_title="Número de participantes",
        xaxis=dict(dtick=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Estadísticas descriptivas")

    estadisticas = df[variables_escala].describe().T
    estadisticas.index = [labels[x] for x in estadisticas.index]
    estadisticas = estadisticas.round(2)

    st.dataframe(
        estadisticas,
        use_container_width=True
    )

    st.subheader("Comparación de dispersión")

    datos_boxplot = df[variables_escala].melt(
        var_name="Variable",
        value_name="Respuesta"
    )

    datos_boxplot["Variable"] = datos_boxplot["Variable"].map(labels)

    fig_box = px.box(
        datos_boxplot,
        x="Variable",
        y="Respuesta",
        title="Distribución y dispersión de las respuestas"
    )

    fig_box.update_layout(
        xaxis_title="Dimensiones",
        yaxis_title="Respuesta (1 a 5)",
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig_box, use_container_width=True)

# ==================================================
# TAB 3: RELACIONES ENTRE VARIABLES
# ==================================================

with tab3:

    st.header("Relaciones entre variables")

    st.write(
        "Esta sección permite explorar la asociación estadística "
        "entre las variables de la encuesta."
    )

    metodo = st.selectbox(
        "Selecciona el método de correlación:",
        ["Pearson", "Spearman"]
    )

    metodo_calculo = metodo.lower()

    matriz = df[variables_escala + [p11, p12]].corr(
        method=metodo_calculo
    )

    fig_corr = px.imshow(
        matriz,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title=f"Matriz de correlación — {metodo}"
    )

    st.plotly_chart(fig_corr, use_container_width=True)

    st.divider()

    st.subheader("Relación entre eficiencia y horas perdidas")

    datos_relacion = df[[p11, p12]].dropna()

    correlacion = datos_relacion[p11].corr(
        datos_relacion[p12],
        method=metodo_calculo
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Correlación",
        f"{correlacion:.3f}"
    )

    col2.metric(
        "Eficiencia promedio",
        f"{datos_relacion[p11].mean():.2f}/10"
    )

    col3.metric(
        "Horas perdidas promedio",
        f"{datos_relacion[p12].mean():.2f} h"
    )

    fig_relacion = px.scatter(
        datos_relacion,
        x=p12,
        y=p11,
        trendline="ols",
        title="Eficiencia operativa frente a horas perdidas",
        labels={
            p12: "Horas semanales perdidas",
            p11: "Eficiencia operativa (1 a 10)"
        }
    )

    st.plotly_chart(fig_relacion, use_container_width=True)

    if abs(correlacion) < 0.10:
        fuerza = "prácticamente nula"
    elif abs(correlacion) < 0.30:
        fuerza = "muy débil"
    elif abs(correlacion) < 0.50:
        fuerza = "débil a moderada"
    elif abs(correlacion) < 0.70:
        fuerza = "moderada"
    else:
        fuerza = "fuerte"

    if correlacion > 0:
        direccion = "positiva"
    elif correlacion < 0:
        direccion = "negativa"
    else:
        direccion = "nula"

    st.write(
        f"La correlación de {metodo} entre la eficiencia operativa "
        f"y las horas perdidas es {direccion} y {fuerza} "
        f"(r = {correlacion:.3f})."
    )

    st.info(
        "La correlación permite identificar asociaciones estadísticas, "
        "pero no demuestra que una variable cause cambios en otra."
    )

# ==================================================
# TAB 4: DATOS Y METODOLOGÍA
# ==================================================

with tab4:

    st.header("Datos y metodología")

    st.subheader("Características del estudio")

    st.write("""
    **Caso de estudio:** Balanceados S.A.S. — Planta Berástegui.

    **Enfoque:** Cuantitativo.

    **Diseño:** No experimental y transversal.

    **Técnica de recolección:** Encuesta.

    **Participantes:** 50 personas encuestadas.

    **Instrumento:** Cuestionario compuesto por 12 variables.

    **Análisis:** Estadística descriptiva y análisis exploratorio
    de correlaciones.
    """)

    st.subheader("Escala de medición")

    escala = pd.DataFrame({
        "Valor": [1, 2, 3, 4, 5],
        "Respuesta": [
            "Nunca",
            "Casi nunca",
            "Algunas veces",
            "Casi siempre",
            "Siempre"
        ]
    })

    st.dataframe(escala, hide_index=True, use_container_width=True)

    st.subheader("Variables analizadas")

    tabla_variables = pd.DataFrame({
        "Código": [f"P{i}" for i in range(1, 13)],
        "Variable": [labels[x] for x in variables_escala + [p11, p12]]
    })

    st.dataframe(
        tabla_variables,
        hide_index=True,
        use_container_width=True
    )

    st.subheader("Base de datos anonimizada")

    st.write(
        "La base utilizada contiene los registros numéricos de "
        "los participantes, sin publicar nombres, documentos "
        "de identidad ni otros datos personales."
    )

    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True
    )

    st.download_button(
        label="Descargar base de datos anonimizada",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="datos_balanceados_anonimizados.csv",
        mime="text/csv"
    )

    st.subheader("Limitaciones metodológicas")

    st.warning("""
    Los resultados corresponden a los participantes encuestados
    en Balanceados S.A.S. y no permiten generalizar estadísticamente
    los hallazgos a todas las PYMES del departamento de Córdoba.

    Las correlaciones identifican asociaciones, pero no prueban
    relaciones de causa y efecto. Además, los promedios de las
    respuestas ordinales se utilizan como resúmenes descriptivos.
    """)

# ==================================================
# TAB 5: DIAGNÓSTICO Y OPORTUNIDADES
# ==================================================

with tab5:

    st.header("Diagnóstico de resultados operativos")

    st.write(
        "Interpretación de los resultados obtenidos para identificar "
        "los principales aspectos favorables y las oportunidades "
        "de mejoramiento de Balanceados S.A.S."
    )

    st.info(
        "Escala utilizada: 1 = Nunca, 2 = Casi nunca, "
        "3 = Algunas veces, 4 = Casi siempre y 5 = Siempre. "
        "En P1, P2 y P3 una frecuencia alta representa una situación "
        "desfavorable. En P4 a P10 se interpreta como mayor presencia "
        "de la práctica evaluada, suponiendo que los enunciados "
        "están redactados en sentido positivo."
    )

    # ----------------------------------------------
    # 1. HORAS PERDIDAS
    # ----------------------------------------------

    st.subheader("1. Comportamiento de las horas perdidas")

    p12_data = df[p12].dropna()

    if not p12_data.empty:

        a, b, c, d = st.columns(4)

        a.metric("Promedio semanal", f"{p12_data.mean():.2f} h")
        b.metric("Mediana", f"{p12_data.median():.2f} h")
        c.metric("Mínimo", f"{p12_data.min():.2f} h")
        d.metric("Máximo", f"{p12_data.max():.2f} h")

        fig_p12 = px.histogram(
            df,
            x=p12,
            nbins=10,
            title="Distribución de horas semanales perdidas",
            labels={p12: "Horas semanales"}
        )

        st.plotly_chart(fig_p12, use_container_width=True)

        st.write(
            f"Los participantes reportaron un promedio de "
            f"**{p12_data.mean():.2f} horas semanales** asociadas "
            "a cuellos de botella. Este resultado evidencia la "
            "importancia de revisar las actividades que generan "
            "interrupciones o demoras."
        )

    # ----------------------------------------------
    # 2. EFICIENCIA OPERATIVA
    # ----------------------------------------------

    st.subheader("2. Eficiencia operativa")

    p11_data = df[p11].dropna()

    if not p11_data.empty:

        a, b, c = st.columns(3)

        a.metric("Promedio", f"{p11_data.mean():.2f}/10")
        b.metric("Mediana", f"{p11_data.median():.2f}")
        c.metric("Desviación estándar", f"{p11_data.std():.2f}")

        eficiencia_freq = (
            p11_data.value_counts()
            .sort_index()
            .rename_axis("Calificación")
            .reset_index(name="Cantidad")
        )

        fig_p11 = px.bar(
            eficiencia_freq,
            x="Calificación",
            y="Cantidad",
            text="Cantidad",
            title="Distribución de las calificaciones de eficiencia"
        )

        st.plotly_chart(fig_p11, use_container_width=True)

    # ----------------------------------------------
    # 3. INTERPRETACIÓN DE P1 A P10
    # ----------------------------------------------

    st.subheader("3. Interpretación de las variables operativas")

    variables_negativas = [
        "P1_planificacion_turnos",
        "P2_mantenimiento_no_programado",
        "P3_mermas_materia_prima"
    ]

    variables_positivas = [
        "P4_calidad_insumos",
        "P5_inspeccion_proceso",
        "P6_capacitacion_tecnica",
        "P7_repuestos_herramientas",
        "P8_coordinacion_interdepartamental",
        "P9_protocolos_SSOMA",
        "P10_eficiencia_OEE_tecnologia"
    ]

    def nivel_escala(valor):
        if valor <= 1.80:
            return "Nunca"
        elif valor <= 2.60:
            return "Casi nunca"
        elif valor <= 3.40:
            return "Algunas veces"
        elif valor <= 4.20:
            return "Casi siempre"
        else:
            return "Siempre"

    resultados = []

    for variable in variables_negativas:

        promedio = df[variable].mean()
        nivel = nivel_escala(promedio)

        if promedio >= 3.41:
            interpretacion = "Situación que requiere atención"
        elif promedio >= 2.61:
            interpretacion = "Situación presente ocasionalmente"
        else:
            interpretacion = "Menor frecuencia reportada"

        resultados.append({
            "Variable": labels[variable],
            "Promedio": round(promedio, 2),
            "Frecuencia": nivel,
            "Interpretación": interpretacion
        })

    for variable in variables_positivas:

        promedio = df[variable].mean()
        nivel = nivel_escala(promedio)

        if promedio <= 2.60:
            interpretacion = "Prioridad de mejoramiento"
        elif promedio <= 3.40:
            interpretacion = "Oportunidad de fortalecimiento"
        elif promedio <= 4.20:
            interpretacion = "Comportamiento favorable"
        else:
            interpretacion = "Fortaleza observada"

        resultados.append({
            "Variable": labels[variable],
            "Promedio": round(promedio, 2),
            "Frecuencia": nivel,
            "Interpretación": interpretacion
        })

    diagnostico = pd.DataFrame(resultados)

    st.dataframe(
        diagnostico,
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "Los intervalos se utilizan como criterio descriptivo para "
        "resumir los promedios de la escala de 1 a 5."
    )

    grafico = diagnostico.sort_values(
        "Promedio",
        ascending=True
    )

    fig_diag = px.bar(
        grafico,
        x="Promedio",
        y="Variable",
        orientation="h",
        text="Promedio",
        title="Promedio de las dimensiones operativas",
        range_x=[0, 5]
    )

    st.plotly_chart(fig_diag, use_container_width=True)

    # ----------------------------------------------
    # 4. CORRELACIÓN
    # ----------------------------------------------

    st.subheader("4. Relación entre eficiencia y horas perdidas")

    datos_corr = df[[p11, p12]].dropna()

    r = datos_corr[p11].corr(datos_corr[p12], method="pearson")

    if pd.notna(r):

        st.metric("Correlación de Pearson", f"{r:.3f}")

        if abs(r) < 0.10:
            intensidad = "prácticamente nula"
        elif abs(r) < 0.30:
            intensidad = "muy débil"
        elif abs(r) < 0.50:
            intensidad = "débil a moderada"
        elif abs(r) < 0.70:
            intensidad = "moderada"
        else:
            intensidad = "fuerte"

        if r > 0:
            direccion = "positiva"
        elif r < 0:
            direccion = "negativa"
        else:
            direccion = "nula"

        st.write(
            f"Se encontró una asociación lineal {direccion} y "
            f"{intensidad} entre las horas perdidas y la eficiencia "
            f"operativa (r = {r:.3f}). La relación es muy débil, "
            "por lo que no se observa una asociación lineal importante "
            "en esta muestra. Esto no demuestra causalidad."
        )

    # ----------------------------------------------
    # 5. OPORTUNIDADES DE MEJORAMIENTO
    # ----------------------------------------------

    st.subheader("5. Oportunidades de mejoramiento")

    st.markdown("""
    **Planificación y mantenimiento**
    - Revisar la programación de turnos para reducir retrasos.
    - Analizar las causas de las interrupciones por mantenimiento.
    - Establecer seguimiento preventivo de los equipos.

    **Disponibilidad de recursos**
    - Revisar el inventario de repuestos y herramientas.
    - Identificar los recursos cuya falta retrasa las actividades.
    - Establecer controles para garantizar su disponibilidad.

    **Talento humano y procesos**
    - Fortalecer los programas de capacitación técnica.
    - Mantener los controles de calidad e inspección en línea.
    - Mejorar la coordinación y comunicación entre las áreas.

    **Materia prima y seguridad**
    - Identificar las etapas donde se generan desperdicios.
    - Reforzar las prácticas de recepción y almacenamiento.
    - Mantener el cumplimiento de los protocolos de seguridad.
    """)

    # ----------------------------------------------
    # 6. CONCLUSIÓN
    # ----------------------------------------------

    st.subheader("6. Conclusión del análisis")

    st.write(
        "Los resultados muestran que la empresa presenta aspectos "
        "favorables relacionados con la inspección de los procesos, "
        "la calidad de los insumos y el cumplimiento de los protocolos "
        "de seguridad. Sin embargo, también se identifican oportunidades "
        "de mejoramiento en la disponibilidad de repuestos y herramientas, "
        "la capacitación técnica, la planificación de turnos y el "
        "mantenimiento de los equipos. Además, el promedio de 5.99 horas "
        "semanales reportadas por cuellos de botella señala la importancia "
        "de revisar las actividades que generan demoras. En conjunto, "
        "estos resultados sirven como base para proponer estrategias "
        "orientadas a reducir desperdicios y mejorar la productividad "
        "operativa de Balanceados S.A.S."
    )

    st.warning(
        "El diagnóstico es descriptivo y corresponde a los participantes "
        "encuestados en Balanceados S.A.S. No debe generalizarse a todas "
        "las PYMES de Córdoba ni interpretarse como prueba de causalidad."
    )

# ==================================================
# PIE DE PÁGINA
# ==================================================

st.divider()

st.caption(
    "Proyecto académico de análisis estadístico y operativo | "
    "Balanceados S.A.S. — Planta Berástegui | 2026"
)
