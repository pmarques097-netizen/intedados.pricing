# Teste do menu lateral (V67): abre como administrador, alterna Administração, Fornecedores e Usuários e Redes.
import os
import sys
import traceback

from streamlit.testing.v1 import AppTest

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("_perf", exist_ok=True)
out = open(os.path.join("_perf", "teste_menu.txt"), "w", encoding="utf-8")


def log(*a):
    print(*a, file=out, flush=True)


try:
    at = AppTest.from_file("dashboard_pricing.py", default_timeout=900)
    ss = at.session_state
    for k, v in {"logado": True, "usuario": "paulo", "nome_usuario": "Paulo Marques", "perfil_usuario": "Diretoria",
                 "empresa_id_usuario": "1", "empresa_id_contexto": "1", "auditoria_sessao_iniciada": True}.items():
        ss[k] = v

    def passo(rot):
        at.run()
        exc = [str(e.value)[:300] for e in at.exception] if at.exception else []
        sb = at.sidebar
        botoes = [b.label for b in sb.button]
        md = " ".join(m.value for m in sb.markdown if "v67-" in m.value)[:400]
        log(f"== {rot}: erros={exc}")
        log("   botoes:", botoes)
        log("   cartao:", ("v67-card" in md), ("v67-seg" in md), ("v67-user" in md))
        return botoes

    b = passo("abertura")
    at.sidebar.button(key="v67_admtg").click(); b = passo("administração aberta")
    log("   tem Usuários e Redes:", "Usuários e Redes" in b)
    at.sidebar.button(key="v67_nav_forn").click(); passo("fornecedores")
    log("   tela:", [m.value for m in at.markdown if "Gestão de Fornecedores" in m.value][:1])
    at.sidebar.button(key="v67_nav_usr").click(); passo("usuários e redes")
    log("   tela:", [m.value for m in at.markdown if "Usuários e Redes" in m.value][:1])
    ss["intedados_pagina_global"] = "⬆️ Subir Preço"
    ss["v59_abrir"] = False
    passo("subir preço")
    log("   contadores:", ss["_v67_qtd"] if "_v67_qtd" in ss else None)
    log("OK")
except Exception:
    log("FALHA", traceback.format_exc())
