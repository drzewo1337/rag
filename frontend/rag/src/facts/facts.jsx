import './facts.css'
import { useDropzone } from 'react-dropzone'
import { useCallback, useEffect, useState } from 'react'
import { deleteDocument, listDocuments, uploadPdf } from '../api/factsApi'
import { IconDatabase, IconRefresh, IconTrash, IconUpload } from '../icons'

const MAX_PDF_BYTES = 50 * 1024 * 1024

function formatSize(bytes) {
  if (bytes < 1024) {
    return `${bytes} B`
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatCreatedAt(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return ''
  }
  return date.toLocaleDateString()
}

function chunkLabel(count) {
  return count === 1 ? '1 chunk' : `${count} chunks`
}

function FactsApp() {
  const [refreshToken, setRefreshToken] = useState(0)
  const refreshDocuments = useCallback(() => {
    setRefreshToken((current) => current + 1)
  }, [])

  return (
    <div className="facts">
      <div className="facts-manager">
        <Upload onUploaded={refreshDocuments} />
        <DocumentList refreshToken={refreshToken} />
      </div>
    </div>
  )
}

function Upload({ onUploaded }) {
  const [uploading, setUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState('')
  const [uploadError, setUploadError] = useState(false)

  const onDrop = useCallback(async (files) => {
    const file = files[0]
    if (!file) {
      return
    }

    setUploading(true)
    setUploadMessage('')
    setUploadError(false)

    try {
      const document = await uploadPdf(file)
      setUploadMessage(`Added ${document.filename} (${chunkLabel(document.chunk_count)}).`)
      onUploaded()
    } catch (error) {
      setUploadError(true)
      setUploadMessage(error.message ?? 'Upload failed')
    } finally {
      setUploading(false)
    }
  }, [onUploaded])

  const onDropRejected = useCallback((rejections) => {
    const code = rejections[0]?.errors[0]?.code
    setUploadError(true)
    if (code === 'file-too-large') {
      setUploadMessage('File exceeds 50 MB')
      return
    }
    if (code === 'file-invalid-type') {
      setUploadMessage('Only PDF files are accepted')
      return
    }
    setUploadMessage('Upload failed')
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDropRejected,
    multiple: false,
    disabled: uploading,
    maxSize: MAX_PDF_BYTES,
    accept: { 'application/pdf': ['.pdf'] },
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
            {uploading ? 'Uploading…' : 'Upload PDF'}
          </p>
          <p className="facts-upload-hint">
            {isDragActive ? 'Drop your PDF here' : 'One PDF, up to 50 MB'}
          </p>
        </div>
      </div>
      {uploadMessage ? (
        <p
          className={`facts-upload-status${uploadError ? ' facts-upload-status-error' : ''}`}
          role={uploadError ? 'alert' : 'status'}
        >
          {uploadMessage}
        </p>
      ) : null}
    </div>
  )
}

function DocumentList({ refreshToken }) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [reloadKey, setReloadKey] = useState(0)
  const [deletingId, setDeletingId] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    listDocuments()
      .then((next) => {
        if (!cancelled) {
          setDocuments(next)
          setError('')
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message ?? 'Failed to load documents')
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [refreshToken, reloadKey])

  const onRefresh = () => {
    setLoading(true)
    setError('')
    setReloadKey((current) => current + 1)
  }

  const onDelete = async (document) => {
    if (!window.confirm(`Delete ${document.filename} and its embeddings?`)) {
      return
    }

    setDeletingId(document.id)
    setError('')

    try {
      await deleteDocument(document.id)
      setDocuments((current) => current.filter((item) => item.id !== document.id))
    } catch (err) {
      setError(err.message ?? 'Failed to delete document')
    } finally {
      setDeletingId(null)
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
          onClick={onRefresh}
          disabled={loading || deletingId !== null}
          aria-label="Refresh documents"
          title="Refresh"
        >
          <IconRefresh width={18} height={18} />
        </button>
      </div>
      {loading && documents.length === 0 ? <p className="facts-empty">Loading…</p> : null}
      {!loading && documents.length === 0 && !error ? (
        <p className="facts-empty">No documents yet</p>
      ) : null}
      {documents.length > 0 ? (
        <ul className="facts-docs">
          {documents.map((document) => (
            <li key={document.id} className="facts-doc">
              <div className="facts-doc-main">
                <span className="facts-doc-name" title={document.filename}>
                  {document.filename}
                </span>
                <span className="facts-doc-meta">
                  {formatSize(document.size_bytes)} · {chunkLabel(document.chunk_count)} · {formatCreatedAt(document.created_at)}
                </span>
              </div>
              <button
                type="button"
                className="facts-doc-delete"
                onClick={() => onDelete(document)}
                disabled={deletingId !== null}
                aria-label={`Delete ${document.filename}`}
                title="Delete"
              >
                <IconTrash width={16} height={16} />
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      {error ? <p className="facts-error" role="alert">{error}</p> : null}
    </div>
  )
}

export default FactsApp
