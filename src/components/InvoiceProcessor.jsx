import React, { useState, useCallback } from "react";
import {
  FileUp,
  Upload,
  File,
  CheckCircle2,
  AlertCircle,
  Loader2,
  XCircle,
} from "lucide-react";
import { motion } from "framer-motion";

function App() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("idle");
  const [preview, setPreview] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [extractedData, setExtractedData] = useState(null);

  const handleDrop = useCallback((event) => {
    event.preventDefault();
    setIsDragging(false);
    const droppedFile = event.dataTransfer.files[0];
    handleFile(droppedFile);
  }, []);

  const handleFileSelect = useCallback((event) => {
    const selectedFile = event.target.files?.[0];
    handleFile(selectedFile);
  }, []);

  const handleFile = (file) => {
    if (file?.type.startsWith("image/") || file?.type === "application/pdf") {
      setFile(file);
      setUploadStatus("idle");
      setUploadProgress(0);

      if (file.type.startsWith("image/")) {
        setPreview(URL.createObjectURL(file));
      } else if (file.type === "application/pdf") {
        setPreview(URL.createObjectURL(file));
      } else {
        setPreview(null);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    setUploadStatus("uploading");
    setUploadProgress(0);

    const formData = new FormData();
    formData.append("invoice", file);

    try {
      const response = await fetch("http://localhost:5000/process-invoice", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to process invoice");
      }

      const result = await response.json();
      setExtractedData(result); // Save both structured data and raw text
      setUploadStatus("success");
    } catch (error) {
      setUploadStatus("error");
      console.error("Error processing invoice:", error);
    } finally {
      setIsProcessing(false);
      setUploadProgress(100);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black flex items-center justify-center p-6 animate-gradientShift">
      <motion.div
        className="w-full max-w-xl bg-gray-800 bg-opacity-90 p-8 rounded-3xl shadow-2xl backdrop-blur-lg"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-center space-x-3 mb-6">
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            <FileUp className="w-12 h-12 text-blue-500 animate-pulse" />
          </motion.div>
          <h1 className="text-4xl font-extrabold text-white bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
            AI Invoice Processor
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File Drop Area */}
          <motion.div
            className={`border-2 border-dashed rounded-2xl p-8 transition-all ${
              isDragging
                ? "border-blue-500 bg-blue-500/10 shadow-lg"
                : "border-gray-500 hover:border-gray-400"
            }`}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
          >
            <div className="text-center">
              <Upload className="w-14 h-14 text-gray-400 mx-auto" />
              <p className="text-gray-300">Drag & Drop your invoice or</p>
              <input
                type="file"
                id="file-input"
                className="hidden"
                onChange={handleFileSelect}
                accept="image/*,.pdf"
              />
              <motion.button
                type="button"
                onClick={() => document.getElementById("file-input").click()}
                className="mt-4 px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg shadow-lg hover:from-blue-600 hover:to-purple-600"
                whileHover={{ scale: 1.1 }}
              >
                Browse Files
              </motion.button>
            </div>
          </motion.div>

          {/* File Display */}
          {file && (
            <motion.div
              className="bg-gray-700 p-4 rounded-xl flex items-center space-x-4 shadow-md"
              animate={{ opacity: 1 }}
              initial={{ opacity: 0 }}
            >
              <File className="w-6 h-6 text-blue-400" />
              <span className="text-white truncate">{file.name}</span>
              {uploadStatus === "success" && (
                <CheckCircle2 className="w-6 h-6 text-green-400" />
              )}
              {uploadStatus === "error" && (
                <AlertCircle className="w-6 h-6 text-red-400" />
              )}
              <button onClick={() => setFile(null)}>
                <XCircle className="w-6 h-6 text-gray-400 hover:text-red-400" />
              </button>
            </motion.div>
          )}

          {/* Preview Section */}
          {preview && file?.type.startsWith("image/") && (
            <motion.div
              className="overflow-hidden rounded-xl border-2 border-gray-700 shadow-lg mt-4"
              animate={{ scale: 1 }}
              initial={{ scale: 0.95 }}
            >
              <img src={preview} alt="Preview" className="w-full object-cover" />
            </motion.div>
          )}

          {/* Progress Bar */}
          {uploadStatus === "uploading" && (
            <motion.div
              className="w-full bg-gray-600 rounded-xl overflow-hidden mt-4"
              initial={{ width: "0%" }}
              animate={{ width: `${uploadProgress}%` }}
              style={{
                background: "linear-gradient(to right, #4e54c8, #8f94fb)",
                boxShadow: "0 0 15px #8f94fb",
              }}
            />
          )}

          {/* Submit Button */}
          <motion.button
            type="submit"
            disabled={!file || isProcessing}
            className={`w-full py-3 rounded-lg text-white font-semibold transition-all ${
              !file
                ? "bg-gray-600 cursor-not-allowed"
                : "bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 shadow-md"
            }`}
            whileHover={{ scale: 1.05 }}
          >
            {isProcessing ? (
              <motion.div className="flex items-center justify-center space-x-2">
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Processing...</span>
              </motion.div>
            ) : (
              "Process Invoice"
            )}
          </motion.button>
        </form>

        {extractedData && (
          <motion.div
            className="bg-gradient-to-r from-indigo-600 to-purple-600 shadow-lg mt-6 p-4 rounded-xl text-white"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <h3 className="text-lg font-bold">Raw Extracted Text:</h3>
            <pre className="text-sm whitespace-pre-wrap">
              {extractedData.raw_text}
            </pre>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}

export default App;
