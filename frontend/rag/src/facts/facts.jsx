import './facts.css'
import { useDropzone } from "react-dropzone";

function Upload() {
  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (files) => {
      console.log(files);
    },
  });

  return (
    <div {...getRootProps()}>
      <input {...getInputProps()} />
      <p>Przeciągnij plik lub kliknij, aby wybrać</p>
    </div>
  );
}


function FactsApp() {

  return (  
    <div className="facts">
      <h1>Facts manager</h1>
      <div className="facts-manager">
        <div className="facts-manager-input">
          <input type="text" placeholder="Submit a pdf file" />
        </div>
        <div className="facts-manager-field">
          <Upload />
        </div>
      </div>
    </div>
  )
}

export default FactsApp
