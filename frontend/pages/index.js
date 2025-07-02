import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function Home() {
  const [apiStatus, setApiStatus] = useState('Checking...');
  const router = useRouter();

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
      router.push('/dashboard');
      return;
    }

    // Check API Gateway health
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setApiStatus('Connected ✅'))
      .catch(() => setApiStatus('Disconnected ❌'));
  }, []);

  const handleLoginRedirect = () => {
    router.push('/login');
  };

  const handleDashboardRedirect = () => {
    router.push('/dashboard');
  };

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
        
        <div style={{ marginTop: '20px' }}>
          <button 
            onClick={handleLoginRedirect}
            style={{
              backgroundColor: '#059669',
              color: 'white',
              padding: '12px 24px',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              cursor: 'pointer',
              marginRight: '10px'
            }}
          >
            Go to Login
          </button>
          <button 
            onClick={handleDashboardRedirect}
            style={{
              backgroundColor: '#2563eb',
              color: 'white',
              padding: '12px 24px',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              cursor: 'pointer'
            }}
          >
            Go to Dashboard
          </button>
        </div>
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
          <li><strong>Admin:</strong> admin / admin123</li>
          <li><strong>Super Admin:</strong> superadmin / superadmin123</li>
        </ul>
      </div>

      <div style={{ marginTop: '30px', textAlign: 'center', color: '#666' }}>
        <p>ShroomLab v1.0.0 - Phase 1 Complete</p>
      </div>
    </div>
  );
} 