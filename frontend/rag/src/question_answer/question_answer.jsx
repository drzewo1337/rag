import './question_answer.css'

function QuestionAnswerApp() {

  const handleSubmit = (e) => {
    e.preventDefault();
    const question = e.target.question.value;
    console.log(question);
  }

  return (  
    <div className="question-answer">
      <h1>Question Answer</h1>
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Enter your question" name="question" />
        <button type="submit">Answer</button>
      </form>
    </div>
  )
}

export default QuestionAnswerApp
