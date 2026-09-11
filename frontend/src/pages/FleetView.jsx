import React, { useState, useEffect } from 'react';
import { selectFleetMachine, injectSimulatorFault, clearSimulatorFault } from '../services/api';
import { Activity, AlertTriangle, CheckCircle2, Flame, RefreshCw, Zap, Gauge, Wrench } from 'lucide-react';

export default function FleetView({ fleetData, onSelectMachine, currentMachineId }) {
  const [selectedFault, setSelectedFault] = useState('bearing_degradation');
  const [faultDuration, setFaultDuration] = useState(25);
  const [actionStatus, setActionStatus] = useState(null);

  const machines = fleetData?.fleet || [];

  const handleInjectFault = async (machineId) => {
    try {
      const res = await injectSimulatorFault(selectedFault, faultDuration, machineId);
      setActionStatus({ type: 'success', message: `Injected ${selectedFault.replace('_', ' ')} on ${machineId}` });
      setTimeout(() => setActionStatus(null), 4000);
    } catch (err) {
      setActionStatus({ type: 'error', message: 'Failed to inject fault' });
    }
  };

  const handleClearFault = async (machineId) => {
    try {
      await clearSimulatorFault(machineId);
      setActionStatus({ type: 'success', message: `Cleared active faults on ${machineId}` });
      setTimeout(() => setActionStatus(null), 4000);
    } catch (err) {
      setActionStatus({ type: 'error', message: 'Failed to clear fault' });
    }
  };

  const getStatusBadge = (status, health) => {
    if (health >= 80) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Healthy
        </span>
      );
    }
    if (health >= 60) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
          <Activity className="w-3.5 h-3.5 text-amber-600" /> Slight Wear
        </span>
      );
    }
    if (health >= 40) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-orange-50 text-orange-700 border border-orange-200">
          <AlertTriangle className="w-3.5 h-3.5 text-orange-600" /> Moderate Wear
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200 animate-pulse">
        <Flame className="w-3.5 h-3.5 text-red-600" /> Critical Condition
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Industrial Asset Fleet Overview</h1>
              <p className="text-sm text-gray-500">Real-time condition monitoring across 4 multi-stage plant units</p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4 text-sm text-gray-600 bg-gray-50 px-4 py-2 rounded-lg border border-gray-200">
          <div><span className="font-semibold text-gray-900">{machines.length}</span> Total Assets</div>
          <div className="h-4 w-px bg-gray-300"></div>
          <div><span className="font-semibold text-emerald-600">{machines.filter(m => m.health >= 80).length}</span> Healthy</div>
          <div className="h-4 w-px bg-gray-300"></div>
          <div><span className="font-semibold text-amber-600">{machines.filter(m => m.health >= 40 && m.health < 80).length}</span> Warning</div>
          <div className="h-4 w-px bg-gray-300"></div>
          <div><span className="font-semibold text-red-600">{machines.filter(m => m.health < 40).length}</span> Critical</div>
        </div>
      </div>

      {actionStatus && (
        <div className={`p-4 rounded-lg text-sm font-medium border ${actionStatus.type === 'success' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-red-50 text-red-800 border-red-200'}`}>
          {actionStatus.message}
        </div>
      )}

      {/* Fleet Asset Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {machines.length === 0 && (
          [1, 2, 3, 4].map((idx) => (
            <div key={idx} className="bg-white rounded-xl shadow-xs border border-gray-200 p-5 animate-pulse space-y-4">
              <div className="h-4 bg-gray-200 rounded w-1/3"></div>
              <div className="h-6 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              <div className="h-16 bg-gray-100 rounded"></div>
            </div>
          ))
        )}
        {machines.map((m) => {
          const isSelected = m.machine_id === currentMachineId;
          const healthColor = m.health >= 80 ? 'bg-emerald-500' : (m.health >= 60 ? 'bg-amber-500' : (m.health >= 40 ? 'bg-orange-500' : 'bg-red-500'));

          return (
            <div
              key={m.machine_id}
              className={`bg-white rounded-xl shadow-xs border transition-all duration-200 flex flex-col justify-between ${
                isSelected ? 'border-blue-600 ring-2 ring-blue-500/20 shadow-md' : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="p-5">
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div>
                    <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-gray-100 text-gray-700">
                      {m.machine_id}
                    </span>
                    <h3 className="font-bold text-gray-900 text-base mt-1.5 line-clamp-1">{m.name}</h3>
                    <p className="text-xs text-gray-500">{m.type}</p>
                  </div>
                  {getStatusBadge(m.status, m.health)}
                </div>

                <p className="text-xs text-gray-400 mb-4">{m.location}</p>

                {/* Health & RUL */}
                <div className="space-y-3 pt-3 border-t border-gray-100">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-500">Machine Health</span>
                      <span className="font-bold text-gray-900">{m.health}%</span>
                    </div>
                    <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full transition-all duration-500 ${healthColor}`} style={{ width: `${m.health}%` }}></div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs bg-gray-50 p-2.5 rounded-lg border border-gray-100">
                    <span className="text-gray-600">Remaining Useful Life</span>
                    <span className="font-bold text-blue-700 font-mono text-sm">{m.rul_days} Days</span>
                  </div>

                  {m.active_fault && m.active_fault !== 'None' && (
                    <div className="bg-red-50 border border-red-200 text-red-700 text-xs px-2.5 py-1.5 rounded-md flex items-center gap-1.5">
                      <Flame className="w-3.5 h-3.5 flex-shrink-0 text-red-600" />
                      <span className="font-semibold uppercase tracking-wider text-[10px]">Fault: {m.active_fault.replace('_', ' ')}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Bottom Actions */}
              <div className="p-4 bg-gray-50/80 border-t border-gray-100 rounded-b-xl flex items-center justify-between gap-2">
                <button
                  onClick={() => onSelectMachine(m.machine_id)}
                  className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-colors ${
                    isSelected
                      ? 'bg-blue-600 text-white shadow-xs'
                      : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {isSelected ? 'Active Machine' : 'Select Unit'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Interactive Fault Injection & Digital Twin Console */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
            <Wrench className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-gray-900">Physics-Based Digital Twin Fault Injection Console</h2>
            <p className="text-xs text-gray-500">Inject mechanical stress scenarios to test real-time AI detection and CMMS response</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-2">
          <div className="p-4 rounded-xl border border-gray-200 bg-gray-50 flex flex-col justify-between">
            <div>
              <h4 className="font-bold text-sm text-gray-900">Bearing Degradation</h4>
              <p className="text-xs text-gray-500 mt-1">High-frequency vibration spike (3.2x) with micro-spalling noise.</p>
            </div>
            <button
              onClick={() => { setSelectedFault('bearing_degradation'); handleInjectFault(currentMachineId); }}
              className="mt-4 w-full py-2 px-3 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-lg transition-colors shadow-xs"
            >
              Trigger Bearing Fault
            </button>
          </div>

          <div className="p-4 rounded-xl border border-gray-200 bg-gray-50 flex flex-col justify-between">
            <div>
              <h4 className="font-bold text-sm text-gray-900">Thermal Runaway</h4>
              <p className="text-xs text-gray-500 mt-1">Coolant failure causing rapid temperature surge (+32°C).</p>
            </div>
            <button
              onClick={() => { setSelectedFault('thermal_runaway'); handleInjectFault(currentMachineId); }}
              className="mt-4 w-full py-2 px-3 bg-orange-600 hover:bg-orange-700 text-white text-xs font-bold rounded-lg transition-colors shadow-xs"
            >
              Trigger Thermal Surge
            </button>
          </div>

          <div className="p-4 rounded-xl border border-gray-200 bg-gray-50 flex flex-col justify-between">
            <div>
              <h4 className="font-bold text-sm text-gray-900">Cavitation Surge</h4>
              <p className="text-xs text-gray-500 mt-1">Hydraulic line pressure drop (62%) with acoustic crackle.</p>
            </div>
            <button
              onClick={() => { setSelectedFault('cavitation'); handleInjectFault(currentMachineId); }}
              className="mt-4 w-full py-2 px-3 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-lg transition-colors shadow-xs"
            >
              Trigger Cavitation
            </button>
          </div>

          <div className="p-4 rounded-xl border border-gray-200 bg-gray-50 flex flex-col justify-between">
            <div>
              <h4 className="font-bold text-sm text-gray-900">Rotor Imbalance</h4>
              <p className="text-xs text-gray-500 mt-1">Mass eccentricity causing motor current overload (1.85x) and RPM drop.</p>
            </div>
            <div className="mt-4 flex gap-2">
              <button
                onClick={() => { setSelectedFault('rotor_imbalance'); handleInjectFault(currentMachineId); }}
                className="flex-1 py-2 px-3 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-lg transition-colors shadow-xs"
              >
                Trigger Imbalance
              </button>
              <button
                onClick={() => handleClearFault(currentMachineId)}
                className="py-2 px-3 bg-gray-200 hover:bg-gray-300 text-gray-800 text-xs font-bold rounded-lg transition-colors"
                title="Clear all faults"
              >
                Clear
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
