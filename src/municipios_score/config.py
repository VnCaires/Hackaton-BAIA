"""Configuracao de ambiente: carrega .env (se existir) e detecta o provedor de LLM.

A chave NUNCA e versionada: `.env` esta no .gitignore e `.env.example` e so um modelo.
Sem chave, a camada de IA usa fallback offline (ver ia.py).
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"

# nomes alternativos aceitos para a chave OpenAI (compatibilidade com ~/.secrets)
_OPENAI_ALIASES = ("OPENAI_API_KEY", "OPEN_AI_KEY", "OPEN_API_PERSONAL_KEY")


def carregar_env() -> None:
    """Carrega pares CHAVE=VALOR de .env para o ambiente (sem sobrescrever os ja definidos)."""
    if not ENV_FILE.exists():
        return
    for linha in ENV_FILE.read_text().splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


def _openai_key() -> str | None:
    for nome in _OPENAI_ALIASES:
        valor = os.environ.get(nome)
        if valor:
            if nome != "OPENAI_API_KEY":
                os.environ.setdefault("OPENAI_API_KEY", valor)  # SDK le OPENAI_API_KEY
            return valor
    return None


def provedor_llm() -> str | None:
    """Retorna 'openai', 'anthropic' ou None (sem chave -> fallback offline)."""
    carregar_env()
    preferido = os.environ.get("LLM_PROVIDER", "openai").lower()
    if preferido == "anthropic" and os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if _openai_key():
        return "openai"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    return None
