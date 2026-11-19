import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://bc-api:8000").rstrip("/")
API_KEY = os.getenv("API_KEY", "")
TITLE = os.getenv("APP_TITLE", "Aide au diagnostic - Breast Cancer")
HEADERS = {"X-API-Key": API_KEY}

st.set_page_config(page_title=TITLE, page_icon="🩺", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

    :root {
      --ink: #1a2332;
      --muted: #5c6b7a;
      --bg1: #e8f0f4;
      --bg2: #f4f7f5;
      --accent: #0d7377;
      --accent-dark: #095456;
      --warn: #b33a3a;
      --ok: #2d6a4f;
      --card: rgba(255,255,255,0.72);
      --line: rgba(26,35,50,0.08);
    }

    html, body, [class*="css"] {
      font-family: "DM Sans", sans-serif;
      color: var(--ink);
    }

    .stApp {
      background:
        radial-gradient(1200px 600px at 10% -10%, #c5dde6 0%, transparent 55%),
        radial-gradient(900px 500px at 100% 0%, #d5e8df 0%, transparent 50%),
        linear-gradient(165deg, var(--bg1), var(--bg2));
    }

    .block-container {
      padding-top: 1.6rem;
      padding-bottom: 2.5rem;
      max-width: 1100px;
    }

    #MainMenu, footer, header { visibility: hidden; }

    .hero-brand {
      font-family: "Fraunces", Georgia, serif;
      font-size: clamp(1.9rem, 3.2vw, 2.6rem);
      font-weight: 700;
      letter-spacing: -0.02em;
      line-height: 1.15;
      margin: 0 0 0.35rem 0;
      color: var(--ink);
    }
    .hero-sub {
      color: var(--muted);
      font-size: 0.98rem;
      margin: 0 0 1.4rem 0;
      max-width: 38rem;
    }
    .badge {
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--accent-dark);
      background: rgba(13,115,119,0.12);
      border: 1px solid rgba(13,115,119,0.22);
      padding: 0.28rem 0.65rem;
      margin-bottom: 0.75rem;
    }

    .metric-row {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 0.75rem;
      margin-bottom: 1.25rem;
    }
    .metric-card {
      background: var(--card);
      backdrop-filter: blur(8px);
      border: 1px solid var(--line);
      padding: 0.9rem 1rem;
      border-left: 3px solid var(--accent);
    }
    .metric-card .label {
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
      margin-bottom: 0.25rem;
    }
    .metric-card .value {
      font-family: "Fraunces", Georgia, serif;
      font-size: 1.35rem;
      font-weight: 600;
      color: var(--ink);
    }

    .result-box {
      background: var(--card);
      border: 1px solid var(--line);
      padding: 1.1rem 1.25rem;
      margin-top: 1rem;
    }
    .result-malin {
      border-left: 4px solid var(--warn);
    }
    .result-benin {
      border-left: 4px solid var(--ok);
    }
    .result-title {
      font-family: "Fraunces", Georgia, serif;
      font-size: 1.45rem;
      font-weight: 700;
      margin: 0 0 0.35rem 0;
    }
    .result-meta {
      color: var(--muted);
      font-size: 0.88rem;
    }

    div[data-testid="stTabs"] button {
      font-weight: 600;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
      color: var(--accent-dark) !important;
    }

    .stButton > button[kind="primary"] {
      background: var(--accent) !important;
      border: none !important;
      color: white !important;
      font-weight: 600 !important;
      padding: 0.55rem 1.2rem !important;
      border-radius: 2px !important;
    }
    .stButton > button[kind="primary"]:hover {
      background: var(--accent-dark) !important;
    }

    @media (max-width: 800px) {
      .metric-row { grid-template-columns: 1fr 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="badge">TP Kubernetes · démo pédagogique</div>
    <h1 class="hero-brand">{TITLE}</h1>
    <p class="hero-sub">
      Classification malin / bénin et prédiction de la surface moyenne —
      pas un outil médical. Les modèles sont servis par l’API déployée sur Minikube.
    </p>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=30)
def get_info():
    r = requests.get(f"{API_URL}/api/info", timeout=3)
    r.raise_for_status()
    return r.json()


try:
    info = get_info()
except Exception as exc:  # noqa: BLE001
    st.error(f"API injoignable ou modèles pas encore prêts ({API_URL}) : {exc}")
    st.info("Vérifiez : kubectl get pods,svc ; le Job d'entraînement a-t-il terminé ?")
    st.stop()

st.markdown(
    f"""
    <div class="metric-row">
      <div class="metric-card"><div class="label">Version API</div>
        <div class="value">{info["app_version"]}</div></div>
      <div class="metric-card"><div class="label">Modèles</div>
        <div class="value">{info["model_version"]} · {info["algo"]}</div></div>
      <div class="metric-card"><div class="label">Accuracy classif.</div>
        <div class="value">{info["classification"]["metrics"]["accuracy"]}</div></div>
      <div class="metric-card"><div class="label">R² régression</div>
        <div class="value">{info["regression"]["metrics"]["r2"]}</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_clf, tab_reg, tab_stats = st.tabs(
    ["Classification (malin / bénin)", "Régression (mean area)", "Statistiques"]
)


def feature_form(prefix: str, features: list, defaults: dict) -> dict:
    values = {}
    cols = st.columns(3)
    for i, f in enumerate(features):
        values[f] = cols[i % 3].number_input(
            f, value=float(defaults[f]), format="%.5f", key=f"{prefix}-{f}"
        )
    return values


def post(path: str, features: dict):
    r = requests.post(
        f"{API_URL}{path}", json={"features": features}, headers=HEADERS, timeout=5
    )
    if r.status_code != 200:
        st.error(f"Erreur {r.status_code} : {r.text}")
        return None
    return r.json()


with tab_clf:
    st.write(
        "Choisis un préremplissage, ajuste les mesures si besoin, puis lance la prédiction."
    )
    ex = st.radio(
        "Pré-remplir avec :",
        ["exemple malin", "exemple bénin", "moyennes"],
        horizontal=True,
        key="clf-ex",
    )
    defaults = {
        "exemple malin": info["examples"]["malin"],
        "exemple bénin": info["examples"]["benin"],
        "moyennes": info["feature_means"],
    }[ex]
    with st.expander("Les 30 mesures de la tumeur", expanded=False):
        vals = feature_form(f"clf-{ex}", info["classification"]["features"], defaults)
    if st.button("Prédire le diagnostic", type="primary", key="btn-clf"):
        res = post("/api/predict/classification", vals)
        if res:
            kind = "result-malin" if res["prediction"] == "malin" else "result-benin"
            label = res["prediction"].upper()
            st.markdown(
                f"""
                <div class="result-box {kind}">
                  <p class="result-title">Prédiction : {label}</p>
                  <p class="result-meta">
                    Probabilité malin = {res["proba_malin"]:.2%}
                    · seuil = {res["threshold_malin"]}
                    · pod {res["pod"]} · API {res["app_version"]}
                    · modèles {res["model_version"]} · cache = {res["cache"]}
                  </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(
                min(max(res["proba_malin"], 0.0), 1.0),
                text=f'Probabilité malin = {res["proba_malin"]:.2%}',
            )

with tab_reg:
    st.write(
        f'Prédire **{info["regression"]["target"]}** à partir des 29 autres mesures.'
    )
    feats = info["regression"]["features"]
    base = info["examples"]["benin"]
    with st.expander("Les 29 mesures", expanded=False):
        vals_r = feature_form("reg", feats, base)
    if st.button("Prédire mean area", type="primary", key="btn-reg"):
        res = post("/api/predict/regression", vals_r)
        if res:
            st.markdown(
                f"""
                <div class="result-box">
                  <p class="result-title">Surface moyenne prédite : {res["prediction"]}</p>
                  <p class="result-meta">
                    Valeur réelle de l'exemple : {base["mean area"]}
                    · pod {res["pod"]} · API {res["app_version"]} · cache = {res["cache"]}
                  </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

with tab_stats:
    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("Rafraîchir les stats"):
            st.cache_data.clear()
            st.rerun()
    try:
        s = requests.get(f"{API_URL}/api/stats", timeout=3).json()
        m1, m2, m3 = st.columns(3)
        m1.metric("Classifications", s.get("classification", 0))
        m2.metric("Régressions", s.get("regression", 0))
        m3.metric("Cache hits", s.get("cache_hits", 0))
        st.caption(f"Dernière réponse servie par : `{s.get('served_by', '?')}`")
        st.dataframe(pd.DataFrame([s]), hide_index=True, use_container_width=True)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Statistiques indisponibles : {exc}")
    st.markdown("##### Configuration modèle (ConfigMap)")
    st.json(info.get("model_config", {}))
