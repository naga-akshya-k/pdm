import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
});

export const getStatus = async () => {
  const res = await api.get('/status');
  return res.data;
};

export const getFleetOverview = async () => {
  const res = await api.get('/fleet/overview');
  return res.data;
};

export const selectFleetMachine = async (machine_id) => {
  const res = await api.post('/fleet/select', { machine_id });
  return res.data;
};

export const getCurrentData = async (unit_system = 'metric') => {
  const res = await api.get('/current', { params: { unit_system } });
  return res.data;
};

export const getEarlyWarningAnalysis = async () => {
  const res = await api.get('/early_warning');
  return res.data;
};

export const getHistoryData = async () => {
  const res = await api.get('/history');
  return res.data;
};

export const injectSimulatorFault = async (fault_type, duration_steps = 25, machine_id = null) => {
  const res = await api.post('/simulator/fault', { fault_type, duration_steps, machine_id });
  return res.data;
};

export const clearSimulatorFault = async (machine_id = null) => {
  const res = await api.post('/simulator/clear_fault', { machine_id });
  return res.data;
};

export const getCandidateModelsBenchmark = async () => {
  const res = await api.get('/models/benchmark');
  return res.data;
};

export const setActiveInferenceModel = async (model_name) => {
  const res = await api.post('/models/select', { model_name });
  return res.data;
};

export const getDriftStatus = async () => {
  const res = await api.get('/drift/status');
  return res.data;
};

export const getRegenerativeStatus = async () => {
  const res = await api.get('/regenerative/status');
  return res.data;
};

export const triggerRegenerativeRetraining = async () => {
  const res = await api.post('/regenerative/retrain');
  return res.data;
};

export const deployCandidateModel = async (candidate_name, approver_name = 'Lead Reliability Engineer', notes = '') => {
  const res = await api.post('/regenerative/deploy', { candidate_name, approver_name, notes });
  return res.data;
};

export const getWorkOrders = async () => {
  const res = await api.get('/cmms/work_orders');
  return res.data;
};

export const createManualWorkOrder = async (orderData) => {
  const res = await api.post('/cmms/create_order', orderData);
  return res.data;
};

export const getMaintenanceData = async () => {
  const res = await api.get('/maintenance');
  return res.data;
};

export const postControlAction = async (action, speed = 1.0) => {
  const res = await api.post('/control', { action, speed });
  return res.data;
};

export const getRecentLogs = async (unit_system = 'metric') => {
  const res = await api.get('/logs', { params: { unit_system } });
  return res.data;
};

export const getModelMetrics = async () => {
  const res = await api.get('/model');
  return res.data;
};

export const getLiveTags = async () => {
  const res = await api.get('/tags/live');
  return res.data;
};

export const getMqttStatus = async () => {
  const res = await api.get('/mqtt/status');
  return res.data;
};
