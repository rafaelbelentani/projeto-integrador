import streamlit as st
from streamlit_autorefresh import st_autorefresh
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

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
    docs = db.collection("leituras").stream()

    dados = []
    for doc in docs:
        dados.append(doc.to_dict())

    df = pd.DataFrame(dados)

    if df.empty:
        return df

    df["temperatura"] = pd.to_numeric(df["temperatura"], errors="coerce")
    df["umidade"] = pd.to_numeric(df["umidade"], errors="coerce")

    return df


# =========================
# 📈 DASHBOARD
# =========================
st.title("🌡️ Monitor IoT em Tempo Real")

df = carregar_dados()


from streamlit_autorefresh import st_autorefresh

st.title("🌡️ Monitor IoT em Tempo Real")

st_autorefresh(interval=5000, key="refresh")

# =========================
# ⚠️ LEITURA ATUAL + ALERTAS
# =========================
if not df.empty:
    last = df.iloc[-1]

    temp = last["temperatura"]
    hum = last["umidade"]

    col1, col2 = st.columns(2)

    with col1:
        st.metric("🌡️ Temperatura Atual", f"{temp:.1f} °C")

    with col2:
        st.metric("💧 Umidade Atual", f"{hum:.1f} %")

    # ALERTAS
    if temp > 30:
        st.error("🔥 ALERTA: Temperatura alta!")
    elif temp < 10:
        st.warning("❄️ Temperatura muito baixa")

    if hum < 30:
        st.warning("💨 Umidade baixa")

    # =========================
    # 📊 GRÁFICO (ÚNICO)
    # =========================
    st.subheader("📊 Monitoramento")

    st.line_chart(df[["temperatura", "umidade"]])

else:
    st.warning("Sem dados ainda no Firebase")
