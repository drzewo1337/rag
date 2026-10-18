import './App.css'
import FactsApp from './facts/facts'
import QuestionAnswerApp from './question_answer/question_answer'
import Header from './header/header'

function App() {

  return (
    <div className="App">
      <Header />
      <main className="app-main">
        <FactsApp />
        <QuestionAnswerApp />
      </main>
    </div>
  )
}

export default App
