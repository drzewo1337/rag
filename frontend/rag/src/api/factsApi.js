import { apiRequest } from './http'

const FACTS_API = '/api/facts'

export async function fetchFacts() {
  const data = await apiRequest(`${FACTS_API}/facts`)
  return {
    count: data?.count ?? 0,
    facts: data?.facts ?? [],
  }
}

export async function createFact(factText) {
  return apiRequest(`${FACTS_API}/facts`, {
    method: 'POST',
    body: JSON.stringify({ fact_text: factText }),
  })
}

export async function uploadFactsFromFile(file) {
  const text = await file.text()
  const lines = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)

  if (lines.length === 0) {
    throw new Error('File is empty')
  }

  for (const line of lines) {
    await createFact(line)
  }

  return lines.length
}
