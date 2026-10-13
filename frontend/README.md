# EconoCausal Frontend

A responsive React + Vite analytics dashboard inspired by the supplied EconoCausal reference image.

## Requirements
- Node.js 18.18+ (Node.js 20 LTS recommended)
- npm

## Run locally
1. Extract this ZIP.
2. Open the extracted `EconoCausal-Frontend` folder in VS Code.
3. Open Terminal → New Terminal.
4. Run:

   ```bash
   npm install
   npm run dev
   ```

5. Open the local URL Vite prints (normally `http://localhost:5173`).

## Build for production
```bash
npm run build
npm run preview
```

## Working interactions
- Responsive desktop/tablet/mobile layout.
- English, Spanish, and Hindi language switch.
- Sidebar and top navigation switch between Analytics, Campaigns, Models, Settings, and Reporting.
- Segment search filters customer groups.
- Date menu changes the displayed reporting period.
- Notification popover.
- Settings form updates the displayed budget and stores threshold state for the current session.
- CSV export downloads the displayed demo segment data.
- Charts render using Recharts.

## Important data note
This is a functional **frontend prototype** with illustrative demo metrics modeled after the reference image. It is not connected to a trained causal model or a live backend, and it must not be presented as validated business results. The model screen explains the planned Double Machine Learning workflow. Connect your project's Python/FastAPI endpoints before using real estimates.

## Language switch
Use EN (English), ES (Spanish), or HI (Hindi) in the top-right corner. Text for primary dashboard/navigation/actions is translated. Some technical model labels remain in English because they are standard ML terminology.
