
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Balanceados S.A.S. | Análisis operativo",
    page_icon="📊",
    layout="wide"
)

st.title("Análisis estadístico y gráfico")
st.subheader("Balanceados S.A.S. — Planta Berástegui")
st.caption(
    "Diagnóstico de tiempos muertos, mermas operativas "
    "y oportunidades de optimización"
)

DATA_PATH = Path(__file__).parent / "datos_balanceados_anonimizados.csv"

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH)

    # Convertir las variables de análisis a formato numérico
    for col in data.columns:
        if col != "encuestado":
            data[col] = pd.to_numeric(data[col], errors="coerce")

    return data

df = load_data()

id_col = "encuestado"
questions = [c for c in df.columns if c != id_col]
operational_questions = questions[:10]

labels = {
    "P1_planificacion_turnos": "P1 · Planificación de turnos",
    "P2_mantenimiento_no_programado": "P2 · Mantenimiento no programado",
    "P3_mermas_materia_prima": "P3 · Mermas de materia prima",
    "P4_calidad_insumos": "P4 · Calidad de insumos",
    "P5_inspeccion_proceso": "P5 · Inspección en proceso",
    "P6_capacitacion_tecnica": "P6 · Capacitación técnica",
    "P7_repuestos_herramientas": "P7 · Repuestos y herramientas",
    "P8_coordinacion_interdepartamental": "P8 · Coordinación interdepartamental",
    "P9_protocolos_SSOMA": "P9 · Protocolos SSOMA",
    "P10_eficiencia_OEE_tecnologia": "P10 · Eficiencia OEE / tecnología",
    "P11_eficiencia_operativa_1_10": "P11 · Eficiencia operativa (1–10)",
    "P12_horas_semanales_cuellos_botella": "P12 · Horas semanales por cuellos de botella",
}

p11 = "P11_eficiencia_operativa_1_10"
p12 = "P12_horas_semanales_cuellos_botella"

st.info(
    "Base anonimizada: se excluyeron nombres, documentos de identidad, "
    "cargos y fechas personales. El análisis utiliza los registros "
    "individuales de los participantes."
)

# Filtros
st.sidebar.header("Explorar resultados")

selected = st.sidebar.multiselect(
    "Variables para comparar",
    options=questions,
    default=operational_questions,
    format_func=lambda x: labels.get(x, x)
)

if not selected:
    selected = operational_questions

# Indicadores principales
c1, c2, c3, c4 = st.columns(4)

c1.metric("Encuestados", f"{len(df)}")
c2.metric("Variables", f"{len(questions)}")
c3.metric("Promedio P11", f"{df[p11].mean():.2f} / 10")
c4.metric("Promedio P12", f"{df[p12].mean():.2f} h/semana")

# Pestañas
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Resumen",
    "Distribución de respuestas",
    "Relaciones entre variables",
    "Datos y metodología",
    "Diagnóstico y oportunidades"
])

# --------------------------------------------------
# TAB 1: RESUMEN
# --------------------------------------------------

with tab1:

    st.markdown("### Promedios de las variables operativas")

    means = (
        df[operational_questions]
        .mean()
        .rename_axis("variable")
        .reset_index(name="promedio")
    )

    means["nombre"] = means["variable"].map(labels)
    means = means.sort_values("promedio", ascending=False)

    fig = px.bar(
        means,
        x="nombre",
        y="promedio",
        text_auto=".2f",
        labels={
            "nombre": "Variable",
            "promedio": "Promedio registrado"
        },
        title="Promedios descriptivos de P1 a P10"
    )

    fig.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Los promedios se presentan únicamente como descripción de "
        "las respuestas. No se interpretan como niveles favorables "
        "o desfavorables porque se requiere confirmar la codificación "
        "y el sentido de cada escala."
    )

    st.markdown("### Estadísticos descriptivos")

    desc = df[questions].describe().T
    desc.index = [labels.get(i, i) for i in desc.index]

    desc = desc.rename(columns={
        "count": "N",
        "mean": "Media",
        "std": "Desv. estándar",
        "min": "Mínimo",
        "25%": "P25",
        "50%": "Mediana",
        "75%": "P75",
        "max": "Máximo"
    })

    st.dataframe(desc.round(2), use_container_width=True)

# --------------------------------------------------
# TAB 2: DISTRIBUCIÓN
# --------------------------------------------------

