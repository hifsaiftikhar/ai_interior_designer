import { useRef, useState } from "react";
import "../styles/designer.css";

function ImageUploader({ onImageSelect }) {
  const inputRef = useRef(null);
  const [preview, setPreview] = useState(null);
  const [dragging, setDragging] = useState(false);

  const handleFile = (file) => {
    if (!file || !file.type.startsWith("image/")) return;

    const previewUrl = URL.createObjectURL(file);

    setPreview(previewUrl);

    onImageSelect(file);
  };

  const handleInputChange = (event) => {
    const file = event.target.files?.[0];
    handleFile(file);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragging(false);

    const file = event.dataTransfer.files?.[0];
    handleFile(file);
  };

  return (
    <div
      className={`image-uploader ${dragging ? "dragging" : ""} ${
        preview ? "has-preview" : ""
      }`}
      onDragOver={(event) => {
        event.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={handleInputChange}
        hidden
      />

      {preview ? (
        <>
          <img
            src={preview}
            alt="Selected room"
            className="room-preview"
          />

          <div className="preview-overlay">
            <span>Change image</span>
          </div>
        </>
      ) : (
        <div className="upload-content">
          <div className="upload-icon">＋</div>

          <h3>Drop your room here</h3>

          <p>
            or click to browse
            <br />
            JPG, PNG · Max 10MB
          </p>
        </div>
      )}
    </div>
  );
}

export default ImageUploader;