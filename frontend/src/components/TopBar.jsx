import React, { useState, useEffect } from 'react';
import { Cpu, Factory, Clock, Globe, AlertTriangle, Radio } from 'lucide-react';

const TopBar = ({ backendStatus, statusData, currentData, unitSystem, setUnitSystem }) => {
  const [timeStr, setTimeStr] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeStr(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const dataSource = currentData?.data_source || statusData?.data_source || 'SIMULATION';
  const isOfflineAlarm = Boolean(currentData?.real_telemetry_offline_alarm || statusData?.real_telemetry_offline_alarm);

  return (
    <header className="bg-slate-900 text-white px-5 py-2.5 shadow-md flex items-center justify-between text-xs sm:text-sm font-medium border-b border-slate-800 shrink-0 select-none">
      <div className="flex items-center space-x-4 sm:space-x-6">
        <div className="flex items-center space-x-2">
          <span className="bg-blue-600 text-white px-2 py-0.5 rounded text-[11px] font-bold tracking-wide">ASSET</span>
          <span className="font-mono font-bold text-slate-100">{currentData?.machine_id || statusData?.active_machine_id || 'MCH-802X'}</span>
        </div>

        <div className="hidden md:flex items-center space-x-1.5 text-slate-300 text-xs">
          <Factory className="w-3.5 h-3.5 text-blue-400" />
          <span className="font-medium">{currentData?.machine_name || statusData?.machine_name || 'Turbine Motor Unit A1'}</span>
        </div>

        <div className="hidden lg:flex items-center space-x-1.5 text-slate-400 text-xs">
          <span className="text-slate-500">Location:</span>
          <span>{currentData?.location || statusData?.location || 'Power Gen Bay 4'}</span>
        </div>
      </div>

      <div className="flex items-center space-x-3 sm:space-x-5">
        {/* Watchdog Communication Offline Alarm */}
        {isOfflineAlarm && (
          <div className="flex items-center gap-1.5 px-3 py-1 bg-red-600/90 text-white font-bold text-xs rounded-full animate-bounce shadow-md border border-red-400">
            <AlertTriangle className="w-4 h-4" />
            <span>REAL TELEMETRY OFFLINE</span>
          </div>
        )}

        {/* Operating Mode Indicator (Section 30 requirement) */}
        <div
          className={`hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-full border text-[11px] font-bold ${
            dataSource === 'REAL INDUSTRIAL DATA'
              ? 'bg-emerald-950/80 border-emerald-500 text-emerald-300'
              : (dataSource === 'HISTORICAL REPLAY' ? 'bg-purple-950/80 border-purple-500 text-purple-300' : 'bg-amber-950/80 border-amber-500 text-amber-300')
          }`}
        >
          <span className={`w-2 h-2 rounded-full ${dataSource === 'REAL INDUSTRIAL DATA' ? 'bg-emerald-400 animate-ping' : 'bg-amber-400'}`}></span>
          <span className="tracking-wide uppercase font-mono">{dataSource}</span>
        </div>

        {/* Unit Scale Switcher */}
        <div className="flex items-center bg-slate-800 p-0.5 rounded-lg border border-slate-700 text-[11px]">
          <button
            onClick={() => setUnitSystem('metric')}
            className={`px-2 py-1 rounded-md font-semibold transition-all ${
              unitSystem === 'metric' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-300 hover:text-white'
            }`}
            title="Metric: °C, mm/s, bar"
          >
            Metric (°C)
          </button>
          <button
            onClick={() => setUnitSystem('imperial')}
            className={`px-2 py-1 rounded-md font-semibold transition-all ${
              unitSystem === 'imperial' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-300 hover:text-white'
            }`}
            title="Imperial: °F, ips, psi"
          >
            Imperial (°F)
          </button>
        </div>

        {/* Active Model & Version */}
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

        {/* Backend Connectivity Status */}
        <div className="flex items-center space-x-2 bg-slate-800 px-2.5 py-1 rounded-full border border-slate-700">
          <span className={`w-2 h-2 rounded-full ${backendStatus ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></span>
          <span className="text-[11px] text-slate-300 font-medium">{backendStatus ? 'ONLINE' : 'DISCONNECTED'}</span>
        </div>
      </div>
    </header>
  );
};

export default TopBar;
