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

from municipios_score import ia, io, vulnerabilidade as vuln

st.set_page_config(page_title="Calculadora de Orcamento Climatico - Bahia", layout="wide")

METRICAS = {
    "Vulnerabilidade geral": "ameaca",
    "Seca": "seca",
    "Enchente": "enchente",
    "Calor": "calor",
    "Projecao 2030": "ameaca_futura",
}
PALETA = ["#1a9850", "#fee08b", "#f46d43", "#a50026"]


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
        st.caption("Peso relativo de cada risco (re-normalizado para somar 1):")
        ws = st.slider("Seca", 0.0, 1.0, 0.33, 0.01)
        wf = st.slider("Enchente", 0.0, 1.0, 0.33, 0.01)
        wc = st.slider("Calor", 0.0, 1.0, 0.34, 0.01)
        usar_sliders = st.checkbox("Usar pesos personalizados (em vez do PCA)", value=False)
    base = df.copy()
    if usar_sliders:
        hazard = vuln.hazard_por_pesos(base, ws, wf, wc)
        base["peso"] = vuln.peso_per_capita(hazard, base["capacidade"]).to_numpy()
    aloc = vuln.alocar(base, orcamento)
    with c2:
        m1, m2 = st.columns(2)
        m1.metric("Municipios contemplados", f"{(aloc.valor_rs > 0).sum()} / 417")
        m2.metric("Soma alocada", f"R$ {aloc.valor_rs.sum():,.0f}")
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
        st.info(ia.explicar_municipio(nome, sub, r.arquetipo, r.tendencia))


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
    st.title("Calculadora de Orcamento Climatico da Bahia")
    st.caption(
        "Informe o orcamento e veja quanto vai para cada um dos 417 municipios, priorizando os mais "
        "vulneraveis. Indice nao-supervisionado a partir de 21 anos de dados INMET (PCA + clustering + projecao)."
    )
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
