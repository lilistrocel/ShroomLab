import { useState, useEffect } from 'react';

export default function Home() {
  const [apiStatus, setApiStatus] = useState('Checking...');

  useEffect(() => {
    // Check API Gateway health
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setApiStatus('Connected ✅'))
      .catch(() => setApiStatus('Disconnected ❌'));
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🍄 ShroomLab Management System</h1>
      <div style={{ 
        background: '#f5f5f5', 
        padding: '20px', 
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h2>System Status</h2>
        <p><strong>API Gateway:</strong> {apiStatus}</p>
        <p><strong>Frontend:</strong> Running ✅</p>
      </div>
      
      <div style={{ 
        background: '#e8f5e8', 
        padding: '20px', 
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h2>🚀 Welcome to ShroomLab!</h2>
        <p>Your comprehensive mushroom farm management system is ready.</p>
        <ul>
          <li>✅ Microservices Architecture</li>
          <li>✅ Real-time IoT Monitoring</li>
          <li>✅ Production Management</li>
          <li>✅ Business Operations</li>
          <li>✅ Analytics & Reporting</li>
        </ul>
      </div>

      <div style={{ 
        background: '#fff3cd', 
        padding: '20px', 
        borderRadius: '8px',
        border: '1px solid #ffeaa7'
      }}>
        <h3>🔗 Quick Links</h3>
        <ul>
          <li><a href="http://localhost:8000/docs" target="_blank">API Documentation</a></li>
          <li><a href="http://localhost:8086" target="_blank">InfluxDB UI</a></li>
          <li><strong>Default Login:</strong> admin / admin123</li>
        </ul>
      </div>

      <div style={{ marginTop: '30px', textAlign: 'center', color: '#666' }}>
        <p>ShroomLab v1.0.0 - Phase 1 Complete</p>
      </div>
    </div>
  );
} 