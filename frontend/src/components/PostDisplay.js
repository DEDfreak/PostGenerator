import React, { useState } from 'react';

function PostDisplay({ posts }) {
  const [copiedIndex, setCopiedIndex] = useState(null);

  const copyToClipboard = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  if (!posts || posts.length === 0) {
    return null;
  }

  return (
    <div className="posts-container">
      {posts.map((post, index) => (
        <div key={index} className="post-card">
          <div className="post-header">
            <span className="post-number">Post {index + 1}</span>
            <button 
              className={`copy-button ${copiedIndex === index ? 'copied' : ''}`}
              onClick={() => copyToClipboard(post, index)}
              title="Copy to clipboard"
            >
              {copiedIndex === index ? '✓ Copied!' : '📋 Copy'}
            </button>
          </div>
          <div className="post-content">
            <p>{post}</p>
          </div>
          <div className="post-actions">
            <span className="character-count">{post.length} characters</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default PostDisplay;