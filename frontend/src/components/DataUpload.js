// frontend/src/components/DataUpload.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { createApiUrl } from '../config/api';

const DataUpload = ({ onDataUploaded, isOpen, onToggle }) => {
  const [files, setFiles] = useState([]);
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

  // UI state for tab selection
  const [selectedDataSource, setSelectedDataSource] = useState(null);

  // Handle escape key to close modal and reset state
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onToggle();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden'; // Prevent background scrolling
    } else {
      // Reset state when modal is closed
      setSelectedDataSource(null);
      setUploadStatus(null);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onToggle]);

  const handleFilesSelect = (selectedFiles) => {
    const csvFiles = Array.from(selectedFiles).filter(file => file.type === 'text/csv');

    if (csvFiles.length === 0) {
      setUploadStatus({ type: 'error', message: 'Please select CSV files' });
      return;
    }

    if (csvFiles.length !== selectedFiles.length) {
      setUploadStatus({ type: 'warning', message: `${csvFiles.length} CSV files selected, ${selectedFiles.length - csvFiles.length} non-CSV files ignored` });
    }

    setFiles(csvFiles);
    if (csvFiles.length === selectedFiles.length) {
      setUploadStatus(null);
    }
  };

  const handleFileChange = (e) => {
    handleFilesSelect(e.target.files);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const items = Array.from(e.dataTransfer.items);
    const files = [];

    // Handle both files and folders
    const processItems = async () => {
      for (const item of items) {
        if (item.kind === 'file') {
          const entry = item.webkitGetAsEntry();
          if (entry) {
            if (entry.isFile) {
              const file = item.getAsFile();
              if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
                files.push(file);
              }
            } else if (entry.isDirectory) {
              await processDirectory(entry, files);
            }
          }
        }
      }

      if (files.length > 0) {
        setFiles(files);
        setUploadStatus(null);
      } else {
        setUploadStatus({ type: 'error', message: 'No CSV files found in the dropped items' });
      }
    };

    processItems();
  };

  const processDirectory = async (directoryEntry, files) => {
    return new Promise((resolve) => {
      const reader = directoryEntry.createReader();
      reader.readEntries(async (entries) => {
        for (const entry of entries) {
          if (entry.isFile && entry.name.endsWith('.csv')) {
            entry.file((file) => {
              files.push(file);
            });
          } else if (entry.isDirectory) {
            await processDirectory(entry, files);
          }
        }
        resolve();
      });
    });
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
    if (!files || files.length === 0) {
      setUploadStatus({ type: 'error', message: 'Please select files first' });
      return;
    }

    setUploading(true);
    setUploadStatus(null);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await axios.post(createApiUrl('/api/upload-multiple-data/'), formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadStatus({
        type: 'success',
        message: `${response.data.stocks_loaded.length} stock files uploaded successfully! Total: ${response.data.total_rows} rows loaded.`
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
      const response = await axios.post(createApiUrl('/api/load-dow30/'));

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
      const response = await axios.post(createApiUrl('/api/set-date-range/'), {
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
      const response = await axios.post(createApiUrl('/api/load-yfinance/'), {
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
        <div className="data-upload-overlay" onClick={() => {
          setSelectedDataSource(null);
          setUploadStatus(null);
          onToggle();
        }}>
          <div className="data-upload-modal" onClick={(e) => e.stopPropagation()}>
            <div className="data-upload-header">
              <h3>Data Source Options</h3>
              <button className="data-upload-close-btn" onClick={() => {
                setSelectedDataSource(null);
                setUploadStatus(null);
                onToggle();
              }}>×</button>
            </div>

            <div className="data-upload-content">
              {/* Data Source Selection Cards */}
              {!selectedDataSource && (
                <div className="data-source-selection">
                  <h4 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
                    Choose Your Data Source
                  </h4>

                  <div className="data-source-cards">
                    {/* CSV File Card */}
                    <div
                      className="data-source-card"
                      onClick={() => setSelectedDataSource('csv')}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="card-icon">📁</div>
                      <h5>Upload CSV Files</h5>
                      <p>Upload multiple stock files or a folder</p>
                      <small>Each file = 1 stock, OHLCV format</small>
                    </div>

                    {/* Dow Jones 30 Card */}
                    <div
                      className="data-source-card"
                      onClick={() => setSelectedDataSource('dow30')}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="card-icon">📊</div>
                      <h5>Dow Jones 30</h5>
                      <p>Load all 30 DJ stocks</p>
                      <small>Pre-loaded historical data</small>
                    </div>

                    {/* Yahoo Finance Card */}
                    <div
                      className="data-source-card"
                      onClick={() => setSelectedDataSource('yfinance')}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="card-icon">🌐</div>
                      <h5>Yahoo Finance</h5>
                      <p>Fetch live market data</p>
                      <small>Any stocks, custom dates</small>
                    </div>
                  </div>
                </div>
              )}

              {/* Selected Data Source Content */}
              {selectedDataSource && (
                <div className="selected-data-source">
                  <div className="data-source-header">
                    <button
                      className="back-button"
                      onClick={() => setSelectedDataSource(null)}
                      style={{
                        background: 'none',
                        border: 'none',
                        fontSize: '18px',
                        cursor: 'pointer',
                        color: '#666'
                      }}
                    >
                      ← Back
                    </button>
                    <h4 style={{ margin: 0, flex: 1, textAlign: 'center' }}>
                      {selectedDataSource === 'csv' && 'Upload CSV Files'}
                      {selectedDataSource === 'dow30' && 'Dow Jones 30 Data'}
                      {selectedDataSource === 'yfinance' && 'Yahoo Finance Data'}
                    </h4>
                    <div style={{ width: '60px' }}></div> {/* Spacer for centering */}
                  </div>

                  {/* CSV Upload Content */}
                  {selectedDataSource === 'csv' && (
                    <div className="upload-section">
                      <p style={{ fontSize: '14px', color: '#666', margin: '20px 0 15px 0' }}>
                        Upload multiple CSV files or drag a folder. Each file should represent one stock with columns: Open, High, Low, Close, Volume
                      </p>

                      <div
                        className={`upload-area ${dragOver ? 'dragover' : ''}`}
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onClick={() => document.getElementById('file-input').click()}
                      >
                        <div className="upload-icon">📁</div>
                        <div className="upload-text">
                          {files.length > 0
                            ? `${files.length} CSV file${files.length > 1 ? 's' : ''} selected`
                            : 'Drop CSV files or folder here, or click to browse'}
                        </div>
                        <input
                          id="file-input"
                          type="file"
                          accept=".csv"
                          multiple
                          webkitdirectory=""
                          onChange={handleFileChange}
                          className="file-input"
                        />
                      </div>

                      <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                        <button
                          style={{
                            padding: '8px 16px',
                            background: '#f8f9fa',
                            border: '1px solid #dee2e6',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '14px'
                          }}
                          onClick={() => {
                            const input = document.createElement('input');
                            input.type = 'file';
                            input.multiple = true;
                            input.accept = '.csv';
                            input.onchange = (e) => handleFilesSelect(e.target.files);
                            input.click();
                          }}
                        >
                          📄 Select Files
                        </button>
                        <button
                          style={{
                            padding: '8px 16px',
                            background: '#f8f9fa',
                            border: '1px solid #dee2e6',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '14px'
                          }}
                          onClick={() => {
                            const input = document.createElement('input');
                            input.type = 'file';
                            input.webkitdirectory = true;
                            input.onchange = (e) => handleFilesSelect(e.target.files);
                            input.click();
                          }}
                        >
                          📁 Select Folder
                        </button>
                      </div>

                      {files.length > 0 && (
                        <div style={{ maxHeight: '120px', overflowY: 'auto', marginBottom: '15px' }}>
                          <small style={{ color: '#666', display: 'block', marginBottom: '5px' }}>
                            Selected files:
                          </small>
                          {files.map((file, index) => (
                            <div key={index} style={{
                              fontSize: '12px',
                              color: '#333',
                              padding: '2px 0',
                              display: 'flex',
                              justifyContent: 'space-between'
                            }}>
                              <span>{file.name}</span>
                              <button
                                onClick={() => {
                                  const newFiles = files.filter((_, i) => i !== index);
                                  setFiles(newFiles);
                                }}
                                style={{
                                  background: 'none',
                                  border: 'none',
                                  color: '#dc3545',
                                  cursor: 'pointer',
                                  fontSize: '12px'
                                }}
                              >
                                ×
                              </button>
                            </div>
                          ))}
                        </div>
                      )}

                      <button
                        className="upload-button"
                        onClick={handleUpload}
                        disabled={files.length === 0 || uploading}
                      >
                        {uploading ? 'Uploading...' : `Upload ${files.length} File${files.length !== 1 ? 's' : ''}`}
                      </button>
                    </div>
                  )}

                  {/* Dow Jones 30 Content */}
                  {selectedDataSource === 'dow30' && (
                    <div className="upload-section">
                      <p style={{ fontSize: '14px', color: '#666', margin: '20px 0 15px 0' }}>
                        Load historical data for all 30 stocks in the Dow Jones Industrial Average.
                        This includes companies like Apple (AAPL), Microsoft (MSFT), and Boeing (BA).
                      </p>

                      <div style={{
                        background: '#f8f9fa',
                        padding: '15px',
                        borderRadius: '8px',
                        marginBottom: '20px',
                        fontSize: '13px',
                        color: '#666'
                      }}>
                        <strong>What's included:</strong><br/>
                        • All 30 Dow Jones stocks<br/>
                        • Historical OHLCV data<br/>
                        • Automatically filtered to common date range
                      </div>

                      <button
                        className="upload-button dow30-button"
                        onClick={handleLoadDow30}
                        disabled={loadingDow30}
                      >
                        {loadingDow30 ? 'Loading...' : 'Load Dow Jones 30'}
                      </button>
                    </div>
                  )}

                  {/* Yahoo Finance Content */}
                  {selectedDataSource === 'yfinance' && (
                    <div className="upload-section">
                      <p style={{ fontSize: '14px', color: '#666', margin: '20px 0 15px 0' }}>
                        Fetch real-time data from Yahoo Finance for any publicly traded stocks.
                        Enter ticker symbols and select your preferred date range.
                      </p>

                      <div className="yfinance-inputs">
                        <label style={{ display: 'block', marginBottom: '15px' }}>
                          <strong>Stock Tickers:</strong>
                          <input
                            type="text"
                            value={tickers}
                            onChange={(e) => setTickers(e.target.value)}
                            placeholder="AAPL, GOOGL, MSFT, TSLA"
                            className="ticker-input"
                            style={{
                              width: '100%',
                              padding: '10px',
                              margin: '8px 0 0 0',
                              border: '1px solid #ddd',
                              borderRadius: '6px',
                              fontSize: '14px',
                              fontFamily: 'monospace'
                            }}
                          />
                          <small style={{ color: '#888', fontSize: '12px' }}>
                            Separate multiple tickers with commas
                          </small>
                        </label>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
                          <label>
                            <strong>Start Date:</strong>
                            <input
                              type="date"
                              value={startDate}
                              onChange={(e) => setStartDate(e.target.value)}
                              style={{
                                width: '100%',
                                padding: '10px',
                                margin: '8px 0 0 0',
                                border: '1px solid #ddd',
                                borderRadius: '6px'
                              }}
                            />
                          </label>
                          <label>
                            <strong>End Date:</strong>
                            <input
                              type="date"
                              value={endDate}
                              onChange={(e) => setEndDate(e.target.value)}
                              style={{
                                width: '100%',
                                padding: '10px',
                                margin: '8px 0 0 0',
                                border: '1px solid #ddd',
                                borderRadius: '6px'
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
                  )}
                </div>
              )}

              {/* Date Range Picker - shown after data is loaded */}
              {dateRange && selectedDataSource && (
                <div className="date-range-section" style={{ marginTop: '30px', paddingTop: '20px', borderTop: '1px solid #eee' }}>
                  <h5>Adjust Date Range (Optional)</h5>
                  <p style={{ fontSize: '13px', color: '#666', marginBottom: '15px' }}>
                    Available: {dateRange.min_date} to {dateRange.max_date}
                  </p>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                    <label>
                      Start Date:
                      <input
                        type="date"
                        min={dateRange.min_date}
                        max={dateRange.max_date}
                        defaultValue={dateRange.min_date}
                        onChange={(e) => {
                          const endDateInput = document.getElementById('end-date-filter');
                          if (endDateInput && endDateInput.value) {
                            handleDateRangeChange(e.target.value, endDateInput.value);
                          }
                        }}
                        style={{
                          width: '100%',
                          padding: '8px',
                          margin: '5px 0 0 0',
                          border: '1px solid #ddd',
                          borderRadius: '4px'
                        }}
                      />
                    </label>
                    <label>
                      End Date:
                      <input
                        id="end-date-filter"
                        type="date"
                        min={dateRange.min_date}
                        max={dateRange.max_date}
                        defaultValue={dateRange.max_date}
                        onChange={(e) => {
                          const startDateInput = document.querySelector('#end-date-filter').previousElementSibling.previousElementSibling;
                          if (startDateInput && startDateInput.value) {
                            handleDateRangeChange(startDateInput.value, e.target.value);
                          }
                        }}
                        style={{
                          width: '100%',
                          padding: '8px',
                          margin: '5px 0 0 0',
                          border: '1px solid #ddd',
                          borderRadius: '4px'
                        }}
                      />
                    </label>
                  </div>
                </div>
              )}

              {/* Status Messages */}
              {uploadStatus && (
                <div
                  className={uploadStatus.type === 'success' ? 'success-message' : 'error-message'}
                  style={{ marginTop: '20px' }}
                >
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