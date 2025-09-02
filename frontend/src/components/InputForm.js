import React, { useState } from 'react';

function InputForm({ onGenerate }) {
  const [topic, setTopic] = useState('');
  const [tone, setTone] = useState('professional');
  const [postLength, setPostLength] = useState('medium');
  const [hashtags, setHashtags] = useState('#linkedin #socialmedia');

  const handleSubmit = (event) => {
    event.preventDefault();
    onGenerate(topic, { tone, postLength, hashtags }); // Pass topic and options to the parent component
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="topic">Topic:</label>
        <input
          type="text"
          id="topic"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="tone">Tone:</label>
        <select id="tone" value={tone} onChange={(e) => setTone(e.target.value)}>
          <option value="professional">Professional</option>
          <option value="casual">Casual</option>
          <option value="humorous">Humorous</option>
        </select>
      </div>
      <div>
        <label htmlFor="postLength">Post Length:</label>
        <select id="postLength" value={postLength} onChange={(e) => setPostLength(e.target.value)}>
          <option value="short">Short</option>
          <option value="medium">Medium</option>
          <option value="long">Long</option>
        </select>
      </div>
      <div>
        <label htmlFor="hashtags">Hashtags:</label>
        <input
          type="text"
          id="hashtags"
          value={hashtags}
          onChange={(e) => setHashtags(e.target.value)}
        />
      </div>
      <button type="submit">Generate</button>
    </form>
  );
}

export default InputForm;