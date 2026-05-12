"""
=============================================================
  PROCESSADOR DE BASE — PAINEL MOVE 07.02.50
=============================================================
  Lê o Excel mais recente em data/
  Processa a aba "Base"
  Gera docs/data.json para o site consumir
=============================================================
"""

import json
import os
import re
import glob
from datetime import datetime
import pandas as pd

# ── Configuração ─────────────────────────────────────────
TARGET_VERSION = "07.02.50"

# Mapeamento DDD → Diretoria (ajuste se necessário)
DIRETORIA_MAP = {
    "61": "Dir CO",  "62": "Dir CO",  "64": "Dir CO",  "65": "Dir CO",
    "65A":"Dir CO",  "66": "Dir CO",  "66A":"Dir CO",  "68": "Dir CO",  "69": "Dir CO",
    "31": "Dir MG/BA","33":"Dir MG/BA","35":"Dir MG/BA","38":"Dir MG/BA",
    "74": "Dir MG/BA","75":"Dir MG/BA","77":"Dir MG/BA",
    "91": "Dir NORTE","92":"Dir NORTE","93":"Dir NORTE","94":"Dir NORTE",
    "95": "Dir NORTE","96":"Dir NORTE","97":"Dir NORTE",
}

DIR_ORDER = ["Dir CO", "Dir MG/BA", "Dir NORTE", "Outros"]

# ── Utilitários ───────────────────────────────────────────

def normalizar_col(nome: str) -> str:
    """Lowercase + remove acentos + substitui espaços por _"""
    nome = nome.strip().lower()
    nome = nome.encode("ascii", "ignore").decode()   # remove acentos (aproximado)
    nome = re.sub(r"[^\w]", "_", nome)
    nome = re.sub(r"_+", "_", nome).strip("_")
    return nome


def encontrar_excel() -> str:
    """Retorna o caminho do Excel mais recente na pasta data/"""
    padrao = os.path.join("data", "*.xlsx")
    arquivos = sorted(glob.glob(padrao), key=os.path.getmtime, reverse=True)
    if not arquivos:
        padrao_xls = os.path.join("data", "*.xls")
        arquivos = sorted(glob.glob(padrao_xls), key=os.path.getmtime, reverse=True)
    if not arquivos:
        raise FileNotFoundError(
            "Nenhum arquivo .xlsx encontrado na pasta data/. "
            "Coloque a base Excel lá e faça push."
        )
    print(f"  [OK] Arquivo encontrado: {arquivos[0]}")
    return arquivos[0]


def ler_aba_base(caminho: str) -> pd.DataFrame:
    """Lê a aba 'Base' do Excel e normaliza os nomes de coluna."""
    xl = pd.ExcelFile(caminho)
    aba_base = None
    for nome in xl.sheet_names:
        if nome.strip().lower() == "base":
            aba_base = nome
            break
    if aba_base is None:
        raise ValueError(
            f"Aba 'Base' não encontrada. Abas disponíveis: {xl.sheet_names}"
        )
    print(f"  [OK] Aba encontrada: '{aba_base}'")
    df = pd.read_excel(caminho, sheet_name=aba_base, dtype=str).fillna("")
    df.columns = [normalizar_col(c) for c in df.columns]
    print(f"  [OK] {len(df)} linhas | Colunas: {list(df.columns)}")
    return df


def resolver_coluna(df: pd.DataFrame, candidatos: list[str]) -> str | None:
    """Retorna o nome da coluna que bate com um dos candidatos."""
    for c in candidatos:
        if c in df.columns:
            return c
    return None


# ── Processamento principal ───────────────────────────────

