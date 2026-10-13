import React, { useMemo, useState } from 'react'
import {
  BarChart3, TrendingUp, Boxes, Settings, CircleHelp, ChevronDown,
  Search, Bell, Download, SlidersHorizontal, Languages, Menu, X,
  Users, Target, IndianRupee, ArrowUpRight, Check, CalendarDays,
  LayoutDashboard, FlaskConical, FileText
} from 'lucide-react'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
  PieChart, Pie, Cell, LineChart, Line, Area, AreaChart, ReferenceLine
} from 'recharts'

const copy = {
  EN: {
    overview:'Overview', analytics:'Analytics', settings:'Settings', reporting:'Reporting',
    campaigns:'Campaigns', models:'Models', help:'Help', title:'Causal Discount Optimization: Q4 Campaign',
    budget:'Budget Allocation', totalBudget:'Total Discount Budget Allocation', used:'used', utilized:'utilized',
    allocated:'Allocated', roi:'ROI', revenueUplift:'Revenue Uplift', effect:'Causal Effect Distribution',
    segmentBudget:'Budget Distribution by Segment', organic:'Organic Buyers (No Discount Needed)',
    persuadable:'Persuadable Buyers (High Causal Effect)', lost:'Lost Causes (No Purchase Risk)',
    segment:'Segment', users:'Users', low:'Low', high:'High', causal:'Causal Effect',
    uplift:'Uplift Curve', optimalAllocation:'Optimal Allocation', optimalDiscount:'Optimal Discount',
    projected:'Projected Revenue vs. Discount Spend (₹)', revenue:'Projected Revenue', spend:'Discount Spend',
    score:'Causal Effect Score', frequency:'Frequency', cumulative:'Cumulative Uplift (%)',
    population:'% of Population Targeted', date:'Oct 1 – Oct 31, 2026', search:'Search analytics…',
    notifications:'Notifications', export:'Export report', refreshed:'Dashboard updated', language:'Language',
    dashboard:'Dashboard', quick:'Quick actions', save:'Save settings', cancel:'Cancel',
    settingsTitle:'Dashboard Settings', settingsDesc:'Customize how your analytics dashboard behaves.',
    budgetLimit:'Budget limit (₹)', confidence:'Minimum causal effect threshold', saved:'Settings saved successfully.',
    reportTitle:'Reports', reportDesc:'Review and export the latest campaign performance.',
    downloadCsv:'Download CSV', campaignStatus:'Campaign status', active:'Active', period:'Reporting period',
    modelTitle:'Causal Models', modelDesc:'Model summary and estimation diagnostics.',
    model:'Double Machine Learning (DML)', trained:'Demo model ready', modelNote:'Connect the Python API to replace demo estimates with model outputs.',
    campaignTitle:'Campaigns', campaignDesc:'Review audience segments and recommended discount strategy.',
    segmentName:'Customer segment', allocation:'Recommended allocation', effectLabel:'Estimated causal effect',
    action:'Action', noDiscount:'No discount', target:'Target with discount', exclude:'Exclude from campaign',
    budgetSaved:'Budget setting updated.', close:'Close', usersCount:'customers'
  },
  HI: {
    overview:'अवलोकन', analytics:'विश्लेषण', settings:'सेटिंग्स', reporting:'रिपोर्टिंग',
    campaigns:'अभियान', models:'मॉडल', help:'सहायता', title:'कारणात्मक छूट अनुकूलन: Q4 अभियान',
    budget:'बजट आवंटन', totalBudget:'कुल छूट बजट आवंटन', used:'उपयोग किया', utilized:'उपयोग',
    allocated:'आवंटित', roi:'ROI', revenueUplift:'राजस्व वृद्धि', effect:'कारणात्मक प्रभाव वितरण',
    segmentBudget:'सेगमेंट के अनुसार बजट', organic:'ऑर्गेनिक खरीदार (छूट आवश्यक नहीं)',
    persuadable:'प्रभावित हो सकने वाले खरीदार (उच्च प्रभाव)', lost:'कम संभावना वाले खरीदार',
    segment:'सेगमेंट', users:'उपयोगकर्ता', low:'कम', high:'उच्च', causal:'कारणात्मक प्रभाव',
    uplift:'अपलिफ्ट वक्र', optimalAllocation:'इष्टतम आवंटन', optimalDiscount:'इष्टतम छूट',
    projected:'अनुमानित राजस्व बनाम छूट खर्च (₹)', revenue:'अनुमानित राजस्व', spend:'छूट खर्च',
    score:'कारणात्मक प्रभाव स्कोर', frequency:'आवृत्ति', cumulative:'संचयी अपलिफ्ट (%)',
    population:'लक्षित जनसंख्या का %', date:'1–31 अक्टूबर, 2026', search:'विश्लेषण खोजें…',
    notifications:'सूचनाएँ', export:'रिपोर्ट निर्यात करें', refreshed:'डैशबोर्ड अपडेट हुआ', language:'भाषा',
    dashboard:'डैशबोर्ड', quick:'त्वरित कार्रवाई', save:'सेटिंग्स सहेजें', cancel:'रद्द करें',
    settingsTitle:'डैशबोर्ड सेटिंग्स', settingsDesc:'अपने विश्लेषण डैशबोर्ड को अनुकूलित करें।',
    budgetLimit:'बजट सीमा (₹)', confidence:'न्यूनतम कारणात्मक प्रभाव सीमा', saved:'सेटिंग्स सफलतापूर्वक सहेजी गईं।',
    reportTitle:'रिपोर्ट', reportDesc:'नवीनतम अभियान प्रदर्शन देखें और निर्यात करें।',
    downloadCsv:'CSV डाउनलोड करें', campaignStatus:'अभियान स्थिति', active:'सक्रिय', period:'रिपोर्टिंग अवधि',
    modelTitle:'कारणात्मक मॉडल', modelDesc:'मॉडल सारांश और अनुमान निदान।',
    model:'डबल मशीन लर्निंग (DML)', trained:'डेमो मॉडल तैयार', modelNote:'डेमो अनुमान की जगह वास्तविक मॉडल परिणामों के लिए Python API जोड़ें।',
    campaignTitle:'अभियान', campaignDesc:'ऑडियंस सेगमेंट और सुझाई गई छूट रणनीति देखें।',
    segmentName:'ग्राहक सेगमेंट', allocation:'सुझाया गया आवंटन', effectLabel:'अनुमानित कारणात्मक प्रभाव',
    action:'कार्रवाई', noDiscount:'छूट नहीं', target:'छूट लक्षित करें', exclude:'अभियान से हटाएँ',
    usersCount:'ग्राहक'
  },
  ES: {
    overview:'Resumen', analytics:'Analítica', settings:'Ajustes', reporting:'Informes',
    campaigns:'Campañas', models:'Modelos', help:'Ayuda', title:'Optimización causal de descuentos: campaña Q4',
    budget:'Asignación de presupuesto', totalBudget:'Presupuesto total de descuentos', used:'usado', utilized:'utilizado',
    allocated:'Asignado', roi:'ROI', revenueUplift:'Aumento de ingresos', effect:'Distribución del efecto causal',
    segmentBudget:'Presupuesto por segmento', organic:'Compradores orgánicos (sin descuento)',
    persuadable:'Compradores persuadibles (alto efecto causal)', lost:'Casos perdidos (sin riesgo de compra)',
    segment:'Segmento', users:'Usuarios', low:'Bajo', high:'Alto', causal:'Efecto causal',
    uplift:'Curva de uplift', optimalAllocation:'Asignación óptima', optimalDiscount:'Descuento óptimo',
    projected:'Ingresos proyectados vs. gasto en descuentos (₹)', revenue:'Ingresos proyectados', spend:'Gasto en descuentos',
    score:'Puntuación de efecto causal', frequency:'Frecuencia', cumulative:'Uplift acumulado (%)',
    population:'% de población objetivo', date:'1–31 oct. 2026', search:'Buscar analítica…',
    notifications:'Notificaciones', export:'Exportar informe', refreshed:'Panel actualizado', language:'Idioma',
    dashboard:'Panel', quick:'Acciones rápidas', save:'Guardar ajustes', cancel:'Cancelar',
    settingsTitle:'Ajustes del panel', settingsDesc:'Personaliza el comportamiento del panel de análisis.',
    budgetLimit:'Límite de presupuesto (₹)', confidence:'Umbral mínimo de efecto causal', saved:'Ajustes guardados correctamente.',
    reportTitle:'Informes', reportDesc:'Revisa y exporta el rendimiento más reciente.',
    downloadCsv:'Descargar CSV', campaignStatus:'Estado de campaña', active:'Activa', period:'Periodo del informe',
    modelTitle:'Modelos causales', modelDesc:'Resumen del modelo y diagnósticos de estimación.',
    model:'Doble aprendizaje automático (DML)', trained:'Modelo de demostración listo', modelNote:'Conecta la API de Python para sustituir las estimaciones de demostración.',
    campaignTitle:'Campañas', campaignDesc:'Revisa los segmentos y la estrategia de descuento recomendada.',
    segmentName:'Segmento de clientes', allocation:'Asignación recomendada', effectLabel:'Efecto causal estimado',
    action:'Acción', noDiscount:'Sin descuento', target:'Aplicar descuento', exclude:'Excluir de campaña',
    usersCount:'clientes'
  }
}

