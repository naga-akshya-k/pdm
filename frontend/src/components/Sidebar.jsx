import React from 'react';
import {
  Factory,
  AlertOctagon,
  LayoutDashboard,
  Cpu,
  ShieldAlert,
  Sparkles,
  Wrench,
  Play,
  Pause,
  SkipForward,
  RotateCcw,
  Sliders,
  Wifi,
  WifiOff
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

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col justify-between h-[calc(100vh-49px)] shadow-xs shrink-0 select-none">
      <div className="p-3.5 space-y-4 overflow-y-auto">
        {/* Title */}
        <div>
          <h1 className="text-sm font-bold text-gray-900 tracking-tight flex items-center space-x-2">
            <Factory className="w-4 h-4 text-blue-600" />
            <span>Industrial PdM Platform</span>
          </h1>
          <p className="text-[11px] text-gray-400">ISO 13374 Condition-Based PDM</p>
        </div>

        {/* Navigation Tabs */}
        <nav className="space-y-1">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === 'dashboard'
                ? 'bg-blue-50 text-blue-700 border border-blue-200 font-bold'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <LayoutDashboard className="w-4 h-4 text-blue-600" />
            <span>Turbine Motor Telemetry</span>
          </button>

          {/* Early Warning Tab with dynamic badge */}
          <button
            onClick={() => setActiveTab('early_warning')}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === 'early_warning'
                ? 'bg-red-50 text-red-700 border border-red-200 font-bold'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center space-x-2.5">
              <AlertOctagon className="w-4 h-4 text-red-600" />
              <span>Early Failure & P-F</span>
            </div>
            {ewLevel !== 'GREEN' && (
              <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('fleet')}
            className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === 'fleet'
                ? 'bg-blue-50 text-blue-700 border border-blue-200 font-bold'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <Factory className="w-4 h-4 text-slate-600" />
            <span>Asset Specs & Diagnostics</span>
          </button>

          <button
            onClick={() => setActiveTab('benchmark')}
            className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === 'benchmark'
                ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <Cpu className="w-4 h-4 text-indigo-600" />
            <span>Multi-Model AI Engine</span>
          </button>

          <button
            onClick={() => setActiveTab('drift')}
            className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === 'drift'
                ? 'bg-amber-50 text-amber-700 border border-amber-200 font-bold'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <ShieldAlert className="w-4 h-4 text-amber-600" />
            <span>Reliability & Drift Studio</span>
          </button>

          <button
            onClick={() => setActiveTab('regenerative')}
            className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === 'regenerative'
                ? 'bg-purple-50 text-purple-700 border border-purple-200 font-bold'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <Sparkles className="w-4 h-4 text-purple-600" />
            <span>Regenerative AI Layer</span>
          </button>

          <button
            onClick={() => setActiveTab('workorders')}
            className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === 'workorders'
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <Wrench className="w-4 h-4 text-emerald-600" />
            <span>CMMS & Work Orders</span>
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
