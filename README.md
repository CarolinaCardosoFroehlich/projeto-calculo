# Calculadora de Cálculo I

Uma calculadora web para as quatro operações que mais aparecem em Cálculo I: **limite**, **derivada**, **integral indefinida** e **integral definida**. Você digita a função, escolhe a operação e a página mostra o resultado exato e o gráfico.

Fiz este projeto para a disciplina de Cálculo do curso de Ciência da Computação na Unimar. A proposta era criar uma solução computacional usando os conceitos vistos em aula, e eu quis uma ferramenta que não só desse a resposta, mas também mostrasse visualmente o que cada operação significa.

**Acesse online:** `https://CarolinaCardosoFroehlich.github.io/projeto-calculo`

---

## O que ela faz

- **Derivada** de qualquer ordem, desenhada junto com a função original. Dá para ver que a derivada zera nos pontos de máximo e mínimo.
- **Integral indefinida**, com o + C e o gráfico de uma primitiva.
- **Integral definida**, com a área pintada no gráfico e o passo F(b) − F(a) aplicando o Teorema Fundamental do Cálculo.
- **Limite**, pela esquerda, pela direita, dos dois lados ou no infinito. Quando os limites laterais são diferentes, a página avisa que o limite não existe. O gráfico marca o ponto com uma bolinha aberta quando a função não está definida ali.

Os resultados são **exatos**, não aproximados. A calculadora responde π/4, √2 ou (x − 1)eˣ + C, igual a gente faria no caderno.

## Como funciona

A matemática é feita pelo [SymPy](https://www.sympy.org/), uma biblioteca de Python para cálculo simbólico. A diferença para uma calculadora comum é que ele trabalha com as letras, não só com números: a derivada de x² é 2x, e não algo como 6,0000001 em x = 3.

A parte curiosa é que o Python roda **dentro do navegador**, graças ao [Pyodide](https://pyodide.org/), que é o Python compilado para WebAssembly. Por isso o projeto não tem back-end: é só uma página estática, e dá para hospedar no GitHub Pages sem custo.

O fluxo é assim:

1. Você digita a função e escolhe a operação.
2. O JavaScript manda os dados para o Python em formato JSON.
3. O Python lê a função, faz a conta com o SymPy e devolve o resultado, mais os pontos do gráfico.
4. A página mostra a fórmula com o [KaTeX](https://katex.org/) e desenha o gráfico num `<canvas>`.

Escrevi uma explicação bem mais detalhada, com o conceito de cada operação e o que cada parte do código faz, no arquivo [EXPLICACAO.md](EXPLICACAO.md).

## Como escrever as funções

| Para escrever | Digite |
|---|---|
| x² | `x^2` |
| 2·x | `2x` (a multiplicação pode ficar implícita) |
| eˣ e e^(−x²) | `e^x` e `e^(-x^2)` |
| seno, cosseno, tangente | `sen(x)`, `cos(x)`, `tg(x)` |
| logaritmo natural | `ln(x)` |
| raiz quadrada | `sqrt(x)` |
| módulo \|x\| | `abs(x)` |
| π e infinito | `pi` e `inf` |

Quando o expoente tiver mais de um termo, coloque entre parênteses: `e^(-x^2)`, e não `e^-x^2`.

Alguns exemplos para testar:

- Derivada de `x^3 - 3x`
- Integral de `x e^x` (integração por partes)
- Integral definida de `sen(x)` de `0` a `2pi`, que dá 0, porque a área de cima cancela a de baixo
- Limite de `(x^2-4)/(x-2)` com x tendendo a `2`
- Limite de `(1+1/x)^x` com x tendendo a `inf`, que dá o número *e*

## Rodando no seu computador

Como a página carrega o arquivo `calculo.py`, ela precisa ser aberta por um servidor local. Abrir o `index.html` com dois cliques não funciona, porque o navegador bloqueia a leitura de arquivos nesse modo.

Dentro da pasta do projeto, rode:

```bash
python -m http.server 8000
```

E abra **http://127.0.0.1:8000** no navegador. Se usar o VS Code, a extensão Live Server também resolve.

Na primeira vez, a página baixa o Python e o SymPy (uns 15 MB), então demora alguns segundos para o botão "Calcular" ficar disponível. Precisa de internet para isso.

> **Dica:** se você alterar algum arquivo e a página não mudar, provavelmente é cache do navegador. Abra numa aba anônima ou, com o F12 aberto, marque "Disable cache" na aba Network.

## Testes

A parte matemática tem testes automáticos, que conferem casos conhecidos da aula: limite fundamental, integração por partes, limites laterais e o próprio Teorema Fundamental do Cálculo (integrar e derivar de volta tem que dar a função original).

```bash
pip install sympy
python testes/testar_calculo.py
```

## Estrutura

```
projeto-calculo/
├── index.html               a página
├── css/style.css            aparência
├── js/app.js                conecta a página ao Python
├── js/grafico.js            desenha o gráfico
├── python/calculo.py        toda a matemática (SymPy)
├── testes/testar_calculo.py testes da parte matemática
└── EXPLICACAO.md            explicação detalhada do projeto
```

Se você quiser entender só a matemática, o arquivo que importa é o `python/calculo.py`. O resto é interface.

## Tecnologias

Python, SymPy, Pyodide, JavaScript, HTML, CSS, Canvas API e KaTeX.
