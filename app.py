import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("Control de Turnos y Recargos")

# Inputs
fecha_inicio = st.date_input("Fecha inicio")
fecha_fin = st.date_input("Fecha fin")

turno = st.selectbox("Turno", ["Mañana", "Tarde", "Madrugada"])

tipo_dia = st.selectbox("Tipo de día", ["Normal", "Licencia", "Festivo"])

hora_inicio = st.time_input("Hora inicio")

horas_max_semana = st.number_input("Horas máximas semanales", value=44)

if st.button("Calcular"):

    dias = pd.date_range(fecha_inicio, fecha_fin)
    resultados = []

    for dia in dias:

        horas_normales = 0
        horas_extra = 0

        if tipo_dia == "Licencia":
            horas_normales = 7

        else:
            if turno == "Madrugada":
                horas_normales = 9
                horas_extra = 3
            elif turno == "Mañana":
                horas_normales = 8
            else:
                horas_normales = 8

        # Descuento almuerzo
        if horas_normales + horas_extra >= 12:
            horas_normales -= 1

        resultados.append({
            "Fecha": dia,
            "Turno": turno,
            "Tipo día": tipo_dia,
            "Horas normales": horas_normales,
            "Horas extra": horas_extra
        })

    df = pd.DataFrame(resultados)

    st.dataframe(df)

    st.write("Total horas normales:", df["Horas normales"].sum())
    st.write("Total horas extra:", df["Horas extra"].sum())
