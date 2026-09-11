import React, { useState, useEffect } from 'react';
import { getRegenerativeStatus, triggerRegenerativeRetraining, deployCandidateModel } from '../services/api';
import { Sparkles, CheckCircle2, AlertTriangle, ArrowRight, ShieldCheck, RefreshCw, Cpu, Layers, History, Play } from 'lucide-react';

export default function RegenerativeStudio() {
  const [pipelineData, setPipelineData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [retraining, setRetraining] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [approverName, setApproverName] = useState('Lead Reliability Engineer');
  const [engineerNotes, setEngineerNotes] = useState('');
  const [actionMsg, setActionMsg] = useState(null);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const data = await getRegenerativeStatus();
      setPipelineData(data);
      if (data?.candidates) {
        const top = Object.values(data.candidates).sort((a, b) => b.r2_score - a.r2_score)[0];
        if (top && !selectedCandidate) setSelectedCandidate(top.name);
      }
    } catch (err) {
      console.error('Failed to load regenerative pipeline status:', err);
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
      setPipelineData(prev => ({
        ...prev,
        pipeline_state: res.pipeline_state,
        candidates: res.candidates
      }));
      setSelectedCandidate(res.recommended_candidate);
      setActionMsg({ type: 'success', text: `Retraining completed in ${res.duration_sec}s. Recommended candidate: ${res.recommended_candidate}` });
    } catch (err) {
      setActionMsg({ type: 'error', text: 'Retraining failed' });
    } finally {
      setRetraining(false);
    }
  };

  const handleDeploy = async () => {
    if (!selectedCandidate) return;
    try {
      const res = await deployCandidateModel(selectedCandidate, approverName, engineerNotes);
      setActionMsg({ type: 'success', text: res.message });
      await fetchStatus();
      setEngineerNotes('');
    } catch (err) {
      setActionMsg({ type: 'error', text: 'Deployment failed' });
    }
  };

  const candidates = pipelineData?.candidates ? Object.values(pipelineData.candidates) : [];
  const currentMetrics = pipelineData?.current_metrics || {};

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-50 text-purple-600 rounded-lg">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Closed-Loop Regenerative AI & Model Governance Layer</h1>
            <p className="text-sm text-gray-500">
              Section 9 Proposed Architecture: Automated continuous retraining, engineering governance validation, and controlled hot-deployment
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-purple-50 border border-purple-200 px-3.5 py-1.5 rounded-lg text-right">
            <span className="text-[11px] text-purple-700 font-semibold block">Production Model</span>
            <span className="text-sm font-bold text-purple-900 font-mono">v{pipelineData?.current_production_version || '1.0'} ({pipelineData?.active_model_name})</span>
          </div>
        </div>
      </div>

      {/* 8-Step Architecture Process Flow */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-5">
        <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-3">8-Step Human-Supervised Regenerative Workflow</span>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2 text-center text-xs">
          {[
            { step: '1', name: 'Telemetry Monitor' },
            { step: '2', name: 'Drift Detection' },
            { step: '3', name: 'Auto Retrain' },
            { step: '4', name: 'Benchmark Eval' },
            { step: '5', name: 'Gov Validation' },
            { step: '6', name: 'Select Best' },
            { step: '7', name: 'Deploy Version' },
            { step: '8', name: 'Monitor Deployed' }
          ].map((item, idx) => (
            <div key={item.step} className="p-2 rounded-lg bg-gray-50 border border-gray-100 flex flex-col items-center justify-center">
              <span className="w-5 h-5 rounded-full bg-purple-100 text-purple-700 font-bold text-[10px] flex items-center justify-center mb-1">
                {item.step}
              </span>
              <span className="text-[11px] font-medium text-gray-700 leading-tight">{item.name}</span>
            </div>
          ))}
        </div>
      </div>

      {actionMsg && (
        <div className={`p-4 rounded-lg text-sm font-medium border ${actionMsg.type === 'success' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-red-50 text-red-800 border-red-200'}`}>
          {actionMsg.text}
        </div>
      )}

      {/* Retraining Action Bar */}
      <div className="bg-gradient-to-r from-purple-900 to-indigo-900 rounded-xl p-6 text-white flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-md">
        <div>
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-[11px] font-bold bg-purple-800 text-purple-200 mb-2">
            Automated Domain Adaptation
          </span>
          <h2 className="text-xl font-bold">Trigger Regenerative Retraining Pipeline</h2>
          <p className="text-xs text-purple-200 max-w-2xl mt-1">
            Adapts candidate models to newly accumulated operational wear patterns, drift signatures, and fault states without shutting down live plant telemetry.
          </p>
        </div>
        <button
          disabled={retraining}
          onClick={handleRetrain}
          className="px-6 py-3 bg-white hover:bg-purple-50 text-purple-900 font-bold rounded-xl shadow-md text-sm transition-all duration-200 flex items-center gap-2 flex-shrink-0 disabled:opacity-50"
        >
          {retraining ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin text-purple-600" />
              Retraining 4 Candidate Models...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 text-purple-700 fill-current" />
              Execute Retraining Pipeline
            </>
          )}
        </button>
      </div>

      {/* Candidate Retraining Benchmark Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl shadow-xs border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold text-gray-900">Retrained Candidate Performance Leaderboard</h3>
              <p className="text-xs text-gray-500">Compare newly retrained candidates against active production model</p>
            </div>
          </div>

          <div className="space-y-3">
            {candidates.map((c) => {
              const isSelected = selectedCandidate === c.name;
              const r2Delta = (c.r2_score - (currentMetrics.r2_score || 0.865)) * 100;

              return (
                <div
                  key={c.name}
                  onClick={() => setSelectedCandidate(c.name)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all duration-200 flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                    isSelected ? 'border-purple-600 bg-purple-50/40 ring-1 ring-purple-500/20' : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2.5 rounded-lg ${isSelected ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-600'}`}>
                      <Cpu className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-gray-900 text-sm">{c.name}</h4>
                        {c.is_active && (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                            Active Live Model
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-gray-500">Latency: {c.inference_latency_ms}ms • Train Time: {c.train_duration_sec}s</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-6 text-xs">
                    <div className="text-right">
                      <span className="text-gray-400 block">R² Score</span>
                      <span className="font-bold text-gray-900 font-mono text-sm">{(c.r2_score * 100).toFixed(1)}%</span>
                    </div>
                    <div className="text-right">
                      <span className="text-gray-400 block">MAE Error</span>
                      <span className="font-bold text-gray-900 font-mono text-sm">{c.mae} d</span>
                    </div>
                    <div className="text-right">
                      <span className="text-gray-400 block">RMSE</span>
                      <span className="font-bold text-gray-900 font-mono text-sm">{c.rmse} d</span>
                    </div>
                    <div className="text-right">
                      <span className="text-gray-400 block">Accuracy Δ</span>
                      <span className={`font-bold font-mono text-sm ${r2Delta >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                        {r2Delta >= 0 ? `+${r2Delta.toFixed(1)}%` : `${r2Delta.toFixed(1)}%`}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Engineering Governance & Deployment Action Panel */}
        <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <ShieldCheck className="w-5 h-5 text-purple-600" />
              <h3 className="font-bold text-gray-900 text-base">Engineering Governance & Sign-Off</h3>
            </div>
            <p className="text-xs text-gray-500 mb-4">
              Human-in-the-loop review. Replacement occurs only after verified engineering sign-off.
            </p>

            <div className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-gray-700 block mb-1">Selected Candidate for Deployment</label>
                <div className="p-2.5 bg-gray-50 rounded-lg border border-gray-200 font-bold text-sm text-purple-900 font-mono">
                  {selectedCandidate || 'None Selected'}
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-700 block mb-1">Approver / Sign-Off Role</label>
                <input
                  type="text"
                  value={approverName}
                  onChange={(e) => setApproverName(e.target.value)}
                  className="w-full text-xs p-2.5 rounded-lg border border-gray-200 focus:outline-none focus:ring-1 focus:ring-purple-500"
                  placeholder="e.g. Lead Reliability Engineer"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-700 block mb-1">Validation Notes / Change Summary</label>
                <textarea
                  value={engineerNotes}
                  onChange={(e) => setEngineerNotes(e.target.value)}
                  rows={3}
                  className="w-full text-xs p-2.5 rounded-lg border border-gray-200 focus:outline-none focus:ring-1 focus:ring-purple-500"
                  placeholder="e.g. Domain adapted model retrained on recent operational wear cycles..."
                />
              </div>
            </div>
          </div>

          <button
            onClick={handleDeploy}
            disabled={!selectedCandidate}
            className="mt-6 w-full py-2.5 px-4 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-xl shadow-xs text-xs transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <ShieldCheck className="w-4 h-4" />
            Approve & Hot-Deploy as Next Production Version
          </button>
        </div>
      </div>

      {/* Model Version History Audit Trail */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <History className="w-5 h-5 text-gray-600" />
          <h3 className="font-bold text-gray-900 text-base">Model Deployment Version Audit Trail</h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-600 font-semibold border-y border-gray-200">
              <tr>
                <th className="py-2.5 px-3">Version</th>
                <th className="py-2.5 px-3">Deployed At</th>
                <th className="py-2.5 px-3">Model Architecture</th>
                <th className="py-2.5 px-3">R² Score</th>
                <th className="py-2.5 px-3">MAE (Days)</th>
                <th className="py-2.5 px-3">Approved By</th>
                <th className="py-2.5 px-3">Engineering Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {pipelineData?.version_history?.map((v, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  <td className="py-2.5 px-3 font-mono font-bold text-purple-700">v{v.version}</td>
                  <td className="py-2.5 px-3 text-gray-500 font-mono">{v.deployed_at}</td>
                  <td className="py-2.5 px-3 font-semibold text-gray-900">{v.model_name}</td>
                  <td className="py-2.5 px-3 font-mono font-semibold text-gray-900">{(v.r2_score * 100).toFixed(1)}%</td>
                  <td className="py-2.5 px-3 font-mono text-gray-700">{v.mae}</td>
                  <td className="py-2.5 px-3 text-gray-700 font-medium">{v.approver}</td>
                  <td className="py-2.5 px-3 text-gray-500 max-w-xs truncate">{v.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
