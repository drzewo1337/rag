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

function errorDetail(data, response) {
  if (typeof data?.detail === 'string') {
    return data.detail
  }
  return `Request failed (${response.status})`
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
    throw new Error(errorDetail(data, response))
  }

  return data
}

export async function apiUpload(path, formData) {
  const response = await fetch(path, {
    method: 'POST',
    body: formData,
  })

  const data = await parseJsonResponse(response)

  if (!response.ok) {
    throw new Error(errorDetail(data, response))
  }

  return data
}

export function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}
