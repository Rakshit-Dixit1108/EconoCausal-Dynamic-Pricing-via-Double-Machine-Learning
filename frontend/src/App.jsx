import React, { useMemo, useState } from 'react'
import Plot from 'react-plotly.js'
import { Activity, ArrowDownRight, ArrowUpRight, BarChart3, BrainCircuit, CheckCircle2, ChevronDown, CircleHelp, Download, FileSpreadsheet, Gauge, LayoutDashboard, LoaderCircle, Menu, MousePointer2, Settings2, ShieldCheck, Sparkles, Target, UploadCloud, Users, Wallet, X } from 'lucide-react'
import { analyzeCsv, optimizeDiscounts, checkHealth } from './api'
import { demoMetrics, discountCurve, effectDistribution, initialRecommendations, strategies } from './demoData'

const money = n => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n)
const pct = n => `${Number(n).toFixed(1)}%`
const plotLayout = {
  paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
  font: { color: '#a7b1c7', family: 'Inter, ui-sans-serif, system-ui', size: 11 },
  margin: { l: 42, r: 12, t: 10, b: 38 },
  xaxis: { gridcolor: '#202a40', zerolinecolor: '#202a40', linecolor: '#27324a' },
  yaxis: { gridcolor: '#202a40', zerolinecolor: '#202a40', linecolor: '#27324a' },
  showlegend: false, autosize: true
}
const config = { displayModeBar: false, responsive: true }

