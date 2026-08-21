from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

MARKER = '/* MONTHLY ALL-AGENT REPORT V1 */'
if MARKER in text:
    print('Monthly all-agent report already applied; nothing to do.')
    raise SystemExit(0)

monthly_css = r'''
  /* MONTHLY ALL-AGENT REPORT V1 */
  .rep-monthly-summary,.rep-monthly-agent{box-sizing:border-box}
  .rep-monthly-summary{min-height:0}
  .rep-monthly-agent{margin-top:26px;padding-top:2px;border-top:1px solid #eef0f3}
  .rep-agent-head{display:flex;align-items:center;gap:14px;margin-bottom:16px;padding-bottom:13px;border-bottom:2px solid #123a5e}
  .rep-agent-photo{width:58px;height:58px;border-radius:14px;object-fit:cover;border:2px solid #c6952a;background:#eef2f6;flex:0 0 58px}
  .rep-agent-initials{width:58px;height:58px;border-radius:14px;border:2px solid #c6952a;background:#eef2f6;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;color:#123a5e;flex:0 0 58px}
  .rep-agent-name{font-size:21px;font-weight:700;color:#101828;line-height:1.1}
  .rep-agent-role{font-size:11px;font-weight:600;color:#123a5e;margin-top:4px}
  .rep-agent-month{font-size:10.5px;color:#667085;margin-top:4px}
  .rep-agent-ranks{margin-left:auto;text-align:right;font-size:10.5px;line-height:1.65;color:#667085}
  .rep-agent-ranks b{color:#123a5e}
  .rep-target-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px}
  .rep-target{border:1px solid #e4e7ec;border-radius:10px;padding:10px 12px;background:#fafbfc}
  .rep-target .l{font-size:8.5px;letter-spacing:.8px;text-transform:uppercase;color:#667085;font-weight:600}
  .rep-target .v{font-size:14px;font-weight:700;color:#101828;margin-top:4px}
  .rep-target .p{font-size:10px;color:#667085;margin-top:3px}
  .rep-eff{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:10px}
  .rep-eff .e{border:1px solid #e4e7ec;border-radius:9px;padding:9px 10px;text-align:center}
  .rep-eff .v{font-size:15px;font-weight:700;color:#123a5e}
  .rep-eff .l{font-size:8px;letter-spacing:.55px;text-transform:uppercase;color:#98a2b3;margin-top:3px}
  .rep-weekly th:nth-child(1){width:27%}
  .rep-weekly th:nth-child(n+2){width:18.25%}
  .rep-ach{font-weight:700;color:#123a5e}
  .rep-ach.good{color:#2f9e5b}
  .rep-ach.warn{color:#b5842a}
  @media(max-width:700px){
    .rep-kgrid{grid-template-columns:repeat(2,1fr)}
    .rep-eff{grid-template-columns:repeat(2,1fr)}
    .rep-target-grid{grid-template-columns:1fr}
    .rep-agent-ranks{display:none}
    .rep-body{padding:20px 16px 26px}
  }
  @media print{
    .rep-monthly-agent{break-before:page;page-break-before:always;margin-top:0;padding-top:0;border-top:0}
    .rep-monthly-summary,.rep-monthly-agent{break-inside:avoid-page;page-break-inside:avoid}
    .rep-agent-head,.rep-kgrid,.rep-target-grid,.rep-eff,.rep-tbl,.rep-h{break-inside:avoid;page-break-inside:avoid}
    .rep-body{padding:0!important}
    .rep-monthly-summary,.rep-monthly-agent{width:100%}
    @page{size:A4;margin:12mm}
  }
'''

print_anchor = '  @media print{\n    body>*{display:none!important}'
if print_anchor not in text:
    raise RuntimeError('Could not find report print CSS anchor')
text = text.replace(print_anchor, monthly_css + '\n  @media print{\n    body>*{display:none!important}', 1)

