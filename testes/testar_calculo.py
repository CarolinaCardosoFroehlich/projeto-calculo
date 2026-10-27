import json
import os
import sys

import sympy as sp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))
from calculo import calcular, ler, x  


def rodar(expr, op, **extras):
    dados = {'expr': expr, 'op': op, **extras}
    return json.loads(calcular(json.dumps(dados)))

CASOS = [
    ('Derivada de polinômio',        'x^3 - 2x',        'derivada', {'ordem': 1}, "3 x^{2} - 2"),
    ('Segunda derivada de ln(x)',    'ln(x)',           'derivada', {'ordem': 2}, "- \\frac{1}{x^{2}}"),
    ('Integral por partes',          'x e^x',           'integral', {},           "\\left(x - 1\\right) e^{x} + C"),
    ('Integral definida de x²',      'x^2',             'definida', {'a': '0', 'b': '3'}, "9"),
    ('Limite fundamental sen(x)/x',  'sen(x)/x',        'limite',   {'ponto': '0', 'lado': '+-'}, "1"),
    ('Limite que não existe (1/x)',  '1/x',             'limite',   {'ponto': '0', 'lado': '+-'}, "não existe"),
    ('Limite no infinito → e',       '(1 + 1/x)^x',     'limite',   {'ponto': 'inf'}, "e"),
    ('Indeterminação 0/0',           '(x^2-4)/(x-2)',   'limite',   {'ponto': '2', 'lado': '+-'}, "4"),
    ('Limite lateral de |x|/x',      'abs(x)/x',        'limite',   {'ponto': '0', 'lado': '-'}, "-1"),
]

falhas = 0
for nome, expr, op, extras, esperado in CASOS:
    r = rodar(expr, op, **extras)
    ok = esperado in r['resultado_latex']
    falhas += not ok
    print(f"[{'OK ' if ok else 'ERRO'}] {nome}: {r['resultado_latex']}")

f = ler('x^2 sen(x)')
F = sp.integrate(f, x)
ok = sp.simplify(sp.diff(F, x) - f) == 0
falhas += not ok
print(f"[{'OK ' if ok else 'ERRO'}] Teorema Fundamental: d/dx ∫f dx = f")

print()
print('Todos os testes passaram!' if falhas == 0 else f'{falhas} teste(s) falharam.')
sys.exit(1 if falhas else 0)