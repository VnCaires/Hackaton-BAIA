"""Calculadora de Orcamento Climatico da Bahia - app Streamlit.

Distribui um orcamento entre os 417 municipios proporcional ao risco climatico.
Rode: streamlit run app.py  (usa data/processed/scores.csv ou examples/scores_municipios.csv)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import branca.colormap as cm
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from municipios_score import io, vulnerabilidade as vuln

st.set_page_config(
    page_title="Calculadora de Orcamento Climatico - Bahia", layout="wide", page_icon="BA"
)

_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Fira Sans', system-ui, sans-serif; }
  .hero {
    background: linear-gradient(120deg, #1E3A8A 0%, #1E40AF 60%, #2563EB 100%);
    color: #fff; border-radius: 14px; padding: 22px 26px; margin-bottom: 18px;
  }
  .hero h1 { font-size: 28px; font-weight: 700; margin: 0 0 4px; letter-spacing: -.4px; }
  .hero p { margin: 0; opacity: .92; font-size: 15px; max-width: 760px; }
  .hero .gold { color: #FBBF24; font-weight: 700; }
  .kpi-row { display: flex; gap: 12px; flex-wrap: wrap; margin: 2px 0 18px; }
  .kpi { flex: 1; min-width: 130px; background: #fff; border: 1px solid #DBEAFE;
    border-left: 4px solid #D97706; border-radius: 10px; padding: 12px 16px; }
  .kpi b { display: block; font-size: 24px; color: #1E3A8A; line-height: 1.1;
    font-variant-numeric: tabular-nums; }
  .kpi span { font-size: 11px; color: #5B6B86; text-transform: uppercase; letter-spacing: .4px; }
  div[data-testid="stMetricValue"] { color: #1E3A8A; }
  .stButton>button, .stDownloadButton>button { border-radius: 8px; font-weight: 600; }
  .stTabs [data-baseweb="tab"] { font-weight: 600; }
  .stTabs [aria-selected="true"] { color: #D97706; }
</style>
"""


def _hero() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="hero"><h1>Calculadora de Orcamento Climatico da Bahia</h1>'
        '<p>Informe o orcamento e veja <span class="gold">quanto vai para cada um dos 417 '
        "municipios</span>, priorizando os mais vulneraveis. Nao prevemos o tempo: dizemos onde "
        "investir.</p></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="kpi-row">'
        '<div class="kpi"><b>417</b><span>municipios</span></div>'
        '<div class="kpi"><b>21 anos</b><span>INMET 2000-2021</span></div>'
        '<div class="kpi"><b>45</b><span>estacoes</span></div>'
        '<div class="kpi"><b>&Sigma; = 1</b><span>pesos normalizados</span></div>'
        "</div>",
        unsafe_allow_html=True,
    )

METRICAS = {
    "Vulnerabilidade geral": "ameaca",
    "Seca": "seca",
    "Enchente": "enchente",
    "Calor": "calor",
    "Projecao 2030": "ameaca_futura",
}
PALETA = ["#1a9850", "#fee08b", "#f46d43", "#a50026"]
ROTULO_RISCO = {"seca": "seca", "enchente": "enchentes", "calor": "calor extremo"}


@st.cache_data
def carregar() -> tuple[pd.DataFrame, dict]:
    return io.load_scores(), io.load_malha_geojson()


def mapa(df: pd.DataFrame, geo: dict, coluna: str) -> folium.Map:
    valores = df.set_index("codigo")[coluna]
    nomes = df.set_index("codigo")["nome"]
    escala = cm.LinearColormap(PALETA, vmin=0, vmax=1, caption=coluna)
    for f in geo["features"]:
        cod = str(f["properties"]["codarea"])
        v = float(valores.get(cod, 0))
        f["properties"]["valor"] = round(v, 3)
        f["properties"]["nome"] = nomes.get(cod, cod)
        f["properties"]["cor"] = escala(v)
    m = folium.Map(location=[-12.5, -41.7], zoom_start=6, tiles="CartoDB positron")
    folium.GeoJson(
        geo,
        style_function=lambda x: {
            "fillColor": x["properties"]["cor"], "color": "white",
            "weight": 0.4, "fillOpacity": 0.75,
        },
        tooltip=folium.GeoJsonTooltip(fields=["nome", "valor"], aliases=["Municipio", "Indice"]),
    ).add_to(m)
    escala.add_to(m)
    return m


