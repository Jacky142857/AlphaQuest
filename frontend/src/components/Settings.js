// frontend/src/components/Settings.js
import React, { useState, useEffect } from 'react';
import { useNotification } from '../contexts/NotificationContext';
import './Settings.css';

const Settings = ({ onSettingsChange, isOpen, onToggle }) => {
  const { showNotification } = useNotification();
  const [settings, setSettings] = useState({
    neutralization: false,
    decay: 0,
    truncation: 0.08,
    delay: 1
  });

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

  const handleSettingChange = (key, value) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    onSettingsChange(newSettings);
  };

  const handleApplySettings = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/update-settings/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Settings updated successfully:', result);

        // Close the settings window
        onToggle();

        // Show custom success notification
        showNotification('Settings applied successfully! Your strategy configuration has been updated.', 'success', 5000);
      } else {
        console.error('Failed to update settings');
        showNotification('Failed to update settings. Please try again.', 'error', 6000);
      }
    } catch (error) {
      console.error('Error updating settings:', error);
      showNotification('Error updating settings. Please check your connection and try again.', 'error', 6000);
    }
  };

  return (
    <>
      <button className="settings-toggle-btn" onClick={onToggle}>
        ⚙️ Settings
      </button>

      {isOpen && (
        <div className="settings-overlay" onClick={onToggle}>
          <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
      <div className="settings-header">
        <h3>Strategy Settings</h3>
        <button className="settings-close-btn" onClick={onToggle}>×</button>
      </div>

      <div className="settings-content">
        <div className="settings-row">
          <div className="setting-group">
            <label className="setting-label">
              MARKET NEUTRALIZATION ⓘ
            </label>
            <select
              className="setting-select"
              value={settings.neutralization ? "On" : "Off"}
              onChange={(e) => handleSettingChange('neutralization', e.target.value === "On")}
            >
              <option value="Off">Off</option>
              <option value="On">On</option>
            </select>
          </div>

          <div className="setting-group">
            <label className="setting-label">
              DECAY ⓘ
            </label>
            <div className="setting-slider">
              <input
                type="range"
                min="0"
                max="10"
                value={settings.decay}
                onChange={(e) => handleSettingChange('decay', parseInt(e.target.value))}
                className="slider"
              />
              <span className="slider-value">{settings.decay}</span>
            </div>
          </div>
        </div>

        <div className="settings-row">
          <div className="setting-group">
            <label className="setting-label">
              TRUNCATION ⓘ
            </label>
            <div className="setting-slider">
              <input
                type="range"
                min="0"
                max="0.2"
                step="0.01"
                value={settings.truncation}
                onChange={(e) => handleSettingChange('truncation', parseFloat(e.target.value))}
                className="slider"
              />
              <span className="slider-value">{(settings.truncation * 100).toFixed(0)}%</span>
            </div>
          </div>

          <div className="setting-group">
            <label className="setting-label">
              DELAY (DAYS) ⓘ
            </label>
            <div className="setting-slider">
              <input
                type="range"
                min="0"
                max="5"
                value={settings.delay}
                onChange={(e) => handleSettingChange('delay', parseInt(e.target.value))}
                className="slider"
              />
              <span className="slider-value">{settings.delay}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="settings-footer">
        <button className="settings-default-btn">
          Save as Default
        </button>
        <button className="settings-apply-btn" onClick={handleApplySettings}>
          Apply
        </button>
      </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Settings;