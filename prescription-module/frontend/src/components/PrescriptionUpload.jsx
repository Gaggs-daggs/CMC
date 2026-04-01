import { useState, useRef } from 'react'

export default function PrescriptionUpload({ onUpload, isLoading }) {
    const [file, setFile] = useState(null)
    const [preview, setPreview] = useState(null)
    const [dragging, setDragging] = useState(false)
    const inputRef = useRef(null)

    const handleFile = (f) => {
        if (!f || !f.type.startsWith('image/')) return
        setFile(f)
        const reader = new FileReader()
        reader.onload = (e) => setPreview(e.target.result)
        reader.readAsDataURL(f)
    }

    const handleDrop = (e) => {
        e.preventDefault()
        setDragging(false)
        const f = e.dataTransfer.files[0]
        handleFile(f)
    }

    const handleSubmit = () => {
        if (!file || isLoading) return
        onUpload(file)
    }

    const handleReset = () => {
        setFile(null)
        setPreview(null)
        if (inputRef.current) inputRef.current.value = ''
    }

    return (
        <div className="upload-section">
            <h2>📋 Upload Your Prescription</h2>
            <p>Take a photo or upload an image of your prescription — our AI will analyze every medicine for you.</p>

            <div
                className={`upload-zone ${dragging ? 'dragging' : ''}`}
                onClick={() => !file && inputRef.current?.click()}
                onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
            >
                <input
                    ref={inputRef}
                    type="file"
                    accept="image/*"
                    capture="environment"
                    style={{ display: 'none' }}
                    onChange={(e) => handleFile(e.target.files[0])}
                />

                {!preview ? (
                    <>
                        <div className="upload-icon">📷</div>
                        <div className="upload-text">
                            <h3>Drop your prescription here</h3>
                            <p>or <span className="accent">click to browse</span></p>
                            <p>Supports JPEG, PNG • Max 10MB</p>
                        </div>
                    </>
                ) : (
                    <div className="upload-preview">
                        <img src={preview} alt="Prescription preview" />
                        <div className="file-name">{file.name} ({(file.size / 1024).toFixed(0)} KB)</div>
                    </div>
                )}
            </div>

            {preview && (
                <div className="upload-actions fade-in">
                    <button className="btn-secondary" onClick={handleReset} disabled={isLoading}>
                        ✕ Clear
                    </button>
                    <button className="btn-primary" onClick={handleSubmit} disabled={isLoading}>
                        {isLoading ? '⏳ Analyzing...' : '🔍 Analyze Prescription'}
                    </button>
                </div>
            )}
        </div>
    )
}
