import React from 'react';
import AnalyticsCharts from '../components/AnalyticsCharts';

const Analytics = ({ historyData }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between pb-2 border-b border-gray-200">
        <div>
          <h1 className="text-base font-bold text-gray-900">Historical Trends & Future Projections</h1>
          <p className="text-xs text-gray-500">Comparative multi-parameter degradation analysis</p>
        </div>
      </div>
      <AnalyticsCharts historyData={historyData} />
    </div>
  );
};

export default Analytics;
