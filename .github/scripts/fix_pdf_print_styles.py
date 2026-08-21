from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* PDF PRINT MATCH SCREEN V1 */'
if marker in s:
    raise SystemExit('already applied')
css=r'''
/* PDF PRINT MATCH SCREEN V1 */
@media print{
  @page{size:A4;margin:10mm}
  html,body{background:#fff!important;-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}
  body>*:not(#rep-overlay){display:none!important}
  #rep-overlay{display:block!important;position:static!important;inset:auto!important;background:#fff!important;padding:0!important;overflow:visible!important}
  #rep-overlay.show{display:block!important}
  .rep-paper{width:100%!important;max-width:none!important;margin:0!important;border-radius:0!important;box-shadow:none!important;background:#fff!important;overflow:visible!important}
  .rep-bar{display:none!important}
  .rep-body{padding:0!important;background:#fff!important}
  .rep-hh{display:flex!important;align-items:flex-start!important;justify-content:space-between!important;border-bottom:3px solid #123a5e!important;padding:0 0 16px!important;margin-bottom:20px!important}
  .rep-brand .p{font-size:22px!important;font-weight:700!important;letter-spacing:2px!important;color:#123a5e!important}
  .rep-brand .s{font-size:9px!important;font-weight:600!important;letter-spacing:4px!important;color:#c6952a!important;margin-top:4px!important}
  .rep-meta{text-align:right!important;font-size:10px!important;color:#667085!important;line-height:1.55!important}
  .rep-title{font-size:26px!important;font-weight:700!important;letter-spacing:-.4px!important;color:#101828!important;margin:0 0 4px!important}
  .rep-sub{font-size:11px!important;color:#667085!important;margin-bottom:18px!important}
  .rep-kgrid{display:grid!important;grid-template-columns:repeat(4,1fr)!important;gap:10px!important;margin:14px 0 18px!important}
  .rep-k{display:block!important;border:1px solid #e4e7ec!important;border-radius:12px!important;padding:12px 13px!important;background:#fff!important;break-inside:avoid!important;page-break-inside:avoid!important}
  .rep-k .l{font-size:8.5px!important;letter-spacing:1px!important;text-transform:uppercase!important;color:#667085!important;font-weight:700!important}
  .rep-k .v{font-size:20px!important;font-weight:700!important;color:#101828!important;margin-top:6px!important;line-height:1.05!important}
  .rep-k .d{font-size:9.5px!important;color:#98a2b3!important;margin-top:6px!important;line-height:1.35!important}
  .rep-h{font-size:13px!important;font-weight:700!important;color:#123a5e!important;margin:18px 0 8px!important}
  .rep-tbl{width:100%!important;border-collapse:collapse!important;font-size:10px!important;table-layout:auto!important}
  .rep-tbl th{font-size:8px!important;letter-spacing:.8px!important;text-transform:uppercase!important;color:#667085!important;font-weight:700!important;text-align:left!important;padding:7px 8px!important;border-bottom:1px solid #d0d5dd!important;background:#f8fafc!important}
  .rep-tbl td{padding:7px 8px!important;border-bottom:1px solid #eaecf0!important;color:#344054!important;vertical-align:top!important}
  .rep-tbl .n{text-align:right!important;font-variant-numeric:tabular-nums!important}
  .rep-tbl .rev{color:#b5842a!important;font-weight:700!important}
  .rep-monthly-agent{break-before:page!important;page-break-before:always!important;break-inside:avoid!important;page-break-inside:avoid!important}
  .rep-agent-head,.rep-target-grid,.rep-eff,.rep-tbl{break-inside:avoid!important;page-break-inside:avoid!important}
  .rep-foot{font-size:8px!important;color:#98a2b3!important;margin-top:16px!important;border-top:1px solid #eaecf0!important;padding-top:8px!important}
}
'''
idx=s.rfind('</style>')
if idx==-1:
    raise SystemExit('style close not found')
s=s[:idx]+css+s[idx:]
p.write_text(s,encoding='utf-8')
print('pdf print stylesheet injected')
