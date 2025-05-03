import React, { useState, useEffect } from "react";
import "./App.css";
import { FiZoomIn, FiX, FiUpload, FiImage, FiClock, FiRefreshCw } from "react-icons/fi";

function App() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [selectedDetectionId, setSelectedDetectionId] = useState(null);
  const [zoomedImage, setZoomedImage] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch("http://localhost:5000/history");
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    setImage(file);
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("image", image);

    try {
      const res = await fetch("http://localhost:5000/detect", {
        method: "POST",
        body: formData,
      });
      const data = await res.blob();
      const resultUrl = URL.createObjectURL(data);
      setResult(resultUrl);
      fetchHistory();
    } catch (err) {
      alert("Error uploading image.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectHistory = async (id) => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:5000/history/${id}`);
      const data = await res.blob();
      const url = URL.createObjectURL(data);
      setResult(url);
      setSelectedDetectionId(id);
    } catch (err) {
      alert("Failed to load detection from history.");
    } finally {
      setLoading(false);
    }
  };

  const openZoom = (imgSrc) => {
    setZoomedImage(imgSrc);
  };

  const closeZoom = () => {
    setZoomedImage(null);
  };

  return (
    <div className="app">
      <header>
        <h1>AI Object Detection</h1>
      </header>

      <main>
        <form onSubmit={handleSubmit} className="form">
          <div className="file-input-container">
            <label className="file-input-label">
              <FiUpload className="upload-icon" />
              <span>{image ? image.name : "Choose an image or drag & drop"}</span>
              <input type="file" accept="image/*" onChange={handleImageChange} />
            </label>
          </div>
          
          <button type="submit" disabled={loading || !image}>
            {loading ? (
              <>
                <FiRefreshCw className="loading-icon" /> Processing...
              </>
            ) : (
              <>
                <FiImage /> Detect Objects
              </>
            )}
          </button>
        </form>

        <div className="images-container">
          {preview && (
            <div className="image-card">
              <h3><FiImage /> Original Image</h3>
              <div className="image-wrapper" onClick={() => openZoom(preview)}>
                <img src={preview} alt="Preview" />
                <div className="zoom-hint">
                  <FiZoomIn /> Click to zoom
                </div>
              </div>
            </div>
          )}

          {result && (
            <div className="image-card">
              <h3><FiImage /> Detection Result {selectedDetectionId && `(ID: ${selectedDetectionId})`}</h3>
              <div className="image-wrapper" onClick={() => openZoom(result)}>
                <img src={result} alt="Detection result" />
                <div className="zoom-hint">
                  <FiZoomIn /> Click to zoom
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="history">
          <h3><FiClock /> Detection History</h3>
          {history.length === 0 ? (
            <div className="empty-state">
              <p>No detections yet. Upload an image to get started!</p>
            </div>
          ) : (
            <div className="history-list">
              {history.map(({ id, thumbnail }) => (
                <div 
                  key={id} 
                  className={`history-item ${id === selectedDetectionId ? 'selected' : ''}`}
                  onClick={() => handleSelectHistory(id)}
                >
                  <img 
                    src={`data:image/jpeg;base64,${thumbnail}`} 
                    alt={`Detection ${id}`}
                  />
                </div>
              ))}
            </div>
          )}
      </div>
      </main>

      {zoomedImage && (
        <div className="zoom-modal" onClick={closeZoom}>
          <div className="zoom-content" onClick={e => e.stopPropagation()}>
            <button className="close-button" onClick={closeZoom}>
              <FiX />
            </button>
            <img src={zoomedImage} alt="Zoomed" />
          </div>
        </div>
      )}

      <footer>&copy; 2025 Object Detector by Jakub Sadkiewicz</footer>
    </div>
  );
}

export default App;