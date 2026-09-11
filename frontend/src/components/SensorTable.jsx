import React from 'react';
import StatusBadge from './StatusBadge';

const SensorTable = ({ logs, unitSystem = 'metric' }) => {
  const logList = logs || [];

  return (
    <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-5">
      <div className="flex items-center justify-between pb-3 border-b border-gray-200 mb-3">
        <div>
          <h2 className="text-sm font-bold text-gray-900">Recent Telemetry Event Log</h2>
          <p className="text-xs text-gray-500">Real-time edge telemetry stream with AI Remaining Useful Life and Health</p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 bg-gray-100 text-gray-700 rounded-md border border-gray-200">
          Last {logList.length} readings
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left text-gray-600">
          <thead className="text-[11px] text-gray-500 uppercase bg-gray-50/80 border-b border-gray-200 font-bold tracking-wider">
            <tr>
              <th scope="col" className="px-4 py-2.5">Timestamp</th>
              <th scope="col" className="px-4 py-2.5">Temperature</th>
              <th scope="col" className="px-4 py-2.5">Vibration</th>
              <th scope="col" className="px-4 py-2.5">Pressure</th>
              <th scope="col" className="px-4 py-2.5">Current</th>
              <th scope="col" className="px-4 py-2.5">Predicted RUL</th>
              <th scope="col" className="px-4 py-2.5">Health</th>
              <th scope="col" className="px-4 py-2.5">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 font-mono">
            {logList.length === 0 ? (
              <tr>
                <td colSpan="8" className="px-4 py-4 text-center text-gray-400 font-sans">
                  No telemetry stream available
                </td>
              </tr>
            ) : (
              logList.map((log, idx) => {
                const timestamp = log.timestamp || log.Timestamp || '--';
                const temp = log.temperature ?? log.Temperature ?? '--';
                const vib = log.vibration ?? log.Vibration ?? '--';
                const press = log.pressure ?? log.Pressure ?? '--';
                const curr = log.motor_current ?? log.Motor_Current ?? '--';
                const rul = log.predicted_rul ?? log.Predicted_RUL ?? log.predicted_rul_days ?? '--';
                const health = log.machine_health ?? log.Machine_Health ?? log.health ?? '--';
                const status = log.status || log.Maintenance_Status || log.Machine_Status || 'Healthy';

                const tUnit = log.units?.temperature || (unitSystem === 'imperial' ? '°F' : (unitSystem === 'normalized' ? 'σ' : '°C'));
                const vUnit = log.units?.vibration || (unitSystem === 'imperial' ? 'in/s' : (unitSystem === 'normalized' ? 'σ' : 'mm/s'));
                const pUnit = log.units?.pressure || (unitSystem === 'imperial' ? 'psi' : (unitSystem === 'normalized' ? 'σ' : 'bar'));
                const cUnit = unitSystem === 'normalized' ? 'σ' : 'A';

                return (
                  <tr key={idx} className="hover:bg-gray-50/80 transition-colors">
                    <td className="px-4 py-2.5 text-gray-900 font-sans">{timestamp}</td>
                    <td className="px-4 py-2.5 font-semibold text-gray-800">{temp} <span className="text-[10px] text-gray-400 font-normal">{tUnit}</span></td>
                    <td className="px-4 py-2.5 font-semibold text-gray-800">{vib} <span className="text-[10px] text-gray-400 font-normal">{vUnit}</span></td>
                    <td className="px-4 py-2.5 font-semibold text-gray-800">{press} <span className="text-[10px] text-gray-400 font-normal">{pUnit}</span></td>
                    <td className="px-4 py-2.5 font-semibold text-gray-800">{curr} <span className="text-[10px] text-gray-400 font-normal">{cUnit}</span></td>
                    <td className="px-4 py-2.5 font-bold text-blue-700 font-sans">{rul} Days</td>
                    <td className="px-4 py-2.5 font-bold text-gray-900">{health}%</td>
                    <td className="px-4 py-2.5 font-sans">
                      <StatusBadge status={status} />
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SensorTable;