with tab2:

    st.markdown("### Distribución de respuestas")

    variable = st.selectbox(
        "Selecciona una variable",
        questions,
        format_func=lambda x: labels.get(x, x)
    )

    freq = (
        df[variable]
        .value_counts()
        .sort_index()
        .rename_axis("Respuesta")
        .reset_index(name="Frecuencia")
    )

    freq["Porcentaje"] = (
        100 * freq["Frecuencia"] / freq["Frecuencia"].sum()
    )

    fig = px.bar(
        freq,
        x="Respuesta",
        y="Frecuencia",
        text="Frecuencia",
        hover_data={"Porcentaje": ":.1f"},
        title=f"Frecuencia de respuestas — {labels[variable]}"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        freq.assign(Porcentaje=freq["Porcentaje"].round(1)),
        hide_index=True,
        use_container_width=True
    )

    st.markdown("### Comparación de variables seleccionadas")

    comp = df[selected].melt(
        var_name="Variable",
        value_name="Valor"
    )

    comp["Variable"] = comp["Variable"].map(labels)

    fig2 = px.box(
        comp,
        x="Variable",
        y="Valor",
        points="all",
        title="Variabilidad de las respuestas"
    )

    fig2.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig2, use_container_width=True)

# --------------------------------------------------
# TAB 3: RELACIONES ENTRE VARIABLES
# --------------------------------------------------

with tab3:

    st.markdown("### Matriz de correlación")

    metodo = st.selectbox(
        "Método de correlación",
        ["Spearman", "Pearson"],
        help=(
            "Spearman permite analizar asociaciones monotónicas y "
            "resulta útil cuando las variables son ordinales. "
            "Pearson mide asociaciones lineales."
        )
    )

    corr_cols = st.multiselect(
        "Variables incluidas en la correlación",
        questions,
        default=questions
    )

    if len(corr_cols) >= 2:

        metodo_codigo = "spearman" if metodo == "Spearman" else "pearson"

        corr = df[corr_cols].corr(method=metodo_codigo)

        corr.index = [labels.get(x, x) for x in corr.index]
        corr.columns = [labels.get(x, x) for x in corr.columns]

        fig = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            zmin=-1,
            zmax=1,
            color_continuous_scale="RdBu_r",
            title=f"Matriz de correlación — {metodo}"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.warning(
            "La correlación identifica asociaciones entre variables, "
            "pero no demuestra causalidad. Los resultados deben "
            "interpretarse considerando la naturaleza de las escalas."
        )

    else:
        st.warning("Selecciona al menos dos variables.")

    st.markdown("### Eficiencia operativa y horas perdidas")

    fig = px.scatter(
        df,
        x=p12,
        y=p11,
        trendline="ols",
        labels={
            p12: "Horas semanales por cuellos de botella",
            p11: "Eficiencia operativa (1–10)"
        },
        title="Relación entre horas perdidas y eficiencia"
    )

    st.plotly_chart(fig, use_container_width=True)

    r_pearson = df[p12].corr(df[p11], method="pearson")
    r_spearman = df[p12].corr(df[p11], method="spearman")

    col1, col2 = st.columns(2)

    col1.metric("Pearson", f"{r_pearson:.3f}")
    col2.metric("Spearman", f"{r_spearman:.3f}")

    st.caption(
        "Los coeficientes representan asociaciones observadas en "
        "la muestra. No permiten establecer relaciones de causa y efecto."
    )

# --------------------------------------------------
# TAB 4: DATOS Y METODOLOGÍA
# --------------------------------------------------

with tab4:

    st.markdown("### Base de datos anonimizada")

    st.write(
        "Se presentan los identificadores de encuesta y las "
        "12 variables cuantitativas. No se incluyen datos personales."
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Descargar base anonimizada (CSV)",
        df.to_csv(index=False).encode("utf-8-sig"),
        file_name="datos_balanceados_anonimizados.csv",
        mime="text/csv"
    )

    st.markdown("### Consideraciones metodológicas")

    st.markdown("""
    - Unidad de análisis: registro individual de cada participante.
    - Tamaño de la base: registros disponibles en la matriz.
    - Variables: P1 a P10, P11 (escala de 1 a 10) y P12
      (horas semanales por cuellos de botella).
    - Se calcularon frecuencias, porcentajes, medidas descriptivas
      y correlaciones exploratorias.
    - Se excluyó la fila de promedio general de la matriz original
      para evitar duplicar información.
    - La base publicada está anonimizada.
    - Los resultados corresponden al caso estudiado y no representan
      estadísticamente a todas las PYMES de Córdoba.
    """)

    st.caption(
        "Fuente: matriz cuantitativa suministrada para el proyecto "
        "de investigación de Balanceados S.A.S. — Planta Berástegui."
    )

# --------------------------------------------------
# TAB 5: DIAGNÓSTICO Y OPORTUNIDADES
# --------------------------------------------------

