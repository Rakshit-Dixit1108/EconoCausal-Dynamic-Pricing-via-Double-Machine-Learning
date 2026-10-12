# EconoCausal Frontend

Modern React + Vite dashboard starter for **EconoCausal: Dynamic Pricing via Double Machine Learning**.

## Requirements
- Node.js 18+ (20+ recommended)
- npm
- Optional: running Python backend at `http://127.0.0.1:8000`

## Run it
```bash
npm install
npm run dev
```
Open the URL printed by Vite, usually `http://localhost:5173`.

## Backend integration
Set `VITE_API_BASE_URL` in `.env` to your API base URL. The UI attempts:
- `POST /api/analyze` with `multipart/form-data` field `file`
- `POST /api/optimize` with JSON `{ budget, max_discount, objective }`
- `GET /api/health`

If the API is unavailable, the frontend remains usable in **demo mode** with clearly labeled sample/simulated data. Demo metrics are not actual model results. Replace/adjust endpoint paths in `src/api.js` to match your backend.

## CSV expectations
The frontend accepts a CSV file and previews its headers and rows. The backend should validate your dataset and identify fields such as:
- customer identifier (optional)
- outcome / purchase indicator
- treatment / discount received
- revenue / order value
- confounders / customer features

The exact schema should be agreed by the team before implementing model training.

## Build
```bash
npm run build
npm run preview
```

## Suggested API response
`POST /api/analyze` can return:
```json
{
  "metrics": {
    "customers": 1200,
    "purchaseRate": 0.184,
    "averageDiscount": 0.09,
    "revenueImprovement": 0.072
  },
  "effectDistribution": [{"effect": -0.02, "count": 8}],
  "discountCurve": [{"discount": 0, "purchaseRate": 0.12}],
  "beneficiaries": [{"customerId": "C-1001", "uplift": 0.08, "recommendedDiscount": 0.1}],
  "diagnostics": {"method": "Double Machine Learning", "status": "complete"}
}
```
The dashboard is a frontend shell, not a causal model. Real causal estimates require a backend and a suitable dataset.
