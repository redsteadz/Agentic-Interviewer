import React from 'react';

const InterviewTest = () => {
  console.log('InterviewTest component loaded successfully');
  
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Interview Dashboard Test</h1>
      <p>If you can see this, the component is loading correctly.</p>
      <button 
        onClick={() => console.log('Button clicked')}
        className="bg-blue-500 text-white px-4 py-2 rounded mt-4"
      >
        Test Button
      </button>
    </div>
  );
};

export default InterviewTest;