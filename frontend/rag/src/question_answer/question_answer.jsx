import './question_answer.css'
import { useEffect, useRef, useState } from 'react'
import { askQuestionAndWaitForAnswer } from '../api/askApi'

function QuestionAnswerApp() {
  const [exchanges, setExchanges] = useState([])
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [exchanges, loading])

  const handleSubmit = async (e) => {
    e.preventDefault()
    const form = e.currentTarget
    const question = form.question.value.trim()

    if (!question || loading) {
      return
    }

    const exchangeId = crypto.randomUUID()
    setExchanges((prev) => [
      ...prev,
      { id: exchangeId, question, answer: null, status: 'pending', error: '' },
    ])
    setLoading(true)
    form.reset()

    try {
      const answerText = await askQuestionAndWaitForAnswer(question)
      setExchanges((prev) =>
        prev.map((item) =>
          item.id === exchangeId
            ? { ...item, answer: answerText, status: 'done', error: '' }
            : item,
        ),
      )
    } catch (err) {
      setExchanges((prev) =>
        prev.map((item) =>
          item.id === exchangeId
            ? {
                ...item,
                status: 'error',
                error: err.message ?? 'Failed to get answer',
              }
            : item,
        ),
      )
    } finally {
      setLoading(false)
    }
  }

  const showPlaceholder = exchanges.length === 0 && !loading

  return (
    <div className="question-answer">
      <h1>Question and answer</h1>
      <div className="question-answer-response" aria-live="polite">
        <div className="question-answer-messages">
          {showPlaceholder ? (
            <p className="question-answer-response-empty">Answer will appear here.</p>
          ) : null}
          {exchanges.map((item) => (
            <article key={item.id} className="question-answer-exchange">
              <p className="question-answer-message question-answer-message-user">
                <span className="question-answer-message-label">You</span>
                {item.question}
              </p>
              {item.status === 'pending' ? (
                <p className="question-answer-message question-answer-message-assistant question-answer-response-loading">
                  <span className="question-answer-message-label">RAG</span>
                  Generating answer...
                </p>
              ) : null}
              {item.status === 'done' ? (
                <p className="question-answer-message question-answer-message-assistant">
                  <span className="question-answer-message-label">RAG</span>
                  {item.answer}
                </p>
              ) : null}
              {item.status === 'error' ? (
                <p className="question-answer-message question-answer-message-error">
                  <span className="question-answer-message-label">Error</span>
                  {item.error}
                </p>
              ) : null}
            </article>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>
      <div className="question-answer-panel">
        <form className="question-answer-form cyber-chamfer" onSubmit={handleSubmit}>
          <input
            className="question-answer-input"
            type="text"
            placeholder="Enter your question"
            name="question"
            disabled={loading}
          />
          <button
            type="submit"
            className="question-answer-submit cyber-btn cyber-btn-solid cyber-chamfer-sm"
            disabled={loading}
          >
            {loading ? 'Asking...' : 'Ask'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default QuestionAnswerApp