def tela_calculadora(df: pd.DataFrame) -> None:
    st.subheader("Quanto cada municipio recebe do orcamento")
    c1, c2 = st.columns([1, 2])
    with c1:
        orcamento = st.number_input(
            "Orcamento total (R$)", min_value=0, value=100_000_000, step=10_000_000, format="%d"
        )
        st.caption("A alocacao usa os pesos aprendidos pela PCA, sem ajuste manual por categoria.")
    aloc = vuln.alocar(df, orcamento)
    with c2:
        m1, m2 = st.columns(2)
        m1.metric("Municipios contemplados", f"{(aloc.valor_rs > 0).sum()} / 417")
        m2.metric("Soma alocada", f"R$ {aloc.valor_rs.sum():,.0f}")
    st.caption(
        f"Municipios com risco abaixo do limiar de contemplacao ({vuln.LIMIAR_CONTEMPLACAO:.0%}) "
        "nao recebem verba: baixo risco climatico nao e prioridade e evita micro-transferencias."
    )
    tabela = aloc.rename(columns={"nome": "Municipio", "peso": "Peso", "valor_rs": "Valor (R$)", "ameaca": "Ameaca"})
    st.dataframe(
        tabela[["Municipio", "Ameaca", "Peso", "Valor (R$)"]],
        use_container_width=True, height=420,
        column_config={
            "Ameaca": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1),
            "Peso": st.column_config.NumberColumn(format="%.5f"),
            "Valor (R$)": st.column_config.NumberColumn(format="R$ %.0f"),
        },
    )
    st.download_button("Baixar alocacao (CSV)", aloc.to_csv(index=False).encode(), "alocacao.csv", "text/csv")


def tela_mapa(df: pd.DataFrame, geo: dict) -> None:
    col_mapa, col_painel = st.columns([2, 1])
    with col_mapa:
        rotulo = st.selectbox("Camada de risco", list(METRICAS), index=0)
        st_folium(mapa(df, geo, METRICAS[rotulo]), height=560, use_container_width=True)
    with col_painel:
        nome = st.selectbox("Inspecionar municipio", sorted(df["nome"]))
        r = df[df["nome"] == nome].iloc[0]
        sub = {"seca": r.seca, "enchente": r.enchente, "calor": r.calor}
        st.metric("Ameaca composta", f"{r.ameaca:.0%}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Seca", f"{r.seca:.0%}")
        c2.metric("Enchente", f"{r.enchente:.0%}")
        c3.metric("Calor", f"{r.calor:.0%}")
        st.caption(f"Arquetipo: {r.arquetipo} | Tendencia: {r.tendencia} | IDHM {r.idhm:.3f}")
        risco, valor = max(sub.items(), key=lambda item: item[1])
        st.info(
            f"Maior fator de risco: {ROTULO_RISCO[risco]} ({valor:.0%}). "
            f"Perfil: {r.arquetipo}; tendencia historica: {str(r.tendencia).lower()}."
        )


def tela_arquetipos(df: pd.DataFrame) -> None:
    st.subheader("Arquetipos de vulnerabilidade (KMeans nao-supervisionado)")
    resumo = (
        df.groupby("arquetipo")
        .agg(municipios=("codigo", "size"), seca=("seca", "mean"),
             enchente=("enchente", "mean"), calor=("calor", "mean"))
        .round(2).reset_index()
    )
    st.dataframe(resumo, use_container_width=True)
    st.subheader("Tendencia historica projetada (2026-2030)")
    st.bar_chart(df["tendencia"].value_counts())


def main() -> None:
    _hero()
    df, geo = carregar()
    aba1, aba2, aba3 = st.tabs(["Calculadora de Orcamento", "Mapa de Risco", "Arquetipos & Projecao"])
    with aba1:
        tela_calculadora(df)
    with aba2:
        tela_mapa(df, geo)
    with aba3:
        tela_arquetipos(df)


if __name__ == "__main__":
    main()