monthly_js = r'''

  function esc(v){return String(v==null?'':v).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));}
  function fPct(v){return (Math.round((Number(v)||0)*10)/10).toFixed(1).replace(/\.0$/,'')+'%';}
  function achievement(actual,target){return target>0?Math.round(actual/target*100):0;}
  function achievementClass(v){return v>=100?'good':v>=75?'warn':'';}
  function initials(name){return String(name||'').trim().split(/\s+/).slice(0,2).map(p=>p[0]||'').join('').toUpperCase()||'—';}
  function selectedMonthOpt(){
    const opts=buildPeriods('month');
    let key=(typeof state!=='undefined'&&state.period==='month')?state.periodKey:null;
    const pick=document.getElementById('period-pick');
    if(typeof state!=='undefined'&&state.period==='month'&&pick&&pick.value)key=pick.value;
    return opts.find(o=>o.key===key)||opts[opts.length-1];
  }
  function monthWeekRanges(range){
    const out=[];let cur=parseD(range.start),end=parseD(range.end),i=1;
    while(cur<=end){
      const daysToSun=(7-cur.getUTCDay())%7;
      let stop=addDays(cur,daysToSun);if(stop>end)stop=end;
      out.push({label:'Week '+i,start:fmtD(cur),end:fmtD(stop)});
      cur=addDays(stop,1);i++;
    }
    return out;
  }
  function rankFor(rows,name,key){
    const sorted=[...rows].sort((a,b)=>(b[key]||0)-(a[key]||0)||a.name.localeCompare(b.name));
    return sorted.findIndex(r=>r.name===name)+1;
  }
  function agentPhotoHTML(name){
    const meta=AGENT_META[name]||{};
    return meta.photo?`<img class="rep-agent-photo" src="${esc(meta.photo)}" alt="${esc(name)}">`:`<div class="rep-agent-initials">${esc(initials(name))}</div>`;
  }
  function openMonthlyOverlay(body,label){
    let ov=document.getElementById('rep-overlay');
    if(!ov){ov=document.createElement('div');ov.id='rep-overlay';document.body.appendChild(ov);ov.onclick=e=>{if(e.target===ov)ov.classList.remove('show');};}
    ov.innerHTML=`<div class="rep-paper"><div class="rep-bar"><div class="t">Monthly Report · ${esc(label)} · All Active Agents</div><div class="btns"><button class="rep-print" onclick="window.print()">🖨 Print / Save as PDF</button><button class="rep-close" onclick="document.getElementById('rep-overlay').classList.remove('show')">✕ Close</button></div></div><div class="rep-body">${body}</div></div>`;
    ov.classList.add('show');ov.scrollTop=0;
  }
  function generateMonthlyAllAgent(){
    const opt=selectedMonthOpt();
    if(!opt)return;
    const key=opt.key,range=rangeOf('month',key),agg=aggregate(range);
    const agents=activeAgents(range);
    const rows=agents.map(name=>({name,...aggregate(range,name),activeLeads:latestLeads(name,range)})).sort((a,b)=>b.rev-a.rev||b.deals-a.deals||b.mtg-a.mtg||b.calls-a.calls||a.name.localeCompare(b.name));
    const teamFactor=teamTargetFactor('month',range);
    const tCalls=Math.round(T.callsPerMonth*teamFactor),tMtg=Math.round(T.meetingsPerMonth*teamFactor),tRev=Math.round(T.revenuePerMonth*teamFactor);
    const dealsList=DEALS.filter(d=>inRange(d.date,range)).sort((a,b)=>a.date<b.date?1:-1);
    const fdate=d=>new Date(d+'T00:00:00Z').toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});
    const generated=new Date().toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});
    const ach=(actual,target)=>`<span class="rep-ach ${achievementClass(achievement(actual,target))}">${achievement(actual,target)}%</span>`;
    const summary=`
      <section class="rep-monthly-summary">
        <div class="rep-hh"><div class="rep-brand"><div class="p">PROVIDENT</div><div class="s">REAL ESTATE</div></div><div class="rep-meta">Team Rashwan · Monthly Management Report<br>Generated ${generated}<br>Confidential — Internal Use Only</div></div>
        <div class="rep-title">TEAM RASHWAN — ${esc(opt.label.toUpperCase())} SUMMARY</div>
        <div class="rep-sub">Reporting period: ${fdate(range.start)} – ${fdate(range.end)} &nbsp;·&nbsp; ${rows.length} active agent${rows.length===1?'':'s'}</div>
        <div class="rep-kgrid">
          <div class="rep-k"><div class="l">Total Calls</div><div class="v">${num(agg.calls)}</div><div class="d">${num(tCalls)} target · ${ach(agg.calls,tCalls)}</div></div>
          <div class="rep-k"><div class="l">Total Meetings</div><div class="v">${num(agg.mtg)}</div><div class="d">${num(tMtg)} target · ${ach(agg.mtg,tMtg)}</div></div>
          <div class="rep-k"><div class="l">Deals Closed</div><div class="v">${agg.deals}</div><div class="d">${agg.pending?agg.pending+' value pending':'all confirmed'}</div></div>
          <div class="rep-k"><div class="l">Total Revenue</div><div class="v" style="color:#b5842a">${fFull(agg.rev)}</div><div class="d">${fFull(tRev)} target · ${ach(agg.rev,tRev)}</div></div>
        </div>
        <div class="rep-h">Agent Leaderboard — ${esc(opt.label)}</div>
        <table class="rep-tbl rep-agent-tbl"><thead><tr><th>#</th><th>Agent</th><th class="n">Calls</th><th class="n">Meetings</th><th class="n">Deals</th><th class="n">Revenue (AED)</th></tr></thead><tbody>
          ${rows.length?rows.map((a,i)=>`<tr class="${i===0?'top':''}"><td>${i+1}</td><td>${esc(a.name)}</td><td class="n">${num(a.calls)}</td><td class="n">${num(a.mtg)}</td><td class="n">${a.deals}</td><td class="n rev">${a.rev?num(a.rev):'—'}</td></tr>`).join(''):'<tr><td colspan="6" style="text-align:center;color:#98a2b3;padding:16px">No activity in this month.</td></tr>'}
          <tr style="font-weight:700;background:#eef2f6"><td></td><td>TEAM TOTAL</td><td class="n">${num(agg.calls)}</td><td class="n">${num(agg.mtg)}</td><td class="n">${agg.deals}</td><td class="n rev">${num(agg.rev)}</td></tr>
        </tbody></table>
        <div class="rep-h">Deals Closed — ${dealsList.length} deal${dealsList.length===1?'':'s'}</div>
        <table class="rep-tbl"><thead><tr><th>Date</th><th>Agent</th><th class="n">Value (AED)</th></tr></thead><tbody>
          ${dealsList.length?dealsList.map(d=>`<tr><td>${fdate(d.date)}${d.approxDate?' *':''}</td><td>${esc(d.name)}</td><td class="n rev">${d.aed?num(d.aed):'value pending'}</td></tr>`).join(''):'<tr><td colspan="3" style="text-align:center;color:#98a2b3;padding:16px">No deals closed in this month.</td></tr>'}
        </tbody></table>
      </section>`;
    const agentSections=rows.map(a=>{
      const meta=AGENT_META[a.name]||{},factor=targetFactor(a.name,'month',range);
      const callsTarget=Math.round(T.callsPerMonth*factor),mtgTarget=Math.round(T.meetingsPerMonth*factor),revTarget=Math.round(T.revenuePerMonth*factor);
      const c2m=a.calls?a.mtg/a.calls*100:0,m2d=a.mtg?a.deals/a.mtg*100:0,c2d=a.calls?a.deals/a.calls*100:0,rpd=a.deals?a.rev/a.deals:0;
      const weeks=monthWeekRanges(range).map(w=>({w,...aggregate({start:w.start,end:w.end},a.name)}));
      return `<section class="rep-monthly-agent">
        <div class="rep-agent-head">${agentPhotoHTML(a.name)}<div><div class="rep-agent-name">${esc(a.name)} — ${esc(opt.label.toUpperCase())} PERFORMANCE</div><div class="rep-agent-role">${esc(meta.role||'Sales Agent')}</div><div class="rep-agent-month">${fdate(range.start)} – ${fdate(range.end)}</div></div><div class="rep-agent-ranks"><b>Revenue #${rankFor(rows,a.name,'rev')}</b> of ${rows.length}<br>Deals #${rankFor(rows,a.name,'deals')} · Calls #${rankFor(rows,a.name,'calls')} · Meetings #${rankFor(rows,a.name,'mtg')}</div></div>
        <div class="rep-kgrid">
          <div class="rep-k"><div class="l">Calls</div><div class="v">${num(a.calls)}</div><div class="d">${num(callsTarget)} target · ${ach(a.calls,callsTarget)}</div></div>
          <div class="rep-k"><div class="l">Meetings</div><div class="v">${num(a.mtg)}</div><div class="d">${num(mtgTarget)} target · ${ach(a.mtg,mtgTarget)}</div></div>
          <div class="rep-k"><div class="l">Deals Closed</div><div class="v">${a.deals}</div><div class="d">${a.pending?a.pending+' value pending':'confirmed'}</div></div>
          <div class="rep-k"><div class="l">Revenue</div><div class="v" style="color:#b5842a">${fFull(a.rev)}</div><div class="d">${fFull(revTarget)} target · ${ach(a.rev,revTarget)}</div></div>
        </div>
        <div class="rep-target-grid">
          <div class="rep-target"><div class="l">Calls Target Achievement</div><div class="v">${num(a.calls)} / ${num(callsTarget)}</div><div class="p">${achievement(a.calls,callsTarget)}% of target</div></div>
          <div class="rep-target"><div class="l">Meetings Target Achievement</div><div class="v">${num(a.mtg)} / ${num(mtgTarget)}</div><div class="p">${achievement(a.mtg,mtgTarget)}% of target</div></div>
          <div class="rep-target"><div class="l">Active Leads</div><div class="v">${a.activeLeads==null?'—':num(a.activeLeads)}</div><div class="p">Latest available in selected month</div></div>
        </div>
        <div class="rep-h">Conversion &amp; Efficiency</div>
        <div class="rep-eff"><div class="e"><div class="v">${fPct(c2m)}</div><div class="l">Calls → Meetings</div></div><div class="e"><div class="v">${fPct(m2d)}</div><div class="l">Meetings → Deals</div></div><div class="e"><div class="v">${fPct(c2d)}</div><div class="l">Calls → Deals</div></div><div class="e"><div class="v">${a.deals?fFull(rpd):'—'}</div><div class="l">Revenue / Deal</div></div></div>
        <div class="rep-h">Monthly Breakdown</div>
        <table class="rep-tbl rep-weekly"><thead><tr><th>Week</th><th class="n">Calls</th><th class="n">Meetings</th><th class="n">Deals</th><th class="n">Revenue</th></tr></thead><tbody>${weeks.map(x=>`<tr><td>${x.w.label}<br><span style="font-size:9px;color:#98a2b3">${fdate(x.w.start)}–${fdate(x.w.end)}</span></td><td class="n">${num(x.calls)}</td><td class="n">${num(x.mtg)}</td><td class="n">${x.deals}</td><td class="n rev">${x.rev?num(x.rev):'—'}</td></tr>`).join('')}</tbody></table>
        <div class="rep-foot">Team Rashwan Command Dashboard · Provident Real Estate · ${esc(opt.label)} · Confidential — Internal Use Only</div>
      </section>`;
    }).join('');
    openMonthlyOverlay(summary+agentSections,opt.label);
  }

  function updateReportButton(){
    const mainBtn=document.getElementById('rep-btn');if(!mainBtn)return;
    if(typeof state!=='undefined'&&state.period==='month'){
      const opt=selectedMonthOpt();mainBtn.textContent='▣ Generate '+(opt?opt.label:'Monthly')+' Report';
    }else mainBtn.textContent='▣ Generate Report';
  }
'''

