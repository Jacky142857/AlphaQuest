// frontend/src/components/AlphaFormula.js
import React, { useState } from 'react';
import axios from 'axios';
import { createApiUrl } from '../config/api';
import AlphaFormulaEditor from './AlphaFormulaEditor';
import './AlphaFormulaEditor.css';

const AlphaFormula = ({ onResult, isDataUploaded, setLoading, strategySettings, onFormulaChange }) => {
  const [formula, setFormula] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLocalLoading] = useState(false);

  const handleSubmit = async () => {
    if (!formula.trim()) {
      setError('Please enter an alpha formula');
      return;
    }

    if (!isDataUploaded) {
      setError('Please upload data first');
      return;
    }

    setLocalLoading(true);
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(createApiUrl('/api/calculate-alpha/'), {
        alpha_formula: formula,
        settings: strategySettings
      });

      // Include the formula with the result
      onResult({
        ...response.data,
        formula: formula
      });
      setError(null);
    } catch (error) {
      setError(error.response?.data?.error || 'Calculation failed');
    } finally {
      setLocalLoading(false);
      setLoading(false);
    }
  };

  const handleFormulaChange = (newFormula) => {
    setFormula(newFormula);
    if (error) setError(null); // Clear error when user starts typing
    if (onFormulaChange) {
      onFormulaChange(newFormula.trim().length > 0);
    }
  };

  return (
    <div>
      <AlphaFormulaEditor
        value={formula}
        onChange={handleFormulaChange}
        onSubmit={handleSubmit}
        isDataUploaded={isDataUploaded}
        loading={loading}
      />

      {error && (
        <div className="calculation-error">
          <div className="error-icon">❌</div>
          <div className="error-content">
            <div className="error-title">Calculation Error</div>
            <div className="error-message">{error}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlphaFormula;