import React, { useState, useEffect } from 'react';
import { getWorkOrders, createManualWorkOrder, getMaintenanceData } from '../services/api';
import { Wrench, AlertTriangle, CheckCircle2, DollarSign, Clock, ShieldCheck, Plus, FileText, Activity } from 'lucide-react';

export default function WorkOrders({ currentMachineId }) {
  const [orders, setOrders] = useState([]);
  const [maintData, setMaintData] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    machine_id: currentMachineId || 'MCH-802X',
    priority: 'High',
    action: 'Urgent bearing lubrication and seal replacement',
    assigned_role: 'Senior Reliability Engineer',
    parts: 'Precision Roller Bearings, Synthetic Lubricant'
  });
  const [msg, setMsg] = useState(null);

  const fetchData = async () => {
    try {
      const [woRes, maintRes] = await Promise.all([getWorkOrders(), getMaintenanceData()]);
      setOrders(woRes.work_orders || []);
      setMaintData(maintRes);
    } catch (err) {
      console.error('Failed to fetch work orders or maintenance data:', err);
    }
  };

  useEffect(() => {
    fetchData();
  }, [currentMachineId]);

  const handleCreateOrder = async (e) => {
    e.preventDefault();
    try {
      const partsArray = formData.parts.split(',').map(p => p.trim());
      await createManualWorkOrder({
        machine_id: formData.machine_id,
        priority: formData.priority,
        action: formData.action,
        assigned_role: formData.assigned_role,
        parts: partsArray
      });
      setMsg({ type: 'success', text: 'CMMS Work Order successfully created & dispatched' });
      setShowModal(false);
      await fetchData();
      setTimeout(() => setMsg(null), 4000);
    } catch (err) {
      setMsg({ type: 'error', text: 'Failed to create work order' });
    }
  };

  const fin = maintData?.financial_analysis || {
    estimated_unplanned_downtime_loss_usd: 15000,
    estimated_preventive_servicing_cost_usd: 2100,
    net_roi_savings_usd: 12900
  };

  const subcomps = maintData?.subcomponents || {
    bearing_assembly: 85.0,
    stator_windings: 92.0,
    rotor_balance: 88.0,
    cooling_system: 78.0,
    hydraulic_seals: 90.0
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
            <Wrench className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">CMMS Maintenance & Work Order Dispatcher</h1>
            <p className="text-sm text-gray-500">
              ISO 13374 Condition-Based Servicing: Automated work orders, component health, and financial downtime ROI
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-xs transition-colors"
        >
          <Plus className="w-4 h-4" /> Dispatch Work Order
        </button>
      </div>

      {msg && (
        <div className={`p-4 rounded-lg text-sm font-medium border ${msg.type === 'success' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-red-50 text-red-800 border-red-200'}`}>
          {msg.text}
        </div>
      )}

      {/* Financial ROI & Subcomponents Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Financial Card */}
        <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-3">
            <DollarSign className="w-5 h-5 text-emerald-600" />
            <h3 className="font-bold text-gray-900 text-sm">Downtime Financial Risk & ROI</h3>
          </div>
          <div className="space-y-2.5 text-xs">
            <div className="flex justify-between items-center p-2 rounded-lg bg-red-50 text-red-800 border border-red-100">
              <span>Unplanned Downtime Risk:</span>
              <span className="font-mono font-bold">${fin.estimated_unplanned_downtime_loss_usd?.toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded-lg bg-gray-50 text-gray-700 border border-gray-100">
              <span>Planned Preventive Cost:</span>
              <span className="font-mono font-bold">${fin.estimated_preventive_servicing_cost_usd?.toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-100 font-semibold">
              <span>Net Cost Avoidance Savings:</span>
              <span className="font-mono font-bold text-sm text-emerald-700">${fin.net_roi_savings_usd?.toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Subcomponents Breakdown */}
        <div className="md:col-span-2 bg-white rounded-xl shadow-xs border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="w-5 h-5 text-blue-600" />
            <h3 className="font-bold text-gray-900 text-sm">Subsystem Physical Health Breakdown</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {Object.entries(subcomps).map(([comp, score]) => {
              const color = score >= 80 ? 'bg-emerald-500' : (score >= 60 ? 'bg-amber-500' : 'bg-red-500');
              return (
                <div key={comp} className="p-3 bg-gray-50 rounded-xl border border-gray-100 flex flex-col justify-between">
                  <span className="text-[11px] font-semibold text-gray-700 line-clamp-1 capitalize">
                    {comp.replace('_', ' ')}
                  </span>
                  <div className="mt-2">
                    <div className="flex justify-between text-[11px] font-mono mb-1">
                      <span className="font-bold text-gray-900">{score}%</span>
                    </div>
                    <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full ${color}`} style={{ width: `${score}%` }}></div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Active Work Orders Table */}
      <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-gray-900">CMMS Active Maintenance Work Orders</h3>
            <p className="text-xs text-gray-500">Dispatch log and condition-based repair assignments</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-600 font-semibold border-y border-gray-200">
              <tr>
                <th className="py-2.5 px-3">Work Order ID</th>
                <th className="py-2.5 px-3">Asset</th>
                <th className="py-2.5 px-3">Priority</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">Recommended Action</th>
                <th className="py-2.5 px-3">Required Parts</th>
                <th className="py-2.5 px-3">Assigned Role</th>
                <th className="py-2.5 px-3">Est. Duration</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {orders.map((wo) => {
                const priorityColor =
                  wo.priority === 'Critical'
                    ? 'bg-red-100 text-red-800'
                    : (wo.priority === 'Urgent' ? 'bg-orange-100 text-orange-800' : (wo.priority === 'High' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'));

                return (
                  <tr key={wo.order_id} className="hover:bg-gray-50">
                    <td className="py-2.5 px-3 font-mono font-bold text-gray-900">{wo.order_id}</td>
                    <td className="py-2.5 px-3 font-semibold text-gray-800">{wo.machine_name}</td>
                    <td className="py-2.5 px-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold ${priorityColor}`}>
                        {wo.priority}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-gray-600">{wo.maintenance_type}</td>
                    <td className="py-2.5 px-3 text-gray-900 max-w-xs truncate">{wo.recommended_action}</td>
                    <td className="py-2.5 px-3 text-gray-600">{Array.isArray(wo.required_parts) ? wo.required_parts.join(', ') : wo.required_parts}</td>
                    <td className="py-2.5 px-3 font-medium text-gray-700">{wo.assigned_role}</td>
                    <td className="py-2.5 px-3 font-mono text-gray-600">{wo.estimated_duration_hours}h</td>
                    <td className="py-2.5 px-3">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                        {wo.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Dispatch Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-gray-200">
            <h3 className="text-lg font-bold text-gray-900 mb-1">Dispatch CMMS Maintenance Work Order</h3>
            <p className="text-xs text-gray-500 mb-4">Create and assign a condition-based maintenance task to plant technicians.</p>

            <form onSubmit={handleCreateOrder} className="space-y-4 text-xs">
              <div>
                <label className="font-semibold text-gray-700 block mb-1">Target Asset ID</label>
                <select
                  value={formData.machine_id}
                  onChange={(e) => setFormData({ ...formData, machine_id: e.target.value })}
                  className="w-full p-2.5 border rounded-lg border-gray-200"
                >
                  <option value="MCH-802X">MCH-802X: Turbine Motor Unit A1</option>
                  <option value="PMP-401B">PMP-401B: Centrifugal Slurry Pump B2</option>
                  <option value="CMP-605C">CMP-605C: Reciprocating Gas Compressor C3</option>
                  <option value="CNC-900D">CNC-900D: High-Speed CNC Spindle D4</option>
                </select>
              </div>

              <div>
                <label className="font-semibold text-gray-700 block mb-1">Priority Level</label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  className="w-full p-2.5 border rounded-lg border-gray-200"
                >
                  <option value="Critical">Critical (0–4 Hours Emergency Response)</option>
                  <option value="Urgent">Urgent (24–48 Hours Servicing)</option>
                  <option value="High">High (7–14 Days Preventive)</option>
                  <option value="Moderate">Moderate (30 Days Inspection)</option>
                  <option value="Low">Low (Routine)</option>
                </select>
              </div>

              <div>
                <label className="font-semibold text-gray-700 block mb-1">Recommended Action / Task Description</label>
                <textarea
                  rows={2}
                  value={formData.action}
                  onChange={(e) => setFormData({ ...formData, action: e.target.value })}
                  className="w-full p-2.5 border rounded-lg border-gray-200"
                />
              </div>

              <div>
                <label className="font-semibold text-gray-700 block mb-1">Assigned Role</label>
                <input
                  type="text"
                  value={formData.assigned_role}
                  onChange={(e) => setFormData({ ...formData, assigned_role: e.target.value })}
                  className="w-full p-2.5 border rounded-lg border-gray-200"
                />
              </div>

              <div>
                <label className="font-semibold text-gray-700 block mb-1">Required Spare Parts (comma-separated)</label>
                <input
                  type="text"
                  value={formData.parts}
                  onChange={(e) => setFormData({ ...formData, parts: e.target.value })}
                  className="w-full p-2.5 border rounded-lg border-gray-200"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="py-2 px-4 rounded-lg bg-gray-100 text-gray-700 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="py-2 px-5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold shadow-xs"
                >
                  Dispatch Work Order
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
