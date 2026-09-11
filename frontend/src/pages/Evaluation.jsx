import React from 'react';
import ModelEvaluation from '../components/ModelEvaluation';

const Evaluation = ({ modelData }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between pb-2 border-b border-gray-200">
        <div>
          <h1 className="text-base font-bold text-gray-900">Machine Learning Model Diagnostics</h1>
          <p className="text-xs text-gray-500">Model performance, accuracy metrics, and error distribution</p>
        </div>
      </div>
      <ModelEvaluation modelData={modelData} />
    </div>
  );
};

export default Evaluation;
