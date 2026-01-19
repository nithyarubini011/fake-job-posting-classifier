import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [domain, setDomain] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [animatedScore, setAnimatedScore] = useState(0);

  // Animate the score number when result changes
  useEffect(() => {
    if (result) {
      let start = 0;
      const end = result.risk_score;
      const duration = 1000;
      const startTime = performance.now();

      const animate = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease out cubic
        const ease = 1 - Math.pow(1 - progress, 3);
        
        setAnimatedScore(Math.floor(start + (end - start) * ease));

        if (progress < 1) {
          requestAnimationFrame(animate);
        }
      };

      requestAnimationFrame(animate);
    }
  }, [result]);

  const verifyInternship = async () => {
    if (!message && !domain) {
      alert("Please enter a domain or message to verify.");
      return;
    }
    
    setLoading(true);
    setResult(null); // Reset result for re-animation
    try {
      const res = await fetch("http://127.0.0.1:5000/api/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, domain })
      });

      const data = await res.json();
      setResult(data);
    } catch {
      alert("Backend not running or network error");
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevel = (score) => {
    if (score < 30) return "low";
    if (score < 60) return "medium";
    return "high";
  };

  const getGradientId = (score) => {
    const level = getRiskLevel(score);
    return `grad-${level}`;
  };
  
  const getVerdictStyle = (verdict) => {
    if (verdict === "Looks Legit") return "verdict-safe";
    if (verdict === "Suspicious") return "verdict-warning";
    return "verdict-danger";
  };

  // Gauge Calculations
  const radius = 80;
  const circumference = Math.PI * radius;
  const visualScore = result ? Math.min(result.risk_score, 100) : 0;
  const strokeDashoffset = circumference - (visualScore / 100) * circumference;

  return (
    <div className="app-container">
      {/* Background ambient glow */}
      <div className="ambient-glow glow-1"></div>
      <div className="ambient-glow glow-2"></div>

      <div className="content-wrapper">
        <div className="header">
          <div className="logo-badge">IS</div>
          <h1>InternShield <span className="highlight">AI</span></h1>
          <p>Internship Scam Detection Analytics</p>
        </div>

        <div className="main-card glass-panel">
          
          <div className="floating-group">
            <input
              id="domain"
              className="floating-input"
              placeholder=" "
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
            />
            <label htmlFor="domain" className="floating-label">Email or Company Domain</label>
            <div className="input-highlight"></div>
          </div>

          <div className="floating-group">
            <textarea
              id="message"
              className="floating-input"
              placeholder=" "
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={5}
            />
            <label htmlFor="message" className="floating-label">Internship Message Content</label>
            <div className="input-highlight"></div>
          </div>

          <button 
            className={`verify-btn ${loading ? 'loading' : ''}`}
            onClick={verifyInternship}
            disabled={loading}
          >
            <span className="btn-text">{loading ? "Analyzing..." : "Analyze Risk"}</span>
            <div className="btn-glow"></div>
          </button>

          {result && (
            <div className="result-dashboard">
              <div className="gauge-section">
                <div className="gauge-wrapper">
                  <svg className="gauge-svg" viewBox="0 0 200 110">
                    <defs>
                      <linearGradient id="grad-low" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#34d399" />
                        <stop offset="100%" stopColor="#10b981" />
                      </linearGradient>
                      <linearGradient id="grad-medium" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#fbbf24" />
                        <stop offset="100%" stopColor="#f59e0b" />
                      </linearGradient>
                      <linearGradient id="grad-high" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#f87171" />
                        <stop offset="100%" stopColor="#ef4444" />
                      </linearGradient>
                      <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                        <feMerge>
                          <feMergeNode in="coloredBlur" />
                          <feMergeNode in="SourceGraphic" />
                        </feMerge>
                      </filter>
                    </defs>
                    
                    {/* Background Arc */}
                    <path 
                      d="M 20 100 A 80 80 0 0 1 180 100" 
                      className="gauge-bg-arc" 
                    />
                    
                    {/* Value Arc */}
                    <path
                      d="M 20 100 A 80 80 0 0 1 180 100"
                      className="gauge-value-arc"
                      filter="url(#glow)"
                      style={{
                        strokeDasharray: circumference,
                        strokeDashoffset: strokeDashoffset,
                        stroke: `url(#${getGradientId(result.risk_score)})`
                      }}
                    />
                  </svg>
                  
                  <div className="gauge-content">
                     <div className={`score-display ${getRiskLevel(result.risk_score)}`}>
                       {animatedScore}
                     </div>
                     <div className="score-label">RISK SCORE</div>
                  </div>
                </div>
              </div>

              <div className="verdict-container">
                <div className={`verdict-badge ${getVerdictStyle(result.verdict)}`}>
                  {result.verdict}
                </div>
              </div>

              {result.reasons && result.reasons.length > 0 && (
                <div className="analysis-card">
                  <div className="card-header">
                    <span className="icon">⚠</span>
                    <span>Risk Factors Detected</span>
                  </div>
                  <ul className="analysis-list">
                    {result.reasons.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}
               
               {result.reasons && result.reasons.length === 0 && result.risk_score === 0 && (
                   <div className="analysis-card safe">
                      <div className="card-header">
                        <span className="icon">🛡</span>
                        <span>Safety Analysis</span>
                      </div>
                      <p className="safe-text">No evident risk factors found. Proceed with standard caution.</p>
                   </div>
               )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
