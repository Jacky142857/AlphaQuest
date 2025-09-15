// Simulate.js - The current simulation functionality moved to a separate component
import React, { useState } from 'react';
import AlphaFormula from './AlphaFormula';
import PnLChart from './PnLChart';
import DataUpload from './DataUpload';
import Settings from './Settings';

function Simulate() {
  const [pnlData, setPnlData] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [isDataUploaded, setIsDataUploaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [dataUploadOpen, setDataUploadOpen] = useState(false);
  const [strategySettings, setStrategySettings] = useState({
    neutralization: 'Subindustry',
    decay: 4,
    truncation: 0.08,
    pasteurization: 'On',
    nanHandling: 'Off',
    maxTrade: 'Off',
    delay: 1,
    commission: 0.001,
    bookSize: 1000000,
    minWeight: 0.01,
    maxWeight: 0.05,
    rebalanceFreq: 'Daily'
  });

  const handleDataUpload = () => {
    setIsDataUploaded(true);
    setPnlData(null);
    setMetrics(null);
  };

  const handleAlphaResult = (result) => {
    setPnlData(result.pnl_data);
    setMetrics(result.metrics);
  };

  const handleSettingsChange = (newSettings) => {
    setStrategySettings(newSettings);
  };

  const toggleSettings = () => {
    setSettingsOpen(!settingsOpen);
  };

  const toggleDataUpload = () => {
    setDataUploadOpen(!dataUploadOpen);
  };

  return (
    <div className="simulate-container">
      <div className="main-content">
        <div className="left-panel">
          <div className="panel-controls">
            <Settings
              onSettingsChange={handleSettingsChange}
              isOpen={settingsOpen}
              onToggle={toggleSettings}
            />
            <DataUpload
              onDataUploaded={handleDataUpload}
              isOpen={dataUploadOpen}
              onToggle={toggleDataUpload}
            />
          </div>
          <AlphaFormula
            onResult={handleAlphaResult}
            isDataUploaded={isDataUploaded}
            setLoading={setLoading}
            strategySettings={strategySettings}
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

export default Simulate;