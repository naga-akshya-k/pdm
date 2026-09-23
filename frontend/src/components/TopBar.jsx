import React, { useState, useEffect } from 'react';
import { Cpu, Factory, Clock, Globe, Layers } from 'lucide-react';

const TopBar = ({ backendStatus, statusData, currentData, unitSystem, setUnitSystem }) => {
  const [timeStr, setTimeStr] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeStr(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="bg-slate-900 text-white px-5 py-2.5 shadow-md flex items-center justify-between text-xs sm:text-sm font-medium border-b border-slate-800 shrink-0 select-none">
      <div className="flex items-center space-x-4 sm:space-x-6">
        <div className="flex items-center space-x-2">
          <span className="bg-blue-600 text-white px-2 py-0.5 rounded text-[11px] font-bold tracking-wide">PLANT FLEET</span>
          <span className="font-mono font-bold text-slate-100">{currentData?.machine_id || statusData?.active_machine_id || 'MCH-802X'}</span>
        </div>

        <div className="hidden md:flex items-center space-x-1.5 text-slate-300 text-xs">
          <Factory className="w-3.5 h-3.5 text-blue-400" />
          <span className="font-medium">{currentData?.machine_name || statusData?.machine_name || 'Turbine Motor Unit A1'}</span>
        </div>

        <div className="hidden lg:flex items-center space-x-1.5 text-slate-400 text-xs">
          <span className="text-slate-500">Location:</span>
          <span>{currentData?.location || statusData?.location || 'Bay 4'}</span>
        </div>
      </div>

      <div className="flex items-center space-x-3 sm:space-x-5">
        {/* Universal Industrial Unit Normalization Switcher */}
        <div className="flex items-center bg-slate-800 p-0.5 rounded-lg border border-slate-700 text-[11px]">
          <span className="px-2 text-slate-400 hidden sm:inline flex items-center gap-1">
            <Globe className="w-3 h-3 text-slate-400" /> Scale:
          </span>
          <button
            onClick={() => setUnitSystem('metric')}
            className={`px-2 py-1 rounded-md font-semibold transition-all ${
              unitSystem === 'metric' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-300 hover:text-white'
            }`}
            title="Metric / SI: Celsius (°C), mm/s, bar, kN"
          >
            Metric (°C)
          </button>
          <button
            onClick={() => setUnitSystem('imperial')}
            className={`px-2 py-1 rounded-md font-semibold transition-all ${
              unitSystem === 'imperial' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-300 hover:text-white'
            }`}
            title="Imperial / US Customary: Fahrenheit (°F), in/s (ips), psi, lbf"
          >
            Imperial (°F)
          </button>
          <button
            onClick={() => setUnitSystem('normalized')}
            className={`px-2 py-1 rounded-md font-semibold transition-all ${
              unitSystem === 'normalized' ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-300 hover:text-white'
            }`}
            title="Dimensionless Z-Score: Zero-centered standard deviations [-3σ, +3σ]"
          >
            Z-Score (σ)
          </button>
        </div>

        {/* Active AI Model Pill */}
        <div className="hidden sm:flex items-center space-x-1.5 bg-slate-800/80 px-2.5 py-1 rounded-lg border border-slate-700 text-xs">
          <Cpu className="w-3.5 h-3.5 text-indigo-400" />
          <span className="text-slate-300 font-semibold">{currentData?.active_ai_model || statusData?.active_ai_model || 'Random Forest'}</span>
          <span className="text-[10px] text-indigo-400 font-mono font-bold px-1 rounded bg-indigo-950/80">v{currentData?.model_version || statusData?.model_version || '1.0'}</span>
        </div>

        {/* Live Clock */}
        <div className="hidden md:flex items-center space-x-1.5 text-slate-300 font-mono text-xs">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>{timeStr}</span>
        </div>

        {/* Data Source & MQTT Ingestion Indicator */}
        <div
          className={`hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-full border text-[11px] font-bold ${
            currentData?.mqtt_live
              ? 'bg-emerald-950/80 border-emerald-500 text-emerald-300'
              : 'bg-slate-800/90 border-slate-700 text-slate-300'
          }`}
          title={
            currentData?.mqtt_live
              ? `Live Ingestion from Workstation GPU via MQTT (Interval: ${currentData?.mqtt_delta_t_ms || 1000}ms)`
              : 'Physics-Based Digital Twin SCADA Simulation'
          }
        >
          <span className={`w-2 h-2 rounded-full ${currentData?.mqtt_live ? 'bg-emerald-400 animate-ping' : 'bg-amber-400'}`}></span>
          <span>{currentData?.mqtt_live ? `MQTT GPU LIVE [${Math.round(currentData?.mqtt_delta_t_ms || 1000)}ms]` : 'SIMULATION'}</span>
        </div>

        {/* Backend Status Indicator */}
        <div className="flex items-center space-x-2 bg-slate-800 px-2.5 py-1 rounded-full border border-slate-700">
          <span className={`w-2 h-2 rounded-full ${backendStatus ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></span>
          <span className="text-[11px] font-bold text-slate-200">{backendStatus ? 'ONLINE' : 'OFFLINE'}</span>
        </div>
      </div>
    </header>
  );
};

export default TopBar;
