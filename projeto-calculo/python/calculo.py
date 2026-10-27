import json
import math

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

# 1. LEITURA DA FUNÇÃO
x = sp.symbols('x') #x vira valor
TRANSFORMACOES = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

# Dicionário de "apelidos": nomes em português (e atalhos) 
NOMES = {
    'x': x,
    'e': sp.E,            # número de Euler (2,718...)
    'pi': sp.pi,          # π
    'ln': sp.log,         # no SymPy, log(x) é o logaritmo natural
    'log': sp.log,
    'sen': sp.sin, 'sin': sp.sin,
    'cos': sp.cos,
    'tg': sp.tan, 'tan': sp.tan,
    'sqrt': sp.sqrt, 'raiz': sp.sqrt,
    'abs': sp.Abs,        # módulo |x|
    'exp': sp.exp,
    'inf': sp.oo, 'oo': sp.oo, 'infinito': sp.oo,   # ∞
}

#transforma o texto digitado em expressao matematica
def ler(texto):
    """Converte o texto digitado (ex.: 'x^2 + 3x') em uma expressão do SymPy."""
    texto = (
        str(texto).strip()
        .replace('**', '^')
        .replace('√', 'sqrt')
        .replace('∞', 'oo')
        .replace(',', '.')      
    )
    if not texto:
        raise ValueError('Digite uma expressão.')
    return parse_expr(texto, local_dict=NOMES, transformations=TRANSFORMACOES) #trasforma o texto em expressoes

# 2. FUNÇÕES AUXILIARES (convertem valores em decimais)
def numero(valor): #ex π/4 vira 0.785398.
    try:
        v = complex(sp.N(valor))
        if abs(v.imag) > 1e-12: #(ie-12 ≅ 0)
            return None
        v = v.real
        return v if math.isfinite(v) else None
    except Exception:
        return None

#mostra no grafico os pontos
def amostrar(expr, xmin, xmax, n=500):
    f = sp.lambdify(x, expr, modules=['math'])

    xs, ys = [], []
    for i in range(n + 1):
        xv = xmin + (xmax - xmin) * i / n
        try:
            yv = f(xv) #calcula o f(x)
            if isinstance(yv, complex):
                yv = yv.real if abs(yv.imag) < 1e-12 else None
            if yv is not None:
                yv = float(yv)
                if not math.isfinite(yv):
                    yv = None
        except Exception:    
            yv = None
        xs.append(xv)
        ys.append(yv)
    return {'x': xs, 'y': ys} #guarda x e y


def curva(nome, tipo, expr, xmin, xmax):
    return {'nome': nome, 'tipo': tipo, **amostrar(expr, xmin, xmax)}

# AS QUATRO OPERAÇÕES DE CÁLCULO
#--a parte com latex é pra desenhar o resultado
def op_derivada(f, d, xmin, xmax, r):
    ordem = max(1, int(d.get('ordem', 1))) #ordem da derivacao
    resultado = sp.simplify(sp.diff(f, x, ordem)) #deriva f em relacao a x, ordem vezes
    linhas = "'" * ordem if ordem <= 3 else f'^{{({ordem})}}' #monta a escrita de lanaige
    if ordem == 1:
        r['operacao_latex'] = rf"\frac{{d}}{{dx}}\left[{sp.latex(f)}\right]" #escreve a conta como leibniz
    else:
        r['operacao_latex'] = rf"\frac{{d^{{{ordem}}}}}{{dx^{{{ordem}}}}}\left[{sp.latex(f)}\right]"
    r['resultado_latex'] = rf"f{linhas}(x) = {sp.latex(resultado)}"
    r['curvas'].append(curva(f"f{linhas}(x)", 'g', resultado, xmin, xmax))


def op_integral(f, d, xmin, xmax, r):
    resultado = sp.integrate(f, x) #encontra uma primitiva de f
    if resultado.has(sp.Integral):
        raise ValueError('O SymPy não encontrou uma primitiva em forma fechada para essa função.')

    r['operacao_latex'] = rf"\int {sp.latex(f)}\,dx"
    r['resultado_latex'] = rf"F(x) = {sp.latex(sp.simplify(resultado))} + C"
    r['curvas'].append(curva('F(x)  (com C = 0)', 'g', resultado, xmin, xmax))


