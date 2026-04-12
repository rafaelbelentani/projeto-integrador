import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# =========================
# 🔐 FIREBASE INIT
# =========================
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred)

    return firestore.client()

db = init_firebase()

# =========================
# 📊 CARREGAR DADOS
# =========================
@st.cache_data(ttl=5)
def carregar_dados():
    docs = (
        db.collection("leituras")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(50)
        .stream()
    )

    dados = [doc.to_dict() for doc in docs]

    if len(dados) == 0:
        return pd.DataFrame()

    df = pd.DataFrame(dados)

    df["temperatura"] = pd.to_numeric(df["temperatura"], errors="coerce")
    df["umidade"] = pd.to_numeric(df["umidade"], errors="coerce")

    return df

# =========================
# 📈 DASHBOARD
# =========================
st.title("🌡️ Monitor IoT em Tempo Real")

# 🔄 AUTO REFRESH
st_autorefresh(interval=5000, key="refresh")

# =========================
# 📦 DADOS
# =========================
df = carregar_dados()

# proteção contra erro
if df is None or df.empty:
    st.warning("Sem dados ainda no Firebase")
    st.stop()

# =========================
# ⚡ LEITURA ATUAL
# =========================
last = df.iloc[0]

col1, col2 = st.columns(2)

with col1:
    st.metric("🌡️ Temperatura Atual", f"{last['temperatura']:.1f} °C")

with col2:
    st.metric("💧 Umidade Atual", f"{last['umidade']:.1f} %")

# =========================
# ⚠️ ALERTAS
# =========================
if last["temperatura"] > 30:
    st.error("🔥 ALERTA: Temperatura alta!")

elif last["temperatura"] < 10:
    st.warning("❄️ Temperatura muito baixa")

if last["umidade"] < 30:
    st.warning("💨 Umidade baixa")

# =========================
# 📊 GRÁFICO (1 SÓ)
# =========================
st.subheader("📊 Monitoramento")

st.line_chart(df[["temperatura", "umidade"]])
