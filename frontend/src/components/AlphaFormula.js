// frontend/src/components/AlphaFormula.js
import React, { useState } from 'react';
import axios from 'axios';

const AlphaFormula = ({ onResult, isDataUploaded, setLoading, strategySettings }) => {
  const [formula, setFormula] = useState('');
  const [error, setError] = useState(null);

  const exampleFormulas = [
    'Close / (Close - 0.00000001)',
    'Rank(Delta(Close, 1))',
    'Rank(Ts_rank(Close, 5) * Ts_rank(Volume, 10))',
    'Delta(Close, 1) / Close',
    'Rank(High - Low)',
    'Sum(Volume, 5) / Volume',
    'Abs(Delta(Close, 2))',
    'Sqrt(Volume / Sum(Volume, 10))',
    'Rank(Vwap - Close)'
  ];

  const handleSubmit = async () => {
    if (!formula.trim()) {
      setError('Please enter an alpha formula');
      return;
    }

    if (!isDataUploaded) {
      setError('Please upload data first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/calculate-alpha/', {
        alpha_formula: formula,
        settings: strategySettings
      });

      onResult(response.data);
    } catch (error) {
      setError(error.response?.data?.error || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleFormula) => {
    setFormula(exampleFormula);
    setError(null);
  };

  return (
    <div className="alpha-formula-container">
      <h2>Alpha Formula</h2>
      
      <textarea
        className="formula-input"
        value={formula}
        onChange={(e) => setFormula(e.target.value)}
        placeholder="Enter your alpha formula here...
Example: Close / (Close - 0.00000001)

Available functions:
- Rank(x): Ranks values
- Delta(x, n): Difference with n periods ago
- Sum(x, n): Rolling sum over n periods
- Abs(x): Absolute values
- Sqrt(x): Square root
- Ts_rank(x, n): Time series rank
- Ts_argmax(x, n): Time series argmax
- quantile(x, driver='gaussian', sigma=1.0): Apply distribution transformation
  * driver: 'gaussian', 'uniform', 'cauchy'
  * sigma: scale parameter

Available variables:
- Open, High, Low, Close, Volume, Vwap"
      />
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <button 
        className="submit-button"
        onClick={handleSubmit}
        disabled={!formula.trim() || !isDataUploaded}
      >
        Calculate Alpha
      </button>

      <div className="formula-examples">
        <h3>Example Formulas (click to use):</h3>
        <ul>
          {exampleFormulas.map((example, index) => (
            <li 
              key={index} 
              onClick={() => handleExampleClick(example)}
              title="Click to use this formula"
            >
              {example}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default AlphaFormula;