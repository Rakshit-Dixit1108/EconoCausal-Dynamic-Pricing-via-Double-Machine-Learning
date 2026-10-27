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
