import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { FileCheck2, CheckCircle2, XCircle, Clock, Calendar, User } from 'lucide-react';

export const LeavesDeskView: React.FC = () => {
  const { leaves, updateLeaveStatus } = useErp();

  const [filterType, setFilterType] = useState<'ALL' | 'STUDENT' | 'FACULTY'>('ALL');
  const [filterStatus, setFilterStatus] = useState<'ALL' | 'Pending' | 'Approved' | 'Rejected'>('ALL');

  const filteredLeaves = leaves.filter((leave) => {
    const matchesType = filterType === 'ALL' || leave.applicantType === filterType || leave.applicantRole === filterType;
    const matchesStatus = filterStatus === 'ALL' || leave.status === filterStatus;
    return matchesType && matchesStatus;
  });

  const handleAction = (id: string, status: 'Approved' | 'Rejected') => {
    const remarks = prompt(`Enter review remarks for ${status.toLowerCase()}:`, `${status} by Academic Dean`);
    if (remarks !== null) {
      updateLeaveStatus(id, status, 'Dr. Arthur Sterling', remarks);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Leave Applications Desk</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Executive approval workflow for student absences and faculty duty/medical leaves
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as any)}
            className="py-1.5 px-3 text-xs bg-white border border-slate-200 rounded-xl font-bold text-slate-700 shadow-2xs"
          >
            <option value="ALL">All Applicants</option>
            <option value="STUDENT">Students Only</option>
            <option value="FACULTY">Faculty Only</option>
          </select>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as any)}
            className="py-1.5 px-3 text-xs bg-white border border-slate-200 rounded-xl font-bold text-slate-700 shadow-2xs"
          >
            <option value="ALL">All Statuses</option>
            <option value="Pending">Pending Review</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
          </select>
        </div>
      </div>

      {/* Applications Cards List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredLeaves.map((leave) => {
          const isPending = leave.status === 'Pending';
          return (
            <div
              key={leave.id}
              className={`bg-white rounded-2xl border p-5 shadow-2xs flex flex-col justify-between transition-all ${
                isPending ? 'border-amber-300 ring-2 ring-amber-500/10' : 'border-slate-200'
              }`}
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase ${
                        leave.applicantType === 'STUDENT'
                          ? 'bg-blue-100 text-blue-800 border border-blue-200'
                          : 'bg-purple-100 text-purple-800 border border-purple-200'
                      }`}
                    >
                      {leave.applicantType}
                    </span>
                    <span className="font-bold text-xs text-slate-500">{leave.leaveType} Leave</span>
                  </div>

                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold ${
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

                <div className="mt-3">
                  <h4 className="font-extrabold text-sm text-slate-900">{leave.applicantName}</h4>
                  <p className="text-xs text-slate-500 font-medium">
                    {leave.rollOrEmpNo} • {leave.departmentName}
                  </p>
                </div>

                <div className="mt-3 p-3 bg-slate-50 rounded-xl space-y-1.5 text-xs text-slate-700">
                  <div className="flex items-center space-x-2 text-slate-600">
                    <Calendar className="w-3.5 h-3.5 text-blue-600" />
                    <span>
                      Duration: <strong>{leave.startDate}</strong> to <strong>{leave.endDate}</strong> ({leave.totalDays} Day{leave.totalDays > 1 ? 's' : ''})
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium">Reason:</span>{' '}
                    <span className="text-slate-800 font-medium">{leave.reason}</span>
                  </div>
                  {leave.reviewerRemarks && (
                    <div className="pt-1 border-t border-slate-200 text-[11px] text-slate-500">
                      Dean Remarks: <em>"{leave.reviewerRemarks}"</em>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              {isPending && (
                <div className="flex items-center justify-end space-x-2 pt-4 mt-3 border-t border-slate-100">
                  <button
                    onClick={() => handleAction(leave.id, 'Rejected')}
                    className="px-3 py-1.5 text-xs font-bold text-rose-600 hover:bg-rose-50 border border-rose-200 rounded-xl transition-colors"
                  >
                    Reject
                  </button>
                  <button
                    onClick={() => handleAction(leave.id, 'Approved')}
                    className="px-4 py-1.5 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-xs transition-colors"
                  >
                    Approve Leave
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
