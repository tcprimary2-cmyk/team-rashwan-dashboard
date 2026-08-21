from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marker = '/* MULTI-PERIOD + INDIVIDUAL REPORT V2 */'
if marker in s:
    raise SystemExit('Patch already applied')

insert_at = "\n  function updateReportButton(){"
if insert_at not in s:
    raise SystemExit('updateReportButton anchor not found')

new_code = r'''
  /* MULTI-PERIOD + INDIVIDUAL REPORT V2 */
  function selectedPeriodOpt(period){
    const opts=buildPeriods(period);if(!opts||!opts.length)return null;
    const picker=document.getElementById('period-pick');
    const key=(typeof state!=='undefined'&&state.period===period&&state.periodKey)?state.periodKey:(picker?picker.value:null);
    return opts.find(o=>o.key===key)||opts[opts.length-1];
  }
  function reportDateLabel(d){
    return new Date(d+'T00:00:00Z').toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});
  }
  function periodBreakdownRanges(period,range){
    const out=[];
    const add=(label,start,end)=>out.push({label,start,end});
    if(period==='week'){
      let d=new Date(range.start+'T00:00:00Z'),end=new Date(range.end+'T00:00:00Z');
      while(d<=end){const x=d.toISOString().slice(0,10);add(d.toLocaleDateString('en-GB',{weekday:'short',day:'numeric',month:'short'}),x,x);d.setUTCDate(d.getUTCDate()+1);}
      return out;
    }
    if(period==='month')return monthWeekRanges(range).map((r,i)=>({label:'Week '+(i+1),start:r.start,end:r.end}));
    let d=new Date(range.start+'T00:00:00Z'),end=new Date(range.end+'T00:00:00Z');
    d=new Date(Date.UTC(d.getUTCFullYear(),d.getUTCMonth(),1));
    while(d<=end){
      const ms=d.toISOString().slice(0,10);
      const next=new Date(Date.UTC(d.getUTCFullYear(),d.getUTCMonth()+1,1));
      const meDate=new Date(next.getTime()-86400000);
      const start=ms<range.start?range.start:ms;
      const rawEnd=meDate.toISOString().slice(0,10),finish=rawEnd>range.end?range.end:rawEnd;
      add(d.toLocaleDateString('en-GB',{month:'short',year:'numeric'}),start,finish);
      d=next;
    }
    return out;
  }
  function openPerformanceOverlay(body,period,optLabel,individualName){
    let ov=document.getElementById('rep-overlay');
    if(!ov){ov=document.createElement('div');ov.id='rep-overlay';document.body.appendChild(ov);ov.onclick=e=>{if(e.target===ov)ov.classList.remove('show');};}
    const pLabel=period.charAt(0).toUpperCase()+period.slice(1);
    const scope=individualName?individualName:'All Active Agents';
    ov.innerHTML=`<div class="rep-paper"><div class="rep-bar"><div class="t">${esc(pLabel)} Report · ${esc(optLabel)} · ${esc(scope)}</div><div class="btns"><button class="rep-print" onclick="window.print()">🖨 Print / Save as PDF</button><button class="rep-close" onclick="document.getElementById('rep-overlay').classList.remove('show')">✕ Close</button></div></div><div class="rep-body">${body}</div></div>`;
    ov.classList.add('show');ov.scrollTop=0;
  }
  function generatePerformanceReport(period,individualOnly){
    const opt=selectedPeriodOpt(period);if(!opt)return;
    const range=rangeOf(period,opt.key),isIndividual=!!individualOnly;
    let agents=isIndividual?[state.agent]:activeAgents(range);
    agents=agents.filter(Boolean);
    if(!agents.length){alert('No agent data is available for the selected period.');return;}
    const rows=agents.map(name=>({name,...aggregate(range,name),activeLeads:latestLeads(name,range)}))
      .sort((a,b)=>b.rev-a.rev||b.deals-a.deals||b.mtg-a.mtg||b.calls-a.calls||a.name.localeCompare(b.name));
    const allRows=activeAgents(range).map(name=>({name,...aggregate(range,name)}));
    const team=aggregate(range),teamFactor=teamTargetFactor(period,range);
    const tCalls=Math.round(T.callsPerMonth*teamFactor),tMtg=Math.round(T.meetingsPerMonth*teamFactor),tRev=Math.round(T.revenuePerMonth*teamFactor);
    const dealsList=DEALS.filter(d=>inRange(d.date,range)&&(isIndividual?d.name===state.agent:true)).sort((a,b)=>a.date<b.date?1:-1);
    const generated=new Date().toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});
    const ach=(actual,target)=>`<span class="rep-ach ${achievementClass(achievement(actual,target))}">${achievement(actual,target)}%</span>`;
    const periodName=period.charAt(0).toUpperCase()+period.slice(1);
    const dateRange=reportDateLabel(range.start)+' – '+reportDateLabel(range.end);
    const breakdown=periodBreakdownRanges(period,range);
    let summary='';
    if(!isIndividual){
      summary=`<section class="rep-monthly-summary">
        <div class="rep-section-kicker">TEAM RASHWAN · ${esc(periodName.toUpperCase())} PERFORMANCE REPORT</div>
        <h1>${esc(opt.label)}</h1><div class="rep-sub">${esc(dateRange)} · Generated ${esc(generated)} · ${rows.length} active agents</div>
        <div class="rep-kpi-grid">
          <div class="rep-kpi"><div class="k">Calls</div><div class="v">${fNum(team.calls)}</div><div class="s">Target ${fNum(tCalls)} ${ach(team.calls,tCalls)}</div></div>
          <div class="rep-kpi"><div class="k">Meetings</div><div class="v">${fNum(team.mtg)}</div><div class="s">Target ${fNum(tMtg)} ${ach(team.mtg,tMtg)}</div></div>
          <div class="rep-kpi"><div class="k">Deals</div><div class="v">${fNum(team.deals)}</div><div class="s">Closed in selected ${esc(periodName.toLowerCase())}</div></div>
          <div class="rep-kpi"><div class="k">Revenue</div><div class="v">${fAED(team.rev)}</div><div class="s">Target ${fAED(tRev)} ${ach(team.rev,tRev)}</div></div>
        </div>
        <div class="rep-two-col">
          <div class="rep-card"><h3>Leaderboard</h3><table><thead><tr><th>#</th><th>Agent</th><th>Calls</th><th>Meetings</th><th>Deals</th><th>Revenue</th></tr></thead><tbody>${rows.map((r,i)=>`<tr><td>${i+1}</td><td><b>${esc(r.name)}</b></td><td>${fNum(r.calls)}</td><td>${fNum(r.mtg)}</td><td>${fNum(r.deals)}</td><td>${fAED(r.rev)}</td></tr>`).join('')}</tbody></table></div>
          <div class="rep-card"><h3>Deals Closed</h3>${dealsList.length?`<table><thead><tr><th>Date</th><th>Agent</th><th>Revenue</th></tr></thead><tbody>${dealsList.map(d=>`<tr><td>${reportDateLabel(d.date)}</td><td>${esc(d.name||'—')}</td><td>${d.aed?fAED(d.aed):'Pending'}</td></tr>`).join('')}</tbody></table>`:'<div class="rep-empty">No closed deals in this period.</div>'}</div>
        </div>
      </section>`;
    }
    const agentSections=rows.map(r=>{
      const factor=targetFactor(r.name,period,range),callsTarget=Math.round(T.callsPerMonth*factor),mtgTarget=Math.round(T.meetingsPerMonth*factor),revTarget=Math.round(T.revenuePerMonth*factor);
      const meta=(typeof AGENT_META!=='undefined'&&AGENT_META[r.name])||{};
      const callsToMtg=r.calls?r.mtg/r.calls*100:0,mtgToDeals=r.mtg?r.deals/r.mtg*100:0,callsToDeals=r.calls?r.deals/r.calls*100:0,revPerDeal=r.deals?r.rev/r.deals:0;
      const breakdownRows=breakdown.map(b=>{const a=aggregate({start:b.start,end:b.end},r.name);return `<tr><td><b>${esc(b.label)}</b><div class="rep-mini-date">${esc(reportDateLabel(b.start))}${b.end!==b.start?' – '+esc(reportDateLabel(b.end)):''}</div></td><td>${fNum(a.calls)}</td><td>${fNum(a.mtg)}</td><td>${fNum(a.deals)}</td><td>${fAED(a.rev)}</td></tr>`;}).join('');
      return `<section class="rep-monthly-agent">
        <div class="rep-agent-head">${agentPhotoHTML(r.name)}<div><div class="rep-section-kicker">${isIndividual?'INDIVIDUAL':'AGENT'} PERFORMANCE REPORT</div><h2>${esc(r.name)}</h2><div class="rep-sub">${esc(meta.role||'Sales Agent')} · ${esc(opt.label)} · ${esc(dateRange)}</div></div></div>
        <div class="rep-kpi-grid">
          <div class="rep-kpi"><div class="k">Calls</div><div class="v">${fNum(r.calls)}</div><div class="s">Target ${fNum(callsTarget)} ${ach(r.calls,callsTarget)}</div></div>
          <div class="rep-kpi"><div class="k">Meetings</div><div class="v">${fNum(r.mtg)}</div><div class="s">Target ${fNum(mtgTarget)} ${ach(r.mtg,mtgTarget)}</div></div>
          <div class="rep-kpi"><div class="k">Deals</div><div class="v">${fNum(r.deals)}</div><div class="s">Closed</div></div>
          <div class="rep-kpi"><div class="k">Revenue</div><div class="v">${fAED(r.rev)}</div><div class="s">Target ${fAED(revTarget)} ${ach(r.rev,revTarget)}</div></div>
          <div class="rep-kpi"><div class="k">Active Leads</div><div class="v">${fNum(r.activeLeads||0)}</div><div class="s">Latest available in period</div></div>
        </div>
        <div class="rep-two-col">
          <div class="rep-card"><h3>Conversion & Efficiency</h3><div class="rep-metric-grid"><div><span>Calls → Meetings</span><b>${fPct(callsToMtg)}</b></div><div><span>Meetings → Deals</span><b>${fPct(mtgToDeals)}</b></div><div><span>Calls → Deals</span><b>${fPct(callsToDeals)}</b></div><div><span>Revenue / Deal</span><b>${r.deals?fAED(revPerDeal):'—'}</b></div></div></div>
          <div class="rep-card"><h3>Team Rankings</h3><div class="rep-metric-grid"><div><span>Revenue</span><b>#${rankFor(allRows,r.name,'rev')}</b></div><div><span>Deals</span><b>#${rankFor(allRows,r.name,'deals')}</b></div><div><span>Calls</span><b>#${rankFor(allRows,r.name,'calls')}</b></div><div><span>Meetings</span><b>#${rankFor(allRows,r.name,'mtg')}</b></div></div></div>
        </div>
        <div class="rep-card"><h3>${period==='week'?'Daily':period==='month'?'Weekly':'Monthly'} Breakdown</h3><table><thead><tr><th>Period</th><th>Calls</th><th>Meetings</th><th>Deals</th><th>Revenue</th></tr></thead><tbody>${breakdownRows}</tbody></table></div>
      </section>`;
    }).join('');
    openPerformanceOverlay(summary+agentSections,period,opt.label,isIndividual?state.agent:null);
  }
'''