def processar(df: pd.DataFrame) -> dict:
    # Colunas chave
    col_ddd    = resolver_coluna(df, ["ddd"])
    col_versao = resolver_coluna(df, ["new_versao", "versao_sgv", "versao_app"])
    col_dia    = resolver_coluna(df, ["dia_avaliado", "data_avaliacao", "data"])
    col_sgv    = resolver_coluna(df, ["sgv", "cod_sgv", "codigo_sgv"])
    col_estab  = resolver_coluna(df, ["estabelecimento", "nome_fantasia", "nome"])
    col_modelo = resolver_coluna(df, ["modelo", "modelo_dispositivo"])

    print(f"  [MAP] DDD={col_ddd} | Versão={col_versao} | Dia={col_dia}")

    if not col_ddd or not col_versao:
        raise ValueError("Colunas obrigatórias 'DDD' e/ou 'Versão' não encontradas.")

    # Flag de atualização
    df["_atualizado"] = df[col_versao].str.strip() == TARGET_VERSION

    # ── Agregação por DDD ──────────────────────────────────
    ddd_stats = (
        df.assign(ddd_clean=df[col_ddd].str.strip())
        .groupby("ddd_clean", as_index=False)
        .agg(
            total=("_atualizado", "count"),
            atualizado=("_atualizado", "sum"),
        )
    )
    ddd_stats.rename(columns={"ddd_clean": "ddd"}, inplace=True)
    ddd_stats["desatualizado"] = ddd_stats["total"] - ddd_stats["atualizado"]
    ddd_stats["pct"] = (
        ddd_stats["atualizado"] / ddd_stats["total"] * 100
    ).round(2).fillna(0)
    ddd_stats["diretoria"] = ddd_stats["ddd"].map(DIRETORIA_MAP).fillna("Outros")

    # Ordena por Diretoria → DDD numérico
    ddd_stats["_dir_ord"] = ddd_stats["diretoria"].map(
        lambda d: DIR_ORDER.index(d) if d in DIR_ORDER else 99
    )
    ddd_stats.sort_values(
        ["_dir_ord", "ddd"],
        key=lambda s: s if s.name == "_dir_ord" else pd.to_numeric(s, errors="coerce").fillna(0),
        inplace=True,
    )
    ddd_stats.drop(columns=["_dir_ord"], inplace=True)

    # ── Evolução diária ────────────────────────────────────
    daily = []
    if col_dia:
        df_ok = df[df["_atualizado"]].copy()
        df_ok["_data"] = pd.to_datetime(
            df_ok[col_dia].str.split(" ").str[0], errors="coerce"
        )
        dia_counts = (
            df_ok.dropna(subset=["_data"])
            .groupby("_data")
            .size()
            .reset_index(name="count")
            .sort_values("_data")
        )
        for _, r in dia_counts.iterrows():
            daily.append({
                "date":  r["_data"].strftime("%d/%m/%Y"),
                "count": int(r["count"]),
            })

    # ── Totais gerais ──────────────────────────────────────
    total_geral      = int(df["_atualizado"].count())
    total_atualizado = int(df["_atualizado"].sum())

    return {
        "meta": {
            "target_version":    TARGET_VERSION,
            "total_geral":       total_geral,
            "total_atualizado":  total_atualizado,
            "total_pendente":    total_geral - total_atualizado,
            "pct_geral":         round(total_atualizado / total_geral * 100, 2) if total_geral else 0,
            "gerado_em":         datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC"),
        },
        "ddd_stats": ddd_stats.to_dict(orient="records"),
        "daily_evolution": daily,
    }


# ── Entrada ────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  PAINEL MOVE — Processador de Base")
    print("=" * 55)

    # Garante que docs/ existe
    os.makedirs("docs", exist_ok=True)

    caminho = encontrar_excel()
    df      = ler_aba_base(caminho)
    dados   = processar(df)

    saida = "docs/data.json"
    with open(saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n  [OK] {saida} gerado com sucesso!")
    print(f"  → Total:       {dados['meta']['total_geral']}")
    print(f"  → Atualizado:  {dados['meta']['total_atualizado']}")
    print(f"  → Pendente:    {dados['meta']['total_pendente']}")
    print(f"  → %:           {dados['meta']['pct_geral']}%")
    print("=" * 55)


if __name__ == "__main__":
    main()
