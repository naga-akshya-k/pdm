import React from 'react';
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
              name: 'Actual',
              line: { color: actualColor, width: 2 },
            },
            {
              x: xFuture,
              y: predicted,
              type: 'scatter',
              mode: 'lines',
              name: 'Predicted Future',
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

const AnalyticsCharts = ({ historyData }) => {
  const healthTrend = historyData?.machine_health_trend?.actual || [];
  let degradationDay = null;
  for (let i = 0; i < healthTrend.length; i++) {
    if (healthTrend[i] < 98.0) {
      degradationDay = i + 1;
      break;
    }
  }

  return (
    <div className="space-y-4">
      {/* 2 Column Grid for Temp, Vib, Current, Health */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
        <SingleTrendPlot
          title="Machine Health Trend"
          yLabel="%"
          trendData={historyData?.machine_health_trend}
          actualColor="#22C55E"
          degradationDay={degradationDay}
        />
      </div>

      {/* Full Width RUL Trend */}
      <SingleTrendPlot
        title="Remaining Useful Life (RUL) Trend"
        yLabel="Days"
        trendData={historyData?.rul_trend}
        actualColor="#2563EB"
        isFullWidth={true}
        degradationDay={degradationDay}
      />
    </div>
  );
};

export default AnalyticsCharts;
