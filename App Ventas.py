import yfinance as yf
import pandas as pd
import datetime
import streamlit as st

# Lista de empresas con sus respectivos tickers
empresas = {
    "IBE.MC": "Iberdrola, S.A.",
    "ITX.MC": "Industria de Diseño Textil, S.A.",
    "SAN.MC": "Banco Santander, S.A.",
    "AAPL": "Apple Inc.",
    "CRM": "Salesforce, Inc.",
    "PANW": "Palo Alto Networks, Inc.",
    "UNH": "UnitedHealth Group Incorporated",
    "UBER": "Uber Technologies, Inc.",
    "LLY": "Eli Lilly and Company",
    "MSTR": "Microstrategy incorporated",
    "CHTR": "Chater Spectrum",
    "LULU": "Lululemon",
    "TJX": "The TJX Companies",
    "JD": "JD.COM",
    "PLTR": "Palantir",
    "TTWO": "TAKE-TWO INTERACTIVE SOFTWARE",
    "MELI": "MERCADO LIBRE",
    "CHTR": "CHARTER SPECTRUM",
    "MAP.MC": "MAPFRE",
    "ORLY": "OREILLY",
    "XOM": "EXXON",
    "ACS.MC": "ACS",
    "ANA.MC": "ACCIONA",
    "AENA.MC": "AENA"
}

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=60)
interval = "1h"

# Función para ejecutar el screener
def ejecutar_screener():
    resultados = []  # Limpiar los resultados previos

    # Ejecutar el análisis para cada empresa
    for ticker, nombre in empresas.items():
        try:
            df = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)
            if df.empty or len(df) < 20:
                resultados.append({"Ticker": ticker, "Nombre": nombre, "Resultado": "ℹ️ Datos insuficientes"})
                continue

            delta = df["Close"].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.ewm(alpha=1/14, min_periods=14).mean()
            avg_loss = loss.ewm(alpha=1/14, min_periods=14).mean()
            rs = avg_gain / avg_loss
            df["RSI"] = 100 - (100 / (1 + rs))

            resultado = "ℹ️ No se detectaron señales relevantes"

            for i in range(4, 0, -1):
                try:
                    rsi_val = df["RSI"].iloc[-i].item()
                    if rsi_val <= 60:
                        continue

                    h_prev = df["High"].iloc[-i - 1].item()
                    h_curr = df["High"].iloc[-i].item()
                    h_next = df["High"].iloc[-i + 1].item()
                    h_ref  = df["High"].iloc[-i - 2].item()

                    is_peak = h_curr > h_prev and h_curr > h_next
                    is_lh = is_peak and h_curr < h_ref * 0.995

                    if is_lh:
                        resultado = "✅ Señal confirmada"
                        break
                    elif is_peak:
                        resultado = "🚩 Posible techo (pero no LH)"
                        break
                    else:
                        resultado = "ℹ️ RSI alto pero sin pico"

                except:
                    continue

            resultados.append({"Ticker": ticker, "Nombre": nombre, "Resultado": resultado})

        except Exception as e:
            resultados.append({"Ticker": ticker, "Nombre": nombre, "Resultado": "❌ Error al procesar"})

    return resultados

# Crear la interfaz con Streamlit
st.title("Análisis de Acciones - Screener")

# Botón para ejecutar el screener
if st.button("Ejecutar Screener"):
    with st.spinner("Ejecutando análisis..."):
        resultados = ejecutar_screener()
        if resultados:
            st.success("Análisis completado!")
            # Mostrar los resultados en una tabla
            df_out = pd.DataFrame(resultados)
            st.dataframe(df_out)  # Mostrar como tabla interactiva
            # También puedes guardar los resultados en un archivo CSV
            df_out.to_csv("resultados_screener.csv", index=False)
            st.download_button(label="Descargar resultados", data="resultados_screener.csv", file_name="resultados_screener.csv")
        else:
            st.warning("No se detectaron señales relevantes.")

