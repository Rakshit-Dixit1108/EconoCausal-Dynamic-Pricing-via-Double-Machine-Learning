
const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

async function apiRequest(endpoint, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, options);
  } catch {
    throw new Error(
      "Cannot connect to the EconoCausal backend. " +
      "Make sure FastAPI is running and the API URL is correct."
    );
  }

  if (!response.ok) {
    let message = `API request failed (${response.status})`;

    try {
      const errorData = await response.json();

      if (errorData.detail) {
        message =
          typeof errorData.detail === "string"
            ? errorData.detail
            : JSON.stringify(errorData.detail);
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(message);
  }

  return response.json();
}

// Check whether the backend is running.
export function getHealth() {
  return apiRequest("/health");
}

// Get a summary of the currently active dataset.
export function getDataSummary() {
  return apiRequest("/data-summary");
}

// Upload a CSV file and activate it after backend validation.
export function uploadCsv(file) {
  const formData = new FormData();
  formData.append("file", file);

  return apiRequest("/upload-csv", {
    method: "POST",
    body: formData,
  });
}

// Compare observed discount levels.
export function getOptimization(options = {}) {
  const params = new URLSearchParams();

  if (options.budgetInr != null) {
    params.set("budget_inr", String(options.budgetInr));
  }

  if (options.customers != null) {
    params.set("customers", String(options.customers));
  }

  const query = params.toString();

  return apiRequest(
    `/optimization${query ? `?${query}` : ""}`
  );
}

// Group-level causal effect estimates.
// Note: the current backend may use its configured dataset
// rather than the currently uploaded dataset.
export function getSegmentEffects() {
  return apiRequest("/segment-effects");
}

// Customer spending clusters.
// Note: the current backend may use its configured dataset
// rather than the currently uploaded dataset.
export function getSpendingClusters() {
  return apiRequest("/spending-clusters");
}
