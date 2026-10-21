import './facts.css'
import { useDropzone } from 'react-dropzone'
import { useCallback, useState } from 'react'
import { fetchFacts, uploadFactsFromFile } from '../api/factsApi'
import { IconDatabase, IconRefresh, IconUpload } from '../icons'

function FactsApp() {
  return (
    <div className="facts">
      <div className="facts-manager">
        <Upload />
        <FactsList />
      </div>
    </div>
  )
}

function Upload() {
  const [uploading, setUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState('')

  const onDrop = useCallback(async (files) => {
    const file = files[0]
    if (!file) {
      return
    }

    setUploading(true)
    setUploadMessage('')

    try {
      const addedCount = await uploadFactsFromFile(file)
      setUploadMessage(`Added ${addedCount} fact(s).`)
    } catch (error) {
      setUploadMessage(error.message ?? 'Upload failed')
    } finally {
      setUploading(false)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    disabled: uploading,
  })

  return (
    <div className="facts-upload-wrap">
      <div
        {...getRootProps({
          className: `facts-upload${isDragActive ? ' facts-upload-active' : ''}`,
        })}
      >
        <input {...getInputProps()} />
        <span className="facts-upload-icon" aria-hidden="true">
          <IconUpload width={22} height={22} />
        </span>
        <div className="facts-upload-copy">
          <p className="facts-upload-label">
            {uploading ? 'Uploading…' : 'Upload documents'}
          </p>
          <p className="facts-upload-hint">
            {isDragActive
              ? 'Drop your file here'
              : 'Drag and drop or click to browse'}
          </p>
        </div>
      </div>
      {uploadMessage ? (
        <p
          className={`facts-upload-status${uploadMessage.includes('failed') || uploadMessage.includes('empty') ? ' facts-upload-status-error' : ''}`}
          role="status"
        >
          {uploadMessage}
        </p>
      ) : null}
    </div>
  )
}

function FactsList() {
  const [factsCount, setFactsCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const refreshFactsCount = async () => {
    setLoading(true)
    setError('')

    try {
      const { count } = await fetchFacts()
      setFactsCount(count)
    } catch (err) {
      setError(err.message ?? 'Failed to load facts')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="facts-kb">
      <div className="facts-kb-header">
        <span className="facts-kb-icon" aria-hidden="true">
          <IconDatabase width={18} height={18} />
        </span>
        <span className="facts-kb-label">Knowledge Base</span>
        <button
          type="button"
          className="facts-refresh"
          onClick={refreshFactsCount}
          disabled={loading}
          aria-label="Refresh knowledge base count"
          title="Refresh"
        >
          <IconRefresh width={18} height={18} />
        </button>
      </div>
      <p className="facts-count">
        <span className="facts-count-value">{factsCount}</span>
        <span className="facts-count-unit">
          {factsCount === 1 ? 'fact' : 'facts'}
        </span>
      </p>
      {error ? <p className="facts-error" role="alert">{error}</p> : null}
    </div>
  )
}

export default FactsApp
