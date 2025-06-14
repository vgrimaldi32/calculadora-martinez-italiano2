import streamlit as st
import pandas as pd
from PIL import Image

# Cargar logo
image = Image.open("logo_para_app.png")
st.image(image, use_container_width=True)

# Título
st.title("Calculadora MARTINEZ/ITALIANO")
st.header("Comparación de movilidad según ANSeS vs Justicia")

# Entradas del usuario
caso = st.text_input("Nombre del caso")
haber_inicial = st.number_input("Ingrese el haber base", min_value=0.0, format="%f")
fecha_base = st.text_input("Fecha del haber base (YYYY-MM)")

# Validar formato de fecha
if len(fecha_base) != 7 or fecha_base[4] != "-":
    st.error("Ingresá la fecha en formato YYYY-MM (ejemplo: 2020-04)")
else:
    try:
        # Cargar archivos CSV
        df_anses = pd.read_csv("movilidad_anses.csv", sep=";")
        df_justicia = pd.read_csv("movilidad_martinez_italiano.csv", sep=";")

        # Convertir fechas a datetime
        df_anses["Fecha"] = pd.to_datetime(df_anses["Fecha"], format="%Y-%m")
        df_justicia["Fecha"] = pd.to_datetime(df_justicia["Fecha"], format="%Y-%m")

        # Ordenar por fecha
        df_anses = df_anses.sort_values("Fecha")
        df_justicia = df_justicia.sort_values("Fecha")

        # Convertir fecha_base
        fecha_inicio = pd.to_datetime(fecha_base, format="%Y-%m")

        # Filtrar desde la fecha ingresada
        coef_anses = df_anses[df_anses["Fecha"] >= fecha_inicio].copy()
        coef_justicia = df_justicia[df_justicia["Fecha"] >= fecha_inicio].copy()

        # Calcular coeficiente de marzo 2020 si falta en ANSES
        mask_marzo2020 = df_anses["Fecha"] == pd.to_datetime("2020-03")
        if mask_marzo2020.sum() == 0:
            coef_marzo = pd.DataFrame.from_dict({
                "Fecha": [pd.to_datetime("2020-03")],
                "Coeficiente": [1 + ((1500 / haber_inicial) + 0.023)]
            })
            coef_anses = pd.concat([coef_marzo, coef_anses], ignore_index=True)
            coef_anses = coef_anses.sort_values("Fecha")

        # Aplicar coeficientes acumulativos
        coef_total_anses = coef_anses["Coeficiente"].astype(float).prod()
        coef_total_justicia = coef_justicia["Coeficiente"].astype(float).prod()

        # Calcular haberes actualizados
        haber_anses = haber_inicial * coef_total_anses
        haber_justicia = haber_inicial * coef_total_justicia

        # Mostrar resultados
        st.subheader("Resultados:")
        st.markdown(f"**Caso:** {caso}")
        st.markdown(f"**Haber actualizado según ANSeS:** ${haber_anses:,.2f}")
        st.markdown(f"**Haber actualizado según Justicia:** ${haber_justicia:,.2f}")
        diferencia = haber_justicia - haber_anses
        porcentaje = (diferencia / haber_anses * 100) if haber_anses > 0 else 0
        st.markdown(f"**Diferencia:** ${diferencia:,.2f} ({porcentaje:.2f}%)")

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
