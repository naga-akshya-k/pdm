import React, { useState, useEffect } from 'react';
import { getDriftStatus, triggerDriftRecalibrate } from '../services/api';
import { ShieldAlert, AlertTriangle, RefreshCw, Sparkles, Download, LineChart, FileText, CheckCircle2, GitCompare } from 'lucide-react';
import Plot from '../components/Plot';

export default function DriftMonitor() {
  const [driftData, setDriftData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recalibrating, setRecalibrating] = useState(false);
  const [recalResult, setRecalResult] = useState(null);
  const [reportExported, setReportExported] = useState(false);

  const fetchDrift = async () => {
    try {
      const data = await getDriftStatus();
      setDriftData(data);
    } catch (err) {
      console.error('Failed to fetch drift metrics:', err);
    }
  };

  useEffect(() => {
    fetchDrift();
    const interval = setInterval(fetchDrift, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleExportReport = () => {
    if (!driftData) return;
    const reportStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(driftData, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", reportStr);
    downloadAnchor.setAttribute("download", `Drift_Audit_Report_${new Date().toISOString().slice(0,10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    setReportExported(true);
    setTimeout(() => setReportExported(false), 3000);
  };

  const handleRecalibrate = async () => {
    try {
      setRecalibrating(true);
      const res = await triggerDriftRecalibrate();
      setRecalResult({
        type: 'success',
        text: res.message || 'AI models successfully recalibrated and domain adapted!'
      });
      await fetchDrift();
      setTimeout(() => setRecalResult(null), 8000);
    } catch (err) {
      console.error('Failed to recalibrate:', err);
      setRecalResult({
        type: 'error',
        text: 'Failed to complete AI recalibration. Please verify backend status.'
      });
      setTimeout(() => setRecalResult(null), 8000);
    } finally {
      setRecalibrating(false);
    }
  };

  const overallScore = driftData?.overall_drift_score || 0.0;
  const meanPsi = driftData?.mean_psi || 0.02;
  const isRetrainNeeded = driftData?.retraining_recommended;
  const timeline = driftData?.timeline || [];

  const timelineDays = timeline.map(t => `Day ${t.day}`);
  const timelineScores = timeline.map(t => t.drift_score * 100);
  const timelinePsi = timeline.map(t => t.psi);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
            <GitCompare className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Model Drifting & Statistical Reliability Monitor</h1>
            <p className="text-sm text-gray-500">
              Continuous Population Stability Index (PSI), Kolmogorov-Smirnov distribution tracking, and automated retraining triggers
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleExportReport}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            {reportExported ? 'Report Downloaded!' : 'Export Engineering Audit Report'}
          </button>
          <button
            onClick={fetchDrift}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Refresh
          </button>
        </div>
      </div>

      {/* Retraining Alert Banner */}
      {isRetrainNeeded && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-6 h-6 text-amber-600 flex-shrink-0" />
            <div>
              <h3 className="font-bold text-amber-900 text-sm">Automated Recalibration Threshold Exceeded</h3>
              <p className="text-xs text-amber-700 mt-0.5">
                Covariate distribution shift detected (PSI: {meanPsi} &gt; 0.25). Model domain adaptation recommended to maintain 99%+ RUL precision.
              </p>
            </div>
          </div>
          <button
            onClick={handleRecalibrate}
            disabled={recalibrating}
            className={`flex items-center gap-2 px-4 py-2.5 text-white text-xs font-bold rounded-lg shadow-xs transition-all flex-shrink-0 ${
              recalibrating ? 'bg-amber-400 cursor-not-allowed' : 'bg-amber-600 hover:bg-amber-700 active:scale-95'
            }`}
          >
            {recalibrating ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" /> Recalibrating Models...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" /> Trigger AI Recalibration
              </>
            )}
          </button>
        </div>
      )}

      {/* Recalibration Result Banner */}
      {recalResult && (
        <div className={`p-4 rounded-xl text-sm font-semibold flex items-center justify-between gap-3 border shadow-xs animate-in fade-in duration-300 ${
          recalResult.type === 'success'
            ? 'bg-emerald-50 border-emerald-300 text-emerald-900'
            : 'bg-red-50 border-red-300 text-red-900'
        }`}>
          <div className="flex items-center gap-2.5">
            {recalResult.type === 'success' ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
            )}
            <span>{recalResult.text}</span>
          </div>
        </div>
      )}

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-5">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">Fleet Drift Severity Index</span>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-black font-mono text-gray-900">{(overallScore * 100).toFixed(1)}%</span>
            <span className="text-xs text-gray-400">/ 100%</span>
          </div>
          <div className="w-full bg-gray-100 h-2 rounded-full mt-3 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                overallScore >= 0.45 ? 'bg-red-500' : (overallScore >= 0.25 ? 'bg-amber-500' : 'bg-emerald-500')
              }`}
              style={{ width: `${Math.min(100, overallScore * 100)}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Status: <span className="font-semibold text-gray-800">{driftData?.drift_status || 'Nominal'}</span></p>
        </div>

        <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-5">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">Population Stability Index (PSI)</span>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-black font-mono text-indigo-700">{meanPsi}</span>
            <span className="text-xs text-gray-400">PSI</span>
          </div>
          <p className="text-xs text-gray-500 mt-3">
            {meanPsi < 0.10 ? 'Stable (< 0.10)' : (meanPsi < 0.25 ? 'Moderate Shift (0.10–0.25)' : 'Significant Shift (> 0.25)')}
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-5">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">Drift Categorization</span>
          <span className="text-sm font-bold text-gray-900 block mt-2">{driftData?.drift_category || 'Nominal Factory Baseline'}</span>
          <p className="text-xs text-gray-400 mt-2">Covariate vs Concept Shift Classification</p>
        </div>

        <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-5">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">Drifting Channels</span>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-black font-mono text-amber-600">
              {driftData?.feature_metrics?.filter(f => f.status !== 'Normal').length || 0}
            </span>
            <span className="text-xs text-gray-400">/ 8 Channels</span>
          </div>
          <p className="text-xs text-gray-500 mt-3">Sample: {driftData?.sample_size || 0} recent operational records</p>
        </div>
      </div>

      {/* Historical Drift Time-Series Timeline Chart */}
      {timeline.length > 1 && (
        <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-5">
          <h3 className="font-bold text-gray-900 text-sm mb-1">Operational Drift Time-Series Evolution</h3>
          <p className="text-xs text-gray-500 mb-3">Tracks day-by-day distribution divergence as equipment accumulates runtime wear</p>

          <div className="w-full h-[260px]">
            <Plot
              data={[
                {
                  x: timelineDays,
                  y: timelineScores,
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'Drift Severity (%)',
                  line: { color: '#F59E0B', width: 2 },
                  marker: { size: 6 }
                },
                {
                  x: timelineDays,
                  y: timelineDays.map(() => 45),
                  type: 'scatter',
                  mode: 'lines',
                  name: 'Critical Threshold (45%)',
                  line: { color: '#EF4444', dash: 'dash', width: 1.5 }
                }
              ]}
              layout={{
                autosize: true,
                height: 250,
                margin: { l: 45, r: 20, t: 20, b: 40 },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: '#FAFAFA',
                xaxis: { gridcolor: '#F3F4F6', title: { text: 'Operational Timeline', font: { size: 10 } } },
                yaxis: { gridcolor: '#F3F4F6', title: { text: 'Drift Index (%)', font: { size: 10 } }, range: [0, 100] },
                legend: { orientation: 'h', y: 1.15, x: 1, xanchor: 'right' }
              }}
              useResizeHandler={true}
              style={{ width: '100%', height: '100%' }}
              config={{ displayModeBar: false, responsive: true }}
            />
          </div>
        </div>
      )}

      {/* Feature-by-Feature Drift Table */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-1">Per-Sensor Distribution Divergence & PSI Matrix</h3>
        <p className="text-xs text-gray-500 mb-4">Compares live telemetry distributions against factory baseline parameters</p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-600 font-semibold border-y border-gray-200">
              <tr>
                <th className="py-2.5 px-3">Telemetry Channel</th>
                <th className="py-2.5 px-3">Drift Index</th>
                <th className="py-2.5 px-3">PSI Metric</th>
                <th className="py-2.5 px-3">KS Statistic</th>
                <th className="py-2.5 px-3">KS p-Value</th>
                <th className="py-2.5 px-3">Live Mean</th>
                <th className="py-2.5 px-3">Baseline Mean</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {driftData?.feature_metrics?.map((f) => {
                const isDrifting = f.status !== 'Normal';
                return (
                  <tr key={f.feature} className={isDrifting ? 'bg-amber-50/40 hover:bg-amber-50/70' : 'hover:bg-gray-50'}>
                    <td className="py-2.5 px-3 font-semibold text-gray-900">{f.feature}</td>
                    <td className="py-2.5 px-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-gray-200 h-2 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              f.drift_score >= 0.45 ? 'bg-red-500' : (f.drift_score >= 0.25 ? 'bg-amber-500' : 'bg-emerald-500')
                            }`}
                            style={{ width: `${Math.min(100, f.drift_score * 100)}%` }}
                          ></div>
                        </div>
                        <span className="font-mono text-gray-700 font-medium">{(f.drift_score * 100).toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className="py-2.5 px-3 font-mono font-bold text-indigo-700">{f.psi}</td>
                    <td className="py-2.5 px-3 font-mono text-gray-700">{f.ks_stat}</td>
                    <td className="py-2.5 px-3 font-mono text-gray-700">{f.ks_p_value}</td>
                    <td className="py-2.5 px-3 font-mono font-semibold text-gray-900">{f.live_mean}</td>
                    <td className="py-2.5 px-3 font-mono text-gray-500">{f.baseline_mean}</td>
                    <td className="py-2.5 px-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold ${
                        f.status === 'Critical Drift'
                          ? 'bg-red-100 text-red-800'
                          : (f.status === 'Moderate Drift' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800')
                      }`}>
                        {f.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
