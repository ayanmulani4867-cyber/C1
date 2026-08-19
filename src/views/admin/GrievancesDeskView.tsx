import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { ShieldAlert, CheckCircle2, Clock, AlertTriangle, MessageSquare } from 'lucide-react';

export const GrievancesDeskView: React.FC = () => {
  const { grievances, updateGrievanceStatus } = useErp();

  const [filterStatus, setFilterStatus] = useState<'ALL' | 'Open' | 'Under Investigation' | 'Resolved' | 'Closed'>('ALL');

  const filteredGrievances = grievances.filter((g) => {
    return filterStatus === 'ALL' || g.status === filterStatus;
  });

  const handleResolve = (id: string) => {
    const note = prompt('Enter resolution action details:', 'Investigated and resolved by Campus Administration.');
    if (note) {
      updateGrievanceStatus(id, 'Resolved', note);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Student & Campus Grievance Desk</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Confidential redressal portal for academic, hostel, infrastructure, and ragging complaints
          </p>
        </div>

        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value as any)}
          className="py-1.5 px-3 text-xs bg-white border border-slate-200 rounded-xl font-bold text-slate-700 shadow-2xs self-start sm:self-auto"
        >
          <option value="ALL">All Grievances</option>
          <option value="Open">Open</option>
          <option value="Under Investigation">Under Investigation</option>
          <option value="Resolved">Resolved</option>
        </select>
      </div>

      {/* Grievance Tickets List */}
      <div className="space-y-3">
        {filteredGrievances.map((ticket) => {
          const isResolved = ticket.status === 'Resolved';
          const isUrgent = ticket.priority === 'High' || ticket.priority === 'Urgent';

          return (
            <div
              key={ticket.id}
              className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs hover:shadow-md transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="space-y-2 max-w-3xl">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                    {ticket.ticketNumber}
                  </span>
                  <span className="text-xs font-bold text-slate-600 bg-slate-100 px-2 py-0.5 rounded">
                    {ticket.category}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      isUrgent ? 'bg-rose-100 text-rose-800' : 'bg-slate-100 text-slate-700'
                    }`}
                  >
                    Priority: {ticket.priority}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      isResolved
                        ? 'bg-emerald-100 text-emerald-800'
                        : ticket.status === 'Under Investigation'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}
                  >
                    {ticket.status}
                  </span>
                </div>

                <h4 className="font-bold text-sm text-slate-900">{ticket.subject}</h4>
                <p className="text-xs text-slate-600 leading-relaxed">{ticket.description}</p>

                <div className="text-[11px] text-slate-400 font-medium pt-1">
                  Filed By: <strong>{ticket.submittedByName}</strong> ({ticket.submittedByRole}) • Date:{' '}
                  {ticket.submittedAt}
                </div>

                {ticket.resolutionNotes && (
                  <div className="bg-emerald-50 p-2.5 rounded-xl border border-emerald-200 text-xs text-emerald-900">
                    <span className="font-bold block">Resolution Action:</span>
                    {ticket.resolutionNotes}
                  </div>
                )}
              </div>

              {/* Actions */}
              {!isResolved && (
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 flex-shrink-0">
                  <button
                    onClick={() => updateGrievanceStatus(ticket.id, 'Under Investigation')}
                    className="px-3 py-1.5 text-xs font-bold text-amber-700 bg-amber-50 hover:bg-amber-100 border border-amber-200 rounded-xl transition-colors"
                  >
                    Mark Investigating
                  </button>
                  <button
                    onClick={() => handleResolve(ticket.id)}
                    className="px-4 py-1.5 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-xs transition-colors"
                  >
                    Resolve Ticket
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
