export const demoMetrics = {
  customers: 2480,
  purchaseRate: 18.4,
  averageDiscount: 9.2,
  revenueImprovement: 7.6
}
export const discountCurve = [
  { discount: 0, purchaseRate: 11.8 },
  { discount: 5, purchaseRate: 13.1 },
  { discount: 10, purchaseRate: 16.7 },
  { discount: 15, purchaseRate: 18.2 },
  { discount: 20, purchaseRate: 18.9 },
  { discount: 25, purchaseRate: 19.1 },
  { discount: 30, purchaseRate: 19.0 }
]
export const effectDistribution = [
  { effect: -0.08, count: 4 }, { effect: -0.04, count: 11 },
  { effect: 0.00, count: 22 }, { effect: 0.04, count: 36 },
  { effect: 0.08, count: 47 }, { effect: 0.12, count: 39 },
  { effect: 0.16, count: 25 }, { effect: 0.20, count: 14 },
  { effect: 0.24, count: 7 }
]
export const initialRecommendations = [
  { id: 'C-1042', segment: 'Repeat buyer', uplift: 18.6, discount: 10, revenue: 420 },
  { id: 'C-1188', segment: 'At-risk', uplift: 16.2, discount: 15, revenue: 385 },
  { id: 'C-1204', segment: 'High intent', uplift: 14.9, discount: 10, revenue: 342 },
  { id: 'C-1327', segment: 'New customer', uplift: 12.4, discount: 5, revenue: 290 },
  { id: 'C-1450', segment: 'Repeat buyer', uplift: 11.8, discount: 10, revenue: 268 },
  { id: 'C-1512', segment: 'At-risk', uplift: 10.5, discount: 15, revenue: 244 }
]
export const strategies = [
  { name: 'No discount', conversion: 11.8, incrementalRevenue: 0, spend: 0 },
  { name: 'Blanket discount', conversion: 19.1, incrementalRevenue: 18200, spend: 14800 },
  { name: 'Targeted discount', conversion: 17.8, incrementalRevenue: 22400, spend: 7200 }
]