const segmentData = [
  { key:'organic', name:'Customer A: Organic Buyers', share:40, users:5200, effect:0.05, kind:'organic', color:'#4e91ec' },
  { key:'persuadable', name:'Customer B: Persuadable Buyers', share:25, users:3250, effect:0.88, kind:'persuadable', color:'#70d4b0' },
  { key:'lost', name:'Customer C: Lost Causes', share:35, users:4550, effect:0.12, kind:'lost', color:'#d99a68' }
]
const effectData = [{x:'0.0',v:5},{x:'0.1',v:13},{x:'0.2',v:25},{x:'0.3',v:39},{x:'0.4',v:52},{x:'0.5',v:43},{x:'0.6',v:31},{x:'0.7',v:18},{x:'0.8',v:9},{x:'0.9',v:4}]
const upliftData = [{x:0,dml:0,random:0},{x:10,dml:18,random:10},{x:20,dml:31,random:20},{x:30,dml:43,random:30},{x:40,dml:52,random:40},{x:50,dml:60,random:50},{x:60,dml:67,random:60},{x:70,dml:73,random:70},{x:80,dml:78,random:80},{x:90,dml:83,random:90},{x:100,dml:87,random:100}]
const spendData = [{x:'₹0',revenue:0,spend:0},{x:'₹10k',revenue:38000,spend:10000},{x:'₹20k',revenue:60000,spend:20000},{x:'₹30k',revenue:80000,spend:30000},{x:'₹40k',revenue:97000,spend:40000},{x:'₹50k',revenue:112000,spend:50000}]
const money = n => '₹' + Number(n).toLocaleString('en-IN')
const fmt = n => Number(n).toLocaleString('en-IN')

