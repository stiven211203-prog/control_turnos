import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.set_page_config(page_title="Control de Turnos", layout="wide")

st.title("📊 Control de Turnos y Recargos")

# 📅 Entradas
fecha_inicio = st.date_input("Fecha inicio")
fecha_fin = st.date_input("Fecha fin")

turno_semana = st.selectbox("Turno de la semana", ["Mañana", "Tarde", "Noche"])

horas_max_semana = st.number_input("Horas máximas semanales", value=44)

# 📌 Días en español
dias_semana = {
    "Monday": "lunes",
    "Tuesday": "martes",
    "Wednesday": "miércoles",
    "Thursday": "jueves",
    "Friday": "viernes",
    "Saturday": "sábado",
    "Sunday": "domingo"
}

# 📌 Crear rango de fechas
fechas = pd.date_range(start=fecha_inicio, end=fecha_fin)

df = pd.DataFrame({
    "Fecha": fechas,
    "Día": [dias_semana[d.strftime("%A")] for d in fechas],
    "Tipo día": ["Normal"] * len(fechas),
    "Hora inicio": ["06:00"] * len(fechas),
    "Hora fin": ["14:00"] * len(fechas)
})

# ✏️ Tabla editable
df = st.data_editor(df, use_container_width=True)

# 🕒 Función nocturna
def es_nocturno(hora):
    return hora >= time(19, 0) or hora < time(6, 0)

# 🚀 Cálculo
if st.button("Calcular"):

    resultados = []

    for i, row in df.iterrows():

        tipo = row["Tipo día"]

        # 🟢 Día descanso
        if tipo == "Descanso":
            resultados.append({
                **row,
                "Horas normales": 0,
                "Horas extra": 0,
                "Recargo nocturno": 0,
                "Recargo dominical": 0,
                "Recargo nocturno dominical": 0
            })
            continue

        inicio = datetime.combine(row["Fecha"], datetime.strptime(row["Hora inicio"], "%H:%M").time())
        fin = datetime.combine(row["Fecha"], datetime.strptime(row["Hora fin"], "%H:%M").time())

        if fin <= inicio:
            fin += timedelta(days=1)

        total_horas = int((fin - inicio).total_seconds() / 3600)

        dia = row["Día"].lower()

        # 🟣 LÓGICA TURNOS
        if turno_semana == "Mañana":
            horas_normales = total_horas
            horas_extra = 0

        elif turno_semana == "Tarde":
            horas_normales = total_horas
            horas_extra = 0

        elif turno_semana == "Noche":

            if dia == "domingo":
                horas_normales = 9
                horas_extra = 0
            else:
                horas_normales = 7
                horas_extra = max(0, total_horas - 7)

        # 🟡 RECARGOS SOLO SOBRE HORAS NORMALES
        rec_nocturno = 0
        rec_dom = 0
        rec_noct_dom = 0

        hora_actual = inicio
        contador = 0

        while hora_actual < fin and contador < horas_normales:

            es_domingo = dia == "domingo" or tipo == "Festivo"
            es_noche = es_nocturno(hora_actual.time())

            if es_domingo and es_noche:
                rec_noct_dom += 1
            elif es_domingo:
                rec_dom += 1
            elif es_noche:
                rec_nocturno += 1

            hora_actual += timedelta(hours=1)
            contador += 1

        resultados.append({
            **row,
            "Horas normales": horas_normales,
            "Horas extra": horas_extra,
            "Recargo nocturno": rec_nocturno,
            "Recargo dominical": rec_dom,
            "Recargo nocturno dominical": rec_noct_dom
        })

    df_resultado = pd.DataFrame(resultados)

    st.subheader("📊 Resultado")
    st.dataframe(df_resultado, use_container_width=True)

    # 📥 Descargar
    st.download_button(
        "Descargar Excel",
        df_resultado.to_csv(index=False).encode("utf-8"),
        "turnos.csv",
        "text/csv"
    )
