import React, { useState, useEffect, useRef } from 'react';
import TopBar from './components/TopBar';
import Sidebar from './components/Sidebar';
import FleetView from './pages/FleetView';
import EarlyWarningView from './pages/EarlyWarningView';
import Dashboard from './pages/Dashboard';
import ModelBenchmark from './pages/ModelBenchmark';
import DriftMonitor from './pages/DriftMonitor';
import RegenerativeStudio from './pages/RegenerativeStudio';
import WorkOrders from './pages/WorkOrders';
import {
  getStatus,
  getFleetOverview,
  selectFleetMachine,
  getCurrentData,
  getHistoryData,
  getRecentLogs,
  getMaintenanceData,
  postControlAction,
  getLiveTags,
} from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [backendStatus, setBackendStatus] = useState(true);
  const [statusData, setStatusData] = useState(null);
  const [fleetData, setFleetData] = useState(null);
  const [currentData, setCurrentData] = useState(null);
  const [historyData, setHistoryData] = useState(null);
  const [maintenanceData, setMaintenanceData] = useState(null);
  const [liveTagsData, setLiveTagsData] = useState(null);
  const [logs, setLogs] = useState([]);
  const [speed, setSpeed] = useState(1.0);
  const [autoPlay, setAutoPlay] = useState(false);
  const [unitSystem, setUnitSystem] = useState('metric');

  const consecutiveFailuresRef = useRef(0);

  // Initial fetch for system status
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const sData = await getStatus();
        setStatusData(sData);
        setBackendStatus(true);
        consecutiveFailuresRef.current = 0;
      } catch (err) {
        // Initial error handling
      }
    };
    fetchInitialData();
  }, []);

  // Polling loop (1000ms) for fleet and active machine telemetry
  useEffect(() => {
    let isSubscribed = true;

    const pollData = async () => {
      try {
        const [curr, hist, lg, maint, flt, tagsData] = await Promise.all([
          getCurrentData(unitSystem),
          getHistoryData(),
          getRecentLogs(unitSystem),
          getMaintenanceData(),
          getFleetOverview(),
          getLiveTags(),
        ]);

        if (isSubscribed) {
          setCurrentData(curr);
          setHistoryData(hist);
          setLogs(lg.logs || []);
          setMaintenanceData(maint);
          setFleetData(flt);
          setLiveTagsData(tagsData);
          setAutoPlay(curr.auto_play);
          setSpeed(curr.simulation_speed);

          consecutiveFailuresRef.current = 0;
          setBackendStatus(true);
        }
      } catch (err) {
        if (isSubscribed) {
          consecutiveFailuresRef.current += 1;
          if (consecutiveFailuresRef.current >= 3) {
            setBackendStatus(false);
          }
        }
      }
    };

    pollData();
    const interval = setInterval(pollData, 1000);

    return () => {
      isSubscribed = false;
      clearInterval(interval);
    };
  }, [unitSystem]);

  // Switch active machine
  const handleSelectMachine = async (machineId) => {
    try {
      await selectFleetMachine(machineId);
      const curr = await getCurrentData(unitSystem);
      setCurrentData(curr);
      const flt = await getFleetOverview();
      setFleetData(flt);
      setActiveTab('dashboard');
    } catch (err) {
      console.error('Failed to select machine:', err);
    }
  };

  // Handle simulation controls
  const handleControlAction = async (action, actionSpeed) => {
    try {
      const targetSpeed = actionSpeed !== undefined ? actionSpeed : speed;
      const res = await postControlAction(action, targetSpeed);
      if (res) {
        setAutoPlay(res.auto_play);
        setSpeed(res.simulation_speed);
      }
    } catch (err) {
      console.error('Control action error:', err);
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F7FA] flex flex-col font-sans text-gray-900 antialiased selection:bg-blue-100">
      {/* Top Header */}
      <TopBar
        backendStatus={backendStatus}
        statusData={statusData}
        currentData={currentData}
        unitSystem={unitSystem}
        setUnitSystem={setUnitSystem}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Navigation Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          currentData={currentData}
          backendStatus={backendStatus}
          onControlAction={handleControlAction}
          speed={speed}
          setSpeed={setSpeed}
          autoPlay={autoPlay}
        />

        {/* Dynamic Main Operations View */}
        <main className="flex-1 overflow-y-auto p-6 max-w-[1680px] mx-auto w-full">
          {activeTab === 'fleet' && (
            <FleetView
              fleetData={fleetData}
              onSelectMachine={handleSelectMachine}
              currentMachineId={currentData?.machine_id}
            />
          )}
          {activeTab === 'early_warning' && (
            <EarlyWarningView
              currentData={currentData}
            />
          )}
          {activeTab === 'dashboard' && (
            <Dashboard
              currentData={currentData}
              historyData={historyData}
              logs={logs}
              liveTagsData={liveTagsData}
              unitSystem={unitSystem}
            />
          )}
          {activeTab === 'benchmark' && (
            <ModelBenchmark
              onModelChange={() => {}}
            />
          )}
          {activeTab === 'drift' && (
            <DriftMonitor
              onNavigateToRegenerative={() => setActiveTab('regenerative')}
            />
          )}
          {activeTab === 'regenerative' && (
            <RegenerativeStudio />
          )}
          {activeTab === 'workorders' && (
            <WorkOrders
              currentMachineId={currentData?.machine_id}
            />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