s = s.replace(insert_at, '\n'+new_code+insert_at, 1)

old_update = '''  function updateReportButton(){
    const mainBtn=document.getElementById('rep-btn');if(!mainBtn)return;
    if(typeof state!=='undefined'&&state.period==='month'){
      const opt=selectedMonthOpt();mainBtn.textContent='▣ Generate '+(opt?opt.label:'Monthly')+' Report';
    }else mainBtn.textContent='▣ Generate Report';
  }'''
new_update = '''  function updateReportButton(){
    const mainBtn=document.getElementById('rep-btn');if(!mainBtn)return;
    mainBtn.style.display='inline-flex';
    if(typeof state==='undefined'){mainBtn.textContent='▣ Generate Report';return;}
    const supported=['week','month','quarter','year'];
    if(state.view==='individual'&&supported.includes(state.period)){
      const opt=selectedPeriodOpt(state.period);
      mainBtn.textContent='▣ Generate '+(state.agent||'Agent')+' Report';
      mainBtn.title=opt?'Generate '+opt.label+' individual performance report':'Generate individual performance report';
    }else if(state.view==='team'&&supported.includes(state.period)){
      const opt=selectedPeriodOpt(state.period);
      mainBtn.textContent='▣ Generate '+(opt?opt.label:(state.period.charAt(0).toUpperCase()+state.period.slice(1)))+' Report';
      mainBtn.title='Generate complete '+state.period+' performance report';
    }else{
      mainBtn.textContent='▣ Generate Report';mainBtn.title='Generate report';
    }
  }'''
