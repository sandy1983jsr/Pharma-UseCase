import React from 'react';

function App() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🏭 Lupin Pharma - Cost Reduction Platform</h1>
      <p>Platform Version: 1.0.0</p>
      <p>Status: <strong style={{ color: 'green' }}>✓ Operational</strong></p>
      
      <h2>Available Endpoints:</h2>
      <ul>
        <li><code>/health</code> - Platform health</li>
        <li><code>/api/dashboard/batches</code> - Batch data</li>
        <li><code>/api/reaction/optimize</code> - Reaction optimization</li>
        <li><code>/api/drying/optimize-endpoint</code> - Drying optimization</li>
      </ul>

      <h2>20+ AI Use Cases:</h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
        <div style={{ border: '1px solid #ddd', padding: '10px' }}>
          <h4>⚗️ Reaction Section</h4>
          <ul>
            <li>Endpoint prediction (30-90 min saved)</li>
            <li>Heat transfer fouling detection</li>
            <li>Agitator RPM optimization</li>
            <li>Catalyst deactivation warning</li>
          </ul>
        </div>
        <div style={{ border: '1px solid #ddd', padding: '10px' }}>
          <h4>💨 Drying</h4>
          <ul>
            <li>Endpoint prediction (15-25% energy)</li>
            <li>Vacuum optimization</li>
            <li>Over-drying prevention</li>
            <li>Heat recovery detection</li>
          </ul>
        </div>
      </div>

      <h2>Expected Savings:</h2>
      <ul>
        <li>Conservative: 5% Opex reduction = ₹5 Cr/year</li>
        <li>Aggressive: 12% Opex reduction = ₹12 Cr/year</li>
      </ul>
    </div>
  );
}

export default App;
