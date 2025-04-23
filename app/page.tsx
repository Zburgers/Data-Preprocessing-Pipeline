import React from 'react';
import Link from 'next/link';
import Head from 'next/head';

export default function Home() {
  return (
    <div className="bg-gradient-to-b from-gray-900 to-gray-800 min-h-screen text-white">
      <Head>
        <title>Data Preprocessing Pipeline</title>
        <meta name="description" content="Universal data preprocessing platform for AI/ML" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="container mx-auto px-4 py-16">
        <div className="flex flex-col items-center justify-center text-center">
          <h1 className="text-5xl font-bold mb-8">
            Data Preprocessing Pipeline
          </h1>
          <p className="text-xl mb-12 max-w-3xl">
            A universal, production-ready, and scalable data preprocessing platform 
            for AI/ML developers. Transform any raw data into clean, model-ready datasets.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            <div className="bg-gray-800 p-8 rounded-lg border border-gray-700 shadow-lg">
              <h2 className="text-2xl font-bold mb-4">Upload Data</h2>
              <p className="mb-6">Upload your raw data files (CSV, JSON, images, audio, etc.) and let us detect the format and suggest preprocessing steps.</p>
              <Link href="/upload" className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition duration-200">
                Start Uploading
              </Link>
            </div>
            <div className="bg-gray-800 p-8 rounded-lg border border-gray-700 shadow-lg">
              <h2 className="text-2xl font-bold mb-4">View Datasets</h2>
              <p className="mb-6">Browse your existing datasets, view preprocessing pipelines, and export in various formats.</p>
              <Link href="/datasets" className="inline-block bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-6 rounded-lg transition duration-200">
                Browse Datasets
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-6xl">
            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <h3 className="text-xl font-semibold mb-3">Multiple Modalities</h3>
              <p>Support for text, tabular, image, audio, and video data. Auto-detect formats and appropriate preprocessing steps.</p>
            </div>
            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <h3 className="text-xl font-semibold mb-3">AI Task Specific</h3>
              <p>Optimized pipelines for classification, regression, NER, object detection, and more ML tasks.</p>
            </div>
            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <h3 className="text-xl font-semibold mb-3">Multiple Export Formats</h3>
              <p>Export to HuggingFace Datasets, PyTorch, TensorFlow, or flat files for immediate use in your models.</p>
            </div>
          </div>
        </div>
      </main>

      <footer className="container mx-auto px-4 py-8 mt-12 border-t border-gray-700">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400">
            &copy; {new Date().getFullYear()} Data Preprocessing Pipeline
          </p>
          <div className="flex space-x-4 mt-4 md:mt-0">
            <Link href="/docs" className="text-gray-400 hover:text-white">
              Documentation
            </Link>
            <Link href="/api" className="text-gray-400 hover:text-white">
              API
            </Link>
            <Link href="https://github.com/yourusername/data-preprocessing-pipeline" className="text-gray-400 hover:text-white">
              GitHub
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
} 