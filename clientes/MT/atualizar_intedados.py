"""Atualização automática do Pricing (cliente desta pasta) (chamada pelo intedados.ia).

Usa as mesmas funções da tela "Banco de dados / Atualização":
- Venda do mês atual (e também do mês anterior nos 3 primeiros dias, para fechar o mês);
- Fotografias de Estoque e Última Venda.
A senha vem da configuração salva com proteção do Windows na própria tela do Pricing.
Uso:  .venv\\Scripts\\python.exe atualizar_intedados.py
Sai com código 1 se algo falhar (o intedados.ia avisa por e-mail).
"""
import sys
import time
from datetime import date

from pricing_database import atualizar_competencia, atualizar_fotografia, carregar_config_banco
from pricing_secure_config import carregar as carregar_seguro

cfg_seguro, senha = carregar_seguro()
cfg = carregar_config_banco()
for k in ("host", "port", "database", "user", "sslmode"):
    if not cfg.get(k) and cfg_seguro.get(k):
        cfg[k] = cfg_seguro[k]
cfg.setdefault("sslmode", "prefer")

# V57 — separação por cliente: cada cliente atualiza só do seu próprio banco.
import json as _js57
from pathlib import Path as _P57
_aqui57 = _P57(__file__).resolve().parent
if _aqui57.parent.name.lower() == "clientes":
    if not str(cfg.get("database", "")).strip():
        sys.exit(f"[ERRO] O banco do cliente {_aqui57.name} ainda não foi configurado. Abra o Pricing {_aqui57.name} > "
                 "Banco de dados / Atualização > Conexão, preencha o banco deste cliente e clique em Salvar.")
    _alvo57 = (str(cfg.get("host", "")).strip().lower(), str(cfg.get("database", "")).strip().lower())
    for _o57 in _aqui57.parent.iterdir():
        if not _o57.is_dir() or _o57 == _aqui57:
            continue
        for _f57 in (_o57 / "data" / "config_banco_paulo.json", _o57 / "config" / "database.json"):
            try:
                _d57 = _js57.loads(_f57.read_text(encoding="utf-8-sig"))
            except Exception:
                continue
            if (str(_d57.get("host", "")).strip().lower(), str(_d57.get("database", "")).strip().lower()) == _alvo57:
                sys.exit(f"[ERRO] O banco {cfg.get('database')} está configurado também no cliente {_o57.name}. "
                         f"Atualização do cliente {_aqui57.name} cancelada para não misturar os dados.")
    print(f"Cliente {_aqui57.name} - banco {cfg.get('database')}", flush=True)

if not senha:
    sys.exit("[ERRO] Senha do banco não está salva. Abra o Pricing > Banco de dados / Atualização > Conexão, "
             "digite a senha e clique em Salvar (fica protegida pelo Windows).")

hoje = date.today()
meses = [(hoje.year, hoje.month)]
if hoje.day <= 3:
    anterior = (hoje.year - (hoje.month == 1), 12 if hoje.month == 1 else hoje.month - 1)
    meses.insert(0, anterior)

erros = 0
for ano, mes in meses:
    t = time.time()
    try:
        n, _ = atualizar_competencia(cfg, senha, ano, mes)
        print(f"Venda {ano}-{mes:02d}: {n:,} registros em {time.time() - t:.0f}s".replace(",", "."), flush=True)
    except Exception as e:  # noqa: BLE001
        erros += 1
        print(f"Venda {ano}-{mes:02d}: ERRO {e}", flush=True)

for nome_sql, saida in (("estoque.sql", "estoque_atual.parquet"), ("ultima_venda.sql", "ultima_venda_atual.parquet")):
    t = time.time()
    try:
        n, _ = atualizar_fotografia(cfg, senha, nome_sql, saida, forcar=True)
        print(f"{nome_sql}: {n:,} registros em {time.time() - t:.0f}s".replace(",", "."), flush=True)
    except Exception as e:  # noqa: BLE001
        erros += 1
        print(f"{nome_sql}: ERRO {e}", flush=True)

sys.exit(1 if erros else 0)
