"""Standalone accessible HTML renderer for sanitized replay models."""

from __future__ import annotations

import html
import json

from .models import ReplayView


def render_replay_html(replay: ReplayView) -> str:
    """Render a self-contained viewer without embedding revealed nonces."""
    data = json.dumps(replay.to_object(), ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</", "<\\/")
    game_id = html.escape(replay.game_id)
    state = "verified" if replay.verdict == "Verified OK" else "tampered"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Replay - {game_id}</title>
<style>
:root{{--ink:#e8edf3;--muted:#9cabbc;--panel:#18212c;--line:#435064;--cop:#3b82f6;
--thief:#f59e0b;--barrier:#111827;--ok:#16a34a;--bad:#dc2626}}*{{box-sizing:border-box}}
body{{margin:0;background:#0b1017;color:var(--ink);font:16px system-ui,sans-serif}}
main{{max-width:980px;margin:auto;padding:28px}}
header{{display:flex;gap:18px;align-items:center;justify-content:space-between;flex-wrap:wrap}}
h1{{font-size:1.45rem;margin:0}}.verdict{{padding:10px 16px;border-radius:999px;
font-weight:800;background:var(--ok)}}
body[data-verdict="tampered"] .verdict{{background:var(--bad)}}
.layout{{display:grid;grid-template-columns:minmax(300px,620px) 1fr;gap:22px;margin-top:24px}}
#board{{display:grid;aspect-ratio:1;border:2px solid var(--line);background:#fff}}
.cell{{position:relative;border:1px solid #cbd5e1}}.blocked{{background:#64748b}}
.barrier{{background:var(--barrier)}}
.agent{{position:absolute;inset:18%;display:grid;place-items:center;border-radius:50%;
color:white;font-weight:900;border:3px solid #0b1017}}.police{{background:var(--cop)}}
.thief{{background:var(--thief);inset:29%}}
aside{{background:var(--panel);padding:18px;border-radius:12px}}
.legend span{{display:block;margin:8px 0}}.dot{{display:inline-block;width:12px;
height:12px;border-radius:50%;margin-right:8px}}
.controls{{display:flex;gap:10px;margin-top:18px}}
button{{padding:10px 14px;border:0;border-radius:8px;font-weight:700;cursor:pointer}}
button:disabled{{opacity:.45;cursor:not-allowed}}
#details{{color:var(--muted);line-height:1.6}}
@media(max-width:720px){{.layout{{grid-template-columns:1fr}}}}
</style></head><body data-verdict="{state}"><main>
<header><h1>Replay Viewer <small>- {game_id}</small></h1>
<div class="verdict" role="status">{replay.verdict}</div></header>
<div class="layout"><section><div id="board" aria-label="Post-game replay board"></div>
<div class="controls"><button id="previous" aria-label="Previous step">Previous step</button>
<button id="next" aria-label="Next step">Next step</button></div></section>
<aside><h2>Playback</h2><p id="details" aria-live="polite"></p><div class="legend">
<span><i class="dot" style="background:var(--cop)"></i>Police</span>
<span><i class="dot" style="background:var(--thief)"></i>Thief</span></div>
<p>Result: <strong>{html.escape(replay.result)}</strong></p>
<p>Integrity is recomputed before this file is written.
Any commitment or physics mismatch invalidates the whole replay.</p>
</aside></div></main><script type="application/json" id="replay-data">{data}</script>
<script>
const data=JSON.parse(document.getElementById('replay-data').textContent);let index=0;
const board=document.getElementById('board'),details=document.getElementById('details');
function key(p){{return p[0]+','+p[1]}}
function render(){{const f=data.frames[index],n=data.board_size;
board.style.gridTemplateColumns=`repeat(${{n}},1fr)`;board.replaceChildren();
const blocked=new Set(f.blocked_cells.map(key)),barriers=new Set(f.barriers.map(key));
for(let row=0;row<n;row++)for(let col=0;col<n;col++){{
const cell=document.createElement('div'),k=row+','+col;
cell.className='cell'+(blocked.has(k)?' blocked':'')+(barriers.has(k)?' barrier':'');
for(const [role,pos,label] of [['police',f.police_position,'P'],['thief',f.thief_position,'T']])
if(pos[0]===row&&pos[1]===col){{const a=document.createElement('span');
a.className='agent '+role;a.textContent=label;
a.setAttribute('aria-label',role);cell.append(a)}}board.append(cell)}}
details.textContent=`Frame ${{index+1}} / ${{data.frames.length}} | step ${{f.step}}
| actor ${{f.actor??'initial'}}`;
previous.disabled=index===0;next.disabled=index===data.frames.length-1}}
const previous=document.getElementById('previous'),next=document.getElementById('next');
previous.onclick=()=>{{index=Math.max(0,index-1);render()}};next.onclick=()=>{{index=Math.min(data.frames.length-1,index+1);render()}};render();
</script></body></html>"""
