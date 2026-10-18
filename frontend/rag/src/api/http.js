async function parseJsonResponse(response) {
  const text = await response.text()
  if (!text) {
    return null
  }

  try {
    return JSON.parse(text)
  } catch {
    throw new Error('Invalid JSON response from API')
  }
}

export async function apiRequest(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  const data = await parseJsonResponse(response)

  if (!response.ok) {
    const detail =
      typeof data?.detail === 'string'
        ? data.detail
        : `Request failed (${response.status})`
    throw new Error(detail)
  }

  return data
}

export function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}
