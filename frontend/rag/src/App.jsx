import './App.css'
import { useCallback, useEffect, useState } from 'react'
import FactsApp from './facts/facts'
import QuestionAnswerApp from './question_answer/question_answer'
import { IconLeaf } from './icons'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const closeSidebar = useCallback(() => setSidebarOpen(false), [])
  const openSidebar = useCallback(() => setSidebarOpen(true), [])

  useEffect(() => {
    if (!sidebarOpen) {
      return undefined
    }

    const onKeyDown = (e) => {
      if (e.key === 'Escape') {
        closeSidebar()
      }
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [sidebarOpen, closeSidebar])

  return (
    <div className="App">
      <div className="app-body">
        <aside
          className={`app-sidebar${sidebarOpen ? ' app-sidebar--open' : ''}`}
          aria-label="Knowledge base sidebar"
        >
          <div className="app-sidebar-brand">
            <span className="app-sidebar-logo" aria-hidden="true">
              <IconLeaf width={22} height={22} />
            </span>
            <div className="app-sidebar-brand-text">
              <span className="app-sidebar-title">RAG</span>
            </div>
          </div>
          <FactsApp />
        </aside>
        {sidebarOpen ? (
          <button
            type="button"
            className="app-sidebar-backdrop"
            aria-label="Close sidebar"
            onClick={closeSidebar}
          />
        ) : null}
        <QuestionAnswerApp onOpenSidebar={openSidebar} />
      </div>
    </div>
  )
}

export default App
