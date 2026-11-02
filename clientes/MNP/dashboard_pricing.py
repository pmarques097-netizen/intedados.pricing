# INTEDADOS PRICING — lançador do cliente MNP.
# O código do Pricing é único e fica em ..\..\app\dashboard_pricing.py.
# Esta pasta guarda só os dados deste cliente (pesquisas, vendas, compras, estoque, cache e cadastros).
INTEDADOS_CLIENTE = "MNP"
import os as _o
import sys as _s

_aqui = _o.path.dirname(_o.path.abspath(__file__))
if _o.getcwd() != _aqui:  # na nuvem o Streamlit roda a partir da raiz do repositório
    _o.chdir(_aqui)
if _aqui not in _s.path:
    _s.path.insert(0, _aqui)
_c = _o.path.normpath(_o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "..", "..", "app", "dashboard_pricing.py"))
_m = _o.path.getmtime(_c)
_k = getattr(_s, "_intedados_codigo", None)
if not _k or _k[0] != (_c, _m):  # compila 1x por versão do código (não a cada clique)
    with open(_c, encoding="utf-8") as _f:
        _s._intedados_codigo = ((_c, _m), compile(_f.read(), _c, "exec"))
exec(_s._intedados_codigo[1], globals())
