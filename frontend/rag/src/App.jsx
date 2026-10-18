import './App.css'
import FactsApp from './facts/facts'
import QuestionAnswerApp from './question_answer/question_answer'
import Header from './header/header'

function App() {

  return (
    <div className="App">
      <Header />
      <div className="app-body">
        <aside className="app-sidebar">
          <FactsApp />
        </aside>
        <QuestionAnswerApp />
      </div>
    </div>
  )
}

export default App
