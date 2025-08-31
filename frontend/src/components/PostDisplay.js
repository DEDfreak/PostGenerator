import React from 'react';

function PostDisplay({ posts }) {
  return (
    <div>
      {posts.map((post, index) => (
        <div key={index} className="post-card">
          <p>{post}</p>
        </div>
      ))}
    </div>
  );
}

export default PostDisplay;