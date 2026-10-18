import './facts.css'
import { useDropzone } from "react-dropzone";
import { useState } from 'react';

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
  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (files) => {
      console.log(files);
    },
  });

  return (
    <div {...getRootProps({ className: 'facts-upload' })}>
      <input {...getInputProps()} />
      <p className="facts-upload-label">Przeciągnij plik lub kliknij, aby wybrać</p>
    </div>
  );
}

function FactsList() {
  const [factsCount, setFactsCount] = useState(0)

  const refreshFactsCount = () => {
    setFactsCount(factsCount + 1)
  }

  return (
    <div className="facts-list">
      <p className="facts-count">Facts count: {factsCount}</p>
      <button type="button" className="facts-refresh" onClick={refreshFactsCount}>
        Refresh
      </button>
    </div>
  );
}

export default FactsApp
