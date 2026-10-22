const CITE = /\[(\d+)\](?!\()/g

function isSource(source) {
  return Boolean(
    source
    && Number.isInteger(source.id)
    && typeof source.filename === 'string'
    && Number.isInteger(source.page)
    && typeof source.content === 'string',
  )
}

export function parseAnswer(answerText) {
  if (typeof answerText !== 'string') {
    return { answer: '', sources: [] }
  }

  try {
    const data = JSON.parse(answerText)
    if (data && typeof data.answer === 'string' && Array.isArray(data.sources)) {
      return {
        answer: data.answer,
        sources: data.sources.filter(isSource),
      }
    }
  } catch {
    // Older answers are plain text.
  }

  return { answer: answerText, sources: [] }
}

export function linkCitations(markdown, sources) {
  const ids = new Set(sources.map((source) => source.id))
  const parts = markdown.split(/(```[\s\S]*?```|`[^`]*`)/g)

  return parts.map((part) => {
    if (part.startsWith('`')) {
      return part
    }
    return part.replace(CITE, (match, rawId) => {
      const id = Number(rawId)
      if (!ids.has(id)) {
        return match
      }
      return `[${rawId}](#source-${rawId})`
    })
  }).join('')
}
