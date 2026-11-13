
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# 1. CONFIGURACIÓN Y DISEÑO
# =========================================================

st.set_page_config(
    page_title="Balanceados S.A.S. | Análisis operativo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #17365D;
    }

    .hero {
        background: linear-gradient(115deg, #17365D, #2878A8);
        padding: 28px;
        border-radius: 16px;
        color: white;
        margin-bottom: 22px;
    }

    .hero h1 {
        color: white;
        font-size: 30px;
        margin-bottom: 5px;
    }

    .hero p {
        color: #eaf3fb;
        font-size: 16px;
        margin-bottom: 0;
    }

    .section-note {
        background-color: #eaf2f8;
        border-left: 5px solid #2878A8;
        padding: 13px;
        border-radius: 7px;
        margin: 10px 0 18px 0;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e1e8ef;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 7px rgba(0,0,0,0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #526579;
    }

    .footer {
        text-align: center;
        color: #718096;
        font-size: 13px;
        padding: 18px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>📊 Análisis estadístico y operativo</h1>
    <p>Balanceados S.A.S. — Planta Berástegui</p>
    <p>Diagnóstico de procesos, eficiencia y oportunidades de mejoramiento · 2026</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 2. NOMBRES DE LAS VARIABLES
# =========================================================

archivo = Path(__file__).parent / "datos_balanceados_anonimizados.csv"

p11 = "P11_eficiencia_operativa_1_10"
p12 = "P12_horas_semanales_cuellos_botella"

variables = [
    "P1_planificacion_turnos",
    "P2_mantenimiento_no_programado",
    "P3_mermas_materia_prima",
    "P4_calidad_insumos",
    "P5_inspeccion_proceso",
    "P6_capacitacion_tecnica",
    "P7_repuestos_herramientas",
    "P8_coordinacion_interdepartamental",
    "P9_protocolos_SSOMA",
    "P10_eficiencia_OEE_tecnologia"
]

variables_negativas = variables[:3]
variables_positivas = variables[3:]

labels = {
    "P1_planificacion_turnos": "P1. Planificación de turnos y retrasos",
    "P2_mantenimiento_no_programado": "P2. Mantenimiento no programado",
    "P3_mermas_materia_prima": "P3. Mermas y desperdicio de materia prima",
    "P4_calidad_insumos": "P4. Calidad y estandarización de insumos",
    "P5_inspeccion_proceso": "P5. Control e inspección del proceso",
    "P6_capacitacion_tecnica": "P6. Capacitación técnica del personal",
    "P7_repuestos_herramientas": "P7. Disponibilidad de repuestos y herramientas",
    "P8_coordinacion_interdepartamental": "P8. Coordinación entre áreas",
    "P9_protocolos_SSOMA": "P9. Protocolos de seguridad (SSOMA)",
    "P10_eficiencia_OEE_tecnologia": "P10. Eficiencia de equipos (OEE / tecnología)",
    p11: "P11. Eficiencia operativa general",
    p12: "P12. Horas semanales perdidas por cuellos de botella"
}

columnas = ["encuestado"] + variables + [p11, p12]

# =========================================================
# 3. CARGA Y VALIDACIÓN DE LA BASE
# =========================================================

@st.cache_data
def cargar_datos(ruta):
    datos = pd.read_csv(ruta)

    faltantes = [c for c in columnas if c not in datos.columns]

    if faltantes:
        raise ValueError(
            "No se encontraron estas columnas: " + ", ".join(faltantes)
        )

    datos = datos[columnas].copy()

    for col in variables + [p11, p12]:
        datos[col] = pd.to_numeric(datos[col], errors="coerce")

    return datos


if not archivo.exists():
    st.error(
        "No se encontró datos_balanceados_anonimizados.csv. "
        "Verifica que esté en el mismo repositorio que app.py."
    )
    st.stop()

try:
    df = cargar_datos(str(archivo))
except Exception as error:
    st.error(f"Error al cargar la base de datos: {error}")
    st.stop()

total = len(df)

# =========================================================
# 4. FUNCIONES DE APOYO
# =========================================================

def nivel_escala(valor):
    """Clasificación orientativa del promedio de una escala 1 a 5."""
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


def clasificar_variable(variable, promedio):
    """
    P1-P3: frecuencia alta significa mayor presencia de una situación
    desfavorable.

    P4-P10: se supone que los enunciados describen prácticas positivas.
    Esta interpretación debe verificarse con la redacción exacta.
    """

    if variable in variables_negativas:
        if promedio >= 3.41:
            return "Atención prioritaria"
        elif promedio >= 2.61:
            return "Seguimiento y control"
        else:
            return "Menor frecuencia reportada"

    if promedio <= 2.60:
        return "Prioridad de mejoramiento"
    elif promedio <= 3.40:
        return "Oportunidad de fortalecimiento"
    elif promedio <= 4.20:
        return "Comportamiento favorable"
    else:
        return "Frecuencia alta de la práctica"


def crear_grafico_barras(datos, x, y, titulo, eje_x, eje_y):
    fig = px.bar(
        datos,
        x=x,
        y=y,
        text=y,
        title=titulo,
        color=y,
        color_continuous_scale="Blues"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
        marker_line_width=0
    )

    fig.update_layout(
        xaxis_title=eje_x,
        yaxis_title=eje_y,
        coloraxis_showscale=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=65, b=30)
    )

    return fig


# =========================================================
# 5. MENÚ DE NAVEGACIÓN
# =========================================================

st.sidebar.title("📚 Panel de navegación")
st.sidebar.write("Análisis de Balanceados S.A.S.")

pestana = st.sidebar.radio(
    "Selecciona una sección:",
    [
        "📌 Resumen general",
        "📊 Distribución de respuestas",
        "🔗 Relaciones entre variables",
        "📁 Datos y metodología",
        "🔎 Diagnóstico y oportunidades"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Proyecto académico · 2026")
st.sidebar.caption(f"Registros cargados: {total}")

# =========================================================
# 6. RESUMEN GENERAL
# =========================================================

if pestana == "📌 Resumen general":

    st.header("Resumen general del estudio")

    st.markdown("""
    <div class="section-note">
    Esta sección presenta los principales indicadores de la encuesta
    aplicada a los participantes de Balanceados S.A.S.
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Participantes", total)
    c2.metric("Variables", 12)
    c3.metric("Eficiencia promedio", f"{df[p11].mean():.2f}/10")
    c4.metric("Horas perdidas", f"{df[p12].mean():.2f} h")

    st.divider()

    st.subheader("Promedio de las dimensiones operativas")

    promedios = df[variables].mean().reset_index()
    promedios.columns = ["Código", "Promedio"]
    promedios["Dimensión"] = promedios["Código"].map(labels)

    fig = px.bar(
        promedios,
        x="Promedio",
        y="Dimensión",
        orientation="h",
        color="Promedio",
        color_continuous_scale="Blues",
        text="Promedio",
        title="Resultados promedio de P1 a P10",
        range_x=[0, 5]
    )

    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_title="Promedio (escala de 1 a 5)",
        yaxis_title="",
        coloraxis_showscale=False,
        plot_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "Importante: P1, P2 y P3 representan situaciones desfavorables "
        "cuando ocurren con mayor frecuencia. Los promedios de P4 a P10 "
        "se interpretan como prácticas favorables únicamente si sus "
        "enunciados están redactados en sentido positivo."
    )

    st.subheader("Indicadores principales")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Mediana de eficiencia",
            f"{df[p11].median():.2f}/10"
        )

    with col2:
        st.metric(
            "Mediana de horas perdidas",
            f"{df[p12].median():.2f} h"
        )

    st.subheader("Lectura general")

    st.write(
        "Los datos permiten examinar las condiciones de planificación, "
        "mantenimiento, desperdicio de materia prima, calidad, capacitación "
        "y disponibilidad de recursos. También permiten observar el nivel "
        "general de eficiencia operativa y las horas reportadas como perdidas "
        "por cuellos de botella."
    )

# =========================================================
# 7. DISTRIBUCIÓN DE RESPUESTAS
# =========================================================

elif pestana == "📊 Distribución de respuestas":

    st.header("Distribución de respuestas")

    st.write(
        "Explora la frecuencia de las respuestas y el comportamiento "
        "de cada una de las dimensiones evaluadas."
    )

    variable = st.selectbox(
        "Selecciona una variable:",
        variables + [p11, p12],
        format_func=lambda x: labels[x]
    )

    valores = df[variable].dropna()

    if not valores.empty:

        frecuencias = (
            valores.value_counts()
            .sort_index()
            .rename_axis("Respuesta")
            .reset_index(name="Cantidad")
        )

        fig = px.bar(
            frecuencias,
            x="Respuesta",
            y="Cantidad",
            text="Cantidad",
            color="Cantidad",
            color_continuous_scale="Blues",
            title=f"Distribución de {labels[variable]}"
        )

        fig.update_traces(textposition="outside")

        fig.update_layout(
            plot_bgcolor="white",
            xaxis_title="Valor de respuesta",
            yaxis_title="Número de participantes",
            coloraxis_showscale=False
        )

        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)

        c1.metric("Promedio", f"{valores.mean():.2f}")
        c2.metric("Mediana", f"{valores.median():.2f}")
        c3.metric("Desviación estándar", f"{valores.std():.2f}")

    else:
        st.warning("No hay datos disponibles para esta variable.")

    st.divider()

    st.subheader("Estadísticas descriptivas de P1 a P10")

    estadisticas = df[variables].describe().T
    estadisticas.index = [labels[x] for x in estadisticas.index]
    estadisticas = estadisticas.round(2)

    st.dataframe(
        estadisticas,
        use_container_width=True
    )

    st.subheader("Comparación de la dispersión")

    datos_box = df[variables].melt(
        var_name="Variable",
        value_name="Respuesta"
    )

    datos_box["Variable"] = datos_box["Variable"].map(labels)

    fig_box = px.box(
        datos_box,
        x="Variable",
        y="Respuesta",
        color="Variable",
        title="Distribución de las respuestas por dimensión"
    )

    fig_box.update_layout(
        showlegend=False,
        xaxis_title="Dimensiones",
        yaxis_title="Respuesta",
        xaxis_tickangle=-45,
        plot_bgcolor="white"
    )

    st.plotly_chart(fig_box, use_container_width=True)

# =========================================================
# 8. RELACIONES ENTRE VARIABLES
# =========================================================

elif pestana == "🔗 Relaciones entre variables":

    st.header("Relaciones entre variables")

    st.write(
        "Esta sección permite explorar las asociaciones estadísticas "
        "entre las variables de la investigación."
    )

    metodo = st.selectbox(
        "Método de correlación:",
        ["Pearson", "Spearman"]
    )

    matriz = df[variables + [p11, p12]].corr(
        method=metodo.lower()
    )

    fig_corr = px.imshow(
        matriz,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title=f"Matriz de correlación de {metodo}"
    )

    fig_corr.update_layout(
        height=650,
        plot_bgcolor="white"
    )

    st.plotly_chart(fig_corr, use_container_width=True)

    st.divider()

    st.subheader("Eficiencia operativa y horas perdidas")

    datos_relacion = df[[p11, p12]].dropna()

    if len(datos_relacion) >= 2:

        correlacion = datos_relacion[p11].corr(
            datos_relacion[p12],
            method=metodo.lower()
        )

        a, b, c = st.columns(3)

        a.metric("Correlación", f"{correlacion:.3f}")
        b.metric("Eficiencia promedio", f"{datos_relacion[p11].mean():.2f}/10")
        c.metric("Horas perdidas promedio", f"{datos_relacion[p12].mean():.2f} h")

        fig_scatter = px.scatter(
            datos_relacion,
            x=p12,
            y=p11,
            title="Relación entre eficiencia y horas perdidas",
            labels={
                p12: "Horas semanales perdidas",
                p11: "Eficiencia operativa (1 a 10)"
            },
            trendline=None
        )

        fig_scatter.update_traces(
            marker=dict(size=11, opacity=0.75)
        )

        fig_scatter.update_layout(
            plot_bgcolor="white"
        )

        st.plotly_chart(fig_scatter, use_container_width=True)

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

        direccion = (
            "positiva" if correlacion > 0
            else "negativa" if correlacion < 0
            else "nula"
        )

        st.info(
            f"La correlación de {metodo} es {direccion} y {fuerza} "
            f"(r = {correlacion:.3f}). Este resultado describe la "
            "asociación observada en la muestra y no demuestra causalidad."
        )

    else:
        st.warning("No hay suficientes registros para calcular la correlación.")

# =========================================================
# 9. DATOS Y METODOLOGÍA
# =========================================================

elif pestana == "📁 Datos y metodología":

    st.header("Datos y metodología")

    st.subheader("Características de la investigación")

    datos_metodo = [
        ("Caso de estudio", "Balanceados S.A.S. — Planta Berástegui"),
        ("Enfoque", "Cuantitativo"),
        ("Diseño", "No experimental y transversal"),
        ("Técnica", "Encuesta"),
        ("Participantes", f"{total} registros"),
        ("Instrumento", "Cuestionario de 12 variables"),
        ("Análisis", "Estadística descriptiva y correlaciones exploratorias")
    ]

    tabla_metodo = pd.DataFrame(
        datos_metodo,
        columns=["Característica", "Descripción"]
    )

    st.table(tabla_metodo)

    st.subheader("Escala de medición de P1 a P10")

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

    st.dataframe(
        escala,
        hide_index=True,
        use_container_width=True
    )

    st.subheader("Variables de la investigación")

    tabla_variables = pd.DataFrame({
        "Código": [f"P{i}" for i in range(1, 11)] + ["P11", "P12"],
        "Dimensión": [labels[x] for x in variables + [p11, p12]]
    })

    st.dataframe(
        tabla_variables,
        hide_index=True,
        use_container_width=True
    )

    st.subheader("Base de datos anonimizada")

    st.write(
        "Se presenta la base numérica utilizada en el análisis. "
        "La información publicada no incluye nombres ni documentos "
        "de identidad de los participantes."
    )

    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True
    )

    st.download_button(
        "⬇️ Descargar base anonimizada",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="datos_balanceados_anonimizados.csv",
        mime="text/csv"
    )

    st.warning(
        "Los resultados corresponden a los participantes encuestados "
        "en Balanceados S.A.S. No deben generalizarse estadísticamente "
        "a todas las PYMES de Córdoba. Las correlaciones no prueban "
        "relaciones de causa y efecto."
    )

# =========================================================
# 10. DIAGNÓSTICO Y OPORTUNIDADES
# =========================================================

elif pestana == "🔎 Diagnóstico y oportunidades":

    st.header("Diagnóstico de resultados operativos")

    st.markdown("""
    <div class="section-note">
    Interpretación de los resultados obtenidos para identificar
    los aspectos favorables y las oportunidades de mejoramiento
    de Balanceados S.A.S.
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "Escala: 1 = Nunca, 2 = Casi nunca, 3 = Algunas veces, "
        "4 = Casi siempre y 5 = Siempre. P1, P2 y P3 representan "
        "situaciones desfavorables cuando ocurren con mayor frecuencia. "
        "La lectura favorable de P4 a P10 depende de que sus enunciados "
        "estén formulados en sentido positivo."
    )

    # ---------------------------------------------
    # 10.1 HORAS PERDIDAS
    # ---------------------------------------------

    st.subheader("1. Comportamiento de las horas perdidas")

    horas = df[p12].dropna()

    if not horas.empty:

        a, b, c, d = st.columns(4)

        a.metric("Promedio semanal", f"{horas.mean():.2f} h")
        b.metric("Mediana", f"{horas.median():.2f} h")
        c.metric("Mínimo", f"{horas.min():.2f} h")
        d.metric("Máximo", f"{horas.max():.2f} h")

        fig_horas = px.histogram(
            df,
            x=p12,
            nbins=10,
            title="Distribución de horas semanales perdidas",
            labels={p12: "Horas semanales"}
        )

        fig_horas.update_traces(
            marker_color="#2878A8",
            marker_line_color="white",
            marker_line_width=1
        )

        fig_horas.update_layout(
            plot_bgcolor="white",
            xaxis_title="Horas semanales",
            yaxis_title="Número de participantes"
        )

        st.plotly_chart(fig_horas, use_container_width=True)

        st.write(
            f"Los participantes reportaron un promedio de "
            f"**{horas.mean():.2f} horas semanales** asociadas "
            "a cuellos de botella. Este resultado señala la "
            "importancia de revisar las actividades que generan "
            "interrupciones y demoras."
        )

    # ---------------------------------------------
    # 10.2 EFICIENCIA
    # ---------------------------------------------

    st.subheader("2. Eficiencia operativa")

    eficiencia = df[p11].dropna()

    if not eficiencia.empty:

        a, b, c = st.columns(3)

        a.metric("Promedio", f"{eficiencia.mean():.2f}/10")
        b.metric("Mediana", f"{eficiencia.median():.2f}")
        c.metric("Desviación estándar", f"{eficiencia.std():.2f}")

        frecuencias_eficiencia = (
            eficiencia.value_counts()
            .sort_index()
            .rename_axis("Calificación")
            .reset_index(name="Participantes")
        )

        fig_eficiencia = px.bar(
            frecuencias_eficiencia,
            x="Calificación",
            y="Participantes",
            text="Participantes",
            title="Distribución de las calificaciones de eficiencia",
            color="Participantes",
            color_continuous_scale="Blues"
        )

        fig_eficiencia.update_traces(textposition="outside")

        fig_eficiencia.update_layout(
            plot_bgcolor="white",
            coloraxis_showscale=False
        )

        st.plotly_chart(fig_eficiencia, use_container_width=True)

    # ---------------------------------------------
    # 10.3 DIAGNÓSTICO DE P1 A P10
    # ---------------------------------------------

    st.subheader("3. Interpretación de las variables operativas")

    resultados = []

    for variable in variables:

        promedio = df[variable].mean()

        resultados.append({
            "Código": variable[:3].upper(),
            "Variable": labels[variable],
            "Promedio": round(promedio, 2),
            "Frecuencia": nivel_escala(promedio),
            "Interpretación": clasificar_variable(variable, promedio),
            "Tipo": (
                "Situación desfavorable"
                if variable in variables_negativas
                else "Práctica evaluada"
            )
        })

    diagnostico = pd.DataFrame(resultados)

    st.dataframe(
        diagnostico[
            ["Código", "Variable", "Promedio", "Frecuencia", "Interpretación"]
        ],
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "Los intervalos de los promedios son criterios descriptivos "
        "orientativos. No constituyen categorías validadas del instrumento."
    )

    # Gráfico horizontal de resultados
    grafico_diag = diagnostico.sort_values(
        "Promedio",
        ascending=True
    )

    fig_diag = px.bar(
        grafico_diag,
        x="Promedio",
        y="Variable",
        orientation="h",
        text="Promedio",
        color="Tipo",
        color_discrete_map={
            "Situación desfavorable": "#D97757",
            "Práctica evaluada": "#2878A8"
        },
        title="Resultados promedio de las dimensiones operativas",
        range_x=[0, 5]
    )

    fig_diag.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_diag.update_layout(
        plot_bgcolor="white",
        xaxis_title="Promedio (1 a 5)",
        yaxis_title="",
        legend_title="Tipo de dimensión",
        margin=dict(l=20, r=40, t=65, b=30)
    )

    st.plotly_chart(fig_diag, use_container_width=True)

    st.caption(
        "Los colores separan las situaciones desfavorables de las "
        "prácticas evaluadas. Los promedios no deben compararse como "
        "si todos tuvieran el mismo sentido."
    )

    # ---------------------------------------------
    # 10.4 PRINCIPALES HALLAZGOS
    # ---------------------------------------------

    st.subheader("4. Principales hallazgos")

    promedio_p1 = df[variables[0]].mean()
    promedio_p2 = df[variables[1]].mean()
    promedio_p3 = df[variables[2]].mean()
    promedio_p6 = df[variables[5]].mean()
    promedio_p7 = df[variables[6]].mean()

    promedio_p5 = df[variables[4]].mean()
    promedio_p9 = df[variables[8]].mean()

    hallazgos = [
        (
            "Planificación de turnos",
            f"P1 presenta un promedio de {promedio_p1:.2f}/5. "
            "La frecuencia reportada de retrasos requiere seguimiento."
        ),
        (
            "Mantenimiento",
            f"P2 registra {promedio_p2:.2f}/5. "
            "Conviene revisar las interrupciones asociadas "
            "al mantenimiento no programado."
        ),
        (
            "Desperdicio de materia prima",
            f"P3 obtiene {promedio_p3:.2f}/5. "
            "Es importante identificar las etapas donde se producen mermas."
        ),
        (
            "Capacitación",
            f"P6 registra {promedio_p6:.2f}/5. "
            "La capacitación técnica representa una oportunidad "
            "de fortalecimiento."
        ),
        (
            "Repuestos y herramientas",
            f"P7 obtiene {promedio_p7:.2f}/5. "
            "Es conveniente revisar la disponibilidad de recursos "
            "para las actividades operativas."
        ),
        (
            "Inspección y seguridad",
            f"P5 registra {promedio_p5:.2f}/5 y P9 obtiene "
            f"{promedio_p9:.2f}/5. Si los enunciados están "
            "formulados positivamente, reflejan una frecuencia "
            "favorable de estas prácticas."
        )
    ]

    for titulo, descripcion in hallazgos:
        with st.expander(titulo):
            st.write(descripcion)

    # ---------------------------------------------
    # 10.5 CORRELACIÓN
    # ---------------------------------------------

    st.subheader("5. Relación entre eficiencia y horas perdidas")

    datos_corr = df[[p11, p12]].dropna()

    if len(datos_corr) >= 2:

        r = datos_corr[p11].corr(datos_corr[p12], method="pearson")

        st.metric("Correlación de Pearson", f"{r:.3f}")

        if abs(r) < 0.10:
            fuerza = "prácticamente nula"
        elif abs(r) < 0.30:
            fuerza = "muy débil"
        elif abs(r) < 0.50:
            fuerza = "débil a moderada"
        elif abs(r) < 0.70:
            fuerza = "moderada"
        else:
            fuerza = "fuerte"

        direccion = (
            "positiva" if r > 0
            else "negativa" if r < 0
            else "nula"
        )

        st.write(
            f"Se encontró una asociación lineal {direccion} y "
            f"{fuerza} entre las horas perdidas y la eficiencia "
            f"operativa (r = {r:.3f}). No se observa una asociación "
            "lineal importante en esta muestra. Este resultado no "
            "demuestra causalidad."
        )

    # ---------------------------------------------
    # 10.6 OPORTUNIDADES DE MEJORAMIENTO
    # ---------------------------------------------

    st.subheader("6. Estrategias de mejoramiento")

    estrategias = [
        {
            "Área": "Planificación y mantenimiento",
            "Acciones": [
                "Revisar la programación de turnos.",
                "Identificar las causas de retrasos y paradas.",
                "Implementar seguimiento preventivo de los equipos."
            ]
        },
        {
            "Área": "Control de recursos",
            "Acciones": [
                "Revisar inventarios de repuestos y herramientas.",
                "Establecer niveles mínimos de disponibilidad.",
                "Realizar seguimiento a los recursos que generan demoras."
            ]
        },
        {
            "Área": "Talento humano",
            "Acciones": [
                "Fortalecer la capacitación técnica.",
                "Realizar seguimiento a las necesidades del personal.",
                "Mejorar la comunicación entre áreas."
            ]
        },
        {
            "Área": "Materia prima y calidad",
            "Acciones": [
                "Identificar los puntos donde se generan desperdicios.",
                "Fortalecer la recepción y almacenamiento de insumos.",
                "Mantener controles e inspecciones durante el proceso."
            ]
        },
        {
            "Área": "Seguridad y tecnología",
            "Acciones": [
                "Mantener el seguimiento a los protocolos SSOMA.",
                "Revisar el funcionamiento de los equipos.",
                "Evaluar oportunidades de mejora tecnológica."
            ]
        }
    ]

    for estrategia in estrategias:
        with st.expander(estrategia["Área"]):
            for accion in estrategia["Acciones"]:
                st.markdown(f"- {accion}")

    # ---------------------------------------------
    # 10.7 CONCLUSIÓN
    # ---------------------------------------------

    st.subheader("7. Conclusión general")

    st.write(
        f"Los resultados de la encuesta aplicada a {total} participantes "
        "de Balanceados S.A.S. permiten identificar aspectos que requieren "
        "seguimiento en el funcionamiento operativo de la planta. Entre "
        f"ellos se encuentran los retrasos en la planificación de turnos "
        f"(P1 = {promedio_p1:.2f}), las interrupciones por mantenimiento "
        f"no programado (P2 = {promedio_p2:.2f}) y la disponibilidad de "
        f"repuestos y herramientas (P7 = {promedio_p7:.2f}). También se "
        f"reportó un promedio de {horas.mean():.2f} horas semanales "
        "perdidas por cuellos de botella y una calificación promedio "
        f"de eficiencia operativa de {eficiencia.mean():.2f}/10. "
        "Estos resultados constituyen una base para formular estrategias "
        "orientadas a mejorar la planificación, fortalecer el mantenimiento, "
        "optimizar el uso de los recursos y reducir los desperdicios "
        "operativos."
    )

    st.warning(
        "El diagnóstico es descriptivo y corresponde a los participantes "
        "encuestados en Balanceados S.A.S. No permite generalizar "
        "estadísticamente los resultados a todas las PYMES de Córdoba. "
        "La interpretación favorable de P4 a P10 debe confirmarse "
        "con la redacción exacta de cada pregunta."
    )

# =========================================================
# 11. PIE DE PÁGINA
# =========================================================

st.divider()

st.markdown("""
<div class="footer">
    Proyecto académico de análisis estadístico y operativo<br>
    Balanceados S.A.S. — Planta Berástegui | 2026
</div>
""", unsafe_allow_html=True)