js_anchor = '\n  function generate(period){\n    const opt=latestOpt(period);'
if js_anchor not in text:
    raise RuntimeError('Could not find report generate() anchor')
text = text.replace(js_anchor, monthly_js + '\n  function generate(period){\n    if(period===\'month\')return generateMonthlyAllAgent();\n    const opt=latestOpt(period);', 1)

old_button = r'''  const btn=document.getElementById('rep-btn'),menu=document.getElementById('rep-menu');
  if(btn){
    btn.onclick=e=>{e.stopPropagation();menu.classList.toggle('hidden');};
    menu.querySelectorAll('button').forEach(b=>b.onclick=e=>{e.stopPropagation();menu.classList.add('hidden');generate(b.dataset.rp);});
    document.addEventListener('click',()=>menu.classList.add('hidden'));
  }'''
new_button = r'''  const btn=document.getElementById('rep-btn'),menu=document.getElementById('rep-menu');
  if(btn){
    updateReportButton();
    btn.onclick=e=>{
      e.stopPropagation();
      if(typeof state!=='undefined'&&state.period==='month'){menu.classList.add('hidden');generate('month');return;}
      menu.classList.toggle('hidden');
    };
    menu.querySelectorAll('button').forEach(b=>b.onclick=e=>{e.stopPropagation();menu.classList.add('hidden');generate(b.dataset.rp);});
    document.addEventListener('click',()=>menu.classList.add('hidden'));
    document.addEventListener('change',e=>{if(e.target&&e.target.id==='period-pick')setTimeout(updateReportButton,0);});
    document.addEventListener('click',e=>{if(e.target&&e.target.closest&&e.target.closest('.seg button'))setTimeout(updateReportButton,0);});
  }'''
if old_button not in text:
    raise RuntimeError('Could not find report button behavior anchor')
text = text.replace(old_button, new_button, 1)

path.write_text(text, encoding='utf-8')
print('Applied monthly all-agent report to index.html')
