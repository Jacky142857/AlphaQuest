import React, { useState, useRef, useEffect } from 'react';
import AceEditor from 'react-ace';
import { useTheme } from '../contexts/ThemeContext';

// Import ACE editor modes and themes
import 'ace-builds/src-noconflict/theme-monokai';
import 'ace-builds/src-noconflict/theme-github';
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/ext-language_tools';

const AlphaFormulaEditor = ({
  value,
  onChange,
  onSubmit,
  isDataUploaded,
  loading
}) => {
  const { isDarkMode } = useTheme();
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const editorRef = useRef(null);

  // Define available functions and variables for autocomplete
  const alphaFunctions = [
    'Rank', 'Delta', 'Sum', 'Abs', 'Sqrt',
    'Ts_rank', 'Ts_argmax', 'quantile'
  ];

  const alphaVariables = [
    'Open', 'Close', 'High', 'Low', 'Volume', 'Vwap'
  ];

  const alphaParameters = [
    'driver=gaussian', 'driver=uniform', 'driver=cauchy',
    'sigma=0.5', 'sigma=1.0', 'sigma=2.0'
  ];

  // Custom completions for ACE editor
  useEffect(() => {
    const editor = editorRef.current?.editor;
    if (!editor) return;

    // Add custom completions
    const completions = [
      ...alphaFunctions.map(func => ({
        name: func,
        value: `${func}()`,
        score: 1000,
        meta: "function",
        caption: func,
        snippet: func === 'quantile' ? 'quantile(${1:expression}, driver=${2:gaussian}, sigma=${3:0.5})' : `${func}(\${1:})`
      })),
      ...alphaVariables.map(variable => ({
        name: variable,
        value: variable,
        score: 900,
        meta: "variable",
        caption: variable
      })),
      ...alphaParameters.map(param => ({
        name: param,
        value: param,
        score: 800,
        meta: "parameter",
        caption: param
      }))
    ];

    editor.completers = [{
      getCompletions: (editor, session, pos, prefix, callback) => {
        callback(null, completions);
      }
    }];
  }, []);

  // Custom syntax validation
  const validateFormula = (formula) => {
    const errors = [];

    // Check for balanced parentheses
    let parenCount = 0;
    for (let char of formula) {
      if (char === '(') parenCount++;
      if (char === ')') parenCount--;
      if (parenCount < 0) {
        errors.push("Unmatched closing parenthesis");
        break;
      }
    }
    if (parenCount > 0) {
      errors.push("Unmatched opening parenthesis");
    }

    // Check for unknown functions
    const functionPattern = /([A-Za-z_][A-Za-z0-9_]*)\s*\(/g;
    let match;
    while ((match = functionPattern.exec(formula)) !== null) {
      const funcName = match[1];
      if (!alphaFunctions.includes(funcName) && !['min', 'max', 'abs', 'sqrt'].includes(funcName.toLowerCase())) {
        errors.push(`Unknown function: ${funcName}`);
      }
    }

    return errors;
  };

  const handleEditorChange = (newValue) => {
    onChange(newValue);

    // Validate in real-time
    const errors = validateFormula(newValue);
    const editor = editorRef.current?.editor;
    if (editor) {
      const session = editor.getSession();
      session.clearAnnotations();

      if (errors.length > 0) {
        const annotations = errors.map((error, index) => ({
          row: 0,
          column: 0,
          text: error,
          type: "error"
        }));
        session.setAnnotations(annotations);
      }
    }
  };

  const examples = [
    {
      title: "Simple Price Change",
      formula: "Rank(Close - Open)",
      description: "Ranks stocks by daily price change"
    },
    {
      title: "Volume-Weighted Returns",
      formula: "Rank((Close - Open) * Volume)",
      description: "Price change weighted by volume"
    },
    {
      title: "Mean Reversion",
      formula: "Rank(Open - Close)",
      description: "Contrarian signal based on daily gap"
    },
    {
      title: "Momentum Signal",
      formula: "Rank(Close - Delta(Close, 5))",
      description: "5-day price momentum"
    },
    {
      title: "Advanced Quantile",
      formula: "quantile(Close - Open, driver=gaussian, sigma=0.5)",
      description: "Gaussian-transformed daily returns"
    }
  ];

  return (
    <div className="alpha-formula-container">
      <h2>Alpha Formula Editor</h2>

      <div className="editor-container">
        <div className="editor-wrapper">
          <AceEditor
            ref={editorRef}
            mode="python"
            theme={isDarkMode ? "monokai" : "github"}
            onChange={handleEditorChange}
            value={value}
            name="alpha-formula-editor"
            width="100%"
            height="200px"
            fontSize={14}
            showPrintMargin={false}
            showGutter={true}
            highlightActiveLine={true}
            setOptions={{
              enableBasicAutocompletion: true,
              enableLiveAutocompletion: true,
              enableSnippets: true,
              showLineNumbers: true,
              tabSize: 2,
              wrap: true,
              useWorker: false
            }}
            placeholder="Enter your alpha formula here... (e.g., Rank(Close - Open))"
            commands={[
              {
                name: 'submit',
                bindKey: { win: 'Ctrl-Enter', mac: 'Cmd-Enter' },
                exec: () => {
                  if (!loading && isDataUploaded && value.trim()) {
                    onSubmit();
                  }
                }
              }
            ]}
          />
          <div className="editor-footer">
            <div className="editor-shortcuts">
              <span>💡 Press Ctrl+Space for suggestions</span>
              <span>⌨️ Ctrl+Enter to calculate</span>
            </div>
            <div className="editor-validation">
              {value && validateFormula(value).length === 0 && (
                <span className="validation-success">✓ Valid syntax</span>
              )}
            </div>
          </div>
        </div>

        <button
          className={`submit-button ${!isDataUploaded ? 'disabled' : ''}`}
          onClick={onSubmit}
          disabled={!isDataUploaded || loading || !value.trim()}
          title={!isDataUploaded ? "Please upload data first" : "Calculate alpha signal"}
        >
          {loading ? 'Calculating...' : 'Calculate Alpha'}
        </button>
      </div>

      <div className="formula-examples">
        <h3>Example Formulas</h3>
        <div className="examples-grid">
          {examples.map((example, index) => (
            <div
              key={index}
              className="example-card"
              onClick={() => onChange(example.formula)}
            >
              <div className="example-title">{example.title}</div>
              <code className="example-formula">{example.formula}</code>
              <div className="example-description">{example.description}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="formula-help">
        <h3>Available Functions</h3>
        <div className="help-grid">
          <div className="help-section">
            <h4>Mathematical Functions</h4>
            <ul>
              <li><code>Rank(x)</code> - Cross-sectional rank (0 to 1)</li>
              <li><code>Delta(x, n)</code> - Difference from n periods ago</li>
              <li><code>Sum(x, n)</code> - Rolling sum over n periods</li>
              <li><code>Abs(x)</code> - Absolute value</li>
              <li><code>Sqrt(x)</code> - Square root</li>
            </ul>
          </div>
          <div className="help-section">
            <h4>Time Series Functions</h4>
            <ul>
              <li><code>Ts_rank(x, n)</code> - Time-series rank</li>
              <li><code>Ts_argmax(x, n)</code> - Days since maximum</li>
              <li><code>quantile(x, driver, sigma)</code> - Distribution transform</li>
            </ul>
          </div>
          <div className="help-section">
            <h4>Market Data</h4>
            <ul>
              <li><code>Open</code> - Opening price</li>
              <li><code>Close</code> - Closing price</li>
              <li><code>High</code> - Highest price</li>
              <li><code>Low</code> - Lowest price</li>
              <li><code>Volume</code> - Trading volume</li>
              <li><code>Vwap</code> - Volume-weighted average price</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlphaFormulaEditor;