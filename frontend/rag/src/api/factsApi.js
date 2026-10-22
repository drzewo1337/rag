import { apiRequest, apiUpload } from './http'

const FACTS_API = '/api/facts'

export async function listDocuments() {
  const data = await apiRequest(`${FACTS_API}/documents`)
  return data?.documents ?? []
}

export async function uploadPdf(file) {
  const body = new FormData()
  body.append('file', file)
  return apiUpload(`${FACTS_API}/documents`, body)
}

export async function deleteDocument(id) {
  return apiRequest(`${FACTS_API}/documents/${id}`, { method: 'DELETE' })
}
