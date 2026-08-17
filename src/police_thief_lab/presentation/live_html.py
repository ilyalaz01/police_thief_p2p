"""Standalone browser UI for a loopback role-local Live GUI feed."""

from __future__ import annotations


def render_live_html() -> str:
    """Return a dependency-free heatmap UI that never requests opponent truth."""
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Police-Thief Live GUI</title><style>
:root{--ink:#edf2f7;--muted:#a8b3c2;--panel:#17212d;--line:#526174;--green:#15803d;
--locked:#64748b;--over:#2563eb;--error:#b91c1c;--agent:#0f62a8;--barrier:#111827}
*{box-sizing:border-box}body{margin:0;background:#0b1017;color:var(--ink);
font:16px system-ui,sans-serif}main{max-width:1000px;margin:auto;padding:26px}
header{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}
h1{font-size:1.45rem;margin:0}.banner{padding:11px 18px;border-radius:9px;font-weight:900;
background:var(--locked)}.banner[data-state="YOUR TURN"]{background:var(--green)}
.banner[data-state="GAME OVER"]{background:var(--over)}
.banner[data-state="ERROR"]{background:var(--error)}
.layout{display:grid;grid-template-columns:minmax(320px,650px) 1fr;gap:22px;margin-top:22px}
#board{display:grid;aspect-ratio:1;border:2px solid var(--line);background:white}
.cell{position:relative;border:1px solid #d3dae3}.blocked{background:#64748b!important}
.barrier{background:var(--barrier)!important}.agent{position:absolute;inset:19%;display:grid;
place-items:center;border:3px solid #07111f;border-radius:50%;background:var(--agent);
color:white;font-size:1.15rem;font-weight:900}aside{background:var(--panel);padding:18px;border-radius:12px}
#details,#notice{color:var(--muted);line-height:1.55}.controls{display:flex;gap:8px;flex-wrap:wrap}
button{padding:9px 12px;border:0;border-radius:7px;font-weight:750;cursor:pointer}
button:disabled{opacity:.45;cursor:not-allowed}.scale{height:14px;border-radius:8px;
background:linear-gradient(90deg,#fff,#ffb0b0,#e00000);border:1px solid #8994a3}
@media(max-width:720px){.layout{grid-template-columns:1fr}}
</style></head><body><main><header><h1>Live GUI (Local Truth)</h1>
<div id="banner" class="banner" data-state="LOCKED" role="status" aria-live="assertive">LOCKED</div>
</header><div class="layout"><section><div id="board" aria-label="Role-local belief heatmap"></div>
<div class="controls">
<button id="previous" aria-label="Previous snapshot">Previous snapshot</button>
<button id="next" aria-label="Next snapshot">Next snapshot</button>
<button id="latest">Follow latest</button></div></section><aside><h2>Observable state</h2>
<p id="details" aria-live="polite">Waiting for the first safe snapshot...</p>
<p id="notice">Only local truth is displayed: my position, public barriers, and my belief about
the other player. The other player's true coordinate is never requested.</p>
<p>Higher belief probability means deeper red.</p>
<div class="scale" aria-label="Belief intensity scale"></div>
</aside></div></main><script>
let history=[],index=-1,follow=true;const board=document.getElementById('board');
const banner=document.getElementById('banner'),details=document.getElementById('details');
const previous=document.getElementById('previous'),next=document.getElementById('next');
function key(value){return value[0]+','+value[1]}
function render(){if(index<0||!history.length)return;const item=history[index],view=item.view;
const belief=new Map(view.belief.map(v=>[v[0]+','+v[1],v[2]]));
const peak=Math.max(0,...view.belief.map(v=>v[2]));
const blocked=new Set(view.blocked_cells.map(key)),barriers=new Set(view.barriers.map(key));
board.style.gridTemplateColumns=`repeat(${view.board_size},1fr)`;board.replaceChildren();
for(let row=0;row<view.board_size;row++)for(let col=0;col<view.board_size;col++){
const cell=document.createElement('div'),cellKey=row+','+col,value=belief.get(cellKey)||0;
const level=peak?Math.min(1,value/peak):0,shade=Math.round(255*(1-.85*level));
cell.className='cell'+(blocked.has(cellKey)?' blocked':'')+(barriers.has(cellKey)?' barrier':'');
cell.style.background=`rgb(255,${shade},${shade})`;if(key(view.own_position)===cellKey){
const agent=document.createElement('span');agent.className='agent';
agent.textContent=view.role==='police'?'P':'T';
agent.setAttribute('aria-label','my '+view.role);cell.append(agent)}board.append(cell)}
banner.textContent=view.banner;banner.dataset.state=view.banner;
details.textContent=`${view.role} | step ${view.step} | snapshot ${item.revision}
| ${index+1}/${history.length}`;
previous.disabled=index<=0;next.disabled=index>=history.length-1}
previous.onclick=()=>{follow=false;index=Math.max(0,index-1);render()};
next.onclick=()=>{index=Math.min(history.length-1,index+1);follow=index===history.length-1;render()};
document.getElementById('latest').onclick=()=>{follow=true;index=history.length-1;render()};
async function poll(){try{const response=await fetch('/snapshot.json',{cache:'no-store'});
if(!response.ok)throw new Error('snapshot unavailable');const feed=await response.json();
history=feed.updates;if(follow||index<0)index=history.length-1;
else index=Math.min(index,history.length-1);render()}catch(error){
details.textContent='Waiting for a valid role-local snapshot...'}setTimeout(poll,250)}poll();
</script></body></html>"""
