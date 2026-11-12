import axios from "axios";

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000",
  timeout: 120000,
});

export const summary = () => api.get("/data-summary");
export const health = () => api.get("/health");

export const optimize = (budget, customers) =>
  api.get("/optimization", {
    params: {
      budget_inr: budget,
      customers,
    },
  });

export const clusters = () => api.get("/spending-clusters");
export const segments = () => api.get("/segment-effects");

export const upload = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/upload-csv", formData);
};

export const dashboardData = () => api.get("/dashboard-data");

// Advanced causal analysis
export const advancedMultilevel = () =>
  api.get("/advanced-causal/multilevel");

export const advancedPropensity = () =>
  api.get("/advanced-causal/propensity");

export const advancedDiagnostics = () =>
  api.get("/advanced-causal/diagnostics");

export const advancedRefutation = () =>
  api.get("/advanced-causal/refutation");

export default api;
