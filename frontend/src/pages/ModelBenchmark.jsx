import React, { useState, useEffect } from 'react';
import { getCandidateModelsBenchmark, setActiveInferenceModel } from '../services/api';
import { Cpu, CheckCircle2, Zap, BarChart3, Gauge, ArrowRight, ShieldCheck, Activity } from 'lucide-react';

export default function ModelBenchmark({ onModelChange }) {
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [switching, setSwitching] = useState(null);
  const [msg, setMsg] = useState(null);

  const fetchBenchmarks = async () => {
    try {
      setLoading(true);
      const data = await getCandidateModelsBenchmark();
      setBenchmarkData(data);
    } catch (err) {
      console.error('Failed to load benchmarks:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBenchmarks();
  }, []);

  const handleSelectModel = async (modelName) => {
    try {
      setSwitching(modelName);
      await setActiveInferenceModel(modelName);
      setMsg({ type: 'success', text: `Switched active inference model to ${modelName}` });
      if (onModelChange) onModelChange(modelName);
      await fetchBenchmarks();
      setTimeout(() => setMsg(null), 3500);
    } catch (err) {
      setMsg({ type: 'error', text: 'Failed to switch active model' });
    } finally {
      setSwitching(null);
    }
  };

  const models = benchmarkData?.benchmarks ? Object.values(benchmarkData.benchmarks) : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Model Evaluation & Algorithm Benchmarking</h1>
            <p className="text-sm text-gray-500">
              Multi-Model Performance Matrix: Compare Random Forest, Gradient Boosting, MLP, and Support Vector Regression (MAE, RMSE, R²)
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="text-right text-xs">
            <div className="text-gray-400 font-medium">Active Production Engine</div>
            <div className="font-bold text-indigo-700 text-sm">{benchmarkData?.active_model || 'Random Forest'} (v{benchmarkData?.model_version || '1.0'})</div>
          </div>
        </div>
      </div>

      {msg && (
        <div className={`p-4 rounded-lg text-sm font-medium border ${msg.type === 'success' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-red-50 text-red-800 border-red-200'}`}>
          {msg.text}
        </div>
      )}

      {/* Candidate Models Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {models.map((m) => {
          const isActive = m.is_active;

          return (
            <div
              key={m.name}
              className={`bg-white rounded-xl shadow-xs border flex flex-col justify-between transition-all duration-200 ${
                isActive ? 'border-indigo-600 ring-2 ring-indigo-500/20 shadow-md' : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="p-5">
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div>
                    <h3 className="font-bold text-gray-900 text-base">{m.name}</h3>
                    <span className="text-[11px] text-gray-400">Model Version: {m.model_version || '1.0'}</span>
                  </div>
                  {isActive ? (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                      <CheckCircle2 className="w-3 h-3 text-indigo-600" /> Active
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-gray-100 text-gray-600">
                      Candidate
                    </span>
                  )}
                </div>

                {/* Accuracy & Metrics */}
                <div className="grid grid-cols-2 gap-2 my-4 pt-3 border-t border-gray-100">
                  <div className="bg-gray-50 p-2.5 rounded-lg border border-gray-100">
                    <span className="text-[11px] text-gray-500 block">R² Accuracy</span>
                    <span className="text-base font-bold text-gray-900 font-mono">{(m.r2_score * 100).toFixed(1)}%</span>
                  </div>
                  <div className="bg-gray-50 p-2.5 rounded-lg border border-gray-100">
                    <span className="text-[11px] text-gray-500 block">MAE Error</span>
                    <span className="text-base font-bold text-gray-900 font-mono">{m.mae} Days</span>
                  </div>
                  <div className="bg-gray-50 p-2.5 rounded-lg border border-gray-100">
                    <span className="text-[11px] text-gray-500 block">RMSE</span>
                    <span className="text-base font-bold text-gray-900 font-mono">{m.rmse} Days</span>
                  </div>
                  <div className="bg-gray-50 p-2.5 rounded-lg border border-gray-100">
                    <span className="text-[11px] text-gray-500 block">Latency</span>
                    <span className="text-base font-bold text-indigo-600 font-mono">{m.inference_latency_ms} ms</span>
                  </div>
                </div>

                {/* Top Features */}
                <div className="space-y-1.5 pt-2">
                  <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider block">Top Feature Weights</span>
                  {m.feature_importance?.slice(0, 3).map((f) => (
                    <div key={f.feature} className="flex justify-between items-center text-xs">
                      <span className="text-gray-600">{f.feature}</span>
                      <span className="font-mono text-gray-900 font-medium">{(f.importance * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Bottom Action */}
              <div className="p-4 bg-gray-50/80 border-t border-gray-100 rounded-b-xl">
                <button
                  disabled={isActive || switching === m.name}
                  onClick={() => handleSelectModel(m.name)}
                  className={`w-full py-2 px-3 rounded-lg text-xs font-bold transition-all duration-200 flex items-center justify-center gap-1.5 ${
                    isActive
                      ? 'bg-indigo-600 text-white cursor-default opacity-90'
                      : 'bg-white border border-gray-200 text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200'
                  }`}
                >
                  {isActive ? (
                    <>
                      <ShieldCheck className="w-3.5 h-3.5" /> Currently Driving Live Telemetry
                    </>
                  ) : switching === m.name ? (
                    'Hot-Swapping...'
                  ) : (
                    <>
                      <Zap className="w-3.5 h-3.5 text-amber-500" /> Hot-Swap to Live Inference
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Feature Importance Deep Dive Table */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-1">Explainability & Feature Sensitivity Matrix</h3>
        <p className="text-xs text-gray-500 mb-4">Relative predictive contribution of each industrial sensor channel across the 4 candidate models</p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-600 font-semibold border-y border-gray-200">
              <tr>
                <th className="py-2.5 px-3">Telemetry Feature</th>
                {models.map(m => (
                  <th key={m.name} className="py-2.5 px-3 font-mono">{m.name}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {['Temperature', 'Vibration', 'Motor_Current', 'Acoustic_Noise', 'Pressure', 'RPM', 'Frequency', 'Load'].map(feat => (
                <tr key={feat} className="hover:bg-gray-50">
                  <td className="py-2.5 px-3 font-medium text-gray-900">{feat}</td>
                  {models.map(m => {
                    const item = m.feature_importance?.find(x => x.feature === feat);
                    const weight = item ? item.importance : 0.0;
                    return (
                      <td key={m.name} className="py-2.5 px-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-gray-200 h-1.5 rounded-full overflow-hidden">
                            <div className="bg-indigo-600 h-full rounded-full" style={{ width: `${Math.min(100, weight * 100)}%` }}></div>
                          </div>
                          <span className="font-mono text-gray-700">{(weight * 100).toFixed(1)}%</span>
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
