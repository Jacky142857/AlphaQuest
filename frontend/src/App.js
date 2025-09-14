// frontend/src/App.js
import React, { useState } from 'react';
import './App.css';
import AlphaFormula from './components/AlphaFormula';
import PnLChart from './components/PnLChart';
import DataUpload from './components/DataUpload';

function App() {
  const [pnlData, setPnlData] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [isDataUploaded, setIsDataUploaded] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleDataUpload = () => {
    setIsDataUploaded(true);
    setPnlData(null);
    setMetrics(null);
  };

  const handleAlphaResult = (result) => {
    setPnlData(result.pnl_data);
    setMetrics(result.metrics);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>Trading Signals Alpha Strategy</h1>
      </header>
      
      <div className="upload-section">
        <DataUpload onDataUploaded={handleDataUpload} />
      </div>

      <div className="main-content">
        <div className="left-panel">
          <AlphaFormula 
            onResult={handleAlphaResult}
            isDataUploaded={isDataUploaded}
            setLoading={setLoading}
          />
        </div>
        
        <div className="right-panel">
          <PnLChart 
            data={pnlData} 
            metrics={metrics}
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
}

export default App;