import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.title("Control de Turnos y Recargos")

# -------------------------
# CONFIGURACIÓN
# -------------------------
horas_max_semana = st.number_input("Horas máximas semanales", value=44)

# -------------------------
# FECHAS
# -------------------------
fecha_inicio = st.date_input("Fecha inicio")
fecha_fin = st.date_input("Fecha fin")

# -------------------------
# TURNO GENERAL
# -------------------------
turno_semana = st.selectbox("Turno de la semana", ["Mañana", "Tarde", "Noche"])

# -------------------------
# GENERAR DÍAS
# -------------------------
if fecha_inicio and fecha_fin:

    dias = pd.date_range(fecha_inicio, fecha_fin)

    data = []

    for dia in dias:

        nombre_dia = dia.strftime("%A").lower()

        # -------------------------
        # HORARIOS SEGÚN TURNO
        # -------------------------
        if turno_semana == "Mañana":

            hora_inicio = time(6, 0)

            if nombre_dia in ["miércoles", "sabado", "sábado"]:
                hora_fin = time(14, 0)
            else:
                hora_fin = time(13, 0)

        elif turno_semana == "Tarde":

            if nombre_dia == "sábado":
                hora_inicio = time(6, 0)
                hora_fin = time(10, 0)
            else:
                hora_inicio = time(13, 0)
                hora_fin = time(21, 0)

        else:  # NOCHE

            if nombre_dia == "domingo":
                hora_inicio = time(21, 0)
            else:
                hora_inicio = time(21, 0)

            hora_fin = time(6, 0)

        data.append({
            "Fecha": dia.strftime("%d/%m/%Y"),
            "Día": dia.strftime("%A"),
            "Hora inicio": hora_inicio,
            "Hora fin": hora_fin,
            "Tipo día": "Normal"
        })

    df = pd.DataFrame(data)

    st.subheader("Editar información por día")
    df_editado = st.data_editor(df, num_rows="dynamic")

    # -------------------------
    # FUNCIONES
    # -------------------------
    def es_nocturno(hora):
        return hora >= time(19, 0) or hora <= time(6, 0)

    # -------------------------
    # CALCULAR
    # -------------------------
    if st.button("Calcular liquidación"):

        resultados = []

        for _, row in df_editado.iterrows():

            # DESCANSO
            if row["Tipo día"] == "Descanso":
                resultados.append({
                    "Fecha": row["Fecha"],
                    "Día": row["Día"],
                    "Horas normales": 0,
                    "Horas extra": 0,
                    "Recargo nocturno": 0,
                    "Recargo dominical": 0,
                    "Recargo nocturno dominical": 0
                })
                continue

            inicio = datetime.strptime(row["Fecha"], "%d/%m/%Y")
            inicio = datetime.combine(inicio, row["Hora inicio"])

            fin = datetime.strptime(row["Fecha"], "%d/%m/%Y")
            fin = datetime.combine(fin, row["Hora fin"])

            if fin < inicio:
                fin += timedelta(days=1)

            total_horas = (fin - inicio).seconds / 3600

            # -------------------------
            # TURNO NOCHE ESPECIAL
            # -------------------------
            horas_normales = 0
            horas_extra = 0

            if turno_semana == "Noche":

                dia_semana = row["Día"].lower()

                if dia_semana == "domingo":
                    horas_normales = 9
                    horas_extra = max(0, total_horas - 9)

                else:
                    horas_normales = 7
                    horas_extra = max(0, total_horas - 7)

            else:

                # Almuerzo
                if total_horas >= 12:
                    total_horas -= 1

                if row["Tipo día"] == "Licencia":
                    horas_normales = 7
                else:
                    if total_horas <= 8:
                        horas_normales = total_horas
                    else:
                        horas_normales = 8
                        horas_extra = total_horas - 8

            # -------------------------
            # RECARGOS
            # -------------------------
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

        st.subheader("Totales")
        st.write("Horas normales:", df_final["Horas normales"].sum())
        st.write("Horas extra:", df_final["Horas extra"].sum())
