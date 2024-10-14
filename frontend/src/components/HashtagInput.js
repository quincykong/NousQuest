import React, { useState, useEffect } from 'react';
import { TextField, Chip, Autocomplete, Box } from '@mui/material';

function HashtagInput({ initialHashtags = [], readOnly = false, onTagClick }) {
  // Ensure that hashtags is always an array
  const [hashtags, setHashtags] = useState(Array.isArray(initialHashtags) ? initialHashtags : []);

  useEffect(() => {
    // Ensure that initialHashtags is an array before setting the state
    if (Array.isArray(initialHashtags)) {
      setHashtags(initialHashtags);
    }
  }, [initialHashtags]);

  // Handle adding hashtags in editable mode
  const handleAddHashtag = (event, newHashtags) => {
    if (!readOnly) {
      setHashtags(newHashtags);
    }
  };

  // Handle deleting hashtags in editable mode
  const handleDeleteHashtag = (chipToDelete) => () => {
    if (!readOnly) {
      setHashtags((chips) => chips.filter((chip) => chip !== chipToDelete));
    }
  };

  // Handle tag click in read-only mode
  const handleTagClick = (tag) => {
    if (readOnly && onTagClick) {
      onTagClick(tag);  // Trigger click handler passed from parent component
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {!readOnly ? (
        // Editable mode - Autocomplete input for adding tags
        <Autocomplete
          multiple
          freeSolo
          id="hashtags-autocomplete"
          options={[]} // Optionally provide predefined hashtags
          value={hashtags}
          onChange={handleAddHashtag}
          renderTags={(value, getTagProps) =>
            value.map((option, index) => (
              <Chip
                key={index}
                variant="outlined"
                label={option}
                {...getTagProps({ index })}
                onDelete={handleDeleteHashtag(option)} // Allow deletion in editable mode
              />
            ))
          }
          renderInput={(params) => (
            <TextField {...params} variant="outlined" label="Hashtags" placeholder="Add hashtags" />
          )}
        />
      ) : (
        // Read-only mode - Display tags as clickable chips
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {hashtags.map((data, index) => (
            <Chip
              key={index}
              label={data}
              variant="outlined"
              sx={{ cursor: 'pointer' }}  // Make the cursor a pointer in read-only mode
              onClick={() => handleTagClick(data)}  // Call the click handler
            />
          ))}
        </Box>
      )}
    </Box>
  );
}

export default HashtagInput;
