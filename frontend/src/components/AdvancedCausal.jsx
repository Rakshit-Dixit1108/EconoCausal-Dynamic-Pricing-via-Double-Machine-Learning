import { useEffect, useState } from "react";
import {
  advancedMultilevel, advancedPropensity, advancedDiagnostics, advancedRefutation
} from "../api";
import "./AdvancedCausal.css";

const copy = {
  en: {
    title:"Advanced Causal Analysis", intro:"Multilevel effects, propensity scores, treatment balance and robustness checks.",
    multilevel:"Multilevel Discount Impact", multilevelSub:"Estimated purchase-probability effect relative to 0% discount.",
    propensity:"Propensity Score Summary", propensitySub:"Average predicted probability of the actual discount group.",
    diagnostics:"Treatment Balance Diagnostics", diagnosticsSub:"Standardized mean differences (SMD) against the 0% control group.",
    refutation:"Causal Refutation", refutationSub:"DoWhy robustness checks for the binary discount treatment.",
    discount:"Discount", control:"Control", effect:"Effect", pp:"Percentage points", customers:"Customers",
    mean:"Mean propensity", min:"Minimum", max:"Maximum", feature:"Feature", smd:"SMD",
    absSmd:"Absolute SMD", status:"Status", balanced:"Balanced", unbalanced:"Potential imbalance",
    loading:"Loading advanced causal analysis…", error:"Could not load advanced causal analysis.",
    runFirst:"Ensure backend is running and all four analyses have been executed.",
    missing:"No result rows found. Run the corresponding analysis script first.",
    ppNote:"pp = percentage points. Multilevel model inference may be unreliable if its covariance matrix is underdetermined.",
    notProof:"Refutation tests are robustness diagnostics; they do not prove causal validity."
  },
  hi: {
    title:"उन्नत कारणात्मक विश्लेषण", intro:"मल्टीलेवल प्रभाव, प्रोपेन्सिटी स्कोर, ट्रीटमेंट संतुलन और robustness जाँच।",
    multilevel:"मल्टीलेवल डिस्काउंट प्रभाव", multilevelSub:"0% डिस्काउंट की तुलना में खरीद संभावना पर अनुमानित प्रभाव।",
    propensity:"प्रोपेन्सिटी स्कोर सारांश", propensitySub:"वास्तविक डिस्काउंट समूह की औसत अनुमानित संभावना।",
    diagnostics:"ट्रीटमेंट संतुलन डायग्नोस्टिक्स", diagnosticsSub:"0% कंट्रोल समूह के विरुद्ध Standardized Mean Difference (SMD)।",
    refutation:"कारणात्मक Refutation", refutationSub:"बाइनरी डिस्काउंट ट्रीटमेंट के लिए DoWhy robustness जाँच।",
    discount:"डिस्काउंट", control:"कंट्रोल", effect:"प्रभाव", pp:"प्रतिशत अंक", customers:"ग्राहक",
    mean:"औसत प्रोपेन्सिटी", min:"न्यूनतम", max:"अधिकतम", feature:"फ़ीचर", smd:"SMD",
    absSmd:"Absolute SMD", status:"स्थिति", balanced:"संतुलित", unbalanced:"संभावित असंतुलन",
    loading:"उन्नत कारणात्मक विश्लेषण लोड हो रहा है…", error:"विश्लेषण लोड नहीं हो सका।",
    runFirst:"Backend चालू करें और चारों विश्लेषण स्क्रिप्ट चलाएँ।",
    missing:"परिणाम नहीं मिले। पहले संबंधित विश्लेषण स्क्रिप्ट चलाएँ।",
    ppNote:"pp = प्रतिशत अंक। Covariance matrix underdetermined होने पर multilevel inference अविश्वसनीय हो सकता है।",
    notProof:"Refutation परीक्षण robustness जाँच हैं; ये causal validity का प्रमाण नहीं हैं।"
  }
};

const n = (v, digits=3) => v == null || Number.isNaN(Number(v)) ? "—" : Number(v).toFixed(digits);
const pick = (obj, ...keys) => {
  for (const key of keys) if (obj?.[key] != null) return obj[key];
  return "—";
};

