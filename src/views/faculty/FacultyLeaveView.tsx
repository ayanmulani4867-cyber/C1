import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { FileCheck2, Plus, Calendar, Clock, CheckCircle2, XCircle } from 'lucide-react';
import { LeaveApplication } from '../../types';

export const FacultyLeaveView: React.FC = () => {
  const { leaves, currentUser, applyForLeave } = useErp();

  const [showApplyModal, setShowApplyModal] = useState(false);

  const [form, setForm] = useState({
    leaveType: 'Casual' as LeaveApplication['leaveType'],
    startDate: '2026-04-14',
    endDate: '2026-04-15',
    totalDays: 2,
    reason: '',
  });

  const myLeaves = leaves.filter((l) => l.applicantId === currentUser.id || l.applicantName === currentUser.fullName || l.applicantName === currentUser.name);

  const handleApply = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.reason) return;

    applyForLeave({
      applicantId: currentUser.id,
      applicantName: currentUser.fullName || currentUser.name || 'Faculty Member',
      applicantType: 'FACULTY',
      rollOrEmpNo: 'EMP-1301',
      departmentName: currentUser.department || 'Computer Science & Engineering',
      leaveType: form.leaveType,
      startDate: form.startDate,
      endDate: form.endDate,
      totalDays: Number(form.totalDays),
      reason: form.reason,
      appliedDate: new Date().toISOString().split('T')[0],
      status: 'Pending',
    });

    setShowApplyModal(false);
    setForm({ leaveType: 'Casual', startDate: '2026-04-14', endDate: '2026-04-15', totalDays: 2, reason: '' });
    alert('Leave application submitted to Head of Department & Dean for approval.');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Faculty Leave Portal</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Apply for Casual, Duty, Medical, or Academic leaves with substitute arrangement
          </p>
        </div>

        <button
          onClick={() => setShowApplyModal(true)}
          className="px-4 py-2 text-xs font-bold text-white bg-purple-600 hover:bg-purple-700 rounded-xl shadow-xs transition-colors flex items-center space-x-1.5 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Apply for Leave</span>
        </button>
      </div>

      {/* History */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {myLeaves.length === 0 ? (
          <div className="col-span-2 bg-white rounded-2xl border border-slate-200 p-8 text-center text-slate-400 text-xs">
            No past leave applications found.
          </div>
        ) : (
          myLeaves.map((leave) => (
            <div key={leave.id} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-extrabold text-xs text-purple-800 bg-purple-100 px-2 py-0.5 rounded-full">
                  {leave.leaveType} Leave
                </span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                    leave.status === 'Approved'
                      ? 'bg-emerald-100 text-emerald-800'
                      : leave.status === 'Rejected'
                      ? 'bg-rose-100 text-rose-800'
                      : 'bg-amber-100 text-amber-800'
                  }`}
                >
                  {leave.status}
                </span>
              </div>

              <div className="text-xs text-slate-700 space-y-1">
                <div>
                  Duration: <strong>{leave.startDate}</strong> to <strong>{leave.endDate}</strong> ({leave.totalDays} Days)
                </div>
                <div>
                  Reason: <em>"{leave.reason}"</em>
                </div>
                {leave.reviewerRemarks && (
                  <div className="text-[11px] text-slate-500 pt-1">
                    Dean Note: <strong>{leave.reviewerRemarks}</strong>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Apply Modal */}
      {showApplyModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-md w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <h3 className="font-extrabold text-base text-slate-900">Faculty Leave Application</h3>
            <form onSubmit={handleApply} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Leave Nature</label>
                <select
                  value={form.leaveType}
                  onChange={(e) => setForm({ ...form, leaveType: e.target.value as any })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                >
                  <option value="Casual">Casual Leave (CL)</option>
                  <option value="Medical">Medical / Health Leave (ML)</option>
                  <option value="Duty">On-Duty / Conference (OD)</option>
                  <option value="Special">Special Research Leave</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Start Date</label>
                  <input
                    type="date"
                    value={form.startDate}
                    onChange={(e) => setForm({ ...form, startDate: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">End Date</label>
                  <input
                    type="date"
                    value={form.endDate}
                    onChange={(e) => setForm({ ...form, endDate: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Reason & Substitute Coverage</label>
                <textarea
                  rows={3}
                  required
                  value={form.reason}
                  onChange={(e) => setForm({ ...form, reason: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="Specify reason and faculty covering lectures..."
                />
              </div>
              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowApplyModal(false)}
                  className="px-4 py-2 font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-bold text-white bg-purple-600 hover:bg-purple-700 rounded-xl shadow-xs"
                >
                  Submit Application
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
