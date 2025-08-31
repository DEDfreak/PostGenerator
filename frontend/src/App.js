import React, { useState } from 'react';
import InputForm from './components/InputForm.js';
import PostDisplay from './components/PostDisplay';
import './App.css';

function App() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generatePosts = async (topic, options) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/generate', { // Assuming Flask backend is running on the same origin
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic, options }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      setPosts(data.posts); // Assuming the backend returns { posts: [...] }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>LinkedIn Post Generator</h1>
      <InputForm onGenerate={generatePosts} />
      {loading && <p>Generating posts...</p>}
      {error && <p className="error">Error: {error}</p>}
      <PostDisplay posts={posts} />
    </div>
  );
}

export default App;