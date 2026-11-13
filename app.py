import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Balanceados S.A.S. | Análisis operativo", page_icon="📊", layout="wide")

st.title("Análisis estadístico y gráfico")
st.subheader("Balanceados S.A.S. — Planta Berástegui")
st.caption("Diagnóstico de tiempos muertos, mermas operativas y optimización operativa")

DATA_PATH = Path(__file__).parent / "datos_balanceados_anonimizados.csv"

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH)
    return data

df = load_data()
id_col = "encuestado"
questions = [c for c in df.columns if c != id_col]
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

st.info("Base anonimizada: se excluyeron nombres, documentos de identidad, cargos y fechas personales. El análisis utiliza 50 registros; la fila de promedio general del archivo original no se cuenta como encuestado.")

# Sidebar filters
st.sidebar.header("Explorar resultados")
selected = st.sidebar.multiselect(
    "Variables para comparar",
    options=questions,
    default=questions[:10],
    format_func=lambda x: labels.get(x, x)
)
if not selected:
    selected = questions

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Encuestados", f"{len(df)}")
c2.metric("Variables", "12")
c3.metric("Promedio P11", f"{df['P11_eficiencia_operativa_1_10'].mean():.2f} / 10")
c4.metric("Promedio P12", f"{df['P12_horas_semanales_cuellos_botella'].mean():.2f} h/semana")

tab1, tab2, tab3, tab4 = st.tabs(["Resumen", "Distribución de respuestas", "Relaciones entre variables", "Datos y metodología"])

with tab1:
    st.markdown("### Promedio por variable")
    means = df[questions].mean().rename_axis("variable").reset_index(name="promedio")
    means["nombre"] = means["variable"].map(labels)
    fig = px.bar(means, x="nombre", y="promedio", text_auto=".2f",
                 labels={"nombre": "Variable", "promedio": "Promedio"},
                 title="Promedios descriptivos de las 12 variables")
    fig.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Los promedios de P1–P10 se muestran como estadísticos descriptivos de las respuestas registradas. No se asigna una interpretación de 'mejor' o 'peor' sin disponer de la codificación completa de cada escala.")

    st.markdown("### Estadísticos descriptivos")
    desc = df[questions].describe().T
    desc.index = [labels.get(i, i) for i in desc.index]
    desc = desc.rename(columns={"count":"N","mean":"Media","std":"Desv. estándar","min":"Mínimo","25%":"P25","50%":"Mediana","75%":"P75","max":"Máximo"})
    st.dataframe(desc.round(2), use_container_width=True)

with tab2:
    st.markdown("### Distribución de respuestas")
    variable = st.selectbox("Selecciona una variable", questions, format_func=lambda x: labels.get(x, x))
    freq = df[variable].value_counts().sort_index().rename_axis("Respuesta").reset_index(name="Frecuencia")
    freq["Porcentaje"] = 100 * freq["Frecuencia"] / len(df)
    fig = px.bar(freq, x="Respuesta", y="Frecuencia", text="Frecuencia",
                 hover_data={"Porcentaje":":.1f"},
                 title=f"Frecuencia de respuestas — {labels[variable]}")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(freq.assign(Porcentaje=freq["Porcentaje"].round(1)), hide_index=True, use_container_width=True)

    st.markdown("### Comparación de variables seleccionadas")
    comp = df[selected].melt(var_name="Variable", value_name="Valor")
    comp["Variable"] = comp["Variable"].map(labels)
    fig2 = px.box(comp, x="Variable", y="Valor", points="all", title="Variabilidad de las respuestas")
    fig2.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.markdown("### Matriz de correlación")
    corr_cols = st.multiselect("Variables incluidas en la correlación", questions,
                               default=questions)
    if len(corr_cols) >= 2:
        corr = df[corr_cols].corr(numeric_only=True)
        corr.index = [labels.get(x, x) for x in corr.index]
        corr.columns = [labels.get(x, x) for x in corr.columns]
        fig = px.imshow(corr, text_auto=".2f", aspect="auto", zmin=-1, zmax=1,
                        color_continuous_scale="RdBu_r",
                        title="Correlaciones de Pearson (exploratorias)")
        st.plotly_chart(fig, use_container_width=True)
        st.warning("La correlación describe asociación lineal en esta muestra; no demuestra causalidad. En variables ordinales, su interpretación debe hacerse con cautela.")
    else:
        st.warning("Selecciona al menos dos variables para calcular la matriz.")

    st.markdown("### Eficiencia operativa y horas perdidas")
    fig = px.scatter(df, x="P12_horas_semanales_cuellos_botella",
                     y="P11_eficiencia_operativa_1_10", trendline="ols",
                     labels={"P12_horas_semanales_cuellos_botella":"Horas semanales por cuellos de botella",
                             "P11_eficiencia_operativa_1_10":"Eficiencia operativa (1–10)"},
                     title="Relación exploratoria entre horas perdidas y eficiencia")
    st.plotly_chart(fig, use_container_width=True)
    r = df["P12_horas_semanales_cuellos_botella"].corr(df["P11_eficiencia_operativa_1_10"])
    st.write(f"Coeficiente de correlación de Pearson: **{r:.3f}**.")
    st.caption("Este resultado es descriptivo y no permite concluir que una variable cause cambios en la otra.")

with tab4:
    st.markdown("### Base de datos anonimizada")
    st.write("Se presentan identificadores de encuesta y las 12 variables cuantitativas. No se incluyen datos personales.")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Descargar base anonimizada (CSV)", df.to_csv(index=False).encode("utf-8-sig"),
                       file_name="datos_balanceados_anonimizados.csv", mime="text/csv")
    st.markdown("### Consideraciones metodológicas")
    st.markdown("""
    - Unidad de análisis: registro de cada jefe o líder participante.
    - Tamaño de la base: 50 registros.
    - Variables: P1 a P10, P11 (escala 1–10) y P12 (horas semanales promedio perdidas por cuellos de botella).
    - Se calcularon frecuencias, porcentajes, medidas descriptivas y correlaciones exploratorias.
    - La fila de promedio general que aparece al final de la hoja original se excluyó para evitar duplicar información.
    - La base publicada está anonimizada. El acta de consentimientos no debe cargarse al repositorio público porque contiene información personal.
    """)
    st.caption("Fuente: matriz cuantitativa suministrada para el proyecto de investigación de Balanceados S.A.S. — Planta Berástegui.")
