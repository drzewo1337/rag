import { apiRequest, sleep } from './http'

const ASK_API = '/api/ask'

export async function createQuestion(questionText) {
  const data = await apiRequest(`${ASK_API}/questions`, {
    method: 'POST',
    body: JSON.stringify({ question_text: questionText }),
  })

  const questionId = data?.question?.id
  if (!questionId) {
    throw new Error('API did not return question id')
  }

  return questionId
}

export async function getAnswersForQuestion(questionId) {
  const data = await apiRequest(`${ASK_API}/questions/${questionId}/answers`)
  return data?.answers ?? []
}

export async function askQuestionAndWaitForAnswer(
  questionText,
  { pollIntervalMs = 2000, maxAttempts = 90 } = {},
) {
  const questionId = await createQuestion(questionText)

  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const answers = await getAnswersForQuestion(questionId)
    if (answers.length > 0) {
      return answers[0].answer_text
    }
    await sleep(pollIntervalMs)
  }

  throw new Error('Answer not ready yet. Try again in a moment.')
}
