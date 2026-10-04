import React from 'react';
import {
  Factory,
  Cpu,
  Wrench,
  Play,
  Pause,
  SkipForward,
  RotateCcw,
  Sliders,
  Activity,
  LineChart,
  GitCompare,
  Layers,
  Radio
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
  const isTelemetry = activeTab === 'telemetry' || activeTab === 'dashboard';
  const isAnalytics = activeTab === 'analytics' || activeTab === 'early_warning';
  const isMaintenance = activeTab === 'maintenance' || activeTab === 'workorders';
  const isDrift = activeTab === 'drift';
  const isMLOps = activeTab === 'mlops' || activeTab === 'evaluation' || activeTab === 'benchmark';
  const isFleet = activeTab === 'fleet';

  const anomalyStatus = currentData?.anomaly_status || 'NORMAL';

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col justify-between h-[calc(100vh-49px)] shadow-xs shrink-0 select-none">
      <div className="p-3.5 space-y-4 overflow-y-auto">
        {/* Title */}
        <div>
          <h1 className="text-sm font-bold text-gray-900 tracking-tight flex items-center space-x-2">
            <Factory className="w-4 h-4 text-blue-600" />
            <span>Industrial PdM v3</span>
          </h1>
          <p className="text-[11px] text-gray-400">Time-Series Reliability & Diagnostics</p>
        </div>

        {/* Navigation Tabs */}
        <nav className="space-y-1">
          {/* 1. Live Telemetry */}
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
              <span>Live Telemetry</span>
              <span className="text-[10px] text-gray-400 font-normal">SCADA Stream & Sensors</span>
            </div>
          </button>

          {/* 2. Anomaly & Diagnostics */}
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
                <span>Anomaly & P-F Curve</span>
                <span className="text-[10px] text-gray-400 font-normal">ISO 10816 Severity</span>
              </div>
            </div>
            {anomalyStatus !== 'NORMAL' && (
              <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
            )}
          </button>

          {/* 3. Maintenance Recommendations */}
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
              <span>Maintenance Advice</span>
              <span className="text-[10px] text-gray-400 font-normal">Explainable Protocols</span>
            </div>
          </button>

          {/* 4. Drift Monitoring */}
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
              <span>Drift Monitoring</span>
              <span className="text-[10px] text-gray-400 font-normal">KS-Tests & PSI Divergence</span>
            </div>
          </button>

          {/* 5. MLOps & Model Governance */}
          <button
            onClick={() => setActiveTab('mlops')}
            className={`w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-lg text-xs font-semibold transition-colors ${
              isMLOps
                ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold shadow-xs'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <Cpu className="w-4 h-4 text-indigo-600 shrink-0" />
            <div className="flex flex-col text-left">
              <span>MLOps Governance</span>
              <span className="text-[10px] text-gray-400 font-normal">Model Registry & Approvals</span>
            </div>
          </button>

          {/* 6. Plant Fleet */}
          <button
            onClick={() => setActiveTab('fleet')}
            className={`w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-lg text-xs font-semibold transition-colors ${
              isFleet
                ? 'bg-blue-50 text-blue-700 border border-blue-200 font-bold shadow-xs'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <Layers className="w-4 h-4 text-blue-600 shrink-0" />
            <div className="flex flex-col text-left">
              <span>Plant Fleet</span>
              <span className="text-[10px] text-gray-400 font-normal">Multi-Asset Condition</span>
            </div>
          </button>
        </nav>

        {/* Active Machine Status Card */}
        <div className="bg-gray-50 rounded-xl p-3 border border-gray-200 space-y-2">
          <div className="flex items-center justify-between text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
            <span>Selected Unit</span>
            <span className="font-mono text-blue-700">{currentData?.machine_id || 'MCH-802X'}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-800 line-clamp-1">{currentData?.machine_name || 'Turbine A1'}</span>
            <StatusBadge status={currentData?.machine_status || 'Healthy'} />
          </div>
          <div className="flex items-center justify-between text-xs text-gray-600 pt-1.5 border-t border-gray-200">
            <span>Machine Health</span>
            <span className="font-bold text-gray-900 font-mono">{currentData?.machine_health ?? 100}%</span>
          </div>
        </div>

        {/* Clock & Replay Loop Controls */}
        <div className="space-y-2.5 pt-2 border-t border-gray-200">
          <div className="text-[11px] font-bold text-gray-700 uppercase tracking-wider flex items-center space-x-1">
            <Sliders className="w-3 h-3 text-gray-500" />
            <span>Telemetry Controls</span>
          </div>

          <div className="grid grid-cols-2 gap-1.5">
            <button
              onClick={() => onControlAction('play')}
              className={`flex items-center justify-center space-x-1 py-1.5 px-2 rounded-lg text-xs font-semibold transition ${
                autoPlay ? 'bg-emerald-600 text-white shadow-xs' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Play className="w-3 h-3" />
              <span>Resume</span>
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
              onClick={() => onControlAction('step')}
              className="flex items-center justify-center space-x-1 py-1.5 px-2 rounded-lg text-xs font-semibold bg-gray-100 text-gray-700 hover:bg-gray-200 transition"
            >
              <SkipForward className="w-3 h-3" />
              <span>Step 1x</span>
            </button>
            <button
              onClick={() => onControlAction('reset')}
              className="flex items-center justify-center space-x-1 py-1.5 px-2 rounded-lg text-xs font-semibold bg-gray-100 text-gray-700 hover:bg-gray-200 transition"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset</span>
            </button>
          </div>

          <div className="space-y-1 pt-1">
            <div className="flex justify-between text-[11px] text-gray-500">
              <span>Cadence Speed</span>
              <span className="font-mono font-bold text-gray-700">{speed}s</span>
            </div>
            <input
              type="range"
              min="0.2"
              max="3.0"
              step="0.2"
              value={speed}
              onChange={e => {
                const s = parseFloat(e.target.value);
                setSpeed(s);
                onControlAction('speed', s);
              }}
              className="w-full accent-blue-600 h-1.5 bg-gray-200 rounded-lg cursor-pointer"
            />
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
