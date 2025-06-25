import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Configuración inicial de la página
st.set_page_config(page_title="Análisis de Residuos 2.0", layout="wide")

# --------------------------------
# Función para lectura de datos
# --------------------------------
@st.cache_data
def lectura_datos():
    """
    Lee el archivo CSV y realiza transformaciones iniciales:
    - Convierte las comas a puntos en columnas numéricas
    - Retorna el DataFrame procesado
    """
    df = pd.read_csv('datos_de_entrada.csv', sep=';', encoding='ISO-8859-1')
    for col in ['QRESIDUOS_DOM', 'QRESIDUOS_NO_DOM', 'QRESIDUOS_MUN']:
        df[col] = df[col].str.replace(',', '.').astype(float)
    return df
df = lectura_datos()

# --------------------------------
# Sidebar lateral
# --------------------------------
st.sidebar.title("Menú de Análisis")
st.sidebar.markdown("---")
st.sidebar.subheader("Análisis Principales")
pagina = st.sidebar.radio(
    "Selecciona un análisis:",
    options=[
        "Inicio",
        "Residuos Domiciliarios por Departamento",
        "Residuos No Domiciliarios por Departamento",
        "Residuos Municipales por Departamento",
        "Análisis por Provincia y Tipo de Residuo",
        "Análisis por Departamento y Año",
        "Crecimiento Porcentual por Departamento"
    ],
    label_visibility="collapsed"
)

# --------------------------------
# Página de Inicio
# --------------------------------
if pagina == "Inicio":
    st.title("Bienvenido al Análisis de Residuos Municipales")
    st.markdown("""Este panel presenta un análisis visual de los residuos sólidos generados por departamento en Perú (2014).""")

    # Cálculos para el resumen
    total_nacional = df['QRESIDUOS_MUN'].sum()
    residuos_por_departamento = df.groupby('DEPARTAMENTO')['QRESIDUOS_MUN'].sum()
    max_dep = residuos_por_departamento.idxmax()
    min_dep = residuos_por_departamento.idxmin()

    # Mostrar métricas
    st.subheader("Resumen General")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total nacional", f"{total_nacional:,.0f} toneladas")
    col2.metric("Más residuos", max_dep)
    col3.metric("Menos residuos", min_dep)

    # Información adicional
    st.markdown("""
        ### Objetivo del Proyecto
        Analizar y visualizar la generación de residuos sólidos municipales por departamento en el Perú,
        para comprender mejor la distribución territorial y facilitar la toma de decisiones informadas.

        ### Integrantes del Grupo
        - Nicolt Genebrozo
        - Jhonatan Suasnabar
        ---
        """)

    # Formulario de contacto
    with st.form("formulario_contacto"):
        email = st.text_input("¿Te gustaría recibir más información? Deja tu correo electrónico:")
        enviado = st.form_submit_button("Enviar")
        if enviado:
            st.success(f"¡Gracias! Te enviaremos más información a: {email}")
    st.markdown("---")
    st.info("Usa el menú lateral para navegar por los diferentes análisis.")

# --------------------------------
# Función para gráficos por departamento
# --------------------------------
def mostrar_grafico_residuos(columna, titulo):
    datos = df.groupby('DEPARTAMENTO')[columna].sum().sort_values(ascending=False)
    st.title(titulo)
    st.sidebar.subheader("Opciones de visualización")
    mostrar_tabla = st.sidebar.checkbox("Mostrar tabla de datos", value=True)

    # Configuración del gráfico
    fig, ax = plt.subplots(figsize=(10, 6))
    datos.plot(kind='bar', color='darkcyan', ax=ax)
    ax.set_ylabel("Residuos (toneladas)")
    ax.set_xlabel("Departamento")
    ax.set_title(titulo)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

# Páginas de gráficos por tipo de residuo
if pagina == "Residuos Domiciliarios por Departamento":
    mostrar_grafico_residuos('QRESIDUOS_DOM', "Residuos Domiciliarios por Departamento")

elif pagina == "Residuos No Domiciliarios por Departamento":
    mostrar_grafico_residuos('QRESIDUOS_NO_DOM', "Residuos No Domiciliarios por Departamento")

elif pagina == "Residuos Municipales por Departamento":
    mostrar_grafico_residuos('QRESIDUOS_MUN', "Residuos Municipales por Departamento")

