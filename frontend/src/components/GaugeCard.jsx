import React from 'react';
import Plot from 'react-plotly.js';

const GaugeCard = ({ value, statusColor = '#22C55E' }) => {
  const healthVal = value ?? 100;

  return (
    <div className="industrial-card p-3 flex flex-col items-center justify-center h-full">
      <div className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Health Index</div>
      <div className="w-full flex justify-center items-center">
        <Plot
          data={[
            {
              type: "indicator",
              mode: "gauge+number",
              value: healthVal,
              number: { suffix: "%", font: { size: 22, color: "#111827", family: "sans-serif" } },
              gauge: {
                axis: { range: [0, 100], tickwidth: 1, tickcolor: "#E5E7EB", visible: false },
                bar: { color: statusColor, width: 0.25 },
                bgcolor: "white",
                borderwidth: 1,
                bordercolor: "#E5E7EB",
                steps: [
                  { range: [0, 40], color: '#FEE2E2' },
                  { range: [40, 60], color: '#FEF3C7' },
                  { range: [60, 80], color: '#DBEAFE' },
                  { range: [80, 100], color: '#D1FAE5' }
                ]
              }
            }
          ]}
          layout={{
            width: 200,
            height: 160,
            margin: { l: 15, r: 15, t: 10, b: 10 },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
          }}
          config={{ displayModeBar: false, responsive: true }}
        />
      </div>
    </div>
  );
};

export default GaugeCard;
