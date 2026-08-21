from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* REPORT STYLE COMPATIBILITY FIX V3 */'
if marker in s:
    raise SystemExit('style fix already present')
anchor='  /* MONTHLY ALL-AGENT REPORT V1 */'
if anchor not in s:
    raise SystemExit('monthly report css anchor not found')
css=r'''  /* REPORT STYLE COMPATIBILITY FIX V3 */
  .rep-section-kicker{font-size:9.5px;letter-spacing:1.15px;text-transform:uppercase;color:#123a5e;font-weight:700;margin-bottom:5px}
  .rep-monthly-summary h1{font-size:23px;line-height:1.15;margin:0 0 5px;color:#101828;font-weight:700}
  .rep-agent-head h2{font-size:21px;line-height:1.1;margin:0;color:#101828;font-weight:700}
  .rep-kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:14px 0 16px}
  .rep-monthly-agent .rep-kpi-grid{grid-template-columns:repeat(5,minmax(0,1fr))}
  .rep-kpi{border:1px solid #e4e7ec;border-radius:12px;padding:13px 14px;background:#fff;min-width:0}
  .rep-kpi .k{font-size:9.5px;letter-spacing:1px;text-transform:uppercase;color:#667085;font-weight:600}
  .rep-kpi .v{font-size:21px;font-weight:700;color:#101828;margin-top:6px;line-height:1.05;white-space:nowrap}
  .rep-kpi .s{font-size:10.5px;margin-top:6px;color:#98a2b3;line-height:1.4}
  .rep-two-col{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,.9fr);gap:14px;margin:14px 0}
  .rep-card{border:1px solid #e4e7ec;border-radius:12px;padding:14px;background:#fff;min-width:0;overflow:hidden}
  .rep-card h3{font-size:12px;margin:0 0 10px;color:#101828;font-weight:700;letter-spacing:.15px}
  .rep-card table{width:100%;border-collapse:collapse;font-size:10px}
  .rep-card th{font-size:8.5px;text-transform:uppercase;letter-spacing:.55px;color:#667085;font-weight:700;text-align:left;background:#f8fafc;padding:7px 6px;border-bottom:1px solid #e4e7ec;white-space:nowrap}
  .rep-card td{padding:7px 6px;border-bottom:1px solid #eef0f3;color:#344054;vertical-align:top}
  .rep-card tbody tr:last-child td{border-bottom:0}
  .rep-card th:not(:first-child),.rep-card td:not(:first-child){text-align:right}
  .rep-card th:nth-child(2),.rep-card td:nth-child(2){text-align:left}
  .rep-metric-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
  .rep-metric-grid>div{border:1px solid #eef0f3;background:#fafbfc;border-radius:9px;padding:9px 10px;display:flex;align-items:center;justify-content:space-between;gap:10px}
  .rep-metric-grid span{font-size:9px;color:#667085}
  .rep-metric-grid b{font-size:12px;color:#123a5e;white-space:nowrap}
  .rep-mini-date{font-size:8px;color:#98a2b3;margin-top:2px;font-weight:400}
  .rep-empty{font-size:10px;color:#98a2b3;padding:12px 4px}
  @media(max-width:700px){
    .rep-kpi-grid,.rep-monthly-agent .rep-kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
    .rep-two-col{grid-template-columns:1fr}
    .rep-card{overflow-x:auto}
  }
  @media print{
    .rep-kpi-grid{grid-template-columns:repeat(4,minmax(0,1fr))}
    .rep-monthly-agent .rep-kpi-grid{grid-template-columns:repeat(5,minmax(0,1fr))}
    .rep-two-col,.rep-card,.rep-kpi-grid,.rep-metric-grid{break-inside:avoid;page-break-inside:avoid}
  }

'''
s=s.replace(anchor,css+anchor,1)
p.write_text(s,encoding='utf-8')
print('report style compatibility CSS added')