def op_definida(f, d, xmin, xmax, r):
    a, b = ler(d['a']), ler(d['b'])

    resultado = sp.integrate(f, (x, a, b))#calcula a integral de a até b, aplicando o Teorema Fundamental do Cálculo, F(b) − F(a).
    primitiva = sp.integrate(f, x)#calcula so pra mostrar na tela
    valor = numero(resultado) #passa pra decimal                
    #monta texto com latex
    r['operacao_latex'] = rf"\int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} {sp.latex(f)}\,dx"
    texto = '' if resultado.has(sp.Integral) else sp.latex(sp.simplify(resultado))
    if valor is not None and texto and texto != f'{valor:g}':
        texto += rf" \approx {valor:.6g}"
    elif valor is not None and not texto:
        texto = rf"\approx {valor:.6g}"
    r['resultado_latex'] = texto or sp.latex(resultado)
    #se existir primitiva mostra o calculo
    if not primitiva.has(sp.Integral):
        r['passo_latex'] = (
            rf"F(x) = {sp.latex(primitiva)} \;\Rightarrow\; "
            rf"F({sp.latex(b)}) - F({sp.latex(a)})"
        )
    av, bv = numero(a), numero(b)
    if av is not None and bv is not None:
        r['area'] = {'a': av, 'b': bv, **amostrar(f, min(av, bv), max(av, bv), 300)}


def op_limite(f, d, xmin, xmax, r):
    p = ler(d['ponto']) #le o ponto pra onde x tende
    lado = d.get('lado', '+-') #ve se é pela esquerda ou direita
    no_infinito = p in (sp.oo, -sp.oo) #se tende a infinito nao tem lado
    if no_infinito:
        lado = '+-'        

    resultado = None
    seta = ''
    if lado == '+-' and not no_infinito: # CASO 1: bilateral num ponto
        esquerda = sp.limit(f, x, p, '-')
        direita = sp.limit(f, x, p, '+')
        if esquerda != direita: 
            r['resultado_latex'] = (
                rf"\text{{não existe: }} "
                rf"\lim_{{x\to {sp.latex(p)}^-}} = {sp.latex(esquerda)},\;"
                rf"\lim_{{x\to {sp.latex(p)}^+}} = {sp.latex(direita)}"
            )
        else:
            resultado = direita
    elif lado == '+-':# CASO 2: no infinito
        resultado = sp.limit(f, x, p)
    else: # CASO 3: só um lado
        resultado = sp.limit(f, x, p, lado)      
        seta = '^+' if lado == '+' else '^-'

    r['operacao_latex'] = rf"\lim_{{x \to {sp.latex(p)}{seta}}} {sp.latex(f)}"
    if resultado is not None:
        r['resultado_latex'] = sp.latex(resultado)
    #como o ponto é desenhado no limite
    pv = numero(p)
    if pv is not None:
        lv = numero(resultado) if resultado is not None else None #limite lateral
        fp = f.subs(x, p)
        fv = None if fp.has(sp.zoo, sp.nan, sp.oo, -sp.oo) else numero(fp)
        buraco = fv is None or (lv is not None and abs(fv - lv) > 1e-9)
        r['marcas'].append({'x': pv, 'y': lv, 'buraco': buraco})


OPERACOES = {
    'derivada': op_derivada,
    'integral': op_integral,
    'definida': op_definida,
    'limite': op_limite,
}

#desenho ideal e escolha do tamanho do grafico
PADRAO = (-10.0, 10.0)  
def janela(d):
    try:
        if d['op'] == 'definida':
            a, b = numero(ler(d['a'])), numero(ler(d['b']))
            if a is not None and b is not None and a != b:
                menor, maior = min(a, b), max(a, b)
                folga = max(1.0, (maior - menor) * 0.5)
                return menor - folga, maior + folga

        if d['op'] == 'limite':
            p = ler(d['ponto'])
            if p == sp.oo:
                return 0.0, 50.0
            if p == -sp.oo:
                return -50.0, 0.0
            pv = numero(p)
            if pv is not None:
                return pv - 5, pv + 5
    except Exception:
        pass       
    return PADRAO


def calcular(dados_json):
    d = json.loads(dados_json)
    f = ler(d['expr'])
    op = d['op']

    if op not in OPERACOES:
        raise ValueError('Operação desconhecida.')

    xmin, xmax = janela(d)
    r = {'op': op, 'f_latex': sp.latex(f), 'xmin': xmin, 'xmax': xmax,
         'curvas': [], 'marcas': []}
    r['curvas'].append(curva('f(x)', 'f', f, xmin, xmax))

    OPERACOES[op](f, d, xmin, xmax, r)
    return json.dumps(r)