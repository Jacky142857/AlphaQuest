// frontend/src/components/DataUpload.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const DataUpload = ({ onDataUploaded, isOpen, onToggle }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [loadingDow30, setLoadingDow30] = useState(false);
  const [dateRange, setDateRange] = useState(null);

  // Handle escape key to close modal
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onToggle();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onToggle]);

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      setUploadStatus(null);
    } else {
      setUploadStatus({ type: 'error', message: 'Please select a CSV file' });
    }
  };

  const handleFileChange = (e) => {
    handleFileSelect(e.target.files[0]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFileSelect(e.dataTransfer.files[0]);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus({ type: 'error', message: 'Please select a file first' });
      return;
    }

    setUploading(true);
    setUploadStatus(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/upload-data/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadStatus({
        type: 'success',
        message: `Data uploaded successfully! ${response.data.rows} rows loaded.`
      });
      onDataUploaded();
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.error || 'Upload failed'
      });
    } finally {
      setUploading(false);
    }
  };

  const handleLoadDow30 = async () => {
    setLoadingDow30(true);
    setUploadStatus(null);

    try {
      const response = await axios.post('/api/load-dow30/');

      setUploadStatus({
        type: 'success',
        message: `Dow Jones 30 data loaded! ${response.data.stocks_loaded.length} stocks, ${response.data.total_dates} dates.`
      });

      setDateRange(response.data.date_range);
      onDataUploaded();
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.error || 'Failed to load Dow Jones 30 data'
      });
    } finally {
      setLoadingDow30(false);
    }
  };

  const handleDateRangeChange = async (startDate, endDate) => {
    try {
      const response = await axios.post('/api/set-date-range/', {
        start_date: startDate,
        end_date: endDate
      });

      setUploadStatus({
        type: 'success',
        message: `Date range set: ${startDate} to ${endDate}`
      });
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.error || 'Failed to set date range'
      });
    }
  };

  return (
    <>
      <button className="data-upload-toggle-btn" onClick={onToggle}>
        📁 Data Upload
      </button>

      {isOpen && (
        <div className="data-upload-overlay" onClick={onToggle}>
          <div className="data-upload-modal" onClick={(e) => e.stopPropagation()}>
            <div className="data-upload-header">
              <h3>Data Source Options</h3>
              <button className="data-upload-close-btn" onClick={onToggle}>×</button>
            </div>

            <div className="data-upload-content">
        {/* Single File Upload */}
        <div className="upload-section">
          <h4>Upload Single CSV File</h4>
        <div
          className={`upload-area ${dragOver ? 'dragover' : ''}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => document.getElementById('file-input').click()}
        >
          <div className="upload-icon">📁</div>
          <div className="upload-text">
            {file ? file.name : 'Drop your CSV file here or click to browse'}
          </div>
          <div className="upload-text" style={{ fontSize: '14px', color: '#888' }}>
            Required columns: Open, High, Low, Close, Volume
          </div>
          <input
            id="file-input"
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="file-input"
          />
        </div>

        <button
          className="upload-button"
          onClick={handleUpload}
          disabled={!file || uploading}
        >
          {uploading ? 'Uploading...' : 'Upload Single File'}
        </button>
      </div>

      {/* Dow Jones 30 Data */}
      <div className="upload-section" style={{ marginTop: '20px' }}>
        <h4>Or Load Dow Jones 30 Data</h4>
        <p style={{ fontSize: '14px', color: '#666', margin: '10px 0' }}>
          Load all 30 stocks from the Dow Jones Industrial Average with date intersection
        </p>
        <button
          className="upload-button dow30-button"
          onClick={handleLoadDow30}
          disabled={loadingDow30}
        >
          {loadingDow30 ? 'Loading...' : 'Load Dow Jones 30'}
        </button>
      </div>

      {/* Date Range Picker */}
      {dateRange && (
        <div className="date-range-section" style={{ marginTop: '20px' }}>
          <h4>Select Date Range</h4>
          <p style={{ fontSize: '14px', color: '#666' }}>
            Available range: {dateRange.min_date} to {dateRange.max_date}
          </p>
          <div className="date-inputs">
            <label>
              Start Date:
              <input
                type="date"
                min={dateRange.min_date}
                max={dateRange.max_date}
                defaultValue={dateRange.min_date}
                onChange={(e) => {
                  const endDateInput = document.getElementById('end-date');
                  if (endDateInput.value) {
                    handleDateRangeChange(e.target.value, endDateInput.value);
                  }
                }}
              />
            </label>
            <label>
              End Date:
              <input
                id="end-date"
                type="date"
                min={dateRange.min_date}
                max={dateRange.max_date}
                defaultValue={dateRange.max_date}
                onChange={(e) => {
                  const startDateInput = document.querySelector('input[type="date"]');
                  if (startDateInput.value) {
                    handleDateRangeChange(startDateInput.value, e.target.value);
                  }
                }}
              />
            </label>
          </div>
        </div>
      )}

              {uploadStatus && (
                <div className={uploadStatus.type === 'success' ? 'success-message' : 'error-message'}>
                  {uploadStatus.message}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default DataUpload;