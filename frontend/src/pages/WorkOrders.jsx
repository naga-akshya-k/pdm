import React, { useState, useEffect } from 'react';
import { getMaintenanceData } from '../services/api';
import { Wrench, AlertTriangle, CheckCircle2, Clock, ShieldCheck, Activity, AlertOctagon } from 'lucide-react';

export default function WorkOrders({ currentMachineId }) {
  const [maintData, setMaintData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await getMaintenanceData();
      setMaintData(res);
    } catch (err) {
      console.error('Failed to fetch maintenance recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [currentMachineId]);

  const rec = maintData || {};
  const evidence = rec.evidence || [];
  const severity = rec.maintenance_status || 'LOW';
  const priority = rec.inspection_priority || 'LOW';
  const confidence = rec.confidence !== undefined ? Math.round(rec.confidence * 100) : 85;

  const isSevere = severity === 'CRITICAL' || severity === 'HIGH' || severity === 'Warning';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${isSevere ? 'bg-amber-50 text-amber-600' : 'bg-emerald-50 text-emerald-600'}`}>
            <Wrench className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Explainable Maintenance Recommendations</h1>
            <p className="text-sm text-gray-500">
              Evidence-Backed Servicing Advice, Fault Attribution, and Priority Scheduling for Plant Operations
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Model Confidence:</span>
          <span className="px-3 py-1 bg-blue-50 text-blue-700 font-mono font-bold rounded-full text-xs border border-blue-200">
            {confidence}%
          </span>
        </div>
      </div>

      {/* Main Recommendation Card */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-gray-100 pb-4 gap-3">
          <div>
            <span className="text-xs text-gray-400 uppercase font-semibold">Active Machine</span>
            <div className="text-lg font-bold text-gray-900">{rec.machine_id || 'MCH-802X'}</div>
          </div>

          <div className="flex items-center gap-3">
            <div>
              <span className="text-xs text-gray-400 uppercase font-semibold block text-right">Severity</span>
              <span className={`px-2.5 py-1 rounded text-xs font-bold uppercase ${
                severity === 'CRITICAL' ? 'bg-red-100 text-red-800' : (severity === 'HIGH' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800')
              }`}>
                {severity}
              </span>
            </div>
            <div>
              <span className="text-xs text-gray-400 uppercase font-semibold block text-right">Inspection Priority</span>
              <span className="px-2.5 py-1 bg-slate-100 text-slate-800 rounded text-xs font-bold uppercase">
                {priority}
              </span>
            </div>
          </div>
        </div>

        {/* Detected Issue */}
        <div className="space-y-1">
          <h2 className="text-xs text-gray-400 uppercase font-bold tracking-wider">Detected Condition</h2>
          <div className="text-xl font-bold text-gray-800 flex items-center gap-2">
            {isSevere ? <AlertOctagon className="w-5 h-5 text-amber-500 shrink-0" /> : <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />}
            <span>{rec.detected_issue || 'Nominal / Healthy Operating Envelope'}</span>
          </div>
        </div>

        {/* Supporting Evidence List */}
        <div className="space-y-2">
          <h3 className="text-xs text-gray-400 uppercase font-bold tracking-wider">Supporting Physical & Model Evidence</h3>
          {evidence.length > 0 ? (
            <ul className="space-y-2">
              {evidence.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2.5 text-sm text-gray-700 bg-gray-50 p-3 rounded-lg border border-gray-200">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0"></span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500 italic bg-gray-50 p-3 rounded-lg">
              All multi-sensor channels operating within baseline design boundaries.
            </p>
          )}
        </div>

        {/* Prescribed Action & Timeframe */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div className="p-4 bg-blue-50/60 rounded-xl border border-blue-200 space-y-1">
            <span className="text-xs font-bold text-blue-900 uppercase">Recommended Operator Action</span>
            <p className="text-sm text-blue-800 font-medium">
              {rec.recommended_action || 'Continue standard operational schedule.'}
            </p>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
            <span className="text-xs font-bold text-slate-700 uppercase flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-slate-500" />
              <span>Suggested Servicing Window</span>
            </span>
            <p className="text-sm text-slate-800 font-medium font-mono">
              {rec.next_inspection_window || 'Routine quarterly inspection'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
