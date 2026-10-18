import './App.css'
import FactsApp from './facts/facts'
import QuestionAnswerApp from './question_answer/question_answer'

function App() {

  return (
    <div className="App">
      <h1>RAG Service</h1>
      <FactsApp />
      <QuestionAnswerApp />
    </div>
  )
}

export default App