function App() {
  const [lang,setLang] = useState('EN')
  const [page,setPage] = useState('analytics')
  const [mobileNav,setMobileNav] = useState(false)
  const [budget,setBudget] = useState(12000)
  const [threshold,setThreshold] = useState(0.2)
  const [draftBudget,setDraftBudget] = useState('12000')
  const [draftThreshold,setDraftThreshold] = useState('0.2')
  const [toast,setToast] = useState('')
  const [date,setDate] = useState('Oct 1 – Oct 31, 2026')
  const [dateOpen,setDateOpen] = useState(false)
  const [search,setSearch] = useState('')
  const [showNotifications,setShowNotifications] = useState(false)
  const t = copy[lang]
  const totalBudget = 10000
  const allocation = Math.min(totalBudget,budget)
  const pieData = [{name:t.persuadable,value:81},{name:t.lost,value:19}]
  const notify = msg => { setToast(msg); window.setTimeout(()=>setToast(''),2600) }
  const nav = [
    {id:'overview',label:t.overview,icon:LayoutDashboard},
    {id:'analytics',label:t.analytics,icon:BarChart3},
    {id:'campaigns',label:t.campaigns,icon:TrendingUp},
    {id:'models',label:t.models,icon:FlaskConical},
    {id:'settings',label:t.settings,icon:Settings},
    {id:'reporting',label:t.reporting,icon:FileText}
  ]
  const visibleSegments = useMemo(()=>segmentData.filter(s=>(s.name+' '+t[s.key]).toLowerCase().includes(search.toLowerCase())),[search,t])
  const exportCsv = () => {
    const rows = [['Segment','Share (%)','Users','Estimated causal effect'],...segmentData.map(s=>[s.name,s.share,s.users,s.effect])]
    const csv = rows.map(r=>r.map(v=>`"${String(v).replaceAll('"','""')}"`).join(',')).join('\n')
    const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8;'}))
    const a=document.createElement('a'); a.href=url; a.download='econocausal-campaign-report.csv'; a.click(); URL.revokeObjectURL(url)
    notify(t.export)
  }
  const changePage = id => {setPage(id);setMobileNav(false)}
  const pageTitle = page==='settings'?t.settingsTitle:page==='reporting'?t.reportTitle:page==='models'?t.modelTitle:page==='campaigns'?t.campaignTitle:t.title

  return <div className="app-shell">
    <header className="topbar">
      <button className="mobile-menu icon-btn" aria-label="Open navigation" onClick={()=>setMobileNav(!mobileNav)}>{mobileNav?<X/>:<Menu/>}</button>
      <div className="brand"><div className="brand-mark"><span>E</span><span>C</span></div><span className="brand-name">EconoCausal</span></div>
      <nav className="top-nav">{nav.slice(0,2).concat(nav.slice(4,6)).map(n=><button key={n.id} className={page===n.id?'top-link active':''} onClick={()=>changePage(n.id)}>{n.label}</button>)}</nav>
      <div className="top-actions">
        <div className="search-box"><Search size={15}/><input aria-label={t.search} placeholder={t.search} value={search} onChange={e=>setSearch(e.target.value)}/></div>
        <div className="relative"><button className="icon-btn" title={t.notifications} onClick={()=>setShowNotifications(!showNotifications)}><Bell size={18}/><i className="notification-dot"/></button>{showNotifications&&<div className="popover notification-pop"><strong>{t.notifications}</strong><p>{t.refreshed}</p><p>Campaign analysis is ready.</p><button className="small-btn" onClick={()=>setShowNotifications(false)}>{t.close}</button></div>}</div>
        <div className="language-control"><Languages size={16}/><span className="language-label">{t.language}</span>{['EN','ES','HI'].map(l=><button key={l} className={lang===l?'lang-active':''} onClick={()=>setLang(l)}>{l}</button>)}</div>
      </div>
    </header>

    <aside className={`sidebar ${mobileNav?'sidebar-open':''}`}>
      <div className="sidebar-label">{t.dashboard}</div>
      {nav.map(n=><button key={n.id} onClick={()=>changePage(n.id)} className={`side-link ${page===n.id?'selected':''}`}><n.icon size={19}/><span>{n.label}</span></button>)}
      <div className="sidebar-bottom"><div className="avatar">AS</div><div><strong>Dr. Anya Sharma</strong><small>Campaign analyst</small></div><button className="icon-btn" onClick={()=>changePage('settings')} aria-label={t.settings}><Settings size={16}/></button></div>
      <div className="sidebar-foot">ECONOCausal <span>v1.0.0</span></div>
    </aside>

    <main className="main-content">
      <div className="page-heading"><div><div className="eyebrow"><span className="live-dot"/>{t.analytics.toUpperCase()} / Q4 2026</div><h1>{pageTitle}</h1><p className="subtitle">{page==='analytics'||page==='overview'?'Understand which customers respond to discounts and allocate budget where it creates incremental value.':page==='settings'?t.settingsDesc:page==='reporting'?t.reportDesc:page==='models'?t.modelDesc:t.campaignDesc}</p></div>
        <div className="heading-actions">{(page==='analytics'||page==='overview'||page==='reporting')&&<div className="relative"><button className="date-btn" onClick={()=>setDateOpen(!dateOpen)}><CalendarDays size={16}/>{date}<ChevronDown size={15}/></button>{dateOpen&&<div className="popover date-pop">{['Oct 1 – Oct 31, 2026','Sep 1 – Sep 30, 2026','Q3 2026','Year to date'].map(d=><button key={d} onClick={()=>{setDate(d);setDateOpen(false)}}>{d}</button>)}</div>}</div>}{page!=='settings'&&<button className="primary-btn" onClick={exportCsv}><Download size={16}/>{t.export}</button>}</div>
      </div>

      {(page==='analytics'||page==='overview')&&<>
        <section className="kpi-grid">
          <div className="panel budget-panel"><div className="panel-head"><h2>{t.budget}</h2><span className="panel-icon"><IndianRupee size={17}/></span></div><div className="budget-line"><span>{t.totalBudget}</span><strong>{money(totalBudget)} <small>/ {money(budget)} {t.used}</small></strong></div><div className="progress-track"><div className="progress-fill" style={{width:`${Math.min(100,totalBudget/Math.max(budget,1)*100)}%`}}/></div><div className="budget-foot"><div><span>{t.allocated}</span><strong>{money(allocation)}</strong></div><div><span>{t.roi}</span><strong className="positive">21.4% <ArrowUpRight size={14}/></strong></div><div><span>{t.revenueUplift}</span><strong>{money(114500)}</strong></div></div></div>
          <div className="panel kpi-card"><div className="kpi-top"><span>{t.roi}</span><span className="kpi-icon green"><TrendingUp size={17}/></span></div><div className="kpi-value">21.4%</div><div className="kpi-foot"><span className="positive">+4.8%</span><span>vs. previous period</span></div><div className="sparkline"><svg viewBox="0 0 140 30"><path d="M2 25 L22 19 L42 22 L62 10 L82 15 L102 7 L122 11 L138 2" fill="none" stroke="#70d4b0" strokeWidth="2.5"/></svg></div></div>
          <div className="panel kpi-card"><div className="kpi-top"><span>{t.revenueUplift}</span><span className="kpi-icon blue"><IndianRupee size={17}/></span></div><div className="kpi-value">{money(114500)}</div><div className="kpi-foot"><span className="positive">+12.6%</span><span>incremental estimate</span></div><div className="sparkline"><svg viewBox="0 0 140 30"><path d="M2 27 L22 23 L42 24 L62 15 L82 17 L102 9 L122 7 L138 2" fill="none" stroke="#5ba6ff" strokeWidth="2.5"/></svg></div></div>
          <div className="panel kpi-card"><div className="kpi-top"><span>Customers analyzed</span><span className="kpi-icon violet"><Users size={17}/></span></div><div className="kpi-value">13,000</div><div className="kpi-foot"><span className="positive">3 segments</span><span>audience groups</span></div><div className="sparkline"><svg viewBox="0 0 140 30"><path d="M2 23 L22 15 L42 19 L62 12 L82 16 L102 6 L122 10 L138 3" fill="none" stroke="#a99aff" strokeWidth="2.5"/></svg></div></div>
        </section>
        <section className="analytics-grid">
          <div className="panel segment-panel"><div className="panel-head"><div><h2>Customer segments</h2><p>Recommended strategy by estimated treatment effect</p></div><SlidersHorizontal size={17} className="muted"/></div><div className="segment-list">{visibleSegments.map((s,i)=><article className="segment-card" key={s.key}><div className="segment-card-top"><span className="segment-number">{String(i+1).padStart(2,'0')}</span><div className="segment-title"><h3>{s.name} <span className={`segment-pill ${s.kind}`}>{s.kind==='persuadable'?t.high:t.low} {t.causal}</span></h3><p>{s.key==='organic'?t.organic:s.key==='persuadable'?t.persuadable:t.lost}</p></div><span className="effect-score" style={{color:s.color}}>{s.effect.toFixed(2)}</span></div><div className="segment-stats"><div><strong>{s.share}%</strong><span>{t.segment}</span></div><div><strong>{fmt(s.users)}</strong><span>{t.users}</span></div><div className="segment-action"><span>{s.kind==='persuadable'?t.target:s.kind==='organic'?t.noDiscount:t.exclude}</span><div className="mini-track"><div style={{width:`${s.share}%`,background:s.color}}/></div></div></div></article>)}{visibleSegments.length===0&&<div className="empty-state">No segments match “{search}”.</div>}</div><div className="panel-footer"><span><span className="legend-dot blue-dot"/> High causal effect</span><span><span className="legend-dot amber-dot"/> Low causal effect</span><span className="foot-note">Demo estimates · not connected to a live model</span></div></div>
          <div className="panel chart-panel effect-panel"><div className="panel-head"><div><h2>{t.effect}</h2><p>Estimated effect score across customers</p></div><button className="dots-btn" aria-label="Chart options" onClick={()=>notify('Causal effect distribution')}>•••</button></div><div className="chart-area"><ResponsiveContainer width="100%" height="100%"><BarChart data={effectData} margin={{top:10,right:8,left:-20,bottom:0}}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#293748"/><XAxis dataKey="x" tick={{fill:'#8f9db0',fontSize:10}} axisLine={false} tickLine={false}/><YAxis tick={{fill:'#8f9db0',fontSize:10}} axisLine={false} tickLine={false}/><Tooltip contentStyle={{background:'#101a27',border:'1px solid #334155',borderRadius:8,color:'#e7edf5'}}/><Bar dataKey="v" name={t.frequency} fill="#5ba6ff" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer><div className="chart-stat"><span>Mean causal effect</span><strong>0.45</strong></div></div><div className="chart-caption"><span>{t.frequency}</span><span>{t.score}</span></div></div>
          <div className="panel chart-panel distribution-panel"><div className="panel-head"><div><h2>{t.segmentBudget}</h2><p>Suggested budget split</p></div><button className="dots-btn" aria-label="Chart options" onClick={()=>notify(t.segmentBudget)}>•••</button></div><div className="donut-wrap"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={pieData} dataKey="value" nameKey="name" innerRadius="61%" outerRadius="83%" paddingAngle={3} stroke="none" startAngle={90} endAngle={-270}><Cell fill="#5ba6ff"/><Cell fill="#273c55"/></Pie><Tooltip contentStyle={{background:'#101a27',border:'1px solid #334155',borderRadius:8,color:'#e7edf5'}}/></PieChart></ResponsiveContainer><div className="donut-center"><strong>{money(totalBudget)}</strong><span>Total budget</span></div></div><div className="donut-legend"><div><i className="legend-dot blue-dot"/><span>{t.persuadable}</span><strong>81%</strong></div><div><i className="legend-dot slate-dot"/><span>{t.lost}</span><strong>19%</strong></div></div></div>
          <div className="panel chart-panel uplift-panel"><div className="panel-head"><div><h2>{t.uplift}</h2><p>Targeting efficiency compared with random selection</p></div><button className="dots-btn" aria-label="Chart options" onClick={()=>notify(t.uplift)}>•••</button></div><div className="chart-area"><ResponsiveContainer width="100%" height="100%"><LineChart data={upliftData} margin={{top:8,right:10,left:-18,bottom:0}}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#293748"/><XAxis dataKey="x" tick={{fill:'#8f9db0',fontSize:10}} axisLine={false} tickLine={false}/><YAxis tick={{fill:'#8f9db0',fontSize:10}} axisLine={false} tickLine={false}/><Tooltip contentStyle={{background:'#101a27',border:'1px solid #334155',borderRadius:8,color:'#e7edf5'}}/><Line type="monotone" dataKey="dml" name="DML targeting" stroke="#70d4b0" strokeWidth={2.5} dot={false}/><Line type="monotone" dataKey="random" name="Random targeting" stroke="#5ba6ff" strokeWidth={2} dot={false} strokeDasharray="5 4"/></LineChart></ResponsiveContainer><div className="chart-stat uplift-stat"><span>{t.optimalAllocation}</span><strong>81%</strong><span>{t.optimalDiscount}: 15–20%</span></div></div><div className="chart-caption"><span>{t.cumulative}</span><span>{t.population}</span></div></div>
          <div className="panel chart-panel revenue-panel"><div className="panel-head"><div><h2>{t.projected}</h2><p>Illustrative budget-response curve</p></div><button className="dots-btn" aria-label="Chart options" onClick={()=>notify(t.projected)}>•••</button></div><div className="chart-area"><ResponsiveContainer width="100%" height="100%"><LineChart data={spendData} margin={{top:10,right:10,left:-12,bottom:0}}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#293748"/><XAxis dataKey="x" tick={{fill:'#8f9db0',fontSize:10}} axisLine={false} tickLine={false}/><YAxis tickFormatter={v=>v===0?'₹0':`₹${v/1000}k`} tick={{fill:'#8f9db0',fontSize:10}} axisLine={false} tickLine={false}/><Tooltip formatter={v=>money(v)} contentStyle={{background:'#101a27',border:'1px solid #334155',borderRadius:8,color:'#e7edf5'}}/><Line type="monotone" dataKey="revenue" name={t.revenue} stroke="#70d4b0" strokeWidth={2.5} dot={{r:3,fill:'#70d4b0'}}/><Line type="monotone" dataKey="spend" name={t.spend} stroke="#5ba6ff" strokeWidth={2.5} dot={{r:3,fill:'#5ba6ff'}}/></LineChart></ResponsiveContainer></div><div className="chart-legend"><span><i className="legend-dot green-dot"/>{t.revenue}</span><span><i className="legend-dot blue-dot"/>{t.spend}</span></div></div>
        </section>
        <section className="bottom-callout"><div className="callout-icon"><Target size={20}/></div><div><strong>Recommendation: prioritize persuadable customers</strong><p>Demo recommendation: test a 15–20% discount on high-effect customers, then validate incremental profit using the trained causal model.</p></div><button onClick={()=>changePage('campaigns')} className="secondary-btn">View campaign <ArrowUpRight size={15}/></button></section>
      </>}

      {page==='settings'&&<section className="panel settings-card"><div className="panel-head"><div><h2>{t.settingsTitle}</h2><p>{t.settingsDesc}</p></div><Settings size={19}/></div><form onSubmit={e=>{e.preventDefault();setBudget(Math.max(1000,Number(draftBudget)||12000));setThreshold(Math.min(1,Math.max(0,Number(draftThreshold)||0)));notify(t.saved)}}><label>{t.budgetLimit}<input type="number" min="1000" step="500" value={draftBudget} onChange={e=>setDraftBudget(e.target.value)}/><small>Used to scale the budget allocation display.</small></label><label>{t.confidence}<input type="number" min="0" max="1" step="0.05" value={draftThreshold} onChange={e=>setDraftThreshold(e.target.value)}/><small>Current threshold: {threshold.toFixed(2)}. This is a demo UI setting.</small></label><label>{t.language}<select value={lang} onChange={e=>setLang(e.target.value)}><option value="EN">English</option><option value="ES">Español</option><option value="HI">हिन्दी</option></select></label><div className="form-actions"><button type="button" className="secondary-btn" onClick={()=>{setDraftBudget(String(budget));setDraftThreshold(String(threshold))}}>{t.cancel}</button><button className="primary-btn" type="submit"><Check size={16}/>{t.save}</button></div></form></section>}

      {page==='campaigns'&&<section className="panel table-panel"><div className="panel-head"><div><h2>{t.campaignTitle}</h2><p>{t.campaignDesc}</p></div><span className="status-pill"><i/>{t.active}</span></div><div className="table-scroll"><table><thead><tr><th>{t.segmentName}</th><th>Share</th><th>{t.users}</th><th>{t.effectLabel}</th><th>{t.allocation}</th><th>{t.action}</th></tr></thead><tbody>{segmentData.map(s=><tr key={s.key}><td><strong>{t[s.key]}</strong></td><td>{s.share}%</td><td>{fmt(s.users)}</td><td><span className={`effect-badge ${s.kind}`}>{s.effect.toFixed(2)}</span></td><td>{s.kind==='persuadable'?'81%':s.kind==='organic'?'0%':'19%'}</td><td><span className={`strategy ${s.kind}`}>{s.kind==='persuadable'?t.target:s.kind==='organic'?t.noDiscount:t.exclude}</span></td></tr>)}</tbody></table></div><div className="table-foot">Estimates shown are illustrative demo data until the causal API is connected.</div></section>}

      {page==='models'&&<section className="model-grid"><div className="panel model-card"><div className="model-icon"><FlaskConical/></div><span className="status-pill"><i/>{t.trained}</span><h2>{t.model}</h2><p>{t.modelNote}</p><div className="model-metrics"><div><span>Mean effect</span><strong>0.45</strong></div><div><span>Targeting AUC</span><strong>0.68</strong></div><div><span>Segments</span><strong>3</strong></div></div></div><div className="panel model-card"><h2>How it works</h2><ol className="steps"><li><b>01</b><div><strong>Nuisance models</strong><p>Estimate treatment assignment and purchase outcome from customer features.</p></div></li><li><b>02</b><div><strong>Orthogonalization</strong><p>Remove predictable effects from treatment and outcome to reduce confounding bias.</p></div></li><li><b>03</b><div><strong>Treatment effects</strong><p>Estimate heterogeneous discount effects to identify customers most likely to respond.</p></div></li></ol></div></section>}

      {page==='reporting'&&<section className="panel report-card"><div className="report-icon"><FileText/></div><h2>{t.reportTitle}</h2><p>{t.reportDesc}</p><div className="report-summary"><div><span>{t.campaignStatus}</span><strong>{t.active}</strong></div><div><span>{t.period}</span><strong>{date}</strong></div><div><span>{t.revenueUplift}</span><strong>{money(114500)}</strong></div><div><span>{t.roi}</span><strong>21.4%</strong></div></div><button className="primary-btn" onClick={exportCsv}><Download size={16}/>{t.downloadCsv}</button></section>}

      <footer className="app-footer"><span>© 2026 EconoCausal</span><span>Dynamic pricing intelligence <i/> Built for causal decision-making</span><span>Demo data · API not connected</span></footer>
    </main>
    {toast&&<div className="toast"><Check size={17}/>{toast}</div>}
  </div>
}
export default App
