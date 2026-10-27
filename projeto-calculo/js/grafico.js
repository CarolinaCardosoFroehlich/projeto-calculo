
// Lê uma cor definida no CSS (ex.: --azul), para o gráfico seguir o tema.
function cor(variavel) {
  return getComputedStyle(document.documentElement).getPropertyValue(variavel).trim();
}

function passoDaGrade(intervalo) {
  const potencia = Math.pow(10, Math.floor(Math.log10(intervalo / 8)));
  return [1, 2, 5, 10].map(k => k * potencia).find(s => intervalo / s <= 10);
}

function faixaY(resultado) {
  const ys = resultado.curvas.flatMap(c => c.y).filter(v => v !== null);
  resultado.marcas.forEach(m => { if (m.y !== null) ys.push(m.y); });
  if (!ys.length) return [-5, 5];

  ys.sort((a, b) => a - b);
  let ymin = ys[Math.floor(ys.length * 0.03)];
  let ymax = ys[Math.ceil(ys.length * 0.97) - 1];
  if (ymax - ymin < 1e-9) { ymin -= 1; ymax += 1; } 
  const folga = (ymax - ymin) * 0.12;
  return [ymin - folga, ymax + folga];
}

function desenharGrafico(canvas, legenda, resultado, xmin, xmax) {
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.clientWidth, H = canvas.clientHeight;
  canvas.width = W * dpr;
  canvas.height = H * dpr;
  const g = canvas.getContext('2d');
  g.scale(dpr, dpr);
  g.clearRect(0, 0, W, H);

  const [ymin, ymax] = faixaY(resultado);
  const M = { esq: 44, dir: 12, topo: 12, base: 28 };
  const X = v => M.esq + (v - xmin) / (xmax - xmin) * (W - M.esq - M.dir);
  const Y = v => M.topo + (ymax - v) / (ymax - ymin) * (H - M.topo - M.base);  

  // ---------- grade e números ----------
  g.font = '11px "IBM Plex Mono", monospace';
  g.lineWidth = 1;
  g.strokeStyle = cor('--grade');
  g.fillStyle = cor('--suave');
  const sx = passoDaGrade(xmax - xmin), sy = passoDaGrade(ymax - ymin);

  for (let v = Math.ceil(xmin / sx) * sx; v <= xmax; v += sx) {
    g.beginPath(); g.moveTo(X(v), M.topo); g.lineTo(X(v), H - M.base); g.stroke();
    g.textAlign = 'center'; g.fillText(+v.toFixed(6), X(v), H - 10);
  }
  for (let v = Math.ceil(ymin / sy) * sy; v <= ymax; v += sy) {
    g.beginPath(); g.moveTo(M.esq, Y(v)); g.lineTo(W - M.dir, Y(v)); g.stroke();
    g.textAlign = 'right'; g.fillText(+v.toFixed(6), M.esq - 6, Y(v) + 4);
  }

  // ---------- eixos x e y ----------
  g.strokeStyle = cor('--suave'); g.lineWidth = 1.2;
  if (ymin < 0 && ymax > 0) { g.beginPath(); g.moveTo(M.esq, Y(0)); g.lineTo(W - M.dir, Y(0)); g.stroke(); }
  if (xmin < 0 && xmax > 0) { g.beginPath(); g.moveTo(X(0), M.topo); g.lineTo(X(0), H - M.base); g.stroke(); }

  g.save();
  g.beginPath(); g.rect(M.esq, M.topo, W - M.esq - M.dir, H - M.topo - M.base); g.clip();

  // ---------- área da integral definida ----------
  if (resultado.area) {
    const A = resultado.area;
    g.fillStyle = cor('--area');
    g.beginPath();
    g.moveTo(X(A.x[0]), Y(0));
    A.x.forEach((xv, i) => {
      const yv = A.y[i] === null ? 0 : Math.max(ymin, Math.min(ymax, A.y[i]));
      g.lineTo(X(xv), Y(yv));
    });
    g.lineTo(X(A.x[A.x.length - 1]), Y(0));
    g.closePath();
    g.fill();

    // linhas tracejadas em x = a e x = b
    g.strokeStyle = cor('--azul'); g.setLineDash([4, 4]);
    [A.a, A.b].forEach(v => { g.beginPath(); g.moveTo(X(v), M.topo); g.lineTo(X(v), H - M.base); g.stroke(); });
    g.setLineDash([]);
  }

  // ---------- curvas ----------
  const cores = { f: cor('--azul'), g: cor('--laranja') };
  const saltoMaximo = (ymax - ymin) * 1.5;  

  resultado.curvas.forEach(c => {
    g.strokeStyle = cores[c.tipo];
    g.lineWidth = 2.4;
    g.beginPath();
    let anterior = null;
    c.x.forEach((xv, i) => {
      const yv = c.y[i];
      const quebra = yv === null || (anterior !== null && Math.abs(yv - anterior) > saltoMaximo);
      if (quebra || anterior === null) { if (yv !== null) g.moveTo(X(xv), Y(yv)); }
      else g.lineTo(X(xv), Y(yv));
      anterior = yv;
    });
    g.stroke();
  });

  // ---------- ponto do limite ----------
  resultado.marcas.forEach(m => {
    g.strokeStyle = cor('--laranja'); g.setLineDash([3, 4]); g.lineWidth = 1.2;
    g.beginPath(); g.moveTo(X(m.x), M.topo); g.lineTo(X(m.x), H - M.base); g.stroke();
    g.setLineDash([]);
    if (m.y !== null) {
      g.beginPath(); g.arc(X(m.x), Y(m.y), 5, 0, Math.PI * 2);
      g.fillStyle = m.buraco ? cor('--folha') : cor('--laranja');
      g.fill();
      g.lineWidth = 2; g.stroke();
    }
  });

  g.restore();

  // ---------- legenda ----------
  const itens = resultado.curvas.map(c => `<span><i style="background:${cores[c.tipo]}"></i>${c.nome}</span>`);
  if (resultado.area) itens.push(`<span><i style="background:${cor('--area')};height:10px"></i>área de a até b</span>`);
  if (resultado.marcas.length) itens.push(`<span><i style="background:${cor('--laranja')}"></i>x → ponto do limite</span>`);
  legenda.innerHTML = itens.join('');
}
