import { useEffect, useState } from "react";
import {
  Leaf, LayoutDashboard, BrainCircuit, Users, Wallet, Database,
  RefreshCw, Upload, Activity, TrendingUp, Languages
} from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, LineChart, Line, AreaChart, Area,
  PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from "recharts";
import {
  summary, health, optimize, clusters, segments, upload, dashboardData,
  advancedMultilevel, advancedPropensity, advancedDiagnostics, advancedRefutation
} from "./api";
import AdvancedCausal from "./components/AdvancedCausal";

const COLORS = ["#6475e8", "#35b8a0", "#f4a45d", "#9b78dc", "#e46f91", "#4e9bd6", "#8bbd5b"];
const fmt = (n) => n == null || Number.isNaN(Number(n)) ? "—" : Number(n).toLocaleString("en-IN");
const pct = (n) => n == null || Number.isNaN(Number(n)) ? "—" : `${(Number(n) * 100).toFixed(1)}%`;

const translations = {
  en: {
    Overview:"Overview", "Causal analysis":"Causal analysis", "Advanced causal":"Advanced causal",
    Segments:"Segments", Optimization:"Optimization", Dataset:"Dataset",
    workspace:"Workspace", connected:"Connected", offline:"Offline", refresh:"Refresh",
    platform:"CAUSAL INTELLIGENCE PLATFORM",
    overviewDesc:"Your customer data, explained through clear visual summaries.",
    causalDesc:"Understand the incremental effect of discounts.",
    segmentsDesc:"Explore customer groups and spending patterns.",
    optimizationDesc:"Plan promotions using causal evidence.",
    datasetDesc:"Upload and review your customer data.",
    overviewHero:"Your customer data · at a glance",
    heroTitle:"Turn customer data", heroTitle2:"into decisions.",
    heroDesc:"Explore who your customers are, how they purchase, and where promotions may create incremental value.",
    explore:"Explore causal insights ↗", overallRate:"overall purchase rate",
    datasetSummary:"Dataset summary", keyNumbers:"Key numbers from your active dataset",
    liveData:"LIVE DATA", noConnection:"NO CONNECTION",
    totalCustomers:"Total customers", customerRecords:"Customer records",
    purchasers:"Purchasers", purchasedCustomers:"Customers who purchased",
    purchaseRate:"Purchase rate", sharePurchasing:"Share of customers purchasing",
    dataFields:"Data fields", availableVariables:"Available variables",
    ageDistribution:"Customer age distribution", byAge:"Customer count by age group",
    customerGroups:"Customer groups", bySegment:"How many customers belong to each segment",
    purchaseOverview:"Purchase overview", purchaseCompare:"Purchasers compared with non-purchasers",
    agePurchases:"Age vs. purchases", agePurchasesDesc:"Purchasers and total customers by age band",
    region:"Customers by region", topRegions:"Top regions in the dataset",
    seasonal:"Seasonal customer distribution", bySeason:"Customer count by season",
    next:"What to explore next", choose:"Choose an analysis to continue",
    estimate:"Estimate the discount effect", compare:"Compare customer groups",
    budgetRec:"Build a budget recommendation", guide:"How to read this dashboard",
    simpleGuide:"Simple guide", counts:"Counts", countExplain:"How many customers are in a group.",
    rateExplain:"Purchasers divided by total customers.",
    causalExplain:"Estimated change attributable to receiving a discount, subject to assumptions.",
    impact:"Discount impact analysis", impactDesc:"Estimate how receiving a discount changes purchase probability.",
    runCausal:"Run causal analysis", analyzing:"Analyzing…",
    noteCausal:"Causal estimates depend on assumptions, data quality and model specification.",
    segmentAnalysis:"Customer segment analysis", segmentVisual:"Visual comparison of group sizes and spending clusters",
    runClustering:"Run clustering", regionalGroups:"Regional groups", customerRegion:"Customer count by region",
    planner:"Promotion budget planner", plannerDesc:"Set the budget and target audience size",
    budget:"Budget (₹)", targetCustomers:"Target customers", calculate:"Generate recommendation",
    calculating:"Calculating…", decisionNote:"Decision support only. Validate campaign constraints before deployment.",
    uploadTitle:"Upload customer data", uploadDesc:"Choose a CSV file. The uploaded dataset becomes the active dataset for analysis.",
    chooseCSV:"Choose CSV", rows:"Rows", positive:"Positive outcomes", outcomeRate:"Outcome rate",
    columns:"Columns", variables:"Variables", fields:"Dataset field overview", fieldDesc:"Available columns",
    footer:"© 2026 EconoCausal", footerText:"Understand data. Make better decisions.",
    apiConnected:"API connected", apiOffline:"API offline", research:"Research workspace",
    loadError:"Dashboard data could not load. Check /dashboard-data.",
    apiError:"API unavailable. Start FastAPI at port 8000.", requestError:"Request failed",
    analysisSummary:"Analysis summary", available:"Available", items:"items",
    noChart:"No chart data available. Check the active dataset or refresh.",
    language:"Language", english:"English", hindi:"हिन्दी",
    advanced:"Advanced Causal Analysis"
  },
  hi: {
    Overview:"मुख्य डैशबोर्ड", "Causal analysis":"कारणात्मक विश्लेषण", "Advanced causal":"उन्नत कारणात्मक विश्लेषण",
    Segments:"ग्राहक समूह", Optimization:"ऑप्टिमाइज़ेशन", Dataset:"डेटासेट",
    workspace:"कार्यस्थान", connected:"कनेक्टेड", offline:"ऑफ़लाइन", refresh:"रीफ़्रेश",
    platform:"कारणात्मक बुद्धिमत्ता प्लेटफ़ॉर्म",
    overviewDesc:"आपके ग्राहक डेटा का स्पष्ट विज़ुअल सारांश।",
    causalDesc:"डिस्काउंट के अतिरिक्त प्रभाव को समझें।",
    segmentsDesc:"ग्राहक समूह और खर्च के पैटर्न देखें।",
    optimizationDesc:"कारणात्मक साक्ष्य के आधार पर प्रमोशन की योजना बनाएं।",
    datasetDesc:"ग्राहक डेटा अपलोड और समीक्षा करें।",
    overviewHero:"आपका ग्राहक डेटा · एक नज़र में",
    heroTitle:"ग्राहक डेटा को", heroTitle2:"निर्णयों में बदलें।",
    heroDesc:"जानें आपके ग्राहक कौन हैं, वे कैसे खरीदते हैं और प्रमोशन कहाँ अतिरिक्त मूल्य बना सकते हैं।",
    explore:"कारणात्मक जानकारी देखें ↗", overallRate:"कुल खरीद दर",
    datasetSummary:"डेटासेट सारांश", keyNumbers:"सक्रिय डेटासेट के मुख्य आँकड़े",
    liveData:"लाइव डेटा", noConnection:"कनेक्शन नहीं",
    totalCustomers:"कुल ग्राहक", customerRecords:"ग्राहक रिकॉर्ड",
    purchasers:"खरीदार", purchasedCustomers:"खरीद करने वाले ग्राहक",
    purchaseRate:"खरीद दर", sharePurchasing:"खरीद करने वाले ग्राहकों का हिस्सा",
    dataFields:"डेटा फ़ील्ड", availableVariables:"उपलब्ध वेरिएबल",
    ageDistribution:"ग्राहकों की आयु वितरण", byAge:"आयु समूह के अनुसार ग्राहक",
    customerGroups:"ग्राहक समूह", bySegment:"प्रत्येक सेगमेंट में ग्राहकों की संख्या",
    purchaseOverview:"खरीद का सारांश", purchaseCompare:"खरीदार बनाम गैर-खरीदार",
    agePurchases:"आयु बनाम खरीद", agePurchasesDesc:"आयु समूह के अनुसार ग्राहक और खरीदार",
    region:"क्षेत्र के अनुसार ग्राहक", topRegions:"डेटासेट के प्रमुख क्षेत्र",
    seasonal:"मौसमी ग्राहक वितरण", bySeason:"सीज़न के अनुसार ग्राहक",
    next:"आगे क्या देखें", choose:"विश्लेषण चुनें",
    estimate:"डिस्काउंट प्रभाव का अनुमान", compare:"ग्राहक समूहों की तुलना",
    budgetRec:"बजट सुझाव तैयार करें", guide:"डैशबोर्ड कैसे पढ़ें",
    simpleGuide:"सरल मार्गदर्शिका", counts:"गिनती", countExplain:"किसी समूह में ग्राहकों की संख्या।",
    rateExplain:"खरीदारों को कुल ग्राहकों से विभाजित करें।",
    causalExplain:"डिस्काउंट से संबंधित अनुमानित बदलाव; मान्यताओं पर निर्भर।",
    impact:"डिस्काउंट प्रभाव विश्लेषण", impactDesc:"खरीद संभावना पर डिस्काउंट का प्रभाव अनुमानित करें।",
    runCausal:"कारणात्मक विश्लेषण चलाएँ", analyzing:"विश्लेषण जारी…",
    noteCausal:"कारणात्मक अनुमान मान्यताओं, डेटा गुणवत्ता और मॉडल पर निर्भर हैं।",
    segmentAnalysis:"ग्राहक समूह विश्लेषण", segmentVisual:"समूह आकार और खर्च क्लस्टर की तुलना",
    runClustering:"क्लस्टरिंग चलाएँ", regionalGroups:"क्षेत्रीय समूह", customerRegion:"क्षेत्र के अनुसार ग्राहक",
    planner:"प्रमोशन बजट योजनाकार", plannerDesc:"बजट और लक्षित ग्राहकों की संख्या निर्धारित करें",
    budget:"बजट (₹)", targetCustomers:"लक्षित ग्राहक", calculate:"सुझाव तैयार करें",
    calculating:"गणना जारी…", decisionNote:"यह निर्णय सहायता है। अभियान से पहले सीमाओं की जाँच करें।",
    uploadTitle:"ग्राहक डेटा अपलोड करें", uploadDesc:"CSV फ़ाइल चुनें। अपलोड किया गया डेटा विश्लेषण के लिए सक्रिय होगा।",
    chooseCSV:"CSV चुनें", rows:"पंक्तियाँ", positive:"सकारात्मक परिणाम", outcomeRate:"परिणाम दर",
    columns:"कॉलम", variables:"वेरिएबल", fields:"डेटासेट फ़ील्ड", fieldDesc:"उपलब्ध कॉलम",
    footer:"© 2026 EconoCausal", footerText:"डेटा समझें। बेहतर निर्णय लें।",
    apiConnected:"API कनेक्टेड", apiOffline:"API ऑफ़लाइन", research:"रिसर्च कार्यस्थान",
    loadError:"डैशबोर्ड डेटा लोड नहीं हुआ। /dashboard-data जाँचें।",
    apiError:"API उपलब्ध नहीं। पोर्ट 8000 पर FastAPI शुरू करें।", requestError:"अनुरोध विफल",
    analysisSummary:"विश्लेषण सारांश", available:"उपलब्ध", items:"आइटम",
    noChart:"चार्ट डेटा उपलब्ध नहीं। डेटासेट या रीफ़्रेश जाँचें।",
    language:"भाषा", english:"English", hindi:"हिन्दी",
    advanced:"उन्नत कारणात्मक विश्लेषण"
  }
};

