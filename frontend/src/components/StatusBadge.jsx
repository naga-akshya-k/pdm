import React from 'react';

const StatusBadge = ({ status }) => {
  const getBadgeStyle = (statusStr) => {
    switch (statusStr) {
      case 'Healthy':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'Slight Wear':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'Moderate Wear':
      case 'Warning':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'Critical':
      case 'Critical Alert':
      case 'Failure':
        return 'bg-red-50 text-red-700 border-red-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getBadgeStyle(status)}`}>
      <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-current"></span>
      {status || 'Unknown'}
    </span>
  );
};

export default StatusBadge;