function Table({ headers, rows, empty }) {
  return <div className="advanced-table-wrap">{rows.length ? <table className="advanced-table"><thead><tr>{headers.map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>{rows}</tbody></table> : <div className="advanced-empty">{empty}</div>}</div>;
}

export default function AdvancedCausal({ language="en" }) {
  const t = (key) => copy[language]?.[key] || copy.en[key] || key;
  const [multilevel,setMultilevel] = useState([]);
  const [propensity,setPropensity] = useState([]);
  const [diagnostics,setDiagnostics] = useState([]);
  const [refutation,setRefutation] = useState("");
  const [loading,setLoading] = useState(true);
  const [error,setError] = useState("");

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true); setError("");
      try {
        const [m,p,d,r] = await Promise.all([
          advancedMultilevel(), advancedPropensity(), advancedDiagnostics(), advancedRefutation()
        ]);
        if (!active) return;
        setMultilevel(Array.isArray(m.data) ? m.data : []);
        setPropensity(Array.isArray(p.data) ? p.data : []);
        setDiagnostics(Array.isArray(d.data) ? d.data : []);
        setRefutation(r.data?.results || "");
      } catch (e) {
        if (active) setError(e.response?.data?.detail || e.message || t("error"));
      } finally { if (active) setLoading(false); }
    }
    load();
    return () => { active = false; };
  }, []);

  if (loading) return <div className="advanced-loading">{t("loading")}</div>;
  if (error) return <div className="advanced-error"><h3>{t("title")}</h3><p>{error}</p><p>{t("runFirst")}</p></div>;

  return <div className="advanced-causal">
    <div className="advanced-header"><div><span className="advanced-eyebrow">ECONOCAUSAL / RESEARCH</span><h2>{t("title")}</h2><p>{t("intro")}</p></div><span className="advanced-status">● Loaded</span></div>

    <section className="advanced-section">
      <h3>{t("multilevel")}</h3><p className="advanced-subtitle">{t("multilevelSub")}</p>
      <div className="advanced-grid">{multilevel.map((x,i)=><div className="advanced-card" key={`${x.discount_percent}-${i}`}><span>{pick(x,"discount_percent")}% {t("discount")}</span><strong>{n(pick(x,"effect_percentage_points"),2)} pp</strong><small>{t("control")}: {pick(x,"control_discount")}%</small></div>)}</div>
      <Table empty={t("missing")} headers={[t("discount"),t("control"),t("effect"),t("pp")]} rows={multilevel.map((x,i)=><tr key={i}><td>{pick(x,"discount_percent")}%</td><td>{pick(x,"control_discount")}%</td><td>{n(pick(x,"estimated_purchase_effect"),5)}</td><td>{n(pick(x,"effect_percentage_points"),2)}</td></tr>)}/>
      <p className="advanced-note">{t("ppNote")}</p>
    </section>

    <section className="advanced-section"><h3>{t("propensity")}</h3><p className="advanced-subtitle">{t("propensitySub")}</p>
      <Table empty={t("missing")} headers={[t("discount"),t("customers"),t("mean"),t("min"),t("max")]} rows={propensity.map((x,i)=><tr key={i}><td>{pick(x,"actual_discount")}%</td><td>{pick(x,"count")}</td><td>{n(pick(x,"mean","mean_propensity"),4)}</td><td>{n(pick(x,"min","minimum"),4)}</td><td>{n(pick(x,"max","maximum"),4)}</td></tr>)}/>
    </section>

    <section className="advanced-section"><h3>{t("diagnostics")}</h3><p className="advanced-subtitle">{t("diagnosticsSub")}</p>
      <Table empty={t("missing")} headers={[t("discount"),t("feature"),t("smd"),t("absSmd"),t("status")]} rows={diagnostics.map((x,i)=>{
        const smd=pick(x,"smd","standardized_mean_difference");
        const abs=pick(x,"absolute_smd","abs_smd");
        const status=pick(x,"balance_status","status");
        const balanced=String(status).toLowerCase().includes("balanc") && !String(status).toLowerCase().includes("imbalance");
        return <tr key={i}><td>{pick(x,"discount_level","discount_percent","treatment")}%</td><td>{pick(x,"feature","variable","column")}</td><td>{n(smd,3)}</td><td>{n(abs,3)}</td><td><span className={balanced?"balance-good":"balance-warning"}>{status}</span></td></tr>;
      })}/>
    </section>

    <section className="advanced-section"><h3>{t("refutation")}</h3><p className="advanced-subtitle">{t("refutationSub")}</p><pre className="refutation-output">{refutation || t("missing")}</pre><p className="advanced-note">{t("notProof")}</p></section>
  </div>;
}