if old_update not in s:
    raise SystemExit('updateReportButton exact block not found')
s = s.replace(old_update,new_update,1)

old_click = '''    btn.onclick=e=>{
      e.stopPropagation();
      if(typeof state!=='undefined'&&state.period==='month'){menu.classList.add('hidden');generate('month');return;}
      menu.classList.toggle('hidden');
    };'''
new_click = '''    btn.onclick=e=>{
      e.stopPropagation();
      if(typeof state!=='undefined'){
        const supported=['week','month','quarter','year'];
        if(state.view==='individual'&&supported.includes(state.period)){menu.classList.add('hidden');generatePerformanceReport(state.period,true);return;}
        if(state.view==='team'&&supported.includes(state.period)){menu.classList.add('hidden');generatePerformanceReport(state.period,false);return;}
      }
      menu.classList.toggle('hidden');
    };'''
if old_click not in s:
    raise SystemExit('report button click block not found')
s = s.replace(old_click,new_click,1)

view_anchor = '''function setView(v){
  state.view=v;
  document.querySelectorAll('#view-seg button').forEach(b=>b.classList.toggle('on',b.dataset.view===v));
  refreshAgentPicker();
  render();
}'''
view_new = '''function setView(v){
  state.view=v;
  document.querySelectorAll('#view-seg button').forEach(b=>b.classList.toggle('on',b.dataset.view===v));
  refreshAgentPicker();
  render();
  if(typeof updateReportButton==='function')updateReportButton();
}'''
if view_anchor not in s:
    raise SystemExit('setView block not found')
