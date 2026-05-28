import { useState } from 'react';

export const useAgentStream = () => {
  const [logs, setLogs] = useState([]); 
  const [jobs, setJobs] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const startSearch = async (payload) => {
    setIsSearching(true);
    setLogs([]); 
    setJobs([]); 

    try {
      const response = await fetch('http://localhost:8000/api/search-jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      
      // FIX: Add a buffer to catch fragmented data chunks
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // Split by newlines, but keep the last incomplete chunk in the buffer
        const lines = buffer.split('\n');
        buffer = lines.pop(); 
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim();
            if (!dataStr) continue;
            
            try {
              const data = JSON.parse(dataStr);
              
              setLogs((prev) => [...prev, data.message]);
              
              // If we got the jobs, render them!
              if (data.final_jobs && data.final_jobs.length > 0) {
                setJobs(data.final_jobs);
              }
            } catch (err) {
              console.warn("Waiting for the rest of the data chunk...");
            }
          }
        }
      }
    } catch (error) {
      setLogs((prev) => [...prev, 'Error: Could not connect to the backend server.']);
    } finally {
      setIsSearching(false);
    }
  };

  return { logs, jobs, isSearching, startSearch };
};