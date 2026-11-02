# Compatibilidade: abre o Pricing do cliente MT. Apps novos: clientes/<CLIENTE>/dashboard_pricing.py
import os, sys
_d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clientes', 'MT')
_f = os.path.join(_d, 'dashboard_pricing.py')
_g = {'__file__': _f, '__name__': '__main__'}
exec(compile(open(_f, encoding='utf-8').read(), _f, 'exec'), _g)
