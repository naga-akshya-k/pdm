import React from 'react';
import {
  Factory,
  AlertOctagon,
  Cpu,
  ShieldAlert,
  Wrench,
  Play,
  Pause,
  SkipForward,
  RotateCcw,
  Sliders,
  Wifi,
  WifiOff,
  Activity,
  LineChart,
  GitCompare
} from 'lucide-react';
import StatusBadge from './StatusBadge';

const Sidebar = ({
  activeTab,
  setActiveTab,
  currentData,
  backendStatus,
  onControlAction,
  speed,
  setSpeed,
  autoPlay
}) => {
  const ewLevel = currentData?.early_warning?.early_warning_level || 'GREEN';

  const isTelemetry = activeTab === 'telemetry' || activeTab === 'dashboard';
  const isEvaluation = activeTab === 'evaluation' || activeTab === 'benchmark';
  const isAnalytics = activeTab === 'analytics' || activeTab === 'early_warning';
  const isDrift = activeTab === 'drift';
  const isMaintenance = activeTab === 'maintenance' || activeTab === 'workorders';

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col justify-between h-[calc(100vh-49px)] shadow-xs shrink-0 select-none">
      <div className="p-3.5 space-y-4 overflow-y-auto">
        {/* Title */}
        <div>
          <h1 className="text-sm font-bold text-gray-900 tracking-tight flex items-center space-x-2">
            <Factory className="w-4 h-4 text-blue-600" />
            <span>Industrial PdM Platform</span>
          </h1>
          <p className="text-[11px] text-gray-400">Turbine Motor Condition Intelligence</p>
        </div>

        {/* Navigation Tabs */}
        <nav className="space-y-1">
          {/* 1. Model Telemetry */}
          <button
            onClick={() => setActiveTab('telemetry')}
            className={`w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-lg text-xs font-semibold transition-colors ${
              isTelemetry
                ? 'bg-blue-50 text-blue-700 border border-blue-200 font-bold shadow-xs'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <Activity className="w-4 h-4 text-blue-600 shrink-0" />
            <div className="flex flex-col text-left">
              <span>Model Telemetry</span>
              <span className="text-[10px] text-gray-400 font-normal">Real-Time SCADA Ingress</span>
            </div>
          </button>

          {/* 2. Model Evaluation */}
          <button
            onClick={() => setActiveTab('evaluation')}
            className={`w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-lg text-xs font-semibold transition-colors ${
              isEvaluation
                ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold shadow-xs'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <Cpu className="w-4 h-4 text-indigo-600 shrink-0" />
            <div className="flex flex-col text-left">
              <span>Model Evaluation</span>
              <span className="text-[10px] text-gray-400 font-normal">Algorithm Benchmarking</span>
            </div>
          </button>

          {/* 3. Analytics */}
          <button
            onClick={() => setActiveTab('analytics')}
            className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition-colors ${
              isAnalytics
                ? 'bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold shadow-xs'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center space-x-2.5">
              <LineChart className="w-4 h-4 text-emerald-600 shrink-0" />
              <div className="flex flex-col text-left">
                <span>Analytics</span>
                <span className="text-[10px] text-gray-400 font-normal">ISO 10816 & P-F Curve</span>
              </div>
            </div>
            {ewLevel !== 'GREEN' && (
              <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
            )}
          </button>

          {/* 4. Model Drifting */}
          <button
            onClick={() => setActiveTab('drift')}
            className={`w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-lg text-xs font-semibold transition-colors ${
              isDrift
                ? 'bg-amber-50 text-amber-700 border border-amber-200 font-bold shadow-xs'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <GitCompare className="w-4 h-4 text-amber-600 shrink-0" />
            <div className="flex flex-col text-left">
              <span>Model Drifting</span>
              <span className="text-[10px] text-gray-400 font-normal">PSI & Statistical Shifts</span>
            </div>
          </button>

          {/* 5. Maintenance Actions */}
          <button
            onClick={() => setActiveTab('maintenance')}
            className={`w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-lg text-xs font-semibold transition-colors ${
              isMaintenance
                ? 'bg-slate-100 text-slate-900 border border-slate-300 font-bold shadow-xs'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <Wrench className="w-4 h-4 text-slate-700 shrink-0" />
            <div className="flex flex-col text-left">
              <span>Maintenance Actions</span>
              <span className="text-[10px] text-gray-400 font-normal">CMMS Work Orders</span>
            </div>
          </button>
        </nav>

        {/* Active Machine Status Card */}
        <div className="bg-gray-50 rounded-xl p-3 border border-gray-200 space-y-2">
          <div className="flex items-center justify-between text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
            <span>Target Unit</span>
            <span className="font-mono text-blue-700">{currentData?.machine_id || 'MCH-802X'}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-800 line-clamp-1">{currentData?.machine_name || 'Turbine A1'}</span>
            <StatusBadge status={currentData?.machine_status || 'Healthy'} />
          </div>
          <div className="flex items-center justify-between text-xs text-gray-600 pt-1.5 border-t border-gray-200">
            <span>Overall Health</span>
            <span className="font-bold text-gray-900 font-mono">{currentData?.machine_health ?? 100}%</span>
          </div>
        </div>

        {/* Simulation Controls */}
        <div className="space-y-2.5 pt-2 border-t border-gray-200">
          <div className="text-[11px] font-bold text-gray-700 uppercase tracking-wider flex items-center space-x-1">
            <Sliders className="w-3 h-3 text-gray-500" />
            <span>SCADA Clock Loop</span>
          </div>

          <div className="grid grid-cols-2 gap-1.5">
            <button
              onClick={() => onControlAction('start')}
              className={`flex items-center justify-center space-x-1 py-1.5 px-2 rounded-lg text-xs font-semibold transition ${
                autoPlay ? 'bg-emerald-600 text-white shadow-xs' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Play className="w-3 h-3" />
              <span>Start</span>
            </button>
            <button
              onClick={() => onControlAction('pause')}
              className={`flex items-center justify-center space-x-1 py-1.5 px-2 rounded-lg text-xs font-semibold transition ${
                !autoPlay ? 'bg-amber-600 text-white shadow-xs' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Pause className="w-3 h-3" />
              <span>Pause</span>
            </button>
          </div>

          <div className="grid grid-cols-2 gap-1.5">
            <button
              onClick={() => onControlAction('next')}
              className="flex items-center justify-center space-x-1 py-1.5 px-2 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 text-xs font-semibold border border-blue-200"
            >
              <SkipForward className="w-3 h-3" />
              <span>Step 1d</span>
            </button>
            <button
              onClick={() => onControlAction('reset')}
              className="flex items-center justify-center space-x-1 py-1.5 px-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 text-xs font-semibold"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset</span>
            </button>
          </div>

          {/* Speed Slider */}
          <div className="space-y-1 pt-1">
            <div className="flex justify-between text-[11px] text-gray-600">
              <span>Sampling Speed</span>
              <span className="font-semibold text-gray-900">{speed}s</span>
            </div>
            <input
              type="range"
              min="0.1"
              max="3.0"
              step="0.1"
              value={speed}
              onChange={(e) => {
                const val = parseFloat(e.target.value);
                setSpeed(val);
                onControlAction('set_speed', val);
              }}
              className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
          </div>
        </div>
      </div>

      {/* Footer Connection Status */}
      <div className="p-3 border-t border-gray-200 bg-gray-50/50">
        <div className="flex items-center space-x-2 text-xs">
          {backendStatus ? (
            <Wifi className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          ) : (
            <WifiOff className="w-4 h-4 text-red-600 flex-shrink-0" />
          )}
          <div className="flex flex-col">
            <span className="font-semibold text-gray-800 text-[11px]">
              {backendStatus ? 'FastAPI Backend Online' : 'Backend Disconnected'}
            </span>
            <span className="text-[9px] text-gray-400">1000ms Async Polling</span>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
