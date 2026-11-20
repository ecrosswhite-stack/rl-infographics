#!/usr/bin/env python3
"""Render index.html (Reticulative Logic branding + Reticulation Sphere) from data/*.json(l)."""
import json, html, os, datetime, collections
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = {r['name']: r for r in json.load(open(f'{HERE}/data/plugins_classified.json'))}
status = {}
for line in open(f'{HERE}/data/port_status.jsonl'):
    line=line.strip()
    if line:
        s=json.loads(line); status[s['name']]=s
today = datetime.date.today().isoformat()
CLS = {'A':('Direct port','mint'),'B':('Re-implementable','cyan'),'C':('Partial','amber'),'D':('Not portable','violet')}
counts = collections.Counter(s['port_class'] for s in status.values())
conf = collections.Counter(s.get('confidence','?') for s in status.values())
cats = collections.Counter(r.get('category') or 'general' for r in rows.values())
def esc(x): return html.escape(str(x) if x is not None else '')
trs=[]
for name in sorted(rows):
    r=rows[name]; s=status.get(name,{})
    c=s.get('port_class','?'); label,col=CLS.get(c,('?','faint'))
    env=', '.join(s.get('env_vars') or []) or '—'
    mcp=', '.join(s.get('verified_mcp_packages') or []) or '—'
    trs.append(f"""<tr data-class="{c}" data-cat="{esc(r.get('category') or 'general')}">
<td><a href="skills/{esc(name)}/SKILL.md"><code>{esc(name)}</code></a><div class="desc">{esc((r.get('description') or '')[:220])}{'…' if len(r.get('description') or '')>220 else ''}</div></td>
<td>{esc(r.get('tier'))}</td><td>{esc(r.get('category') or 'general')}</td>
<td><span class="chip {col}"><i></i>{c} · {label}</span></td>
<td class="mono">{esc(s.get('confidence','?'))}</td>
<td class="mono">{esc(env)}</td><td class="mono">{esc(mcp)}</td>
<td class="mono">{'yes' if r.get('still_in_catalog') else 'dropped'}</td>
<td><a href="{esc(r['repo'])}/tree/{esc(r['sha'])}" rel="noopener">{esc(r['sha'][:7])}</a></td></tr>""")
tiles=''.join(f'<div class="tile"><b>{counts.get(k,0)}</b><span class="chip {CLS[k][1]}"><i></i>{k} · {CLS[k][0]}</span></div>' for k in 'ABCD')
total=len(status)
bar=''.join(f'<i class="{CLS[k][1]}" style="width:{(counts.get(k,0)/max(total,1))*100:.1f}%" title="{k}: {counts.get(k,0)}"></i>' for k in 'ABCD')
page=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hermes 100 · Claude Skills</title>
<meta name="description" content="100 Hermes Agent catalog-launch plugins ported to Claude skills, with port class, confidence and provenance. Reticulative Logic.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300..700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
/* ============ Reticulative Logic · Filament Graphite (single-theme, committed dark) ============ */
:root{{--bg:#0E0F11;--surface:#16181C;--surface-2:#1C1F24;--line:#262A31;--mint:#3FE0A6;--amber:#F2A23C;--violet:#B98CFF;--cyan:#5BC8F5;--ink:#F2F3F5;--dim:#9BA1AB;--faint:#5A6069;--disp:'Space Grotesk',system-ui,-apple-system,'Segoe UI',sans-serif;--mono:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace}}
*{{box-sizing:border-box;margin:0;padding:0}} html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--ink);font:400 16px/1.65 var(--disp);-webkit-font-smoothing:antialiased}}
a{{color:var(--mint);text-decoration:none}} a:hover{{text-decoration:underline;text-underline-offset:3px}}
.topbar{{position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:14px;padding:10px 22px;background:rgba(14,15,17,.82);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}}
.rl-mark{{width:30px;height:30px;flex:none}} .rl-mark .n{{transform-box:fill-box;transform-origin:center;animation:rl-breathe 3s ease-in-out infinite}}
@keyframes rl-breathe{{0%,100%{{opacity:.55;transform:scale(.9)}}50%{{opacity:1;transform:scale(1.12)}}}}
@media (prefers-reduced-motion:reduce){{.rl-mark .n{{animation:none;opacity:1}}}}
.wordmark{{font:600 13px/1 var(--disp);letter-spacing:.22em;text-transform:uppercase;color:var(--ink)}} .wordmark b{{color:var(--mint);font-weight:600}}
.topbar .lane{{margin-left:auto;font:500 10.5px/1 var(--mono);letter-spacing:.15em;text-transform:uppercase;color:var(--faint)}} .topbar .lane em{{font-style:normal;color:var(--dim)}}
.hero{{position:relative;display:grid;grid-template-columns:minmax(0,7fr) minmax(0,5fr);align-items:center;gap:0 24px;padding:64px max(4vw,24px) 36px;background:radial-gradient(1200px 640px at 78% 38%,rgba(63,224,166,.075),transparent 62%),radial-gradient(900px 520px at 8% 88%,rgba(185,140,255,.05),transparent 60%),var(--bg)}}
.kicker{{font:500 11px/1.6 var(--mono);letter-spacing:.15em;text-transform:uppercase;color:var(--faint)}} .kicker .dot{{color:var(--mint)}}
.hero h1{{margin:16px 0 20px;font-weight:640;letter-spacing:-.035em;font-size:clamp(2.2rem,6vw,4.8rem);line-height:1;text-wrap:balance}}
.hero h1 .hollow{{color:transparent;-webkit-text-stroke:1.5px var(--mint)}}
.dek{{max-width:58ch;color:var(--dim);font-size:clamp(1rem,1.4vw,1.15rem)}} .dek strong{{color:var(--ink);font-weight:560}}
.hero-meta{{display:flex;flex-wrap:wrap;gap:10px 26px;margin-top:28px;font:400 11.5px/1.7 var(--mono);color:var(--faint)}}
.hero-meta b{{display:block;color:var(--dim);font-weight:500;letter-spacing:.12em;text-transform:uppercase;font-size:10px}}
.sphere-wrap{{align-self:center;min-width:0}} #rl-sphere{{width:100%;max-width:420px;aspect-ratio:1;display:block;margin:auto}}
.rl-cap{{text-align:center;color:var(--faint);font:400 12px/1.6 var(--mono);margin-top:2px}}
@media (max-width:900px){{.hero{{grid-template-columns:1fr;padding-top:40px}}.sphere-wrap{{order:-1}}#rl-sphere{{max-width:260px}}}}
.legend{{display:flex;flex-wrap:wrap;align-items:center;gap:10px 18px;padding:14px max(4vw,24px);border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:var(--surface);font:400 12px/1.6 var(--mono);color:var(--dim)}}
.chip{{display:inline-flex;align-items:center;gap:7px;padding:3px 10px;border-radius:999px;font:500 10.5px/1.6 var(--mono);letter-spacing:.08em;white-space:nowrap;border:1px solid var(--line);background:var(--bg)}}
.chip i{{width:7px;height:7px;border-radius:50%;flex:none}}
.chip.mint{{color:var(--mint)}}.chip.mint i{{background:var(--mint)}} .chip.cyan{{color:var(--cyan)}}.chip.cyan i{{background:var(--cyan)}}
.chip.amber{{color:var(--amber)}}.chip.amber i{{background:var(--amber)}} .chip.violet{{color:var(--violet)}}.chip.violet i{{background:var(--violet)}}
main{{max-width:1280px;margin:0 auto;padding:28px max(4vw,24px) 80px}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:10px 0 14px}}
.tile{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px}} .tile b{{display:block;font:600 30px/1.1 var(--disp);letter-spacing:-.03em;margin-bottom:8px}}
.bar{{display:flex;height:8px;border-radius:999px;overflow:hidden;background:var(--surface-2);margin:0 0 26px}} .bar i{{display:block;height:100%}}
.bar .mint{{background:var(--mint)}}.bar .cyan{{background:var(--cyan)}}.bar .amber{{background:var(--amber)}}.bar .violet{{background:var(--violet)}}
h2{{font-size:1.5rem;font-weight:620;letter-spacing:-.02em;margin:34px 0 10px}} p.sub{{color:var(--dim);max-width:70ch;margin-bottom:14px}}
.controls{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}} .controls button,.controls input{{font:500 11.5px/1.6 var(--mono);letter-spacing:.06em;background:var(--surface);color:var(--dim);border:1px solid var(--line);border-radius:999px;padding:5px 12px;cursor:pointer}}
.controls button.on{{color:var(--mint);border-color:var(--mint)}} .controls input{{cursor:text;min-width:220px;border-radius:8px}}
.tblwrap{{overflow:auto;border:1px solid var(--line);border-radius:10px}} table{{width:100%;border-collapse:collapse;font-size:13.5px}}
th{{position:sticky;top:0;background:var(--surface-2);text-align:left;font:500 10.5px/1.6 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--faint);padding:10px 12px;border-bottom:1px solid var(--line)}}
td{{padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top;color:#D7DADF}} tr:hover td{{background:var(--surface)}}
td code{{font:500 12.5px/1.5 var(--mono);color:var(--ink)}} td .desc{{color:var(--faint);font-size:12px;max-width:46ch;margin-top:3px}} .mono{{font:400 12px/1.6 var(--mono);color:var(--dim)}}
.prov{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:16px 18px;font-size:14px;color:#D7DADF}} .prov li{{margin:4px 0 4px 18px}}
footer{{display:flex;flex-wrap:wrap;gap:14px 28px;align-items:center;justify-content:space-between;padding:22px max(4vw,24px);border-top:1px solid var(--line);color:var(--faint);font:400 12px/1.6 var(--mono)}}
</style></head><body>
<header class="topbar">
  <svg class="rl-mark" viewBox="0 0 100 100" fill="none" aria-label="Reticulative Logic">
    <line x1="38" y1="36" x2="34" y2="64" stroke="#3FE0A6" stroke-width="3"/><line x1="38" y1="36" x2="66" y2="62" stroke="#3FE0A6" stroke-width="3"/><line x1="34" y1="64" x2="66" y2="62" stroke="#3FE0A6" stroke-width="3"/>
    <circle class="n" cx="38" cy="36" r="8" fill="#3FE0A6"/><circle class="n" cx="34" cy="64" r="8" fill="#3FE0A6" style="animation-delay:.5s"/><circle class="n" cx="66" cy="62" r="8" fill="#3FE0A6" style="animation-delay:1s"/>
  </svg>
  <div class="wordmark">Reticulative <b>Logic</b></div>
  <div class="lane">tooling lane · <em>hermes 100 → claude</em> · {today}</div>
</header>
<div class="hero"><div>
  <p class="kicker"><span class="dot">●</span> skills pack · sourced &amp; state-tagged</p>
  <h1>Hermes <span class="hollow">100</span><br>for Claude</h1>
  <p class="dek"><strong>The Hermes Agent plugin catalog launched with exactly 100 reviewed plugins.</strong> Each one is reconstructed from its pinned commit and ported to a Claude skill, with an honest port class: what Claude can do the same way, what it can do partly, and what has no equivalent outside the Hermes runtime.</p>
  <div class="hero-meta">
    <div><b>Source set</b>hermes-agent @ bb0c230 · 2026-09-16</div>
    <div><b>Method</b>per-plugin source read · packages verified</div>
    <div><b>Epistemics</b>every row carries a confidence</div>
    <div><b>Built</b>{today}</div>
  </div>
</div>
<div class="sphere-wrap"><canvas id="rl-sphere" aria-hidden="true"></canvas><p class="rl-cap">100 nodes, 3 nearest links each: the reticulum of the launch catalog.</p></div></div>
<div class="legend" role="note">
  <span class="chip mint"><i></i>A — direct port (MCP + skill)</span><span class="chip cyan"><i></i>B — re-implementable via same API</span>
  <span class="chip amber"><i></i>C — partial</span><span class="chip violet"><i></i>D — not portable (reference card)</span>
  <span style="flex:1 1 30ch">Confidence is how sure the port works as described: <em>high</em> only when the API or CLI is documented in the plugin source and needs no Hermes runtime.</span>
</div>
<main>
<div class="tiles">{tiles}<div class="tile"><b>{total}</b><span class="chip"><i style="background:var(--dim)"></i>plugins classified</span></div></div>
<div class="bar">{bar}</div>
<h2>Provenance</h2>
<div class="prov"><ul>
<li><b>Announcement.</b> Nous Research on X, 2026-09-16: catalog "starting with 4 official plugins and 96 from the community".</li>
<li><b>Membership.</b> <a href="https://github.com/NousResearch/hermes-agent/tree/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog" rel="noopener">plugin-catalog @ bb0c2303</a> holds exactly 100 entries (96 community, 4 official). Last catalog commit before the announcement.</li>
<li><b>Sources.</b> Every plugin fetched at its catalog-pinned SHA; 98 of 100 reachable. <code>herdr-auto-reconcile</code> and <code>web-oxylabs</code> repositories are no longer public (checked {today}).</li>
<li><b>Confidence split.</b> {' · '.join(f'{k}: {v}' for k,v in sorted(conf.items()))}.</li>
<li><b>Categories.</b> {' · '.join(f'{k}: {v}' for k,v in sorted(cats.items()))}.</li>
</ul></div>
<h2>All 100 plugins</h2>
<p class="sub">Click a name to open its Claude skill. Filter by port class or search.</p>
<div class="controls"><button class="on" data-f="">all</button><button data-f="A">A</button><button data-f="B">B</button><button data-f="C">C</button><button data-f="D">D</button><input id="q" placeholder="search name / description"></div>
<div class="tblwrap"><table><thead><tr><th>Plugin</th><th>Tier</th><th>Category</th><th>Port class</th><th>Confidence</th><th>Env vars</th><th>Verified MCP pkg</th><th>In catalog today</th><th>Pinned</th></tr></thead><tbody id="tb">
{''.join(trs)}
</tbody></table></div>
</main>
<footer>
  <div style="display:flex;align-items:center;gap:12px"><svg class="rl-mark" viewBox="0 0 100 100" fill="none" aria-hidden="true" style="width:24px;height:24px"><line x1="38" y1="36" x2="34" y2="64" stroke="#3FE0A6" stroke-width="3"/><line x1="38" y1="36" x2="66" y2="62" stroke="#3FE0A6" stroke-width="3"/><line x1="34" y1="64" x2="66" y2="62" stroke="#3FE0A6" stroke-width="3"/><circle cx="38" cy="36" r="8" fill="#3FE0A6"/><circle cx="34" cy="64" r="8" fill="#3FE0A6"/><circle cx="66" cy="62" r="8" fill="#3FE0A6"/></svg><span class="wordmark">Reticulative <b>Logic</b></span></div>
  <div><b>Hermes 100 for Claude</b> · tooling lane · built {today} · claims carry states, numbers carry sources</div>
</footer>
<script>
const REDUCE = matchMedia('(prefers-reduced-motion:reduce)').matches;
/* ---------- Reticulation Sphere (insight flashes propagate along edges) ---------- */
(() => {{
  const cv = document.getElementById('rl-sphere'); if(!cv) return;
  const ctx = cv.getContext('2d'); const HUE='#3FE0A6', N=100, K=3;
  let W,H,R,pts=[],edges=[],adj=[],t=0,running=false,raf=0; let flash={{node:-1,age:1e9}};
  function size(){{const d=devicePixelRatio||1,s=cv.clientWidth||320;cv.width=s*d;cv.height=s*d;ctx.setTransform(d,0,0,d,0,0);W=s;H=s;R=s*.4}}
  function build(){{pts=[];const g=Math.PI*(3-Math.sqrt(5));
    for(let i=0;i<N;i++){{const y=1-(i/(N-1))*2,r=Math.sqrt(1-y*y),th=g*i;pts.push({{x:Math.cos(th)*r,y,z:Math.sin(th)*r}})}}
    edges=[];adj=Array.from({{length:N}},()=>[]);
    for(let i=0;i<N;i++){{const d=pts.map((p,j)=>({{j,d:(p.x-pts[i].x)**2+(p.y-pts[i].y)**2+(p.z-pts[i].z)**2}})).sort((a,b)=>a.d-b.d).slice(1,K+1);
      d.forEach(n=>{{if(i<n.j){{edges.push([i,n.j]);adj[i].push(edges.length-1);adj[n.j].push(edges.length-1)}}}})}}}}
  function frame(){{if(!running)return; t+=REDUCE?0:.004;
    if(!REDUCE){{flash.age+=.016; if(flash.age>4.2){{flash={{node:(Math.random()*N)|0,age:0}}}}}}
    ctx.clearRect(0,0,W,H); const cy=Math.cos(t*.6),sy=Math.sin(t*.6);
    const proj=pts.map(p=>{{const x=p.x*cy-p.z*sy,z=p.x*sy+p.z*cy;const s=1/(2.2-z);return {{sx:W/2+x*R*s,sy:H/2+p.y*R*s,z,s}}}});
    const hot=new Set(flash.node>=0&&flash.age<1.6?adj[flash.node]:[]);
    edges.forEach(([a,b],i)=>{{const A=proj[a],B=proj[b];const pulse=REDUCE?.25:(Math.sin(t*3+i)*.5+.5);let al=.06+pulse*.30,lw=.6+pulse*.9;
      if(hot.has(i)){{const k=Math.max(0,1-flash.age/1.6);al=Math.min(1,al+.55*k);lw+=1.3*k}}
      ctx.globalAlpha=al;ctx.strokeStyle=HUE;ctx.lineWidth=lw;ctx.beginPath();ctx.moveTo(A.sx,A.sy);ctx.lineTo(B.sx,B.sy);ctx.stroke()}});
    ctx.globalAlpha=1;
    proj.forEach((p,i)=>{{ctx.fillStyle=HUE;let al=.4+(p.z+1)/2*.6,r=1.4+p.s*1.6;
      if(i===flash.node&&flash.age<1.6){{const k=Math.max(0,1-flash.age/1.6);al=1;r+=2.6*k;ctx.shadowColor=HUE;ctx.shadowBlur=18*k}}
      ctx.globalAlpha=al;ctx.beginPath();ctx.arc(p.sx,p.sy,r,0,7);ctx.fill();ctx.shadowBlur=0}});
    ctx.globalAlpha=1;raf=requestAnimationFrame(frame)}}
  function start(){{if(running)return;running=true;frame()}} function stop(){{running=false;cancelAnimationFrame(raf)}}
  size();build();addEventListener('resize',()=>{{size();build()}});
  if(REDUCE){{running=true;frame();running=false}}
  new IntersectionObserver(es=>es[0].isIntersecting?start():stop(),{{threshold:.05}}).observe(cv);
}})();
/* ---------- filter ---------- */
(() => {{
  const rows=[...document.querySelectorAll('#tb tr')]; let f='',q='';
  const apply=()=>rows.forEach(r=>{{const ok=(!f||r.dataset.class===f)&&(!q||r.textContent.toLowerCase().includes(q));r.style.display=ok?'':'none'}});
  document.querySelectorAll('.controls button').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.controls button').forEach(x=>x.classList.remove('on'));b.classList.add('on');f=b.dataset.f;apply()}});
  document.getElementById('q').oninput=e=>{{q=e.target.value.toLowerCase();apply()}};
}})();
</script></body></html>"""
open(f'{HERE}/index.html','w').write(page)
print('index.html written:', len(page), 'bytes;', total, 'status rows;', counts)
