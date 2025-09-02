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

  // Function to render formatted text with hashtag styling
  const renderFormattedText = (text) => {
    const parts = text.split(/(\#\w+)/g);
    
    return parts.map((part, index) => {
      if (part.startsWith('#')) {
        return (
          <span key={index} className="hashtag">
            {part}
          </span>
        );
      }
      return part;
    });
  };

  // Function to split text into paragraphs and render with proper formatting
  const renderPostContent = (post) => {
    // Split by double line breaks to create paragraphs
    const paragraphs = post.split(/\n\s*\n/).filter(p => p.trim());
    
    return paragraphs.map((paragraph, index) => (
      <p key={index} className="post-paragraph">
        {renderFormattedText(paragraph.trim())}
      </p>
    ));
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
            {renderPostContent(post)}
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