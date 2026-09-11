import React from 'react';
import { Calendar, Wrench, ShieldCheck, Clock } from 'lucide-react';
import MetricCard from './MetricCard';
import StatusBadge from './StatusBadge';
import Plot from './Plot';

const SingleTrendPlot = ({ title, yLabel, trendData, actualColor = '#2563EB', isFullWidth = false, degradationDay = null }) => {
  const actual = trendData?.actual || [];
  const predicted = trendData?.predicted_future || [];

  const xHist = actual.map((_, i) => i + 1);
  const latestDay = xHist.length > 0 ? xHist[xHist.length - 1] : 1;
  const xFuture = actual.length > 0 ? predicted.map((_, i) => latestDay + i) : [];

  const visibleMin = Math.max(1, latestDay - 100);
  const visibleMax = latestDay + 20;

  const shapes = degradationDay ? [
    {
      type: 'line',
      x0: degradationDay,
      x1: degradationDay,
      y0: 0,
      y1: 1,
      yref: 'paper',
      line: { color: '#EF4444', width: 1.5, dash: 'dash' },
    },
  ] : [];

  const annotations = degradationDay ? [
    {
      x: degradationDay,
      y: 1.05,
      yref: 'paper',
      text: `Degradation (Day ${degradationDay})`,
      showarrow: false,
      font: { size: 9, color: '#DC2626' },
      bgcolor: '#FEE2E2',
      bordercolor: '#FCA5A5',
      borderwidth: 1,
      borderpad: 2,
    },
  ] : [];

  return (
    <div className={`industrial-card p-4 ${isFullWidth ? 'w-full' : ''}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">{title}</h3>
        {actual.length > 0 && (
          <span className="text-[11px] text-gray-500 font-mono">
            Latest: {actual[actual.length - 1]} {yLabel}
          </span>
        )}
      </div>

      <div className="w-full h-64">
        <Plot
          data={[
            {
              x: xHist,
              y: actual,
              type: 'scatter',
              mode: 'lines',
              name: 'Historical Reading',
              line: { color: actualColor, width: 2 },
            },
            {
              x: xFuture,
              y: predicted,
              type: 'scatter',
              mode: 'lines',
              name: '20-Step Trend Extrapolation',
              line: { color: '#F59E0B', width: 2, dash: 'dash' },
            },
          ]}
          layout={{
            autosize: true,
            height: 240,
            margin: { l: 40, r: 15, t: 25, b: 35 },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: '#FAFAFA',
            xaxis: {
              title: { text: 'Day', font: { size: 10, color: '#6B7280' } },
              gridcolor: '#F3F4F6',
              zeroline: false,
              range: [visibleMin, visibleMax],
              autorange: false,
            },
            yaxis: {
              title: { text: yLabel, font: { size: 10, color: '#6B7280' } },
              gridcolor: '#F3F4F6',
              zeroline: false,
            },
            shapes: shapes,
            annotations: annotations,
            legend: {
              orientation: 'h',
              y: 1.2,
              x: 1,
              xanchor: 'right',
              font: { size: 10, color: '#4B5563' },
            },
          }}
          useResizeHandler={true}
          style={{ width: '100%', height: '100%' }}
          config={{ displayModeBar: false, responsive: true }}
        />
      </div>
    </div>
  );
};

const MaintenanceDashboard = ({ maintenanceData, historyData }) => {
  const predictedRul = maintenanceData?.predicted_rul_days ?? '--';
  const status = maintenanceData?.maintenance_status || 'Healthy';
  const action = maintenanceData?.recommended_action || 'Continue Normal Operation';
  const priority = maintenanceData?.inspection_priority || 'Low';
  const window = maintenanceData?.next_inspection_window || 'Routine inspection within 90–120 days';

  const healthTrend = historyData?.machine_health_trend?.actual || [];
  let degradationDay = null;
  for (let i = 0; i < healthTrend.length; i++) {
    if (healthTrend[i] < 98.0) {
      degradationDay = i + 1;
      break;
    }
  }

  const getPriorityBadgeClass = (p) => {
    switch (p) {
      case 'Critical':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'Urgent':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'High':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'Moderate':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Row: Key Maintenance Decision Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Predicted RUL */}
        <MetricCard
          title="Predicted Remaining Useful Life"
          value={predictedRul}
          unit="Days"
          icon={Calendar}
          valueColor="text-blue-600"
        />

        {/* Maintenance Status */}
        <MetricCard
          title="Maintenance Status"
          icon={Wrench}
          badgeComponent={<StatusBadge status={status} />}
        />

        {/* Recommended Action */}
        <div className="industrial-card p-4 flex flex-col justify-between h-full flex-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Recommended Action</span>
            <ShieldCheck className="w-4 h-4 text-blue-500 shrink-0 ml-1" />
          </div>
          <div className="mt-2 mb-1">
            <span className="text-xs font-semibold text-gray-800 bg-blue-50 px-2.5 py-1.5 rounded border border-blue-200 block truncate" title={action}>
              {action}
            </span>
          </div>
        </div>

        {/* Inspection Priority & Next Inspection Window */}
        <div className="industrial-card p-4 flex flex-col justify-between h-full flex-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Inspection Priority</span>
            <Clock className="w-4 h-4 text-amber-500 shrink-0 ml-1" />
          </div>
          <div className="mt-2 space-y-1">
            <div className="flex items-center space-x-2">
              <span className={`text-xs font-bold px-2 py-0.5 rounded border ${getPriorityBadgeClass(priority)}`}>
                {priority} Priority
              </span>
            </div>
            <p className="text-[11px] font-medium text-gray-600 truncate" title={window}>
              {window}
            </p>
          </div>
        </div>
      </div>

      {/* Main Full-Width Predicted RUL Trend Chart */}
      <SingleTrendPlot
        title="Predicted Remaining Useful Life Trend & Projection"
        yLabel="Days"
        trendData={historyData?.rul_trend}
        actualColor="#2563EB"
        isFullWidth={true}
        degradationDay={degradationDay}
      />

      {/* 2x2 Grid for Machine Health & Physical Sensor Trends */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SingleTrendPlot
          title="Machine Health Trend"
          yLabel="%"
          trendData={historyData?.machine_health_trend}
          actualColor="#22C55E"
          degradationDay={degradationDay}
        />
        <SingleTrendPlot
          title="Temperature Trend"
          yLabel="°C"
          trendData={historyData?.temperature_trend}
          actualColor="#2563EB"
          degradationDay={degradationDay}
        />
        <SingleTrendPlot
          title="Vibration RMS Trend"
          yLabel="mm/s"
          trendData={historyData?.vibration_trend}
          actualColor="#2563EB"
          degradationDay={degradationDay}
        />
        <SingleTrendPlot
          title="Motor Current Trend"
          yLabel="A"
          trendData={historyData?.motor_current_trend}
          actualColor="#2563EB"
          degradationDay={degradationDay}
        />
      </div>
    </div>
  );
};

export default MaintenanceDashboard;
