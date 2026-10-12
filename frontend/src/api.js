import axios from 'axios'

export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const client = axios.create({ baseURL: API_BASE, timeout: 120000 })

export async function checkHealth() {
  const { data } = await client.get('/api/health')
  return data
}
export async function analyzeCsv(file) {
  const body = new FormData()
  body.append('file', file)
  const { data } = await client.post('/api/analyze', body)
  return data
}
export async function optimizeDiscounts(config) {
  const { data } = await client.post('/api/optimize', config)
  return data
}