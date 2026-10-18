import './question_answer.css'

function QuestionAnswerApp() {

  const handleSubmit = (e) => {
    e.preventDefault();
    const question = e.target.question.value;
    console.log(question);
  }

  return (
    <div className="question-answer">
      <h1>Question and answer</h1>
      <div className="question-answer-panel">
        <form className="question-answer-form" onSubmit={handleSubmit}>
          <input
            className="question-answer-input"
            type="text"
            placeholder="Enter your question"
            name="question"
          />
          <button type="submit" className="question-answer-submit">
            Ask
          </button>
        </form>
        <div className="question-answer-response" aria-live="polite">
          <p className="question-answer-response-empty">Answer will appear here.</p>
        </div>
      </div>
    </div>
  )
}

export default QuestionAnswerApp