s=s.replace(view_anchor,view_new,1)

handlers_old = '''document.getElementById('period-seg').onclick=e=>{const b=e.target.closest('button');if(!b)return;
  state.period=b.dataset.p;document.querySelectorAll('#period-seg button').forEach(x=>x.classList.toggle('on',x.dataset.p===state.period));
  refreshPeriodPicker();render();};
document.getElementById('period-pick').onchange=e=>{state.periodKey=e.target.value;render();};
document.getElementById('agent-pick').onchange=e=>{state.agent=e.target.value;render();};'''
handlers_new = '''document.getElementById('period-seg').onclick=e=>{const b=e.target.closest('button');if(!b)return;
  state.period=b.dataset.p;document.querySelectorAll('#period-seg button').forEach(x=>x.classList.toggle('on',x.dataset.p===state.period));
  refreshPeriodPicker();render();if(typeof updateReportButton==='function')updateReportButton();};
document.getElementById('period-pick').onchange=e=>{state.periodKey=e.target.value;render();if(typeof updateReportButton==='function')updateReportButton();};
document.getElementById('agent-pick').onchange=e=>{state.agent=e.target.value;render();if(typeof updateReportButton==='function')updateReportButton();};'''
if handlers_old not in s:
    raise SystemExit('period/agent handler block not found')
s=s.replace(handlers_old,handlers_new,1)

p.write_text(s,encoding='utf-8')
print('patched', len(s))