function App() {
  const [file, setFile] = useState(null)
  const [csvRows, setCsvRows] = useState([])
  const [headers, setHeaders] = useState([])
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const [apiStatus, setApiStatus] = useState('Demo mode')
  const [metrics, setMetrics] = useState(demoMetrics)
  const [curve, setCurve] = useState(discountCurve)
  const [distribution, setDistribution] = useState(effectDistribution)
  const [recommendations, setRecommendations] = useState(initialRecommendations)
  const [budget, setBudget] = useState(7500)
  const [maxDiscount, setMaxDiscount] = useState(15)
  const [objective, setObjective] = useState('revenue')
  const [activeNav, setActiveNav] = useState('Overview')
  const [mobileNav, setMobileNav] = useState(false)
  const [optimizing, setOptimizing] = useState(false)
  const [diagnostics, setDiagnostics] = useState({ method: 'Double Machine Learning', status: 'Demo data', score: '—' })

  const totalRecommended = useMemo(() => recommendations.reduce((s, r) => s + Number(r.revenue || 0), 0), [recommendations])

  function parseCsv(text) {
    const lines = text.trim().split(/\r?\n/).filter(Boolean)
    if (!lines.length) return { headers: [], rows: [] }
    const split = line => line.split(',').map(v => v.trim().replace(/^"|"$/g, ''))
    return { headers: split(lines[0]), rows: lines.slice(1, 6).map(split) }
  }
  async function handleFile(e) {
    const chosen = e.target.files?.[0]
    if (!chosen) return
    if (!chosen.name.toLowerCase().endsWith('.csv')) { setNotice('Please upload a .csv file.'); return }
    setFile(chosen); setNotice('')
    const text = await chosen.text()
    const parsed = parseCsv(text)
    setHeaders(parsed.headers); setCsvRows(parsed.rows)
    setApiStatus('CSV loaded · not yet analyzed')
  }
  async function runAnalysis() {
    if (!file) { setNotice('Upload a customer CSV first.'); return }
    setBusy(true); setNotice('')
    try {
      const data = await analyzeCsv(file)
      if (data.metrics) setMetrics(data.metrics)
      if (data.discountCurve) setCurve(data.discountCurve)
      if (data.effectDistribution) setDistribution(data.effectDistribution)
      if (data.beneficiaries) setRecommendations(data.beneficiaries.map(r => ({
        id: r.customerId ?? r.id, segment: r.segment ?? 'Customer', uplift: Number(r.uplift ?? 0) * (Number(r.uplift) <= 1 ? 100 : 1),
        discount: Number(r.recommendedDiscount ?? r.discount ?? 0) * (Number(r.recommendedDiscount ?? r.discount) <= 1 ? 100 : 1),
        revenue: Number(r.expectedIncrementalRevenue ?? r.revenue ?? 0)
      })))
      setDiagnostics(data.diagnostics || { method: 'Double Machine Learning', status: 'Analysis complete', score: 'Available in backend' })
      setApiStatus('Connected · real API response')
      setNotice('Analysis completed using the connected backend.')
    } catch (err) {
      setApiStatus('Demo mode')
      setNotice(`Backend unavailable (${err.response?.data?.detail || err.message}). CSV preview loaded; dashboard still shows demo values, not model estimates. Start your backend and try again.`)
    } finally { setBusy(false) }
  }
  async function runOptimization() {
    setOptimizing(true); setNotice('')
    try {
      const data = await optimizeDiscounts({ budget, max_discount: maxDiscount / 100, objective })
      if (data.recommendations) setRecommendations(data.recommendations.map(r => ({
        id: r.customerId ?? r.id, segment: r.segment ?? 'Customer',
        uplift: Number(r.uplift ?? 0) * (Number(r.uplift) <= 1 ? 100 : 1),
        discount: Number(r.recommendedDiscount ?? r.discount ?? 0) * (Number(r.recommendedDiscount ?? r.discount) <= 1 ? 100 : 1),
        revenue: Number(r.expectedIncrementalRevenue ?? r.revenue ?? 0)
      })))
      setNotice('Optimization results received from backend.')
      setApiStatus('Connected · real API response')
    } catch (err) {
      const factor = Math.max(.35, Math.min(1.3, budget / 7500)) * (maxDiscount / 15)
      setRecommendations(initialRecommendations.map((r, i) => ({ ...r, discount: Math.min(r.discount, maxDiscount), uplift: +(r.uplift * (0.9 + factor * 0.1)).toFixed(1), revenue: Math.round(r.revenue * factor * (objective === 'conversion' ? 0.8 : 1)) })).filter(r => r.discount <= maxDiscount).slice(0, Math.max(2, Math.round(budget / 1200))))
      setNotice('Backend optimization endpoint unavailable. Showing illustrative recommendations adjusted to your settings—not causal model output.')
    } finally { setOptimizing(false) }
  }
  async function pingApi() {
    try { const data = await checkHealth(); setApiStatus(`API online${data.status ? ` · ${data.status}` : ''}`) }
    catch { setApiStatus('Demo mode · API offline') }
  }
  function exportCsv() {
    const rows = [['Customer ID','Segment','Estimated uplift (%)','Recommended discount (%)','Expected incremental revenue'], ...recommendations.map(r => [r.id,r.segment,r.uplift,r.discount,r.revenue])]
    const blob = new Blob([rows.map(r => r.map(v => `"${String(v ?? '').replaceAll('"','""')}"`).join(',')).join('\n')], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'econocausal-recommendations.csv'; a.click(); URL.revokeObjectURL(url)
  }

  const navItems = [
    { name: 'Overview', icon: LayoutDashboard },
    { name: 'Causal analysis', icon: BrainCircuit },
    { name: 'Optimization', icon: Target },
    { name: 'Recommendations', icon: BarChart3 }
  ]
  const kpis = [
    { title: 'Customers analyzed', value: Number(metrics.customers ?? 0).toLocaleString('en-IN'), change: 'Dataset coverage', icon: Users, tone: 'blue' },
    { title: 'Purchase rate', value: pct(metrics.purchaseRate ?? 0), change: 'Observed conversion', icon: Activity, tone: 'purple' },
    { title: 'Average discount', value: pct(metrics.averageDiscount ?? 0), change: 'Across customers', icon: Wallet, tone: 'orange' },
    { title: 'Revenue improvement', value: `+${pct(metrics.revenueImprovement ?? 0)}`, change: 'Estimated vs baseline', icon: ArrowUpRight, tone: 'green' }
  ]

  return <div className="app-shell">
    <aside className={`sidebar ${mobileNav ? 'sidebar-open' : ''}`}>
      <div className="brand"><div className="brand-mark"><Sparkles size={20}/></div><div><div className="brand-name">Econo<span>Causal</span></div><div className="brand-caption">PRICING INTELLIGENCE</div></div><button className="mobile-close" onClick={() => setMobileNav(false)}><X size={18}/></button></div>
      <div className="workspace-label">WORKSPACE</div>
      <div className="workspace"><div className="workspace-icon">EC</div><div className="workspace-text"><b>Growth Analytics</b><small>Research workspace</small></div><ChevronDown size={15}/></div>
      <div className="nav-label">ANALYTICS</div>
      <nav>{navItems.map(({ name, icon: Icon }) => <button key={name} className={`nav-item ${activeNav === name ? 'active' : ''}`} onClick={() => { setActiveNav(name); setMobileNav(false); document.getElementById(name.toLowerCase().replace(' ', '-'))?.scrollIntoView({ behavior: 'smooth', block: 'start' }) }}><Icon size={18}/><span>{name}</span>{name === 'Recommendations' && <span className="nav-count">{recommendations.length}</span>}</button>)}</nav>
      <div className="sidebar-bottom"><div className="help-card"><div className="help-icon"><CircleHelp size={18}/></div><b>Need a hand?</b><p>Explore the workflow and model assumptions.</p><button onClick={() => setNotice('Workflow: upload CSV → validate columns → run backend DML analysis → optimize under budget → export recommendations.')}>View workflow <span>↗</span></button></div><div className="profile"><div className="avatar">EC</div><div><b>Project team</b><small>Free workspace</small></div><Settings2 size={17}/></div></div>
    </aside>
    {mobileNav && <div className="mobile-overlay" onClick={() => setMobileNav(false)} />}
    <main className="main-area">
      <header className="topbar"><div className="topbar-left"><button className="menu-btn" onClick={() => setMobileNav(true)}><Menu size={20}/></button><span className="breadcrumb">Workspace <span>/</span> <b>{activeNav}</b></span></div><div className="topbar-right"><div className={`api-pill ${apiStatus.startsWith('Connected') || apiStatus.startsWith('API online') ? 'online' : ''}`}><span className="status-dot"/>{apiStatus}</div><button className="icon-btn" title="Check backend connection" onClick={pingApi}><Activity size={17}/></button><div className="top-avatar">RK</div></div></header>
      <div className="page-content">
        <section className="page-heading"><div><div className="eyebrow"><span className="eyebrow-dot"/> CAUSAL MACHINE LEARNING <span className="version-tag">BETA</span></div><h1>Pricing overview</h1><p>Understand what discounts actually drive incremental purchases.</p></div><div className="heading-actions"><button className="btn btn-secondary" onClick={exportCsv}><Download size={16}/> Export report</button><button className="btn btn-primary" onClick={() => document.getElementById('csv-input').click()}><UploadCloud size={16}/> Upload dataset</button></div></section>

        {notice && <div className={`notice ${notice.toLowerCase().includes('unavailable') ? 'notice-warn' : ''}`}><span>{notice}</span><button onClick={() => setNotice('')}><X size={15}/></button></div>}
        <section className="upload-strip"><div className="upload-symbol"><FileSpreadsheet size={21}/></div><div className="upload-copy"><b>{file ? file.name : 'Start with your customer data'}</b><span>{file ? `${(file.size / 1024).toFixed(1)} KB · ${headers.length} columns detected · ${csvRows.length ? 'preview ready' : 'empty CSV'}` : 'Upload a CSV to validate your data and run causal analysis.'}</span></div><input id="csv-input" type="file" accept=".csv,text/csv" onChange={handleFile} hidden/><button className="btn btn-secondary upload-btn" onClick={() => document.getElementById('csv-input').click()}>{file ? 'Change file' : 'Choose CSV'}</button><button className="btn btn-primary" disabled={!file || busy} onClick={runAnalysis}>{busy ? <LoaderCircle size={16} className="spin"/> : <Sparkles size={16}/>} {busy ? 'Analyzing…' : 'Analyze dataset'}</button></section>
        {file && headers.length > 0 && <section className="panel csv-preview"><div className="panel-heading"><div><h3>CSV data preview</h3><p>First five records · header-based preview only</p></div><span className="soft-badge"><CheckCircle2 size={13}/> {headers.length} columns</span></div><div className="table-wrap"><table><thead><tr>{headers.map((h,i)=><th key={i}>{h}</th>)}</tr></thead><tbody>{csvRows.map((row,i)=><tr key={i}>{headers.map((_,j)=><td key={j}>{row[j] ?? '—'}</td>)}</tr>)}</tbody></table></div><p className="table-footnote">This lightweight preview does not replace backend schema and data-quality validation.</p></section>}

        <section className="kpi-grid" id="overview">{kpis.map(({ title, value, change, icon: Icon, tone }, i) => <article className="kpi-card" key={title}><div className="kpi-top"><span>{title}</span><div className={`kpi-icon ${tone}`}><Icon size={18}/></div></div><div className="kpi-value">{value}</div><div className="kpi-foot"><span className={`kpi-indicator ${i===3?'positive':''}`}>{i===3?<ArrowUpRight size={14}/>:<span className="mini-dot"/>}{change}</span><span className="info-mark" title="Values are illustrative until the backend returns real analysis.">i</span></div></article>)}</section>

        <section className="chart-grid" id="causal-analysis">
          <article className="panel chart-panel"><div className="panel-heading"><div><h3>Discount vs. purchase rate</h3><p>Observed purchase rate across discount levels</p></div><span className="chart-legend"><i className="legend-line"/> Purchase rate</span></div><div className="chart-area"><Plot data={[{ x: curve.map(d=>d.discount), y: curve.map(d=>d.purchaseRate), type: 'scatter', mode: 'lines+markers', line: { color: '#8b7bff', width: 3, shape: 'spline' }, marker: { color: '#b1a7ff', size: 7, line: { color: '#151c31', width: 2 } }, fill: 'tozeroy', fillcolor: 'rgba(139,123,255,0.08)', hovertemplate: 'Discount: %{x}%<br>Purchase rate: %{y:.1f}%<extra></extra>' }]} layout={{...plotLayout, xaxis:{...plotLayout.xaxis,title:{text:'Discount level (%)',font:{size:10}}}, yaxis:{...plotLayout.yaxis,title:{text:'Purchase rate (%)',font:{size:10}}}}} config={config} useResizeHandler style={{width:'100%',height:'100%'}} /></div><div className="chart-insight"><span className="insight-icon"><Sparkles size={14}/></span><span><b>Look for diminishing returns.</b> Higher discounts can lift conversion but may reduce margin.</span></div></article>
          <article className="panel chart-panel"><div className="panel-heading"><div><h3>Estimated treatment effects</h3><p>Distribution of customer-level uplift estimates</p></div><span className="soft-badge purple-badge">CATE</span></div><div className="chart-area"><Plot data={[{ x: distribution.map(d=>d.effect), y: distribution.map(d=>d.count), type:'bar', marker:{color:distribution.map(d=>d.effect < 0 ? '#e59b70':'#6c70df'),line:{width:0}}, hovertemplate:'Effect: %{x:.2f}<br>Customers: %{y}<extra></extra>' }]} layout={{...plotLayout, bargap:.22, xaxis:{...plotLayout.xaxis,title:{text:'Estimated effect',font:{size:10}}}, yaxis:{...plotLayout.yaxis,title:{text:'Customers',font:{size:10}}}}} config={config} useResizeHandler style={{width:'100%',height:'100%'}} /></div><div className="chart-insight"><span className="insight-icon"><BrainCircuit size={14}/></span><span><b>Target positive responders.</b> CATE estimates are individual-level effects, not just correlation.</span></div></article>
        </section>

        <section className="panel optimizer-panel" id="optimization"><div className="panel-heading"><div><div className="section-kicker">DECISION ENGINE</div><h3>Discount optimization</h3><p>Set business constraints to shape the recommended targeting strategy.</p></div><span className="soft-badge"><ShieldCheck size={13}/> Budget-aware</span></div><div className="optimizer-body"><div className="optimizer-controls"><div className="control-block"><div className="control-label"><label htmlFor="budget">Campaign budget</label><b>{money(budget)}</b></div><input id="budget" type="range" min="1000" max="25000" step="500" value={budget} onChange={e=>setBudget(Number(e.target.value))}/><div className="range-labels"><span>₹1,000</span><span>₹25,000</span></div></div><div className="control-block"><div className="control-label"><label htmlFor="discount">Maximum discount</label><b>{maxDiscount}%</b></div><input id="discount" type="range" min="5" max="30" step="5" value={maxDiscount} onChange={e=>setMaxDiscount(Number(e.target.value))}/><div className="range-labels"><span>5%</span><span>30%</span></div></div><div className="control-block objective-control"><label htmlFor="objective">Optimization objective</label><div className="select-wrap"><select id="objective" value={objective} onChange={e=>setObjective(e.target.value)}><option value="revenue">Maximize incremental revenue</option><option value="conversion">Maximize purchase conversion</option><option value="profit">Maximize estimated profit</option></select><ChevronDown size={15}/></div></div><button className="btn btn-primary optimize-btn" onClick={runOptimization} disabled={optimizing}>{optimizing ? <LoaderCircle size={16} className="spin"/> : <Target size={16}/>} {optimizing ? 'Optimizing…' : 'Optimize campaign'} <span>→</span></button></div><div className="optimizer-summary"><div className="summary-icon"><Gauge size={22}/></div><div className="summary-title">Your campaign setup</div><div className="summary-metric"><span>Available budget</span><b>{money(budget)}</b></div><div className="summary-metric"><span>Discount ceiling</span><b>{maxDiscount}%</b></div><div className="summary-metric"><span>Primary objective</span><b>{objective === 'revenue' ? 'Incremental revenue' : objective === 'conversion' ? 'Purchase conversion' : 'Estimated profit'}</b></div><div className="summary-note"><ShieldCheck size={15}/> Recommendations should respect your constraints when calculated by the backend.</div></div></div></section>

        <section className="panel recommendations-panel" id="recommendations"><div className="panel-heading"><div><div className="section-kicker">ACTIONABLE OUTPUT</div><h3>Recommended customer offers</h3><p>Customers with the strongest estimated response to a discount.</p></div><button className="btn btn-secondary compact-btn" onClick={exportCsv}><Download size={15}/> Export CSV</button></div><div className="table-wrap"><table className="recommendation-table"><thead><tr><th>Customer</th><th>Segment</th><th>Estimated uplift</th><th>Recommended discount</th><th>Expected incremental revenue</th><th></th></tr></thead><tbody>{recommendations.map((r,i)=><tr key={`${r.id}-${i}`}><td><div className="customer-cell"><div className={`customer-avatar avatar-${i%4}`}>{String(r.id).replace(/[^a-z0-9]/gi,'').slice(-2).toUpperCase()}</div><b>{r.id}</b></div></td><td><span className="segment-tag">{r.segment}</span></td><td><span className="uplift-value"><ArrowUpRight size={14}/>{pct(r.uplift)}</span></td><td><span className="discount-pill">{r.discount}% off</span></td><td className="revenue-cell">{money(r.revenue)}</td><td><button className="row-action" title="View customer details" onClick={()=>setNotice(`${r.id}: ${r.segment}; estimated uplift ${pct(r.uplift)}; recommended discount ${r.discount}%. Validate these estimates against backend model output.`)}><MousePointer2 size={16}/></button></td></tr>)}</tbody></table></div><div className="table-footer"><span>Showing <b>{recommendations.length}</b> customer recommendations</span><span>Sum of listed incremental revenue: <b>{money(totalRecommended)}</b></span></div></section>

        <section className="panel strategy-panel"><div className="panel-heading"><div><div className="section-kicker">STRATEGY COMPARISON</div><h3>Targeted vs. blanket discounts</h3><p>Illustrative comparison of campaign approaches.</p></div><span className="soft-badge purple-badge">3 strategies</span></div><div className="strategy-grid">{strategies.map((s,i)=><div className={`strategy-card ${i===2?'strategy-featured':''}`} key={s.name}><div className="strategy-card-top"><span className={`strategy-icon strategy-${i}`}>{i===0?<X size={17}/>:i===1?<Users size={17}/>:<Target size={17}/>}</span>{i===2&&<span className="recommended-label">RECOMMENDED</span>}</div><h4>{s.name}</h4><div className="strategy-metric-label">Purchase rate</div><div className="strategy-big">{s.conversion}%</div><div className="strategy-progress"><span style={{width:`${s.conversion/22*100}%`}}/></div><div className="strategy-divider"/><div className="strategy-row"><span>Incremental revenue</span><b>{money(s.incrementalRevenue)}</b></div><div className="strategy-row"><span>Discount spend</span><b>{money(s.spend)}</b></div><div className="strategy-row"><span>Net incremental value</span><b className={s.incrementalRevenue-s.spend>=0?'positive-text':''}>{money(s.incrementalRevenue-s.spend)}</b></div></div>)}</div><p className="strategy-footnote"><CircleHelp size={14}/> Strategy comparison uses illustrative sample values until your API returns measured estimates for all three strategies.</p></section>

        <section className="bottom-grid"><article className="panel diagnostics-panel"><div className="panel-heading"><div><h3>Model diagnostics</h3><p>Analysis pipeline and current status</p></div><BrainCircuit size={19} className="muted-icon"/></div><div className="diagnostic-list"><div><span className="diagnostic-dot green-dot"/><span>Dataset preview</span><b>{file?'Loaded':'Waiting for CSV'}</b></div><div><span className={`diagnostic-dot ${apiStatus.startsWith('Connected')?'green-dot':'orange-dot'}`}/><span>Backend connection</span><b>{apiStatus.startsWith('Connected')?'Connected':'Demo / offline'}</b></div><div><span className="diagnostic-dot purple-dot"/><span>Estimation method</span><b>{diagnostics.method || 'Double Machine Learning'}</b></div><div><span className="diagnostic-dot orange-dot"/><span>Model status</span><b>{diagnostics.status || 'Not run'}</b></div></div><button className="text-button" onClick={()=>setNotice('DML estimates treatment effects while adjusting for observed confounders. Check overlap, treatment/outcome definitions, sample size, and uncertainty before acting on recommendations.')}>Understand model assumptions ↗</button></article><article className="panel pipeline-panel"><div className="panel-heading"><div><h3>Analysis workflow</h3><p>From raw data to campaign decision</p></div></div><div className="pipeline">{[{n:'01',t:'Upload & validate',d:'Check columns, missing values and data types',done:!!file},{n:'02',t:'Estimate causal effects',d:'Fit nuisance models and estimate treatment effects',done:apiStatus.startsWith('Connected')},{n:'03',t:'Optimize offers',d:'Allocate discount budget under constraints',done:false},{n:'04',t:'Export strategy',d:'Share customer list and business impact report',done:false}].map(s=><div className="pipeline-step" key={s.n}><div className={`pipeline-number ${s.done?'step-done':''}`}>{s.done?<CheckCircle2 size={15}/>:s.n}</div><div><b>{s.t}</b><small>{s.d}</small></div></div>)}</div></article></section>
        <footer className="footer"><div className="footer-brand"><Sparkles size={15}/> EconoCausal</div><span>Dynamic pricing via Double Machine Learning</span><span>Built for responsible, budget-aware decisions.</span></footer>
      </div>
    </main>
  </div>
}
export default App
