import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
from streamlit_autorefresh import st_autorefresh

# =========================
# 🔐 FIREBASE INIT
# =========================


@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(st.secrets["firebase"])
        firebase_admin.initialize_app(cred)

    return firestore.client()



# =========================
# 🔥 CONEXÃO SEGURA
# =========================
try:
    db = init_firebase()
except Exception as e:
    st.error(f"Erro Firebase: {e}")
    st.stop()


# =========================
# 📊 CARREGAR DADOS
# =========================
@st.cache_data(ttl=10)
def carregar_dados():
    if db is None:
        return pd.DataFrame()

    docs = db.collection("leituras").stream()

    dados = [doc.to_dict() for doc in docs]

    if len(dados) == 0:
        return pd.DataFrame()

    return pd.DataFrame(dados)


# =========================
# 📈 DASHBOARD
# =========================
st.title("🌡️ Monitor IoT em Tempo Real")

# 🔄 auto refresh
st_autorefresh(interval=5000, key="refresh")

df = carregar_dados()

if not df.empty:
    ultima = df.iloc[-1]

    # 🔥 leitura atual
    st.subheader("📡 Leitura Atual")
    st.metric("Temperatura", f"{ultima.get('temperatura', 0)} °C")
    st.metric("Umidade", f"{ultima.get('umidade', 0)} %")

    # 📊 gráfico simples
    st.subheader("📊 Variação")
    st.line_chart(df[["temperatura", "umidade"]])

else:
    st.warning("Sem dados ainda no Firebase")
