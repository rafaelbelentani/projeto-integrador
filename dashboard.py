import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from streamlit_autorefresh import st_autorefresh

# ==============================
# 🔄 AUTO REFRESH (10 segundos)
# ==============================
st_autorefresh(interval=10000, key="refresh")

# ==============================
# 🔐 FIREBASE (corrigido)
# ==============================
if not firebase_admin._apps:
    cred = credentials.Certificate("PI5.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ==============================
# 🎨 CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(
    page_title="Dashboard IoT",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard IoT - Temperatura e Umidade")

# ==============================
# 📥 CARREGAR DADOS
# ==============================
@st.cache_data(ttl=10)
def carregar_dados():
    docs = db.collection("leituras").order_by("timestamp").stream()

    dados = []
    for doc in docs:
        d = doc.to_dict()

        if (
            d.get("temperatura") is not None and
            d.get("umidade") is not None and
            0 < d["temperatura"] < 50 and
            0 < d["umidade"] < 100
        ):
            dados.append({
                "timestamp": d["timestamp"],
                "temperatura": d["temperatura"],
                "umidade": d["umidade"]
            })

    return pd.DataFrame(dados)

df = carregar_dados()

# ==============================
# 📊 PROCESSAMENTO
# ==============================
if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    temp_atual = df["temperatura"].iloc[-1]
    umid_atual = df["umidade"].iloc[-1]

    # ==============================
    # 📈 MÉTRICAS (CARDS)
    # ==============================
    col1, col2, col3 = st.columns(3)

    col1.metric("🌡️ Temp Atual", f"{temp_atual:.1f} °C")
    col2.metric("💧 Umidade Atual", f"{umid_atual:.1f} %")
    col3.metric("📊 Temp Média", f"{df['temperatura'].mean():.1f} °C")

    # ==============================
    # 🚨 ALERTA (AGORA FUNCIONA)
    # ==============================
    st.subheader("🚨 Status da Temperatura")

    if temp_atual > 28:
        st.error(f"🔥 ALERTA: Temperatura alta! ({temp_atual:.1f} °C)")
    elif temp_atual > 25:
        st.warning(f"⚠️ Atenção: Temperatura moderada ({temp_atual:.1f} °C)")
    else:
        st.success(f"✅ Temperatura normal ({temp_atual:.1f} °C)")

    # ==============================
    # 📉 SUAVIZAÇÃO (MÉDIA MÓVEL)
    # ==============================
    df["temp_suave"] = df["temperatura"].rolling(5).mean()
    df["umid_suave"] = df["umidade"].rolling(5).mean()

    # ==============================
    # 📊 GRÁFICOS
    # ==============================
    st.subheader("📈 Temperatura ao longo do tempo")
    st.line_chart(df.set_index("timestamp")["temp_suave"])

    st.subheader("💧 Umidade ao longo do tempo")
    st.line_chart(df.set_index("timestamp")["umid_suave"])

else:
    st.warning("Sem dados válidos ainda...")

# ==============================
# 📌 RODAPÉ
# ==============================
st.caption("Atualização automática a cada 10 segundos 🚀")
