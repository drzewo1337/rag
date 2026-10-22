import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { linkCitations, parseAnswer } from './answerFormat'

function AnswerMessage({ text, exchangeId }) {
  const { answer, sources } = parseAnswer(text)
  const [openId, setOpenId] = useState(null)
  const markdown = linkCitations(answer, sources)

  const openSource = (id) => {
    setOpenId(id)
    requestAnimationFrame(() => {
      document.getElementById(`${exchangeId}-source-${id}`)?.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
      })
    })
  }

  return (
    <div className="answer">
      <div className="answer-markdown">
        <ReactMarkdown
          components={{
            a: ({ href, children }) => {
              const match = /^#source-(\d+)$/.exec(href ?? '')
              if (!match) {
                return (
                  <a href={href} target="_blank" rel="noreferrer">
                    {children}
                  </a>
                )
              }
              const id = Number(match[1])
              return (
                <button type="button" className="answer-cite" onClick={() => openSource(id)}>
                  [{id}]
                </button>
              )
            },
          }}
        >
          {markdown}
        </ReactMarkdown>
      </div>
      {sources.length > 0 ? (
        <section className="answer-sources" aria-label="Sources">
          <h2 className="answer-sources-title">Sources</h2>
          <ul className="answer-sources-list">
            {sources.map((source) => {
              const open = openId === source.id
              return (
                <li key={source.id} id={`${exchangeId}-source-${source.id}`} className="answer-source">
                  <button
                    type="button"
                    className="answer-source-button"
                    aria-expanded={open}
                    onClick={() => setOpenId(open ? null : source.id)}
                  >
                    <span className="answer-source-id">[{source.id}]</span>
                    <span className="answer-source-name">{source.filename}</span>
                    <span className="answer-source-page">page {source.page}</span>
                  </button>
                  {open ? <p className="answer-source-fragment">{source.content}</p> : null}
                </li>
              )
            })}
          </ul>
        </section>
      ) : null}
    </div>
  )
}

export default AnswerMessage
