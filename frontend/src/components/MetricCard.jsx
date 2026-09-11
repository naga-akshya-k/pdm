import React from 'react';

const MetricCard = ({ title, value, unit, icon: Icon, valueColor = 'text-gray-900', badgeComponent }) => {
  return (
    <div className="industrial-card p-4 flex flex-col justify-between h-full flex-1 min-w-0">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold text-gray-500 uppercase tracking-wider truncate">{title}</span>
        {Icon && <Icon className="w-4 h-4 text-gray-400 shrink-0 ml-1" />}
      </div>
      <div className="mt-2 mb-1 flex items-baseline justify-between">
        {badgeComponent ? (
          badgeComponent
        ) : (
          <div className={`text-xl sm:text-2xl font-bold tracking-tight ${valueColor} truncate`}>
            {value} <span className="text-xs font-normal text-gray-500">{unit}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricCard;
