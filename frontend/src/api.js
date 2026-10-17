const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

async function apiRequest(endpoint) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`);
  } catch {
    throw new Error(
      "Cannot connect to the EconoCausal backend. " +
      "Make sure FastAPI is running on port 8000."
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
      // Keep the default error message if the response is not JSON.
    }

    throw new Error(message);
  }

  return response.json();
}

export function getHealth() {
  return apiRequest("/health");
}

export function getDataSummary() {
  return apiRequest("/data-summary");
}

export function getOptimization(options = {}) {
  const params = new URLSearchParams();

  if (options.budgetInr !== undefined && options.budgetInr !== null) {
    params.set("budget_inr", String(options.budgetInr));
  }

  if (options.customers !== undefined && options.customers !== null) {
    params.set("customers", String(options.customers));
  }

  const query = params.toString();

  return apiRequest(`/optimization${query ? `?${query}` : ""}`);
}
