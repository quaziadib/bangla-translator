import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [text, setText] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('English');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleTranslate = async () => {
    setError('');
    setResult(null);

    try {
      const BACKEND_URL = process.env.REACT_APP_API_BASE || 'http://localhost:8000';
      const response = await axios.post(`${BACKEND_URL}/translate`, {
        text,
        target_language: targetLanguage,
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred');
    }
  };

  return (
    <div className="App">
      <h1>Bangla Translator</h1>
      <textarea
        rows="4"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter Bangla text here"
      />
      <br />
      <select value={targetLanguage} onChange={(e) => setTargetLanguage(e.target.value)}>
        <option value="English">English</option>
        <option value="French">French</option>
        <option value="German">German</option>
        {/* Add more languages as needed */}
      </select>
      <br />
      <button onClick={handleTranslate}>Translate</button>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {result && (
        <div className="result">
          <h2>Translation</h2>
          <p><strong>Original:</strong> {result.original_text}</p>
          <p><strong>Translated:</strong> {result.translated_text}</p>
          {result.formal_alternative && <p><strong>Formal Alternative:</strong> {result.formal_alternative}</p>}
          {result.notes && <p><strong>Notes:</strong> {result.notes}</p>}
        </div>
      )}
    </div>
  );
}

export default App;
