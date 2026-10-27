let pyodide = null;   
let operacao = 'limite';  
let ultimo = null;         

const $ = id => document.getElementById(id);

// Mostra uma fórmula LaTeX usando o KaTeX
function mostrarFormula(latex, elemento) {
  try {
    katex.render(latex, elemento, { displayMode: true, throwOnError: false });
  } catch {
    elemento.textContent = latex;
  }
}

// Interface: troca de operação e exemplos
function escolherOperacao(nova) {
  operacao = nova;
  document.querySelectorAll('#ops button').forEach(b =>
    b.setAttribute('aria-pressed', b.dataset.op === operacao));
  $('p-derivada').hidden = operacao !== 'derivada';
  $('p-definida').hidden = operacao !== 'definida';
  $('p-limite').hidden   = operacao !== 'limite';
}

$('ops').addEventListener('click', e => {
  if (e.target.dataset.op) escolherOperacao(e.target.dataset.op);
});

$('exemplos').addEventListener('click', e => {
  const b = e.target.closest('button');
  if (!b) return;
  $('expr').value = b.dataset.e;
  escolherOperacao(b.dataset.op);
  if (b.dataset.a) { $('a').value = b.dataset.a; $('b').value = b.dataset.b; }
  if (b.dataset.p) $('ponto').value = b.dataset.p;
  calcular();
});

$('form').addEventListener('submit', e => {
  e.preventDefault();   
  calcular();
});


async function iniciar() {
  if (typeof loadPyodide !== 'function') {
    throw new Error(
      'o Pyodide não foi baixado. Confira a internet e se algum bloqueador ' +
      '(AdBlock, antivírus, rede) está bloqueando cdn.jsdelivr.net.'
    );
  }
  pyodide = await loadPyodide();           
  await pyodide.loadPackage('sympy');      
  const resposta = await fetch('python/calculo.py');
  if (!resposta.ok) throw new Error('não achei python/calculo.py');
  pyodide.runPython(await resposta.text());

  $('calc').disabled = false;
  $('calc').textContent = 'Calcular';
  calcular();  // já mostra um exemplo ao abrir
}

// Cálculo: JS -> Python -> JS

function calcular() {
  if (!pyodide) return;
  const dados = {
    expr: $('expr').value,
    op: operacao,
    ordem: $('ordem').value,
    a: $('a').value,
    b: $('b').value,
    ponto: $('ponto').value,
    lado: $('lado').value,
  };

  $('status').className = 'status';
  $('status').textContent = 'Calculando…';
  setTimeout(() => {
    try {
      pyodide.globals.set('entrada', JSON.stringify(dados));
      const r = JSON.parse(pyodide.runPython('calcular(entrada)'));
      mostrarResultado(r);
      ultimo = { r, xmin: r.xmin, xmax: r.xmax };
      redesenhar();
    } catch (erro) {
      const linhas = String(erro.message || erro).split('\n').filter(Boolean);
      mostrarErro(traduzirErro(linhas[linhas.length - 1]));
    }
  }, 20);
}

function mostrarResultado(r) {
  const nomes = {
    derivada: 'Derivada',
    integral: 'Integral indefinida',
    definida: 'Integral definida',
    limite: 'Limite',
  };
  $('status').textContent = nomes[r.op];

  if (r.op === 'derivada' || r.op === 'integral') {
    // linha 1: a conta; linha 2: f'(x) = ... ou F(x) = ... + C
    mostrarFormula(r.operacao_latex, $('eq'));
    mostrarFormula(r.resultado_latex, $('passo'));
  } else {
    // linha 1: conta = resultado; linha 2: passo (se houver)
    mostrarFormula(r.operacao_latex + ' = ' + r.resultado_latex, $('eq'));
    if (r.passo_latex) mostrarFormula(r.passo_latex, $('passo'));
    else $('passo').innerHTML = '';
  }
}

function traduzirErro(msg) {
  if (/SyntaxError|TokenError|invalid syntax/i.test(msg)) {
    return 'Não entendi a expressão. Confira parênteses e operadores.';
  }
  return msg.replace(/^\w+Error:\s*/, '');
}

function mostrarErro(msg) {
  $('status').className = 'status erro';
  $('status').textContent = msg;
  $('eq').innerHTML = '';
  $('passo').innerHTML = '';
}

function redesenhar() {
  if (ultimo) desenharGrafico($('cv'), $('legenda'), ultimo.r, ultimo.xmin, ultimo.xmax);
}
window.addEventListener('resize', redesenhar);
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', redesenhar);

iniciar().catch(e => {
  mostrarErro(
    'Não foi possível iniciar. Abra a página por um servidor local ' +
    '(veja o README) e confira a internet. Detalhe: ' + e.message
  );
});