import React from 'react';
import { Thermometer, Activity, Zap, Calendar, ShieldAlert, Volume2, Gauge, RotateCw, Radio, Weight, Cpu } from 'lucide-react';
import GaugeCard from '../components/GaugeCard';
import MetricCard from '../components/MetricCard';
import StatusBadge from '../components/StatusBadge';
import LiveChart from '../components/LiveChart';
import SensorTable from '../components/SensorTable';
import TagIdMonitorCard from '../components/TagIdMonitorCard';

const Dashboard = ({ currentData, historyData, logs, liveTagsData, unitSystem = 'metric' }) => {
  const health = currentData?.machine_health ?? 100;
  const statusColor =
    health >= 80 ? '#22C55E' : health >= 60 ? '#2563EB' : health >= 40 ? '#F59E0B' : '#EF4444';

  const subcomps = currentData?.subcomponents || {};

  return (
    <div className="space-y-5">
      {/* Top Banner with Machine Details & Active AI Model */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-50 text-blue-600 rounded-xl">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-gray-900">Model Telemetry & SCADA Signal Ingress</h1>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                {currentData?.machine_id || 'MCH-802X'}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">
              Asset: <span className="font-semibold text-gray-800">{currentData?.machine_name || 'Turbine Motor Unit A1'}</span> ({currentData?.machine_type || 'Gas Turbine Compressor'}) &bull; Location: {currentData?.location || 'Plant Floor (Bay 4)'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-indigo-50 border border-indigo-200 px-3 py-1.5 rounded-lg text-right">
            <span className="text-[10px] text-indigo-700 font-semibold uppercase tracking-wider block">Inference Engine</span>
            <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-950 font-mono">
              <Cpu className="w-3.5 h-3.5 text-indigo-600" />
              {currentData?.active_ai_model || 'Random Forest'} (v{currentData?.model_version || '1.0'})
              <span className="text-[10px] font-normal text-indigo-600">[{currentData?.inference_latency_ms || 1.2}ms]</span>
            </div>
          </div>

          <StatusBadge status={currentData?.machine_status || 'Healthy'} />
        </div>
      </div>

      {/* Row 1: Health Gauge, RUL Prediction, Alert Status */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3 items-stretch">
        <div className="lg:col-span-2 min-w-[200px]">
          <GaugeCard value={health} statusColor={statusColor} />
        </div>

        <div className="lg:col-span-2">
          <MetricCard
            title="Predicted Remaining Useful Life"
            value={currentData?.predicted_rul_days ?? '--'}
            unit="Days"
            icon={Calendar}
            valueColor="text-blue-600"
          />
        </div>

        <div className="lg:col-span-2">
          <MetricCard
            title="Turbine Motor Maintenance Status"
            badgeComponent={<StatusBadge status={currentData?.alert_status || 'Healthy'} />}
          />
        </div>

        <div className="lg:col-span-2">
          <MetricCard
            title="Turbine Operational State"
            value={currentData?.active_event !== 'None' ? currentData?.active_event : 'Nominal Baseline'}
            icon={ShieldAlert}
            valueColor={currentData?.active_event !== 'None' ? 'text-red-600' : 'text-emerald-600'}
          />
        </div>
      </div>

      {/* Industrial Tag ID Telemetry Inspector (Company Workstation GPU Stream) */}
      <TagIdMonitorCard liveTagsData={liveTagsData} />

      {/* Row 2: 8 Physical Telemetry Channels */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
        <MetricCard
          title="Temperature"
          value={currentData?.temperature ?? '--'}
          unit={currentData?.units?.temperature || "°C"}
          icon={Thermometer}
        />
        <MetricCard
          title="Vibration RMS"
          value={currentData?.vibration ?? '--'}
          unit={currentData?.units?.vibration || "mm/s"}
          icon={Activity}
        />
        <MetricCard
          title="Motor Current"
          value={currentData?.motor_current ?? '--'}
          unit={currentData?.units?.motor_current || "A"}
          icon={Zap}
        />
        <MetricCard
          title="Acoustic Noise"
          value={currentData?.acoustic_noise ?? '--'}
          unit={currentData?.units?.acoustic_noise || "dB"}
          icon={Volume2}
        />
        <MetricCard
          title="Line Pressure"
          value={currentData?.pressure ?? '--'}
          unit={currentData?.units?.pressure || "bar"}
          icon={Gauge}
        />
        <MetricCard
          title="Rotation Speed"
          value={currentData?.rpm ?? '--'}
          unit={currentData?.units?.rpm || "RPM"}
          icon={RotateCw}
        />
        <MetricCard
          title="Frequency"
          value={currentData?.frequency ?? '--'}
          unit={currentData?.units?.frequency || "Hz"}
          icon={Radio}
        />
        <MetricCard
          title="Operating Load"
          value={currentData?.load ?? '--'}
          unit={currentData?.units?.load || "kN"}
          icon={Weight}
        />
      </div>

      {/* Row 3: Subcomponent Health Diagnostics */}
      {Object.keys(subcomps).length > 0 && (
        <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-4">
          <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-3">Subsystem Physical Health Indices</h3>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {Object.entries(subcomps).map(([comp, val]) => {
              const barColor = val >= 80 ? 'bg-emerald-500' : (val >= 60 ? 'bg-amber-500' : 'bg-red-500');
              return (
                <div key={comp} className="p-2.5 bg-gray-50 rounded-lg border border-gray-100">
                  <div className="flex justify-between items-center text-xs mb-1">
                    <span className="text-gray-600 capitalize font-medium">{comp.replace('_', ' ')}</span>
                    <span className="font-bold font-mono text-gray-900">{val}%</span>
                  </div>
                  <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${barColor}`} style={{ width: `${val}%` }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Row 4: Live Sensor Graph */}
      <LiveChart historyData={historyData} />

      {/* Row 5: Recent Telemetry Log Table */}
      <SensorTable logs={logs} unitSystem={unitSystem} />
    </div>
  );
};

export default Dashboard;