# --------------------------------
# Análisis por Provincia y Tipo de Residuo
# --------------------------------
if pagina == "Análisis por Provincia y Tipo de Residuo":
    st.title("Residuos per cápita por Distrito")
    st.markdown(
        "Selecciona un departamento, una provincia, un año y el tipo de residuo para ver la generación por persona.")

    # Filtros en el sidebar
    st.sidebar.subheader("Filtros de Análisis")
    deptos = sorted(df['DEPARTAMENTO'].unique())
    departamento = st.sidebar.selectbox("Departamento:", deptos)
    provincias = sorted(df[df['DEPARTAMENTO'] == departamento]['PROVINCIA'].unique())
    provincia = st.sidebar.selectbox("Provincia:", provincias)
    periodos = sorted(df[df['DEPARTAMENTO'] == departamento]['PERIODO'].unique())
    periodo = st.sidebar.selectbox("Periodo:", periodos)
    tipo_residuo = st.sidebar.radio("Tipo de residuo:",options=["Domiciliario", "No domiciliario", "Municipal"],horizontal=True)

    # Mapeo de tipos de residuo a columnas
    columna_residuo = {"Domiciliario": "QRESIDUOS_DOM","No domiciliario": "QRESIDUOS_NO_DOM","Municipal": "QRESIDUOS_MUN"}[tipo_residuo]

    # Aplicar los filtros
    df_filtrado = df[(df['DEPARTAMENTO'] == departamento) & (df['PROVINCIA'] == provincia) & (df['PERIODO'] == periodo)]

    # Cálculo de residuos per cápita
    df_filtrado = df_filtrado[df_filtrado['POB_TOTAL'] > 0].copy()
    df_filtrado['RESIDUO_PERCAPITA'] = (df_filtrado[columna_residuo] * 1000) / df_filtrado['POB_TOTAL']
    resultado = df_filtrado[['DISTRITO', 'RESIDUO_PERCAPITA']].sort_values(by='RESIDUO_PERCAPITA', ascending=False)

    # Mostrar resultados
    st.subheader(f"{tipo_residuo} - Provincia de {provincia} ({departamento}) - {periodo}")

    # Configuración del gráfico
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(resultado['DISTRITO'], resultado['RESIDUO_PERCAPITA'], color='mediumslateblue')
    ax.set_ylabel("kg por persona")
    ax.set_xlabel("Distrito")
    ax.set_title(f"Generación de residuos {tipo_residuo.lower()} por persona")
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    # Mostrar tabla de datos
    st.markdown("### Tabla de datos")
    st.dataframe(resultado.rename(columns={"DISTRITO": "Distrito", "RESIDUO_PERCAPITA": "kg por persona"}))

# --------------------------------
# Análisis por Departamento y Año
# --------------------------------
if pagina == "Análisis por Departamento y Año":
    st.title("Análisis por Departamento y Año")
    st.markdown("Selecciona un departamento y un periodo para visualizar la generación de residuos por tipo.")

    # Filtros del sidebar
    st.sidebar.subheader("Filtros de análisis")
    departamentos = sorted(df['DEPARTAMENTO'].unique())
    departamento_seleccionado = st.sidebar.selectbox("Departamento:", departamentos)
    periodos = sorted(df['PERIODO'].unique())
    periodo_seleccionado = st.sidebar.selectbox("Periodo:", periodos)
    df_filtrado = df[(df['DEPARTAMENTO'] == departamento_seleccionado) & (df['PERIODO'] == periodo_seleccionado)]
    if not df_filtrado.empty:
        # Cálculos de totales
        total_dom = df_filtrado['QRESIDUOS_DOM'].sum()
        total_nodom = df_filtrado['QRESIDUOS_NO_DOM'].sum()
        total_mun = df_filtrado['QRESIDUOS_MUN'].sum()

        # Preparar datos para visualización
        residuos = {"Domiciliario": total_dom,"No Domiciliario": total_nodom,"Municipal": total_mun}

        # Mostrar resultados
        st.subheader(f"{departamento_seleccionado} - Periodo {periodo_seleccionado}")

        # Configuración del gráfico
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(residuos.keys(), residuos.values(), color=['steelblue', 'indianred', 'darkgreen'])
        ax.set_ylabel("Toneladas")
        ax.set_title("Generación de Residuos por Tipo")
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        st.pyplot(fig)

        # Mostrar tabla de datos
        st.markdown("### Tabla de Datos")
        st.dataframe(pd.DataFrame.from_dict(residuos, orient='index', columns=["Residuos (toneladas)"]))
    else:
        st.warning("No se encontraron datos para el departamento y periodo seleccionados.")

# --------------------------------
# Análisis de Crecimiento Porcentual por Departamento
# --------------------------------
if pagina == "Crecimiento Porcentual por Departamento":
    st.title("Crecimiento Porcentual de Residuos por Departamento (2014-2022)")
    st.markdown("""
    Este análisis muestra el crecimiento porcentual de residuos generados por departamento entre los años 2014 y 2022.

    **Fórmula:**  
    Crecimiento porcentual de residuos = ((Residuos 2022 - Residuos 2014) / Residuos 2014) * 100
    """)

    # Selector de tipo de residuo
    tipo_residuo = st.selectbox("Selecciona el tipo de residuo:",["Domiciliario", "No Domiciliario", "Municipal"])

    # Mapeo a columna
    columna_residuo = {"Domiciliario": "QRESIDUOS_DOM","No Domiciliario": "QRESIDUOS_NO_DOM","Municipal": "QRESIDUOS_MUN"}[tipo_residuo]

    # Verifica si es necesario convertir a float
    if df[columna_residuo].dtype == 'object':
        df[columna_residuo] = df[columna_residuo].str.replace(',', '.').astype(float)

    # Filtrar datos de 2014 y 2022
    df_2014 = df[df['PERIODO'] == 2014].groupby('DEPARTAMENTO')[columna_residuo].sum()
    df_2022 = df[df['PERIODO'] == 2022].groupby('DEPARTAMENTO')[columna_residuo].sum()

    # Unir y calcular crecimiento
    crecimiento = pd.concat([df_2014, df_2022], axis=1, keys=['2014', '2022']).dropna()
    crecimiento['Crecimiento %'] = ((crecimiento['2022'] - crecimiento['2014']) / crecimiento['2014']) * 100
    crecimiento = crecimiento.sort_values('Crecimiento %', ascending=False)

    # Gráfico
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(crecimiento.index, crecimiento['Crecimiento %'], color='seagreen')
    ax.set_ylabel("Crecimiento porcentual (%)")
    ax.set_xlabel("Departamento")
    ax.set_title(f"Crecimiento porcentual de residuos {tipo_residuo.lower()} (2014 a 2022)")
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    st.pyplot(fig)

    # Tabla
    st.markdown("### Tabla de crecimiento")
    st.dataframe(crecimiento.reset_index())
