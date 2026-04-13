import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.title("Control de Turnos y Recargos")

# Fechas
fecha_inicio = st.date_input("Fecha inicio")
fecha_fin = st.date_input("Fecha fin")

# Parámetro editable
horas_max_semana = st.number_input("Horas máximas semanales", value=44)

# Generar rango de fechas
if fecha_inicio and fecha_fin:

    dias = pd.date_range(fecha_inicio, fecha_fin)

    data = []

    for dia in dias:
        data.append({
            "Fecha": dia.strftime("%d/%m/%Y"),
            "Día": dia.strftime("%A"),
            "Hora inicio": time(6,0),
            "Hora fin": time(14,0),
            "Tipo día": "Normal"
        })

    df = pd.DataFrame(data)

    st.subheader("Editar información por día")

    df_editado = st.data_editor(df, num_rows="dynamic")

    # Función nocturno
    def es_nocturno(hora):
        return hora >= time(19,0) or hora <= time(6,0)

    # Botón calcular
    if st.button("Calcular liquidación"):

        resultados = []

        for _, row in df_editado.iterrows():

            inicio = datetime.strptime(row["Fecha"], "%d/%m/%Y")
            inicio = datetime.combine(inicio, row["Hora inicio"])

            fin = datetime.strptime(row["Fecha"], "%d/%m/%Y")
            fin = datetime.combine(fin, row["Hora fin"])

            if fin < inicio:
                fin += timedelta(days=1)

            total_horas = (fin - inicio).seconds / 3600

            # Descuento almuerzo
            if total_horas >= 12:
                total_horas -= 1

            # Licencias
            if row["Tipo día"] == "Licencia":
                horas_normales = 7
                horas_extra = 0
            else:
                if total_horas <= 8:
                    horas_normales = total_horas
                    horas_extra = 0
                else:
                    horas_normales = 8
                    horas_extra = total_horas - 8

            # Recargos
            rec_nocturno = 0
            rec_dom = 0
            rec_noct_dom = 0

            hora_actual = inicio

            while hora_actual < fin:
                if es_nocturno(hora_actual.time()):
                    rec_nocturno += 1

                if row["Día"].lower() == "domingo":
                    rec_dom += 1

                if es_nocturno(hora_actual.time()) and row["Día"].lower() == "domingo":
                    rec_noct_dom += 1

                hora_actual += timedelta(hours=1)

            resultados.append({
                "Fecha": row["Fecha"],
                "Día": row["Día"],
                "Hora inicio": row["Hora inicio"],
                "Hora fin": row["Hora fin"],
                "Tipo día": row["Tipo día"],
                "Horas normales": horas_normales,
                "Horas extra": horas_extra,
                "Recargo nocturno": rec_nocturno,
                "Recargo dominical": rec_dom,
                "Recargo nocturno dominical": rec_noct_dom
            })

        df_final = pd.DataFrame(resultados)

        st.subheader("Resultado")
        st.dataframe(df_final)

        # Totales
        st.subheader("Totales")
        st.write("Horas normales:", df_final["Horas normales"].sum())
        st.write("Horas extra:", df_final["Horas extra"].sum())

        # Descargar
        csv = df_final.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Descargar archivo",
            csv,
            "liquidacion_turnos.csv",
            "text/csv"
        )
