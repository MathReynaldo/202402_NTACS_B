import { useState, useEffect } from "react";
// import { invoke } from "@tauri-apps/api/core"; // Descomentaremos cuando Tauri funcione

function App() {
  const [healthScore, setHealthScore] = useState(100);
  const [isScanning, setIsScanning] = useState(false);
  
  // Simulación de estadísticas en tiempo real
  const [cpuUsage, setCpuUsage] = useState(45);
  const [ramUsage, setRamUsage] = useState(60);

  useEffect(() => {
    const interval = setInterval(() => {
      setCpuUsage(prev => Math.max(10, Math.min(100, prev + (Math.random() * 10 - 5))));
      setRamUsage(prev => Math.max(20, Math.min(100, prev + (Math.random() * 4 - 2))));
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  const handleScan = async () => {
    setIsScanning(true);
    // Simulación de escaneo. Aquí llamaríamos a invoke('run_deep_scan')
    setTimeout(() => {
      setIsScanning(false);
      setHealthScore(98);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-cyber-bg text-cyber-text p-6 font-mono flex flex-col w-full">
      {/* Header */}
      <header className="flex justify-between items-center mb-8 border-b border-cyber-accent/30 pb-4">
        <div>
          <h1 className="text-3xl font-bold tracking-wider text-cyber-accent drop-shadow-[0_0_10px_rgba(0,240,255,0.8)]">
            NEX-PULSE
          </h1>
          <p className="text-sm text-cyber-accent/70 uppercase tracking-[0.2em] mt-1">AI Optimizer Core</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-xs text-cyber-text/50 uppercase">System Status</p>
            <p className={`text-xl font-bold ${healthScore > 80 ? 'text-green-400' : 'text-cyber-secondary'}`}>
              {healthScore}% OPTIMAL
            </p>
          </div>
          <div className="w-16 h-16 rounded-full border-2 border-cyber-accent flex items-center justify-center relative shadow-[0_0_15px_rgba(0,240,255,0.4)]">
            <span className="text-2xl">{healthScore}</span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 flex-1">
        {/* Left Panel - Metrics */}
        <div className="md:col-span-2 flex flex-col gap-6">
          <div className="bg-cyber-surface border border-cyber-accent/20 p-6 rounded-lg relative overflow-hidden backdrop-blur-md bg-opacity-80">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyber-accent to-transparent opacity-50"></div>
            <h2 className="text-lg uppercase tracking-widest text-cyber-accent mb-6 flex items-center gap-2">
              <span className="w-2 h-2 bg-cyber-accent rounded-full animate-pulse"></span>
              Live Telemetry
            </h2>
            
            <div className="space-y-6">
              {/* CPU Bar */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-cyber-text/80">CPU CORE STRESS</span>
                  <span className="text-sm font-bold text-cyber-accent">{cpuUsage.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-cyber-bg h-4 rounded-full overflow-hidden border border-cyber-accent/20">
                  <div 
                    className="h-full bg-cyber-accent transition-all duration-500 ease-out shadow-[0_0_10px_rgba(0,240,255,0.8)]"
                    style={{ width: `${cpuUsage}%` }}
                  ></div>
                </div>
              </div>

              {/* RAM Bar */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-cyber-text/80">MEMORY ALLOCATION</span>
                  <span className="text-sm font-bold text-cyber-accent">{ramUsage.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-cyber-bg h-4 rounded-full overflow-hidden border border-cyber-accent/20">
                  <div 
                    className={`h-full transition-all duration-500 ease-out shadow-[0_0_10px_currentColor] ${ramUsage > 80 ? 'bg-cyber-secondary' : 'bg-[#00FF66]'}`}
                    style={{ width: `${ramUsage}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Action Area */}
          <div className="bg-cyber-surface border border-cyber-accent/20 p-6 rounded-lg flex items-center justify-between mt-auto">
            <div>
              <h3 className="text-xl font-bold text-white mb-1">Deep Disk Scan</h3>
              <p className="text-sm text-cyber-text/60">Initialize MFT direct access via Rust kernel</p>
            </div>
            <button 
              onClick={handleScan}
              disabled={isScanning}
              className={`px-8 py-4 uppercase tracking-widest font-bold border-2 transition-all duration-300
                ${isScanning 
                  ? 'border-cyber-secondary text-cyber-secondary bg-cyber-secondary/10 cursor-not-allowed' 
                  : 'border-cyber-accent text-cyber-accent hover:bg-cyber-accent hover:text-cyber-bg shadow-[0_0_15px_rgba(0,240,255,0.4)] hover:shadow-[0_0_30px_rgba(0,240,255,0.8)]'
                }
              `}
            >
              {isScanning ? 'Scanning MFT...' : 'Initiate Purge'}
            </button>
          </div>
        </div>

        {/* Right Panel - Logs */}
        <div className="bg-cyber-surface border border-cyber-accent/20 p-6 rounded-lg flex flex-col">
          <h2 className="text-sm uppercase tracking-widest text-cyber-text/60 mb-4 border-b border-cyber-text/10 pb-2">
            System Events
          </h2>
          <div className="flex-1 space-y-3 overflow-y-auto pr-2 text-xs">
            <div className="flex gap-2">
              <span className="text-cyber-accent">[SYS]</span>
              <span className="text-cyber-text/80">Core engine initialized</span>
            </div>
            <div className="flex gap-2">
              <span className="text-cyber-accent">[NET]</span>
              <span className="text-cyber-text/80">Telemetry sync optimal</span>
            </div>
            {isScanning && (
              <div className="flex gap-2 animate-pulse">
                <span className="text-cyber-secondary">[IO]</span>
                <span className="text-cyber-secondary">Accessing Master File Table...</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
