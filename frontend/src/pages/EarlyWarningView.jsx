import React, { useState, useEffect } from 'react';
import { getEarlyWarningAnalysis } from '../services/api';
import { ShieldAlert, AlertTriangle, Clock, CheckCircle2, Flame, Activity, CheckSquare, Square, ChevronRight, Gauge, LineChart } from 'lucide-react';
import Plot from '../components/Plot';

export default function EarlyWarningView({ currentData }) {
  const [earlyData, setEarlyData] = useState(null);
  const [checkedTasks, setCheckedTasks] = useState({});

  const fetchAnalysis = async () => {
    try {
      const data = await getEarlyWarningAnalysis();
      setEarlyData(data);
    } catch (err) {
      console.error('Failed to fetch early warning diagnostics:', err);
    }
  };

  useEffect(() => {
    fetchAnalysis();
    const interval = setInterval(fetchAnalysis, 2000);
    return () => clearInterval(interval);
  }, [currentData?.machine_id]);

  const toggleTask = (index) => {
    setCheckedTasks((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  const ew = earlyData || currentData?.early_warning || {};
  const pf = ew.pf_curve || { phase_name: 'Design Envelope', degradation_progress_pct: 5.0, is_early_stage: true };
  const iso = ew.iso_10816 || { zone: 'Zone A', label: 'Good Condition', color: '#10B981', current_rms: 0.20 };
  const leadDays = ew.lead_time_to_failure_days ?? currentData?.predicted_rul_days ?? 300;
  const leadHours = ew.lead_time_to_failure_hours ?? leadDays * 24;
  const level = ew.early_warning_level || 'GREEN';

  // P-F Curve Plotly Data
  const pfX = [0, 20, 40, 60, 80, 100];
  const pfY = [100, 96, 88, 72, 40, 0]; // Non-linear P-F degradation curve

  const currentX = pf.degradation_progress_pct || 10;
  // Interpolate current Y
  const currentY = Math.max(0, 100 - (currentX / 100) ** 1.8 * 100);

  const getLevelBadge = () => {
    if (level === 'RED') {
      return <span className="px-3 py-1 rounded-full text-xs font-bold bg-red-100 text-red-800 border border-red-200 animate-pulse flex items-center gap-1.5"><Flame className="w-3.5 h-3.5" /> CRITICAL EMERGENCY</span>;
    }
    if (level === 'ORANGE') {
      return <span className="px-3 py-1 rounded-full text-xs font-bold bg-orange-100 text-orange-800 border border-orange-200 flex items-center gap-1.5"><AlertTriangle className="w-3.5 h-3.5" /> URGENT STAGE P3</span>;
    }
    if (level === 'AMBER') {
      return <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200 flex items-center gap-1.5"><Activity className="w-3.5 h-3.5" /> EARLY WARNING P2</span>;
    }
    if (level === 'YELLOW') {
      return <span className="px-3 py-1 rounded-full text-xs font-bold bg-yellow-100 text-yellow-800 border border-yellow-200 flex items-center gap-1.5"><AlertTriangle className="w-3.5 h-3.5" /> MICRO-WEAR ONSET P1</span>;
    }
    return <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5" /> NOMINAL ENVELOPE</span>;
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-emerald-50 text-emerald-600 rounded-xl">
            <LineChart className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-gray-900">Predictive Analytics & Degradation Dynamics</h1>
              {getLevelBadge()}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Active Unit: <span className="font-bold text-gray-800">{currentData?.machine_name || 'Turbine Motor Unit A1'}</span> ({currentData?.machine_id || 'MCH-802X'}) &bull; Condition Analytics & P-F Curve
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 bg-gray-50 p-3 rounded-xl border border-gray-200">
          <div>
            <span className="text-[11px] text-gray-500 uppercase tracking-wider block">Early Lead Time Warning</span>
            <span className="text-xl font-black font-mono text-blue-700">{leadDays} Days</span>
            <span className="text-xs text-gray-400 ml-1.5">({leadHours} Hours)</span>
          </div>
        </div>
      </div>

      {/* Early Warning Status Alert Bar */}
      <div className={`p-4 rounded-xl border text-sm font-semibold flex items-center justify-between gap-3 ${
        level === 'RED' || level === 'ORANGE' ? 'bg-red-50 border-red-200 text-red-900' : (level === 'AMBER' || level === 'YELLOW' ? 'bg-amber-50 border-amber-200 text-amber-900' : 'bg-emerald-50 border-emerald-200 text-emerald-900')
      }`}>
        <div className="flex items-center gap-2.5">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{ew.early_warning_status || 'Machine operating safely within nominal design limits.'}</span>
        </div>
        <span className="text-xs font-mono font-bold bg-white/80 px-2.5 py-1 rounded-md border">
          Phase: {pf.phase_name}
        </span>
      </div>

      {/* Grid: Interactive P-F Curve & ISO 10816 Vibration Severity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* P-F Curve Visualizer */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-xs border border-gray-200 p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-gray-100 mb-2">
              <div>
                <h3 className="font-bold text-gray-900 text-sm">Non-Linear P-F Degradation Curve Position</h3>
                <p className="text-xs text-gray-500">Maps asset degradation from Potential Failure Point (P) to Functional Breakdown (F)</p>
              </div>
              <span className="text-xs font-mono font-bold text-purple-700 bg-purple-50 px-2.5 py-1 rounded-md border border-purple-200">
                P-F Position: {pf.degradation_progress_pct}%
              </span>
            </div>

            <div className="w-full h-[300px]">
              <Plot
                data={[
                  {
                    x: pfX,
                    y: pfY,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Theoretical P-F Curve',
                    line: { color: '#6366F1', width: 3, shape: 'spline' },
                  },
                  {
                    x: [currentX],
                    y: [currentY],
                    type: 'scatter',
                    mode: 'markers+text',
                    name: 'Current Machine Position',
                    text: [`Live Position (${currentX}%)`],
                    textposition: 'top right',
                    marker: { color: level === 'RED' ? '#EF4444' : (level === 'GREEN' ? '#10B981' : '#F59E0B'), size: 14, symbol: 'diamond' },
                  },
                ]}
                layout={{
                  autosize: true,
                  height: 290,
                  margin: { l: 45, r: 25, t: 25, b: 40 },
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  plot_bgcolor: '#FAFAFA',
                  xaxis: {
                    title: { text: 'Degradation Progression (%)', font: { size: 11, color: '#6B7280' } },
                    gridcolor: '#F3F4F6',
                    range: [0, 105],
                  },
                  yaxis: {
                    title: { text: 'Equipment Health (%)', font: { size: 11, color: '#6B7280' } },
                    gridcolor: '#F3F4F6',
                    range: [0, 105],
                  },
                  annotations: [
                    { x: 25, y: 94, text: 'P1: Ultrasonic / Micro-Wear', showarrow: true, arrowhead: 2, font: { size: 9 } },
                    { x: 50, y: 82, text: 'P2: Vibration Spectrum', showarrow: true, arrowhead: 2, font: { size: 9 } },
                    { x: 75, y: 55, text: 'P3: Thermal Rise', showarrow: true, arrowhead: 2, font: { size: 9 } },
                    { x: 95, y: 15, text: 'Point F: Breakdown', showarrow: true, arrowhead: 2, font: { size: 9, color: '#EF4444' } },
                  ],
                  showlegend: false,
                }}
                useResizeHandler={true}
                style={{ width: '100%', height: '100%' }}
                config={{ displayModeBar: false, responsive: true }}
              />
            </div>
          </div>

          <div className="grid grid-cols-4 gap-2 pt-3 border-t border-gray-100 text-center text-xs">
            <div className="p-2 bg-emerald-50 rounded-lg text-emerald-800 font-medium">1. Acoustic (45-90d)</div>
            <div className="p-2 bg-blue-50 rounded-lg text-blue-800 font-medium">2. Vibration (15-45d)</div>
            <div className="p-2 bg-amber-50 rounded-lg text-amber-800 font-medium">3. Thermal (3-14d)</div>
            <div className="p-2 bg-red-50 rounded-lg text-red-800 font-medium">4. Audible (0-4h)</div>
          </div>
        </div>

        {/* ISO 10816 Vibration Severity Card */}
        <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Gauge className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-gray-900 text-sm">ISO 10816 Vibration Severity</h3>
            </div>
            <p className="text-xs text-gray-500 mb-4">Standardized industrial vibration evaluation limits for rotational equipment</p>

            <div className="p-4 rounded-xl border mb-4 text-center" style={{ backgroundColor: `${iso.color}15`, borderColor: `${iso.color}40` }}>
              <span className="text-xs font-bold uppercase tracking-wider block" style={{ color: iso.color }}>{iso.zone}</span>
              <span className="text-3xl font-black font-mono text-gray-900 mt-1 block">{iso.current_rms} <span className="text-xs font-normal text-gray-500">mm/s RMS</span></span>
              <span className="text-xs font-semibold text-gray-700 mt-1 block">{iso.label}</span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center p-2 rounded-lg bg-emerald-50 text-emerald-900">
                <span className="font-semibold">Zone A (&lt; 0.28 mm/s)</span>
                <span>Good / Commissioned</span>
              </div>
              <div className="flex justify-between items-center p-2 rounded-lg bg-blue-50 text-blue-900">
                <span className="font-semibold">Zone B (0.28 – 0.71 mm/s)</span>
                <span>Acceptable</span>
              </div>
              <div className="flex justify-between items-center p-2 rounded-lg bg-amber-50 text-amber-900">
                <span className="font-semibold">Zone C (0.71 – 1.80 mm/s)</span>
                <span>Restricted / Alert</span>
              </div>
              <div className="flex justify-between items-center p-2 rounded-lg bg-red-50 text-red-900">
                <span className="font-semibold">Zone D (&gt; 1.80 mm/s)</span>
                <span>Danger / Stop Machine</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Grid: Root Cause Attribution & Operator Action Protocol */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Root Cause Attribution Waterfall */}
        <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-5">
          <h3 className="font-bold text-gray-900 text-sm mb-1">Root-Cause Sensor Anomaly Contribution</h3>
          <p className="text-xs text-gray-500 mb-4">Multi-sensor attribution identifying primary physical degradation drivers</p>

          <div className="space-y-3">
            {ew.root_cause_attribution?.map((rc) => (
              <div key={rc.sensor_group}>
                <div className="flex justify-between text-xs font-medium mb-1">
                  <span className="text-gray-700">{rc.sensor_group}</span>
                  <span className="font-mono font-bold text-gray-900">{rc.contribution_pct}%</span>
                </div>
                <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-indigo-600 rounded-full transition-all duration-500"
                    style={{ width: `${rc.contribution_pct}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Prescribed Operator Action Protocol Checklist */}
        <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-5 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-gray-900 text-sm mb-1">Prescribed Operator Shift Action Protocol</h3>
            <p className="text-xs text-gray-500 mb-4">Step-by-step physical inspection tasks generated for field technicians</p>

            <div className="space-y-2.5">
              {ew.operator_action_checklist?.map((task, idx) => {
                const isChecked = !!checkedTasks[idx];
                return (
                  <div
                    key={idx}
                    onClick={() => toggleTask(idx)}
                    className={`p-3 rounded-lg border cursor-pointer transition-all flex items-start gap-3 text-xs ${
                      isChecked ? 'bg-emerald-50/70 border-emerald-200 text-emerald-900' : 'bg-gray-50 border-gray-200 hover:bg-gray-100/70 text-gray-800'
                    }`}
                  >
                    {isChecked ? (
                      <CheckSquare className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                    ) : (
                      <Square className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
                    )}
                    <span className={isChecked ? 'line-through text-gray-500' : 'font-medium'}>{task}</span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-4 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
            <span>Tasks Completed: {Object.values(checkedTasks).filter(Boolean).length} / {ew.operator_action_checklist?.length || 3}</span>
            <span className="font-semibold text-blue-600">ISO 13374 Standard</span>
          </div>
        </div>
      </div>
    </div>
  );
}
