import './question_answer.css'
import { useEffect, useRef, useState } from 'react'
import { askQuestionAndWaitForAnswer } from '../api/askApi'
import { IconPanelLeft, IconSend } from '../icons'

function QuestionAnswerApp({ onOpenSidebar }) {
  const [exchanges, setExchanges] = useState([])
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [exchanges, loading])

  const resizeTextarea = () => {
    const el = textareaRef.current
    if (!el) {
      return
    }
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`
  }

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
    resizeTextarea()

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

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      e.currentTarget.form?.requestSubmit()
    }
  }

  const showWelcome = exchanges.length === 0 && !loading

  return (
    <main className="question-answer">
      <div className="question-answer-toolbar">
        <button
          type="button"
          className="question-answer-menu"
          onClick={onOpenSidebar}
          aria-label="Open knowledge base sidebar"
        >
          <IconPanelLeft width={20} height={20} />
        </button>
      </div>

      <div className="question-answer-scroll" aria-live="polite">
        <div className="question-answer-inner">
          {showWelcome ? (
            <div className="question-answer-welcome">
              <h1 className="question-answer-welcome-title">
                How can I help you today?
              </h1>
              <p className="question-answer-welcome-desc">
                Ask questions and explore knowledge from your documents.
              </p>
            </div>
          ) : null}

          <div className="question-answer-messages">
            {exchanges.map((item) => (
              <article key={item.id} className="question-answer-exchange">
                <div
                  className="question-answer-message question-answer-message-user"
                  aria-label="Your message"
                >
                  {item.question}
                </div>
                {item.status === 'pending' ? (
                  <div
                    className="question-answer-message question-answer-message-assistant question-answer-loading"
                    aria-busy="true"
                  >
                    <span className="question-answer-loading-dots" aria-hidden="true">
                      <span />
                      <span />
                      <span />
                    </span>
                    <span className="question-answer-loading-text">Thinking…</span>
                  </div>
                ) : null}
                {item.status === 'done' ? (
                  <div
                    className="question-answer-message question-answer-message-assistant"
                    aria-label="Assistant response"
                  >
                    {item.answer}
                  </div>
                ) : null}
                {item.status === 'error' ? (
                  <div
                    className="question-answer-message question-answer-message-error"
                    role="alert"
                  >
                    {item.error}
                  </div>
                ) : null}
              </article>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      <div className="question-answer-composer">
        <form className="question-answer-form" onSubmit={handleSubmit}>
          <textarea
            ref={textareaRef}
            className="question-answer-input"
            placeholder="Ask a question about your documents..."
            name="question"
            rows={1}
            disabled={loading}
            onInput={resizeTextarea}
            onKeyDown={handleKeyDown}
          />
          <button
            type="submit"
            className="question-answer-submit"
            disabled={loading}
            aria-label={loading ? 'Sending question' : 'Send question'}
          >
            <IconSend width={18} height={18} />
          </button>
        </form>
        <p className="question-answer-composer-hint">
          Press Enter to send, Shift+Enter for a new line
        </p>
      </div>
    </main>
  )
}

export default QuestionAnswerApp
