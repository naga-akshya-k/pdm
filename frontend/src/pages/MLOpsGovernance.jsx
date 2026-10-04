import React, { useState, useEffect } from 'react';
import { getRegenerativeStatus, triggerRegenerativeRetraining, deployCandidateModel } from '../services/api';
import { CheckCircle2, AlertTriangle, ArrowRight, ShieldCheck, RefreshCw, Cpu, Layers, History, Play, RotateCcw } from 'lucide-react';

export default function MLOpsGovernance() {
  const [pipelineData, setPipelineData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [retraining, setRetraining] = useState(false);
  const [approverName, setApproverName] = useState('Lead Reliability Engineer');
  const [engineerNotes, setEngineerNotes] = useState('');
  const [actionMsg, setActionMsg] = useState(null);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const data = await getRegenerativeStatus();
      setPipelineData(data);
    } catch (err) {
      console.error('Failed to load MLOps pipeline status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleRetrain = async () => {
    try {
      setRetraining(true);
      setActionMsg(null);
      const res = await triggerRegenerativeRetraining();
      setActionMsg({
        type: 'success',
        text: `Candidate model trained successfully (${res.candidate?.algorithm} ${res.candidate?.version}). Waiting for human engineer approval.`
      });
      await fetchStatus();
    } catch (err) {
      setActionMsg({ type: 'error', text: 'Candidate model training failed.' });
    } finally {
      setRetraining(false);
    }
  };

  const handleApprove = async () => {
    const candVersion = pipelineData?.candidate_version;
    if (!candVersion) return;
    try {
      const res = await deployCandidateModel(candVersion, approverName, engineerNotes);
      setActionMsg({ type: 'success', text: res.message });
      await fetchStatus();
      setEngineerNotes('');
    } catch (err) {
      setActionMsg({ type: 'error', text: 'Approval failed.' });
    }
  };

  const activeVer = pipelineData?.current_version || 'v1.0';
  const candVer = pipelineData?.candidate_version;
  const models = pipelineData?.models || {};
  const historyList = Object.values(pipelineData?.version_history || {});

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">MLOps & Continuous Model Improvement</h1>
            <p className="text-sm text-gray-500">
              Drift-Triggered Candidate Retraining, Validation Benchmarks, Human Engineer Sign-Off Gate, and Version Rollback
            </p>
          </div>
        </div>

        <button
          onClick={handleRetrain}
          disabled={retraining}
          className="flex items-center justify-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg shadow-sm transition disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${retraining ? 'animate-spin' : ''}`} />
          <span>{retraining ? 'Training Candidate...' : 'Train Candidate Model'}</span>
        </button>
      </div>

      {actionMsg && (
        <div className={`p-4 rounded-xl border flex items-center gap-3 ${
          actionMsg.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-red-50 border-red-200 text-red-800'
        }`}>
          {actionMsg.type === 'success' ? <CheckCircle2 className="w-5 h-5 shrink-0" /> : <AlertTriangle className="w-5 h-5 shrink-0 text-red-600" />}
          <span className="text-sm font-medium">{actionMsg.text}</span>
        </div>
      )}

      {/* Production vs Candidate Model Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Active Production Model */}
        <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold uppercase">Production Active</span>
              <span className="font-mono font-bold text-gray-900">{activeVer}</span>
            </div>
            <span className="text-xs text-gray-500">Serving Live Inferences</span>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Algorithm</span>
              <span className="font-bold text-gray-800">{pipelineData?.active_model_name || 'Random Forest'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Validation MAE</span>
              <span className="font-mono font-bold text-gray-800">{models['Random Forest']?.mae || 28.5} Days</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Validation R²</span>
              <span className="font-mono font-bold text-gray-800">{models['Random Forest']?.r2_score || 0.865}</span>
            </div>
          </div>
        </div>

        {/* Retraining Candidate Model */}
        <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase ${
                candVer ? 'bg-amber-100 text-amber-800' : 'bg-gray-100 text-gray-600'
              }`}>
                {candVer ? 'Candidate Awaiting Approval' : 'No Pending Candidate'}
              </span>
              {candVer && <span className="font-mono font-bold text-gray-900">{candVer}</span>}
            </div>
            <span className="text-xs text-gray-500">Target Model Version</span>
          </div>

          {candVer ? (
            <div className="space-y-4">
              <div className="p-4 bg-amber-50/60 rounded-lg space-y-2 border border-amber-200">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Candidate Algorithm</span>
                  <span className="font-bold text-gray-800">Gradient Boosting Regressor</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Validation MAE</span>
                  <span className="font-mono font-bold text-emerald-700">{models['Gradient Boosting']?.mae || 24.1} Days (Improved)</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Validation R²</span>
                  <span className="font-mono font-bold text-emerald-700">{models['Gradient Boosting']?.r2_score || 0.892}</span>
                </div>
              </div>

              {/* Engineer Sign-off Form */}
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 space-y-3">
                <div className="flex items-center gap-2 text-xs font-bold text-gray-700 uppercase">
                  <ShieldCheck className="w-4 h-4 text-indigo-600" />
                  <span>Human Engineer Approval Gate</span>
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Approving Engineer Name</label>
                  <input
                    type="text"
                    value={approverName}
                    onChange={e => setApproverName(e.target.value)}
                    className="w-full text-xs p-2 border border-gray-300 rounded bg-white"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Review Notes & Validation Rationale</label>
                  <input
                    type="text"
                    placeholder="e.g. Model shows 15% lower MAE on recent bearing wear data"
                    value={engineerNotes}
                    onChange={e => setEngineerNotes(e.target.value)}
                    className="w-full text-xs p-2 border border-gray-300 rounded bg-white"
                  />
                </div>
                <button
                  onClick={handleApprove}
                  className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded shadow-xs transition"
                >
                  Authorize & Promote {candVer} to Production
                </button>
              </div>
            </div>
          ) : (
            <div className="p-6 text-center text-gray-400 text-xs">
              No candidate model pending. Click "Train Candidate Model" above to generate a new candidate version.
            </div>
          )}
        </div>
      </div>

      {/* Version Registry History */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6 space-y-4">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-gray-500" />
          <h2 className="text-base font-bold text-gray-900">Model Registry Version History</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-600 border-b border-gray-200">
              <tr>
                <th className="p-3">Version</th>
                <th className="p-3">Algorithm</th>
                <th className="p-3">Trained At</th>
                <th className="p-3">Dataset Size</th>
                <th className="p-3">MAE (Days)</th>
                <th className="p-3">R² Score</th>
                <th className="p-3">Status</th>
                <th className="p-3">Approved By</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {historyList.map((ver, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="p-3 font-mono font-bold text-gray-900">{ver.version}</td>
                  <td className="p-3 font-medium text-gray-700">{ver.algorithm}</td>
                  <td className="p-3 text-gray-500 font-mono">{ver.trained_at}</td>
                  <td className="p-3 text-gray-500 font-mono">{ver.dataset_size}</td>
                  <td className="p-3 font-mono text-gray-800">{ver.metrics?.mae}</td>
                  <td className="p-3 font-mono text-gray-800">{ver.metrics?.r2_score}</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      ver.status === 'PRODUCTION'
                        ? 'bg-emerald-100 text-emerald-800'
                        : (ver.status === 'WAITING_FOR_ENGINEER_APPROVAL' ? 'bg-amber-100 text-amber-800' : 'bg-gray-100 text-gray-600')
                    }`}>
                      {ver.status}
                    </span>
                  </td>
                  <td className="p-3 text-gray-600">{ver.approved_by || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
