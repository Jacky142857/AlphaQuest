// frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { AuthProvider } from './contexts/AuthContext';
import './App.css';
import Navigation from './components/Navigation';
import Simulate from './components/Simulate';
import Learn from './components/Learn';
import MyAlphas from './components/MyAlphas';
import LoginModal from './components/LoginModal';

function App() {
  return (
    <ThemeProvider>
      <NotificationProvider>
        <AuthProvider>
          <Router>
            <div className="App">
              <Navigation />

              <div className="app-content">
                <Routes>
                  <Route path="/" element={<Navigate to="/simulate" replace />} />
                  <Route path="/simulate" element={<Simulate />} />
                  <Route path="/learn/*" element={<Learn />} />
                  <Route path="/my-alphas" element={<MyAlphas />} />
                </Routes>
              </div>

              <LoginModal />
            </div>
          </Router>
        </AuthProvider>
      </NotificationProvider>
    </ThemeProvider>
  );
}

export default App;