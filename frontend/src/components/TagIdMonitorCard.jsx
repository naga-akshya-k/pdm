import React from 'react';
import { Tag, Activity, Radio, Cpu, CheckCircle2, AlertTriangle, AlertCircle, Copy, Check } from 'lucide-react';

export default function TagIdMonitorCard({ liveTagsData }) {
  const [copied, setCopied] = React.useState(false);
  const tags = liveTagsData?.tags || [];
  const isLive = Boolean(liveTagsData?.mqtt_live);
  const deltaT = liveTagsData?.mqtt_delta_t_ms;

  const handleCopySchema = () => {
    const sample = {
      machine_id: "MCH-802X",
      timestamp: new Date().toISOString(),
      sampling_interval_ms: 1000,
      tags: {
        TURB_MTR_DE_VIB_RMS: 0.32,
        TURB_MTR_VIB_FREQ_01: 50.0,
        TURB_MTR_STATOR_TEMP: 58.5,
        TURB_MTR_PHASE_CURRENT: 9.2,
        TURB_MTR_ACOUSTIC_DB: 48.0,
        TURB_MTR_LUBE_OIL_PRES: 4.6,
        TURB_MTR_SHAFT_SPEED: 3000.0,
        TURB_MTR_KW_LOAD: 55.0
      }
    };
    navigator.clipboard.writeText(JSON.stringify(sample, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getTagStatus = (tag) => {
    const val = Number(tag.current_value);
    if (isNaN(val)) return { color: 'text-slate-400', bg: 'bg-slate-800', border: 'border-slate-700', label: 'OFFLINE' };
    
    // Check critical threshold
    if (tag.crit_threshold) {
      if (tag.feature_name === 'Pressure' && val <= tag.crit_threshold) {
        return { color: 'text-red-400', bg: 'bg-red-950/40', border: 'border-red-600', label: 'CRITICAL LOW', icon: AlertCircle };
      }
      if (tag.feature_name !== 'Pressure' && val >= tag.crit_threshold) {
        return { color: 'text-red-400', bg: 'bg-red-950/40', border: 'border-red-600', label: 'CRITICAL HIGH', icon: AlertCircle };
      }
    }

    // Check normal bounds
    if (val > tag.normal_max || val < tag.normal_min) {
      return { color: 'text-amber-400', bg: 'bg-amber-950/40', border: 'border-amber-600', label: 'WARNING', icon: AlertTriangle };
    }

    return { color: 'text-emerald-400', bg: 'bg-emerald-950/30', border: 'border-emerald-600/40', label: 'NORMAL', icon: CheckCircle2 };
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg text-white">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-blue-600/20 text-blue-400 border border-blue-500/30 rounded-lg">
            <Tag className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold tracking-tight text-slate-100">
                Industrial SCADA/PLC Tag ID Inspector
              </h2>
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-blue-950/80 text-blue-300 border border-blue-800">
                MCH-802X : Turbine Motor
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Live telemetry ingress for company workstation GPU streams via MQTT
            </p>
          </div>
        </div>

        {/* Status Badges & Copy Schema */}
        <div className="flex items-center space-x-3 flex-wrap gap-y-2">
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold border ${
            isLive
              ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500'
              : 'bg-slate-800 text-slate-300 border-slate-700'
          }`}>
            <span className={`w-2 h-2 rounded-full ${isLive ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`}></span>
            <span>{isLive ? `GPU STREAM ACTIVE [${Math.round(deltaT || 1000)}ms]` : 'DIGITAL TWIN SIMULATION'}</span>
          </div>

          <button
            onClick={handleCopySchema}
            className="flex items-center space-x-1.5 px-3 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-medium rounded-lg transition-colors"
            title="Copy sample JSON payload schema for company engineers"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-slate-400" />}
            <span>{copied ? 'Copied Tag JSON!' : 'Copy Tag Schema'}</span>
          </button>
        </div>
      </div>

      {/* Tag Metadata Info Bar & Live Status Banner */}
      {isLive ? (
        <div className="mt-3 bg-emerald-950/90 border border-emerald-500/80 p-3 rounded-lg flex flex-col sm:flex-row sm:items-center justify-between text-xs text-emerald-200 gap-2 shadow-inner">
          <div className="flex items-center space-x-2">
            <Radio className="w-4 h-4 text-emerald-400 animate-pulse" />
            <span className="font-bold tracking-wide">LIVE DATA TRANSMISSION ACTIVE (Source: Workstation GPU via Tag IDs)</span>
          </div>
          <div className="font-mono text-[11px] text-emerald-300 flex items-center space-x-3">
            <span>Measured Cadence: <strong className="text-white font-bold">{Math.round(deltaT || 1000)} ms</strong></span>
            <span>Target: 1000 ms</span>
            <span className="bg-emerald-800 text-white px-2 py-0.5 rounded text-[10px] font-bold">INGESTING</span>
          </div>
        </div>
      ) : (
        <div className="mt-3 bg-slate-800/60 border border-slate-700/60 p-2.5 rounded-lg flex flex-col sm:flex-row sm:items-center justify-between text-xs text-slate-300 gap-1">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
            <span>Digital Twin Simulation Baseline — Ready to receive live company Tag ID stream</span>
          </div>
          <div className="font-mono text-[11px] text-slate-400">
            <span>Watchdog Failover: 6.0s</span>
          </div>
        </div>
      )}

      {/* Grid of 8 Tag Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4">
        {tags.map((tag) => {
          const st = getTagStatus(tag);
          const Icon = st.icon || CheckCircle2;
          return (
            <div
              key={tag.tag_id}
              className={`p-3.5 rounded-xl border ${st.border} ${st.bg} flex flex-col justify-between transition-all hover:scale-[1.01] ${
                isLive ? 'ring-1 ring-emerald-500/40' : ''
              }`}
            >
              <div>
                <div className="flex items-start justify-between">
                  <span className="font-mono text-xs font-bold text-slate-200 tracking-wide break-all">
                    {tag.tag_id}
                  </span>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded flex items-center space-x-1 ${st.color}`}>
                    <Icon className="w-3 h-3 inline mr-0.5" />
                    {st.label}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 mt-1 line-clamp-1" title={tag.description}>
                  {tag.description}
                </div>
                {isLive && (
                  <div className="text-[10px] font-mono text-emerald-400 mt-1 flex items-center gap-1 font-semibold">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                    TAG TRANSMITTED VIA GPU
                  </div>
                )}
              </div>

              <div className="mt-3 pt-2 border-t border-slate-700/50 flex items-baseline justify-between">
                <div>
                  <span className="text-xl font-bold font-mono text-white tracking-tight">
                    {tag.current_value !== undefined && tag.current_value !== null ? tag.current_value : '--'}
                  </span>
                  <span className="text-xs text-slate-400 ml-1 font-semibold">{tag.unit}</span>
                </div>
                <div className="text-[10px] text-slate-400 font-mono text-right">
                  <span>Norm: {tag.normal_min}-{tag.normal_max}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
