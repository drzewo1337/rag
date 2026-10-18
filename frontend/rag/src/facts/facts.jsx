import './facts.css'
import { useDropzone } from 'react-dropzone'
import { useCallback, useState } from 'react'
import { fetchFacts, uploadFactsFromFile } from '../api/factsApi'

function FactsApp() {
  return (
    <div className="facts">
      <h1>Facts manager</h1>
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
    <div>
      <div
        {...getRootProps({
          className: `facts-upload cyber-chamfer${isDragActive ? ' facts-upload-active' : ''}`,
        })}
      >
        <input {...getInputProps()} />
        <p className="facts-upload-label">
          {uploading
            ? 'Uploading...'
            : isDragActive
              ? 'Drop file here'
              : 'Upload your facts'}
        </p>
      </div>
      {uploadMessage ? <p className="facts-upload-status">{uploadMessage}</p> : null}
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
    <div className="facts-list cyber-chamfer">
      <p className="facts-count">Facts count: {factsCount}</p>
      {error ? <p className="facts-error">{error}</p> : null}
      <button
        type="button"
        className="facts-refresh cyber-btn cyber-chamfer-sm"
        onClick={refreshFactsCount}
        disabled={loading}
      >
        {loading ? 'Loading...' : 'Refresh'}
      </button>
    </div>
  )
}

export default FactsApp