with tab5:

    st.markdown("## Diagnóstico de resultados operativos")

    st.write(
        "Esta sección reúne indicadores descriptivos que ayudan "
        "a reconocer aspectos que merecen revisión dentro de "
        "los procesos operativos de la empresa."
    )

    # Indicadores de horas perdidas
    st.markdown("### 1. Comportamiento de las horas perdidas")

    p12_data = df[p12].dropna()

    if not p12_data.empty:

        a, b, c, d = st.columns(4)

        a.metric("Promedio semanal", f"{p12_data.mean():.2f} h")
        b.metric("Mediana", f"{p12_data.median():.2f} h")
        c.metric("Mínimo registrado", f"{p12_data.min():.2f} h")
        d.metric("Máximo registrado", f"{p12_data.max():.2f} h")

        fig_p12 = px.histogram(
            df,
            x=p12,
            nbins=10,
            title="Distribución de horas semanales perdidas",
            labels={p12: "Horas semanales"}
        )

        st.plotly_chart(fig_p12, use_container_width=True)

        st.write(
            f"En los registros disponibles, el promedio de horas "
            f"semanales asociadas a cuellos de botella es de "
            f"**{p12_data.mean():.2f} horas**. La mediana es de "
            f"**{p12_data.median():.2f} horas**. Estos valores permiten "
            "describir la situación reportada, pero no determinan "
            "por sí solos el costo económico de las pérdidas."
        )

    # Distribución de eficiencia
    st.markdown("### 2. Distribución de la eficiencia operativa")

    p11_data = df[p11].dropna()

    if not p11_data.empty:

        a, b, c = st.columns(3)

        a.metric("Promedio", f"{p11_data.mean():.2f} / 10")
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
            title="Frecuencia de calificaciones de eficiencia"
        )

        st.plotly_chart(fig_p11, use_container_width=True)

        st.write(
            f"La calificación promedio de eficiencia operativa "
            f"registrada por los participantes fue de "
            f"**{p11_data.mean():.2f} sobre 10**. La distribución "
            "permite observar cómo se agrupan las valoraciones "
            "de los encuestados."
        )

    # Variables operativas destacadas
    st.markdown("### 3. Variables operativas destacadas")

    ranking = (
        df[operational_questions]
        .mean()
        .rename_axis("Variable")
        .reset_index(name="Promedio")
    )

    ranking["Nombre"] = ranking["Variable"].map(labels)
    ranking = ranking.sort_values("Promedio", ascending=False)

    st.dataframe(
        ranking[["Nombre", "Promedio"]].round(2),
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "El orden presenta únicamente los promedios observados. "
        "No constituye una clasificación de problemas ni de fortalezas: "
        "para ello es necesario conocer el sentido y la codificación "
        "de las respuestas de cada pregunta."
    )

    # Correlación y lectura general
    st.markdown("### 4. Lectura general de los resultados")

    r = df[p12].corr(df[p11], method="pearson")

    if pd.notna(r):

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

        direccion = (
            "positiva" if r > 0
            else "negativa" if r < 0
            else "nula"
        )

        st.info(
            f"La relación lineal entre las horas perdidas y la eficiencia "
            f"operativa presenta una asociación {direccion} y "
            f"{intensidad} (r = {r:.3f}). Este resultado no demuestra "
            "que una variable cause cambios en la otra."
        )

    # Oportunidades de revisión
    st.markdown("### 5. Oportunidades de mejoramiento")

    st.write(
        "A partir de las dimensiones evaluadas en la encuesta, "
        "se proponen las siguientes líneas de revisión para la empresa:"
    )

    st.markdown("""
    **Planificación y organización**
    - Revisar la programación de turnos y la distribución de actividades.
    - Identificar las etapas del proceso donde se presentan demoras.

    **Mantenimiento y recursos**
    - Examinar los registros de mantenimiento no programado.
    - Verificar la disponibilidad de repuestos y herramientas.
    - Establecer controles para prevenir interrupciones operativas.

    **Materia prima y calidad**
    - Revisar los procedimientos de recepción y almacenamiento.
    - Identificar las etapas donde pueden presentarse desperdicios.
    - Fortalecer la inspección de los insumos y del proceso productivo.

    **Talento humano y coordinación**
    - Evaluar las necesidades de capacitación técnica.
    - Mejorar la comunicación entre las áreas involucradas.
    - Reforzar el seguimiento de los procedimientos de seguridad.
    """)

    st.warning(
        "Estas son propuestas de revisión basadas en las dimensiones "
        "estudiadas. Para priorizarlas se deben contrastar con los "
        "resultados de cada pregunta, sus escalas y los registros "
        "operativos de la empresa."
    )

    st.markdown("### 6. Conclusión del análisis")

    st.write(
        "Los resultados permiten describir la percepción de los "
        "participantes sobre diferentes aspectos de la operación "
        "de Balanceados S.A.S. y cuantificar las horas semanales "
        "reportadas por cuellos de botella. La información constituye "
        "un punto de partida para revisar la planificación, el "
        "mantenimiento, el control de materias primas, la coordinación "
        "y la eficiencia de los procesos. Las decisiones de mejora "
        "deben complementarse con registros internos y seguimiento "
        "de indicadores a lo largo del tiempo."
    )
