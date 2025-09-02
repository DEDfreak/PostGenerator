import React, { useState } from 'react';
import InputForm from './components/InputForm.js';
import PostDisplay from './components/PostDisplay';
import './App.css';

function App() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [suggestedFields, setSuggestedFields] = useState([]);
  const [analyzingTopic, setAnalyzingTopic] = useState(false);
  const [metrics, setMetrics] = useState(null);

  // Get API base URL from environment
  const getApiUrl = (endpoint) => {
    const baseUrl = process.env.REACT_APP_API_URL;
    if (baseUrl) {
      // Remove /api/generate from the end if it exists and add the new endpoint
      const cleanBaseUrl = baseUrl.replace('/api/generate', '');
      return `${cleanBaseUrl}${endpoint}`;
    }
    return `http://localhost:5000${endpoint}`;
  };

  // Stage 1: Analyze topic and get suggested fields
  const analyzeTopic = async (topic) => {
    console.log('=== ANALYZING TOPIC ===');
    console.log('Topic:', topic);
    
    setAnalyzingTopic(true);
    setError(null);
    setSuggestedFields([]);

    try {
      const response = await fetch(getApiUrl('/api/analyze-topic'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
      });

      console.log('Analysis response status:', response.status);

      if (!response.ok) {
        throw new Error(`Analysis failed! Status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Analysis data:', data);
      
      setSuggestedFields(data.suggested_fields || []);
      return data.suggested_fields || [];
    } catch (err) {
      console.error('Analysis error:', err);
      setError(`Topic analysis failed: ${err.message}`);
      return [];
    } finally {
      setAnalyzingTopic(false);
    }
  };

  // Stage 2: Generate posts (basic or enhanced)
  const generatePosts = async (topic, options, enhancedFields = {}) => {
    console.log('=== GENERATING POSTS ===');
    console.log('Topic:', topic);
    console.log('Options:', options);
    console.log('Enhanced fields:', enhancedFields);
    
    setLoading(true);
    setError(null);

    try {
      // Check if we have enhanced fields to use the enhanced endpoint
      const hasEnhancedFields = enhancedFields && Object.keys(enhancedFields).length > 0;
      const endpoint = hasEnhancedFields ? '/api/generate-enhanced' : '/api/generate';
      
      console.log('Using endpoint:', endpoint);
      console.log('Has enhanced fields:', hasEnhancedFields);

      const requestBody = hasEnhancedFields 
        ? { topic, options, enhanced_fields: enhancedFields }
        : { topic, options };

      console.log('Request body:', requestBody);

      const response = await fetch(getApiUrl(endpoint), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      console.log('Generation response status:', response.status);

      if (!response.ok) {
        throw new Error(`Generation failed! Status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Generation data:', data);
      
      setPosts(data.posts || []);
      setMetrics(data.metrics || null);
      
      // Show success message if enhanced generation was used
      if (data.enhanced) {
        console.log('Enhanced generation used with context:', data.context_used);
      }
    } catch (err) {
      console.error('Generation error:', err);
      setError(`Post generation failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>LinkedIn Post Generator</h1>
        <p>Create engaging LinkedIn posts with AI assistance</p>
      </header>
      
      <main className="app-main">
        {/* Left Console - Input Area */}
        <div className="left-console">
          <div className="console-header">
            <h2>📝 Input Console</h2>
          </div>
          <InputForm 
            onGenerate={generatePosts}
            onAnalyzeTopic={analyzeTopic}
            suggestedFields={suggestedFields}
            analyzingTopic={analyzingTopic}
          />
          
          {/* Status Messages */}
          <div className="status-section">
            {loading && (
              <div className="status-message loading">
                <div className="spinner"></div>
                <span>Generating posts...</span>
              </div>
            )}
            {analyzingTopic && (
              <div className="status-message analyzing">
                <div className="spinner"></div>
                <span>Analyzing topic for personalization...</span>
              </div>
            )}
            {error && (
              <div className="status-message error">
                <span>⚠️ {error}</span>
              </div>
            )}
          </div>
        </div>
        
        {/* Right Results - Output Area */}
        <div className="right-results">
          <div className="results-header">
            <h2>✨ Generated Posts</h2>
            <div className="header-info">
              {posts.length > 0 && (
                <span className="posts-count">{posts.length} posts generated</span>
              )}
              {metrics && (
                <div className="metrics-summary">
                  <span className="metric">⏱️ {metrics.generation_time}s</span>
                  <span className="metric">🎯 {metrics.total_tokens} tokens</span>
                  <span className="metric">💰 ${metrics.estimated_cost}</span>
                </div>
              )}
            </div>
          </div>
          <div className="results-content">
            {posts.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📄</div>
                <h3>No posts generated yet</h3>
                <p>Enter a topic in the console and click generate to see your LinkedIn posts here.</p>
              </div>
            ) : (
              <PostDisplay posts={posts} />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;