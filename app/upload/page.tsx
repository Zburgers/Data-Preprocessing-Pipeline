'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, Upload, FileType, CheckCircle, XCircle } from 'lucide-react';

export default function UploadPage() {
  const router = useRouter();
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [taskType, setTaskType] = useState('auto');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(Array.from(e.target.files));
      setError('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (files.length === 0) {
      setError('Please select at least one file to upload');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setError('');
    
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    formData.append('task_type', taskType);

    try {
      // Simulate progress for demo purposes
      const simulateProgress = () => {
        let progress = 0;
        const interval = setInterval(() => {
          progress += 5;
          setUploadProgress(progress > 95 ? 95 : progress);
          if (progress >= 95) clearInterval(interval);
        }, 300);
        return interval;
      };
      
      const progressInterval = simulateProgress();
      
      // Replace with actual API endpoint when ready
      const response = await fetch('/api/datasets/upload', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload files');
      }

      setUploadProgress(100);
      setSuccess(true);
      
      // Redirect to dataset view after successful upload
      const result = await response.json();
      setTimeout(() => {
        router.push(`/datasets/${result.dataset_id}`);
      }, 1500);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Upload Dataset</h1>
        
        {success ? (
          <div className="bg-green-900/30 border border-green-700 rounded-lg p-6 flex items-center">
            <CheckCircle className="h-8 w-8 text-green-500 mr-4" />
            <div>
              <h2 className="font-semibold text-xl">Upload Successful!</h2>
              <p className="text-gray-300">Redirecting to dataset analysis...</p>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="bg-gray-800 rounded-lg p-6 shadow-xl border border-gray-700">
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Task Type</label>
              <select 
                value={taskType}
                onChange={(e) => setTaskType(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="auto">Auto Detect</option>
                <option value="classification">Classification</option>
                <option value="regression">Regression</option>
                <option value="object_detection">Object Detection</option>
                <option value="semantic_segmentation">Semantic Segmentation</option>
                <option value="text_generation">Text Generation</option>
                <option value="translation">Translation</option>
                <option value="summarization">Summarization</option>
                <option value="question_answering">Question Answering</option>
                <option value="audio_classification">Audio Classification</option>
              </select>
              <p className="mt-1 text-sm text-gray-400">Select "Auto Detect" to let the system determine the best task type for your data</p>
            </div>
            
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Upload Files</label>
              <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:bg-gray-700/50 transition-colors" onClick={() => document.getElementById('file-upload')?.click()}>
                <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-lg mb-2 font-medium">Drag files here or click to browse</p>
                <p className="text-sm text-gray-400">
                  Support for CSV, JSON, images (PNG, JPG), audio files (WAV, MP3), and more
                </p>
                <input
                  id="file-upload"
                  type="file"
                  multiple
                  onChange={handleFileChange}
                  className="hidden"
                />
              </div>
              
              {files.length > 0 && (
                <div className="mt-4">
                  <h3 className="font-medium mb-2">Selected Files:</h3>
                  <ul className="space-y-2">
                    {files.map((file, index) => (
                      <li key={index} className="bg-gray-700 rounded px-3 py-2 flex items-center">
                        <FileType className="h-5 w-5 mr-2 text-blue-400" />
                        <span className="truncate">{file.name}</span>
                        <span className="ml-2 text-gray-400 text-sm">({Math.round(file.size / 1024)} KB)</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            
            {error && (
              <div className="mb-6 bg-red-900/30 border border-red-700 rounded-md p-3 flex items-center">
                <XCircle className="h-5 w-5 text-red-500 mr-2" />
                <p className="text-red-300">{error}</p>
              </div>
            )}
            
            {uploading && (
              <div className="mb-6">
                <div className="flex justify-between text-sm mb-1">
                  <span>Uploading...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}
            
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={uploading || files.length === 0}
                className={`
                  px-4 py-2 rounded-md font-medium flex items-center
                  ${uploading || files.length === 0
                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }
                `}
              >
                {uploading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  'Upload and Process'
                )}
              </button>
            </div>
          </form>
        )}
        
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">What happens next?</h2>
          <ol className="list-decimal pl-5 space-y-3 text-gray-300">
            <li>Our system will automatically detect the data modality (tabular, text, image, etc.)</li>
            <li>We'll analyze the data structure and suggest optimal preprocessing steps</li>
            <li>You can customize the preprocessing pipeline or use our recommended settings</li>
            <li>Once processed, you can export your clean dataset in various formats</li>
          </ol>
        </div>
      </div>
    </div>
  );
} 