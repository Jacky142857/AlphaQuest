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

  // YFinance state
  const [loadingYFinance, setLoadingYFinance] = useState(false);
  const [tickers, setTickers] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

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

  const handleLoadYFinance = async () => {
    if (!tickers.trim() || !startDate || !endDate) {
      setUploadStatus({
        type: 'error',
        message: 'Please provide tickers, start date, and end date'
      });
      return;
    }

    setLoadingYFinance(true);
    setUploadStatus(null);

    // Parse tickers - split by comma and clean up
    const tickerList = tickers.split(',').map(t => t.trim().toUpperCase()).filter(t => t);

    try {
      const response = await axios.post('/api/load-yfinance/', {
        tickers: tickerList,
        start_date: startDate,
        end_date: endDate
      });

      let message = `${response.data.stocks_loaded.length} stocks loaded from Yahoo Finance! `;
      message += `Date range: ${response.data.date_range.min_date} to ${response.data.date_range.max_date}`;

      if (response.data.failed_tickers && response.data.failed_tickers.length > 0) {
        message += `\nWarning: Failed to load ${response.data.failed_tickers.join(', ')}`;
      }

      setUploadStatus({
        type: 'success',
        message: message
      });

      setDateRange(response.data.date_range);
      onDataUploaded();
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.error || 'Failed to load data from Yahoo Finance'
      });
    } finally {
      setLoadingYFinance(false);
    }
  };

  // Set default dates on component mount
  useEffect(() => {
    if (!startDate && !endDate) {
      const today = new Date();
      const oneYearAgo = new Date(today);
      oneYearAgo.setFullYear(today.getFullYear() - 1);

      setEndDate(today.toISOString().split('T')[0]);
      setStartDate(oneYearAgo.toISOString().split('T')[0]);
    }
  }, [startDate, endDate]);

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

      {/* Yahoo Finance Data */}
      <div className="upload-section" style={{ marginTop: '20px' }}>
        <h4>Or Load Data from Yahoo Finance</h4>
        <p style={{ fontSize: '14px', color: '#666', margin: '10px 0' }}>
          Enter stock tickers separated by commas (e.g., AAPL, GOOGL, MSFT) and select a date range
        </p>

        <div className="yfinance-inputs">
          <label>
            Stock Tickers:
            <input
              type="text"
              value={tickers}
              onChange={(e) => setTickers(e.target.value)}
              placeholder="AAPL, GOOGL, MSFT, TSLA"
              className="ticker-input"
              style={{
                width: '100%',
                padding: '8px',
                margin: '5px 0 15px 0',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px'
              }}
            />
          </label>

          <div className="date-inputs" style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
            <label style={{ flex: 1 }}>
              Start Date:
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px',
                  margin: '5px 0',
                  border: '1px solid #ddd',
                  borderRadius: '4px'
                }}
              />
            </label>
            <label style={{ flex: 1 }}>
              End Date:
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px',
                  margin: '5px 0',
                  border: '1px solid #ddd',
                  borderRadius: '4px'
                }}
              />
            </label>
          </div>
        </div>

        <button
          className="upload-button yfinance-button"
          onClick={handleLoadYFinance}
          disabled={loadingYFinance || !tickers.trim() || !startDate || !endDate}
          style={{
            backgroundColor: loadingYFinance || !tickers.trim() || !startDate || !endDate ? '#ccc' : '#007bff',
            cursor: loadingYFinance || !tickers.trim() || !startDate || !endDate ? 'not-allowed' : 'pointer'
          }}
        >
          {loadingYFinance ? 'Loading from Yahoo Finance...' : 'Load from Yahoo Finance'}
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