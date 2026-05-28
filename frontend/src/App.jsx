// frontend/src/App.jsx
import { useState } from 'react';
import { useAgentStream } from './hooks/useAgentStream';

function App() {
  // --- STATE VARIABLES ---
  const [resumeText, setResumeText] = useState(null);
  const [userQuery, setUserQuery] = useState("");
  const [uploadStatus, setUploadStatus] = useState("");
  
  // Bring in our custom AI streaming logic
  const { logs, jobs, isSearching, startSearch } = useAgentStream();

  // --- FUNCTIONS ---
  // Handle file upload and send to FastAPI
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadStatus("Extracting text...");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/api/upload-resume", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setResumeText(data.text);
      setUploadStatus("Resume loaded successfully! AI is ready.");
    } catch (error) {
      setUploadStatus("Failed to extract resume.");
    }
  };

  // Trigger the AI Search
  const handleSearch = () => {
    if (!resumeText && !userQuery) {
      alert("Please upload a resume or type a role first.");
      return;
    }
    
    // We send this exact payload to the backend
    startSearch({
      raw_resume_text: resumeText,
      user_query: userQuery,
      filters: { freshness: "Last 7 days" } // You can expand this UI later
    });
  };

  // --- RENDER UI (JSX) ---
  return (
    <div className="min-h-screen max-w-4xl mx-auto py-10 px-4 font-sans">
      
      {/* Header */}
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">AI Job Finder</h1>
        <p className="text-gray-600">Upload your resume or search manually. Let our AI agents do the rest.</p>
      </div>

      {/* Input Section (Cards) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        
        {/* Upload Card */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold mb-4">1. Profile Matching</h2>
          <input 
            type="file" 
            accept=".pdf,.docx" 
            onChange={handleFileUpload}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          {uploadStatus && <p className="text-sm mt-3 text-green-600">{uploadStatus}</p>}
        </div>

        {/* Manual Search Card */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold mb-4">2. Or Search Manually</h2>
          <input 
            type="text"
            placeholder="e.g. Junior Python Developer Remote"
            value={userQuery}
            onChange={(e) => setUserQuery(e.target.value)} // Updates state on every keystroke
            className="w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Search Button */}
      <div className="text-center mb-12">
        <button 
          onClick={handleSearch}
          disabled={isSearching}
          className={`px-8 py-3 rounded-md text-white font-bold text-lg transition-colors ${
            isSearching ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {isSearching ? 'Agent is working...' : 'Find Jobs'}
        </button>
      </div>

      {/* Streaming Agent Logs */}
      {logs.length > 0 && (
        <div className="bg-gray-900 text-green-400 p-4 rounded-md font-mono text-sm mb-8 overflow-y-auto max-h-48">
          {logs.map((log, index) => (
            <div key={index}>&gt; {log}</div>
          ))}
          {isSearching && <span className="animate-pulse">_</span>}
        </div>
      )}

      {/* Results Section */}
      <div className="space-y-4">
        {jobs.map((job, index) => (
          <div key={index} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-xl font-bold text-gray-900">{job.title}</h3>
                <p className="text-blue-600 font-medium">{job.company}</p>
              </div>
              <a 
                href={job.apply_url} 
                target="_blank" 
                rel="noreferrer"
                className="bg-blue-50 text-blue-700 px-4 py-2 rounded-md text-sm font-semibold hover:bg-blue-100"
              >
                Apply Link
              </a>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium border border-gray-200">
                📍 {job.location}
              </span>
              <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium border border-gray-200">
                💼 {job.job_type}
              </span>
              <span className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-xs font-medium border border-green-200">
                💰 {job.salary}
              </span>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}

export default App;