function Card({ title, subtitle, children, action }) {
  return <article className="chartcard"><div className="charthead"><div><h3>{title}</h3>{subtitle && <p>{subtitle}</p>}</div>{action}</div>{children}</article>;
}
function ChartEmpty({ message }) {
  return <div className="chartempty">{message}</div>;
}
function ResultView({ result, t }) {
  const entries = Object.entries(result || {}).filter(([k, v]) => !["detail", "message"].includes(k) && v != null);
  return <div className="resultbox"><h4>{t("analysisSummary")}</h4><div className="resultgrid">
    {entries.map(([k, v]) => <div key={k}><small>{k.replaceAll("_", " ")}</small><b>{typeof v === "object" ? Array.isArray(v) ? `${v.length} ${t("items")}` : t("available") : String(v)}</b></div>)}
  </div><p>Detailed outputs are summarized here in a readable format. Values depend on the selected dataset.</p></div>;
}

export default function App() {
  const [page, P] = useState("Overview");
  const [language, setLanguage] = useState("en");
  const [data, D] = useState({});
  const [online, O] = useState(false);
  const [busy, B] = useState(false);
  const [err, E] = useState("");
  const [result, R] = useState(null);
  const [budget, S] = useState(50000);
  const [customers, C] = useState(5000);

  const t = (key) => translations[language][key] || translations.en[key] || key;
  const nav = [["Overview", LayoutDashboard], ["Causal analysis", BrainCircuit], ["Advanced causal", Activity], ["Segments", Users], ["Optimization", Wallet], ["Dataset", Database]];

  async function load() {
    B(true); E("");
    try {
      const [h, s] = await Promise.all([health(), summary()]);
      O(h.status === 200);
      D(s.data || {});
      try {
        const v = await dashboardData();
        D((prev) => ({ ...prev, ...(s.data || {}), ...(v.data || {}) }));
      } catch (dashboardError) {
        console.warn("Dashboard data endpoint failed:", dashboardError);
        E(dashboardError.response?.data?.detail || t("loadError"));
      }
    } catch (e) {
      O(false);
      E(e.response?.data?.detail || t("apiError"));
    } finally { B(false); }
  }
  useEffect(() => { load(); }, []);

  async function run(fn) {
    B(true); E(""); R(null);
    try { const r = await fn(); R(r.data ?? r); }
    catch (e) { E(e.response?.data?.detail || t("requestError")); }
    finally { B(false); }
  }

  const ageBins = (Array.isArray(data.age_distribution) ? data.age_distribution : []).map((item) => ({
    age: String(item.age ?? item.age_group ?? "Unknown"),
    customers: Number(item.customers ?? item.count ?? 0),
    purchasers: Number(item.purchasers ?? 0),
  }));
  const normalizeGroups = (items, key) => (Array.isArray(items) ? items : []).map((item) => ({
    name: String(item.name ?? item[key] ?? item.label ?? "Unknown"),
    count: Number(item.count ?? item.customers ?? item.value ?? 0),
  }));
  const segmentData = normalizeGroups(data.segment_distribution, "segment");
  const regionData = normalizeGroups(data.region_distribution, "region");
  const seasonData = normalizeGroups(data.season_distribution, "season");
  const purchaseData = (Array.isArray(data.purchase_distribution) ? data.purchase_distribution : []).map((item) => ({
    name: String(item.name ?? item.label ?? "Unknown"),
    value: Number(item.value ?? item.count ?? item.customers ?? 0),
  }));
  const total = Number(data.rows ?? data.total_customers ?? data.customers ?? 0);
  const purchaser = Number(data.purchasers ?? data.purchased_customers ?? 0);
  const purchaseRate = data.overall_purchase_rate != null ? Number(data.overall_purchase_rate) / 100 :
    data.purchase_rate != null ? (Number(data.purchase_rate) > 1 ? Number(data.purchase_rate) / 100 : Number(data.purchase_rate)) :
    total ? purchaser / total : null;

  return <div className="shell">
    <aside>
      <div className="logo"><span><Leaf /></span><b>Econo<span>Causal</span></b></div>
      <small className="navcap">WORKSPACE</small>
      {nav.map(([n, I]) => <button key={n} className={"nav " + (page === n ? "sel" : "")} onClick={() => { P(n); R(null); }}>
        <I size={18} /><span>{n === "Advanced causal" ? t("Advanced causal") : t(n)}</span>
      </button>)}
      <div className="sidefoot"><i className={online ? "green" : "orange"} /><div><b>{online ? t("apiConnected") : t("apiOffline")}</b><small>{t("research")}</small></div></div>
    </aside>
    <main>
      <header><span>{t("workspace")} / <b>{page === "Advanced causal" ? t("Advanced causal") : t(page)}</b></span><div>
        <span className={"status " + (online ? "ok" : "no")}><i /> {online ? t("connected") : t("offline")}</span>
        <label className="language-picker" title={t("language")}><Languages size={15}/><select value={language} onChange={(e) => setLanguage(e.target.value)} aria-label={t("language")}><option value="en">English</option><option value="hi">हिन्दी</option></select></label>
        <button className="refresh" onClick={load} disabled={busy}><RefreshCw size={16}/></button><div className="avatar">EC</div>
      </div></header>
      <section>
        <div className="heading"><div><small>{t("platform")}</small><h1>{page === "Advanced causal" ? t("Advanced causal") : t(page)}</h1>
          <p>{({ Overview: t("overviewDesc"), "Causal analysis": t("causalDesc"), "Advanced causal": t("advanced"), Segments: t("segmentsDesc"), Optimization: t("optimizationDesc"), Dataset: t("datasetDesc") })[page]}</p>
        </div><button className="btn light" onClick={load}><RefreshCw size={15}/> {t("refresh")}</button></div>
        {err && <div className="error">{err}</div>}

        {page === "Overview" && <>
          <div className="hero"><div><small>{t("overviewHero")}</small><h2>{t("heroTitle")}<br/><em>{t("heroTitle2")}</em></h2>
            <p>{t("heroDesc")}</p><button className="btn white" onClick={() => P("Causal analysis")}>{t("explore")}</button>
          </div><div className="heroBadge"><TrendingUp size={28}/><b>{pct(purchaseRate)}</b><small>{t("overallRate")}</small></div></div>
          <div className="sectiontitle"><div><h3>{t("datasetSummary")}</h3><p>{t("keyNumbers")}</p></div><small className="tag">● {online ? t("liveData") : t("noConnection")}</small></div>
          <div className="metrics">{[
            [t("totalCustomers"), fmt(total), t("customerRecords"), Users],
            [t("purchasers"), fmt(purchaser), t("purchasedCustomers"), Activity],
            [t("purchaseRate"), pct(purchaseRate), t("sharePurchasing"), TrendingUp],
            [t("dataFields"), fmt(data.columns?.length ?? data.total_columns), t("availableVariables"), Database],
          ].map(([a,b,c,I]) => <article key={a}><div className="metrichead">{a}<span><I size={17}/></span></div><strong>{b}</strong><small>{c}</small></article>)}</div>
          <div className="chartgrid">
            <Card title={t("ageDistribution")} subtitle={t("byAge")}>{ageBins.length ? <ResponsiveContainer width="100%" height={250}><BarChart data={ageBins}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="age"/><YAxis/><Tooltip/><Bar dataKey="customers" name={t("totalCustomers")} fill="#6877e8" radius={[6,6,0,0]}/></BarChart></ResponsiveContainer> : <ChartEmpty message={t("noChart")}/>}</Card>
            <Card title={t("customerGroups")} subtitle={t("bySegment")}>{segmentData.length ? <ResponsiveContainer width="100%" height={250}><BarChart data={segmentData} layout="vertical" margin={{left:8}}><CartesianGrid strokeDasharray="3 3" horizontal={false}/><XAxis type="number"/><YAxis type="category" dataKey="name" width={95}/><Tooltip/><Bar dataKey="count" name={t("totalCustomers")} fill="#35b8a0" radius={[0,6,6,0]}/></BarChart></ResponsiveContainer> : <ChartEmpty message={t("noChart")}/>}</Card>
            <Card title={t("purchaseOverview")} subtitle={t("purchaseCompare")}>{purchaseData.length ? <ResponsiveContainer width="100%" height={250}><PieChart><Pie data={purchaseData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={4} label>{purchaseData.map((x,i) => <Cell key={x.name} fill={COLORS[i % COLORS.length]}/>)}</Pie><Tooltip/><Legend/></PieChart></ResponsiveContainer> : <ChartEmpty message={t("noChart")}/>}</Card>
            <Card title={t("agePurchases")} subtitle={t("agePurchasesDesc")}>{ageBins.length ? <ResponsiveContainer width="100%" height={250}><LineChart data={ageBins}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="age"/><YAxis/><Tooltip/><Legend/><Line type="monotone" dataKey="customers" name={t("totalCustomers")} stroke="#6877e8" strokeWidth={2}/><Line type="monotone" dataKey="purchasers" name={t("purchasers")} stroke="#35b8a0" strokeWidth={2}/></LineChart></ResponsiveContainer> : <ChartEmpty message={t("noChart")}/>}</Card>
            <Card title={t("region")} subtitle={t("topRegions")}>{regionData.length ? <ResponsiveContainer width="100%" height={250}><BarChart data={regionData}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="name"/><YAxis/><Tooltip/><Bar dataKey="count" name={t("totalCustomers")} fill="#9b78dc" radius={[6,6,0,0]}/></BarChart></ResponsiveContainer> : <ChartEmpty message={t("noChart")}/>}</Card>
            <Card title={t("seasonal")} subtitle={t("bySeason")}>{seasonData.length ? <ResponsiveContainer width="100%" height={250}><AreaChart data={seasonData}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="name"/><YAxis/><Tooltip/><Area type="monotone" dataKey="count" name={t("totalCustomers")} stroke="#f4a45d" fill="#f4a45d" fillOpacity={.2}/></AreaChart></ResponsiveContainer> : <ChartEmpty message={t("noChart")}/>}</Card>
          </div>
          <div className="twocol"><article><h3>{t("next")}</h3><p className="sub">{t("choose")}</p>
            {[["Causal analysis", "estimate", BrainCircuit], ["Segments", "compare", Users], ["Optimization", "budgetRec", Wallet], ["Advanced causal", "advanced", Activity]].map(([n,d,I]) => <button className="quick" key={n} onClick={() => P(n)}><I size={18}/><b>{t(n)}<small>{t(d)}</small></b>↗</button>)}
          </article><article><h3>{t("guide")}</h3><p className="sub">{t("simpleGuide")}</p><div className="guide"><b>{t("counts")}</b><span>{t("countExplain")}</span></div><div className="guide"><b>{t("purchaseRate")}</b><span>{t("rateExplain")}</span></div><div className="guide"><b>{t("Causal analysis")}</b><span>{t("causalExplain")}</span></div></article></div>
        </>}

        {page === "Causal analysis" && <article className="panel"><h3>{t("impact")}</h3><p className="sub">{t("impactDesc")}</p><button className="btn primary" onClick={() => run(segments)} disabled={busy}><BrainCircuit size={16}/>{busy ? t("analyzing") : t("runCausal")}</button>{result && <ResultView result={result} t={t}/>}<div className="note">{t("noteCausal")}</div></article>}

        {page === "Advanced causal" && <AdvancedCausal language={language}/>}

        {page === "Segments" && <><article className="panel"><div className="paneltop"><div><h3>{t("segmentAnalysis")}</h3><p className="sub">{t("segmentVisual")}</p></div><button className="btn primary" onClick={() => run(clusters)} disabled={busy}>{busy ? t("analyzing") : t("runClustering")}</button></div>{result && <ResultView result={result} t={t}/>}</article>
          <div className="chartgrid"><Card title={t("customerGroups")} subtitle={t("bySegment")}>{segmentData.length ? <ResponsiveContainer width="100%" height={280}><BarChart data={segmentData}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="name"/><YAxis/><Tooltip/><Bar dataKey="count" name={t("totalCustomers")} fill="#6877e8" radius={[6,6,0,0]}/></BarChart></ResponsiveContainer> : <ChartEmpty message={t("noChart")}/>}</Card>
          <Card title={t("regionalGroups")} subtitle={t("customerRegion")}>{regionData.length ? <ResponsiveContainer width="100%" height={280}><BarChart data={regionData}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="name"/><YAxis/><Tooltip/><Bar dataKey="count" name={t("totalCustomers")} fill="#35b8a0" radius={[6,6,0,0]}/></BarChart></ResponsiveContainer> : <ChartEmpty message={t("noChart")}/>}</Card></div></>}

        {page === "Optimization" && <article className="panel"><h3>{t("planner")}</h3><p className="sub">{t("plannerDesc")}</p><div className="inputs"><label>{t("budget")}<input type="number" min="0" value={budget} onChange={e => S(e.target.value)}/></label><label>{t("targetCustomers")}<input type="number" min="1" value={customers} onChange={e => C(e.target.value)}/></label></div><button className="btn primary" onClick={() => run(() => optimize(budget, customers))} disabled={busy}>{busy ? t("calculating") : t("calculate")}</button>{result && <ResultView result={result} t={t}/>}<div className="note">{t("decisionNote")}</div></article>}

        {page === "Dataset" && <><article className="upload"><Database size={30}/><h3>{t("uploadTitle")}</h3><p>{t("uploadDesc")}</p><label className="btn primary"><Upload size={16}/> {t("chooseCSV")}<input hidden type="file" accept=".csv" onChange={async e => {const file = e.target.files?.[0]; if (!file) return; B(true); E(""); try {await upload(file); R(null); await load();} catch (x) {E(x.response?.data?.detail || "Upload failed");} finally {B(false); e.target.value = "";}}}/></label></article>
          <div className="metrics">{[[t("rows"),fmt(total),t("customerRecords")],[t("purchasers"),fmt(purchaser),t("positive")],[t("purchaseRate"),pct(purchaseRate),t("outcomeRate")],[t("columns"),fmt(data.columns?.length ?? data.total_columns),t("variables")]].map(([a,b,c]) => <article key={a}><div className="metrichead">{a}</div><strong>{b}</strong><small>{c}</small></article>)}</div>
          <Card title={t("fields")} subtitle={t("fieldDesc")}>{Array.isArray(data.columns) ? <div className="fieldlist">{data.columns.map(x => <span key={x}>{x}</span>)}</div> : <ChartEmpty message={t("noChart")}/>}</Card></>}

        <footer>{t("footer")} <span>● {t("footerText")}</span></footer>
      </section>
    </main>
  </div>;
}
