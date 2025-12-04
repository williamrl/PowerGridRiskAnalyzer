// Simple SVG graph renderer
function renderGraph(svgId, nodes, edges, survivingIds, failedIds) {
  const svg = document.getElementById(svgId);
  if (!svg) return;
  // clear
  while (svg.firstChild) svg.removeChild(svg.firstChild);

  const w = svg.clientWidth || 600;
  const h = svg.clientHeight || 400;

  // layout nodes in circle
  const nodeList = Array.from(nodes).sort();
  const N = nodeList.length;
  const centerX = w/2, centerY = h/2, radius = Math.min(w,h)/3;
  const positions = {};
  nodeList.forEach((n,i)=>{
    const angle = (i / N) * Math.PI * 2;
    positions[n] = {x: centerX + radius * Math.cos(angle), y: centerY + radius * Math.sin(angle)};
  });

  // draw edges
  edges.forEach(e=>{
    const u = e.u, v = e.v;
    const p1 = positions[u], p2 = positions[v];
    const line = document.createElementNS('http://www.w3.org/2000/svg','line');
    line.setAttribute('x1', p1.x); line.setAttribute('y1', p1.y);
    line.setAttribute('x2', p2.x); line.setAttribute('y2', p2.y);
    line.setAttribute('stroke-width', 3);
    const id = e.id;
    if (failedIds.includes(id)) {
      line.setAttribute('stroke', '#d9534f'); // red
    } else if (survivingIds.includes(id)) {
      line.setAttribute('stroke', '#5cb85c'); // green
    } else {
      line.setAttribute('stroke', '#999');
    }
    svg.appendChild(line);
  });

  // draw nodes
  nodeList.forEach(n=>{
    const p = positions[n];
    const circle = document.createElementNS('http://www.w3.org/2000/svg','circle');
    circle.setAttribute('cx', p.x); circle.setAttribute('cy', p.y);
    circle.setAttribute('r', 14); circle.setAttribute('fill', '#337ab7');
    circle.setAttribute('stroke', '#222'); circle.setAttribute('stroke-width', 1);
    svg.appendChild(circle);
    const text = document.createElementNS('http://www.w3.org/2000/svg','text');
    text.setAttribute('x', p.x); text.setAttribute('y', p.y+4);
    text.setAttribute('font-size','12'); text.setAttribute('text-anchor','middle');
    text.setAttribute('fill','#fff');
    text.textContent = n;
    svg.appendChild(text);
  });
}

// Helper to load JSON-encoded data attribute and render
function renderGraphFromData(svgId, dataId) {
  const el = document.getElementById(dataId);
  if (!el) return;
  try {
    const data = JSON.parse(el.textContent);
    renderGraph(svgId, data.nodes, data.edges, data.surviving, data.failed);
  } catch(e){ console.error(e); }
}
