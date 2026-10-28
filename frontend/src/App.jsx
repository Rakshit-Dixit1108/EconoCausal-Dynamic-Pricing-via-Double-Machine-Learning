import React, { useEffect, useMemo, useState } from "react";
import {
  getHealth,
  getDataSummary,
  getOptimization,
  uploadCsv,
} from "./api";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import "./styles.css";

const money = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));

const number = (value) => new Intl.NumberFormat("en-IN").format(Number(value || 0));

export default function App() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [optimization, setOptimization] = useState(null);
  const [budget, setBudget] = useState("12000");
  const [customers, setCustomers] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [backendOnline, setBackendOnline] = useState(false);
  const [activeFileName, setActiveFileName] = useState("Default dataset");

  async function refreshAnalysis(options = {}) {
    setBusy(true);
    setError("");
    try {
      const [summaryResult, optimizationResult] = await Promise.all([
        getDataSummary(),
        getOptimization({
          budgetInr: options.budgetInr ?? (budget === "" ? undefined : Number(budget)),
          customers: options.customers ?? (customers === "" ? undefined : Number(customers)),
        }),
      ]);
      setSummary(summaryResult.data || summaryResult);
      setOptimization(optimizationResult);
      setStatus("Analysis refreshed from the active backend dataset.");
    } catch (err) {
      setError(err.message || "Unable to load analysis.");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    getHealth()
      .then(() => setBackendOnline(true))
      .catch(() => setBackendOnline(false));
    refreshAnalysis();
    // Initial load only; subsequent refreshes are user-triggered.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleAnalyze(event) {
    event.preventDefault();
    setError("");
    setStatus("");
    if (!file) {
      setError("Choose a CSV file before analyzing.");
      return;
    }

    setBusy(true);
    try {
      const uploaded = await uploadCsv(file);
      setActiveFileName(uploaded.filename || file.name);
      const [summaryResult, optimizationResult] = await Promise.all([
        getDataSummary(),
        getOptimization({
          budgetInr: budget === "" ? undefined : Number(budget),
          customers: customers === "" ? undefined : Number(customers),
        }),
      ]);
      setSummary(summaryResult.data || summaryResult);
      setOptimization(optimizationResult);
      setStatus(
        `Uploaded and analyzed ${uploaded.filename || file.name}. ` +
        `${number(uploaded.rows)} rows passed backend validation.`
      );
    } catch (err) {
      setError(err.message || "Upload or analysis failed.");
    } finally {
      setBusy(false);
    }
  }

  async function handleRefresh() {
    await refreshAnalysis();
  }

  const discountRows = useMemo(() => {
    const rows = optimization?.discount_levels || [];
    return rows.map((row) => ({
      ...row,
      label: `${Number(row.discount_percent)}%`,
      purchaseRate: Number(row.purchase_rate_percent || 0),
      avgNetRevenue: Number(row.avg_net_revenue_inr || 0),
      avgDiscountCost: Number(row.avg_discount_cost_inr || 0),
    }));
  }, [optimization]);

  const missingEntries = Object.entries(summary?.missing_values || {});
  const missingTotal = missingEntries.reduce(
    (total, [, count]) => total + Number(count || 0),
    0
  );

  const recommendation = optimization?.recommendation;
  const datasetRows = summary?.rows ?? optimization?.customers_evaluated ?? 0;
  const datasetColumns = summary?.columns ?? "—";
  const groups = summary?.discount_groups || {};
  const purchaseRates = summary?.purchase_rate_by_discount || {};

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark"><span>E</span><span>C</span></div>
          <span className="brand-name">EconoCausal</span>
        </div>
        <div className="top-actions">
          <span className={`status-pill ${backendOnline ? "online" : "offline"}`}>
            <i /> {backendOnline ? "Backend connected" : "Backend unavailable"}
          </span>
          <button className="secondary-btn" onClick={handleRefresh} disabled={busy}>
            Refresh analysis
          </button>
        </div>
      </header>

      <main className="main-content">
        <div className="page-heading">
          <div>
            <div className="eyebrow">DATA ANALYTICS / DYNAMIC PRICING</div>
            <h1>Dataset analysis dashboard</h1>
            <p className="subtitle">
              Upload customer data to refresh the dataset summary and observed discount analysis.
            </p>
          </div>
        </div>

        <section className="panel" style={{ padding: 20, marginBottom: 20 }}>
          <div className="panel-head">
            <div>
              <h2>Import and analyze a CSV</h2>
              <p>CSV is activated only if it passes the backend validation rules.</p>
            </div>
          </div>
          <form onSubmit={handleAnalyze} className="upload-form">
            <label className="upload-field">
              <span>Customer dataset (.csv)</span>
              <input
                type="file"
                accept=".csv,text/csv"
                onChange={(event) => setFile(event.target.files?.[0] || null)}
              />
            </label>
            <label className="upload-field">
              <span>Discount budget (₹)</span>
              <input
                type="number"
                min="0"
                value={budget}
                onChange={(event) => setBudget(event.target.value)}
                placeholder="12000"
              />
            </label>
            <label className="upload-field">
              <span>Customers to evaluate (optional)</span>
              <input
                type="number"
                min="1"
                value={customers}
                onChange={(event) => setCustomers(event.target.value)}
                placeholder="All dataset rows"
              />
            </label>
            <button className="primary-btn" type="submit" disabled={busy}>
              {busy ? "Analyzing…" : "Upload & analyze"}
            </button>
          </form>
          <div className="dataset-meta">
            <span><strong>Active dataset:</strong> {activeFileName}</span>
            {file && <span><strong>Selected:</strong> {file.name}</span>}
          </div>
          {status && <p className="notice success-notice" role="status">{status}</p>}
          {error && <p className="notice error-notice" role="alert">{error}</p>}
          {busy && <p className="muted">Waiting for the backend to validate and analyze the dataset…</p>}
        </section>

        <section className="kpi-grid">
          <div className="panel kpi-card">
            <div className="kpi-top"><span>Customers analyzed</span></div>
            <div className="kpi-value">{number(datasetRows)}</div>
            <div className="kpi-foot"><span>Rows in active dataset</span></div>
          </div>
          <div className="panel kpi-card">
            <div className="kpi-top"><span>Columns</span></div>
            <div className="kpi-value">{number(datasetColumns)}</div>
            <div className="kpi-foot"><span>Fields loaded</span></div>
          </div>
          <div className="panel kpi-card">
            <div className="kpi-top"><span>Missing values</span></div>
            <div className="kpi-value">{number(missingTotal)}</div>
            <div className="kpi-foot"><span>Reported by data summary</span></div>
          </div>
          <div className="panel kpi-card">
            <div className="kpi-top"><span>Discount levels</span></div>
            <div className="kpi-value">{number(discountRows.length)}</div>
            <div className="kpi-foot"><span>Observed levels returned by API</span></div>
          </div>
        </section>

        <section className="analytics-grid">
          <div className="panel chart-panel">
            <div className="panel-head">
              <div>
                <h2>Purchase rate by discount level</h2>
                <p>Observed purchase rates from the active dataset</p>
              </div>
            </div>
            <div className="chart-area">
              {discountRows.length ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={discountRows} margin={{ top: 10, right: 12, left: 0, bottom: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="label" />
                    <YAxis tickFormatter={(value) => `${value}%`} />
                    <Tooltip formatter={(value) => [`${Number(value).toFixed(2)}%`, "Purchase rate"]} />
                    <Bar dataKey="purchaseRate" name="Purchase rate" fill="#5ba6ff" radius={[5, 5, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="empty-state">No discount analysis data available yet. Upload a valid CSV or refresh analysis.</div>
              )}
            </div>
          </div>

          <div className="panel chart-panel">
            <div className="panel-head">
              <div>
                <h2>Average net revenue by discount</h2>
                <p>Observed net revenue, not profit or a causal estimate</p>
              </div>
            </div>
            <div className="chart-area">
              {discountRows.length ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={discountRows} margin={{ top: 10, right: 12, left: 8, bottom: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="label" />
                    <YAxis tickFormatter={(value) => `₹${Number(value).toLocaleString("en-IN")}`} />
                    <Tooltip formatter={(value) => [money(value), "Average net revenue"]} />
                    <Line type="monotone" dataKey="avgNetRevenue" name="Average net revenue" stroke="#70d4b0" strokeWidth={3} dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="empty-state">Revenue chart appears when the API returns discount-level results.</div>
              )}
            </div>
          </div>
        </section>

        <section className="analytics-grid">
          <div className="panel" style={{ padding: 20 }}>
            <div className="panel-head">
              <div><h2>Discount group counts</h2><p>Number of records in each treatment group</p></div>
            </div>
            {Object.keys(groups).length ? (
              <div className="simple-list">
                {Object.entries(groups).map(([group, count]) => (
                  <div className="simple-row" key={group}>
                    <span>{group === "1" ? "Received discount (1)" : "No discount (0)"}</span>
                    <strong>{number(count)}</strong>
                  </div>
                ))}
              </div>
            ) : <p className="muted">Discount group counts are not available.</p>}
          </div>

          <div className="panel" style={{ padding: 20 }}>
            <div className="panel-head">
              <div><h2>Recommendation</h2><p>Returned by the budget-aware endpoint</p></div>
            </div>
            {recommendation ? (
              <div className="recommendation">
                <div className="recommendation-value">{Number(recommendation.discount_percent).toFixed(1)}%</div>
                <p>Recommended observed discount level</p>
                <div className="simple-row"><span>Average net revenue</span><strong>{money(recommendation.avg_net_revenue_inr)}</strong></div>
                <div className="simple-row"><span>Estimated total discount cost</span><strong>{money(recommendation.estimated_total_discount_cost_inr)}</strong></div>
                <div className="simple-row"><span>Customers evaluated</span><strong>{number(recommendation.customers_evaluated)}</strong></div>
              </div>
            ) : <p className="muted">The API has not returned an eligible recommendation for the current inputs.</p>}
          </div>
        </section>

        <section className="panel" style={{ padding: 20, marginTop: 20 }}>
          <div className="panel-head">
            <div><h2>Data quality summary</h2><p>Missing-value counts returned by the backend</p></div>
          </div>
          {missingEntries.length ? (
            <div className="simple-list">
              {missingEntries.map(([column, count]) => (
                <div className="simple-row" key={column}>
                  <span>{column}</span><strong>{number(count)}</strong>
                </div>
              ))}
            </div>
          ) : <p className="muted">No column-level missing-value summary is available yet.</p>}
        </section>

        <section className="bottom-callout">
          <div>
            <strong>Interpret results carefully</strong>
            <p>
              These charts show observed discount comparisons. They do not prove that a discount caused a purchase.
              Individual causal-effect distributions and uplift curves are not shown because the current API does not return
              the customer-level predictions needed to calculate them.
            </p>
          </div>
        </section>
        <footer className="app-footer">
          <span>© 2026 EconoCausal</span>
          <span>{backendOnline ? "Connected to FastAPI" : "Waiting for API connection"}</span>
          <span>{busy ? "Analysis in progress" : "Dashboard values come from API responses"}</span>
        </footer>
      </main>
    </div>
  );
}
