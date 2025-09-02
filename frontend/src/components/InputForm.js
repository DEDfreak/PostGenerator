import React, { useState, useEffect } from 'react';

function InputForm({ onGenerate, onAnalyzeTopic, suggestedFields, analyzingTopic }) {
  // Basic form fields
  const [topic, setTopic] = useState('');
  const [tone, setTone] = useState('professional');
  const [postLength, setPostLength] = useState('medium');
  const [hashtags, setHashtags] = useState('#linkedin #socialmedia');
  
  // Enhanced fields state
  const [enhancedFields, setEnhancedFields] = useState({});
  const [showEnhancedFields, setShowEnhancedFields] = useState(false);
  const [hasAnalyzed, setHasAnalyzed] = useState(false);

  // Reset enhanced fields when topic changes significantly
  useEffect(() => {
    if (topic.length > 0 && hasAnalyzed) {
      setHasAnalyzed(false);
      setShowEnhancedFields(false);
      setEnhancedFields({});
    }
  }, [topic]);

  // Update enhanced fields when suggested fields change
  useEffect(() => {
    if (suggestedFields.length > 0) {
      console.log('Received suggested fields:', suggestedFields);
      setShowEnhancedFields(true);
      setHasAnalyzed(true);
      
      // Initialize enhanced fields with empty values
      const initialFields = {};
      suggestedFields.forEach(field => {
        initialFields[field.field] = '';
      });
      setEnhancedFields(initialFields);
    }
  }, [suggestedFields]);

  // Handle enhanced field changes
  const handleEnhancedFieldChange = (fieldName, value) => {
    console.log(`Enhanced field changed: ${fieldName} = ${value}`);
    setEnhancedFields(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  // Handle topic analysis
  const handleAnalyzeTopic = async () => {
    if (!topic.trim()) {
      alert('Please enter a topic first!');
      return;
    }

    console.log('Analyzing topic:', topic);
    await onAnalyzeTopic(topic);
  };

  // Handle form submission
  const handleSubmit = (event) => {
    event.preventDefault();
    
    if (!topic.trim()) {
      alert('Please enter a topic!');
      return;
    }

    console.log('Submitting form with:', {
      topic,
      options: { tone, post_length: postLength, hashtags },
      enhancedFields
    });

    // Filter out empty enhanced fields
    const filledEnhancedFields = {};
    Object.keys(enhancedFields).forEach(key => {
      if (enhancedFields[key] && enhancedFields[key].trim()) {
        filledEnhancedFields[key] = enhancedFields[key].trim();
      }
    });

    onGenerate(topic, { tone, post_length: postLength, hashtags }, filledEnhancedFields);
  };

  // Handle quick generate (skip analysis)
  const handleQuickGenerate = () => {
    if (!topic.trim()) {
      alert('Please enter a topic!');
      return;
    }

    console.log('Quick generate without analysis');
    onGenerate(topic, { tone, post_length: postLength, hashtags }, {});
  };

  return (
    <div className="input-form-container">
      <form onSubmit={handleSubmit}>
        {/* Basic Fields */}
        <div className="form-section">
          <h3>Basic Information</h3>
          
          <div className="form-group">
            <label htmlFor="topic">Topic:</label>
            <input
              type="text"
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., new internship, job promotion, conference"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="tone">Tone:</label>
              <select id="tone" value={tone} onChange={(e) => setTone(e.target.value)}>
                <option value="professional">Professional</option>
                <option value="excited">Excited</option>
                <option value="casual">Casual</option>
                <option value="humorous">Humorous</option>
                <option value="grateful">Grateful</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="postLength">Post Length:</label>
              <select id="postLength" value={postLength} onChange={(e) => setPostLength(e.target.value)}>
                <option value="short">Short</option>
                <option value="medium">Medium</option>
                <option value="long">Long</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="hashtags">Hashtags:</label>
            <input
              type="text"
              id="hashtags"
              value={hashtags}
              onChange={(e) => setHashtags(e.target.value)}
              placeholder="#linkedin #socialmedia"
            />
          </div>
        </div>

        {/* Analysis Section */}
        <div className="form-section">
          <h3>Personalization (Optional)</h3>
          <p>Get AI-suggested fields to make your posts more specific and engaging!</p>
          
          <div className="button-group">
            <button 
              type="button" 
              onClick={handleAnalyzeTopic}
              disabled={analyzingTopic || !topic.trim()}
              className="analyze-button"
            >
              {analyzingTopic ? 'Analyzing...' : 'Get Personalization Fields'}
            </button>
            
            <button 
              type="button" 
              onClick={handleQuickGenerate}
              disabled={analyzingTopic || !topic.trim()}
              className="quick-button"
            >
              Quick Generate
            </button>
          </div>
        </div>

        {/* Dynamic Enhanced Fields */}
        {showEnhancedFields && suggestedFields.length > 0 && (
          <div className="form-section enhanced-section">
            <h3>Personalization Fields</h3>
            <p>Fill any of these fields to make your posts more specific (all optional):</p>
            
            {suggestedFields.map((field, index) => (
              <div key={`${field.field}-${index}`} className="form-group">
                <label htmlFor={field.field}>
                  {field.label}
                  {field.description && <span className="field-description">({field.description})</span>}
                </label>
                
                {field.type === 'textarea' ? (
                  <textarea
                    id={field.field}
                    value={enhancedFields[field.field] || ''}
                    onChange={(e) => handleEnhancedFieldChange(field.field, e.target.value)}
                    placeholder={field.description || `Enter ${field.label.toLowerCase()}`}
                    rows="3"
                  />
                ) : field.type === 'number' ? (
                  <input
                    type="number"
                    id={field.field}
                    value={enhancedFields[field.field] || ''}
                    onChange={(e) => handleEnhancedFieldChange(field.field, e.target.value)}
                    placeholder={field.description || `Enter ${field.label.toLowerCase()}`}
                  />
                ) : (
                  <input
                    type="text"
                    id={field.field}
                    value={enhancedFields[field.field] || ''}
                    onChange={(e) => handleEnhancedFieldChange(field.field, e.target.value)}
                    placeholder={field.description || `Enter ${field.label.toLowerCase()}`}
                  />
                )}
              </div>
            ))}
          </div>
        )}

        {/* Generate Button */}
        <div className="form-section">
          <button 
            type="submit" 
            className="generate-button"
            disabled={analyzingTopic || !topic.trim()}
          >
            {showEnhancedFields ? 'Generate Enhanced Posts' : 'Generate Posts'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default InputForm;