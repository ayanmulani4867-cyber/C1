import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileSpreadsheet,
  Calendar,
  Search,
  Filter,
  ArrowUpRight,
  TrendingDown,
} from 'lucide-react';

export const AttendanceCenterView: React.FC = () => {
  const { students, subjects, attendanceSessions, divisions, faculty } = useErp();

  const [searchQuery, setSearchQuery] = useState('');
  const [filterThreshold, setFilterThreshold] = useState<'ALL' | 'BELOW_75' | 'ABOVE_75'>('ALL');
  const [activeTab, setActiveTab] = useState<'STUDENT_ANALYTICS' | 'SESSION_LOGS'>('STUDENT_ANALYTICS');

  // Compute student-level attendance %
  const studentAttendanceStats = students.map((student) => {
    let totalClasses = 0;
    let attendedClasses = 0;

    attendanceSessions.forEach((sess) => {
      const rec = sess.records.find((r) => r.studentId === student.id);
      if (rec) {
        totalClasses++;
        if (rec.status === 'Present' || rec.status === 'Late') {
          attendedClasses++;
        }
      }
    });

    const percentage = totalClasses > 0 ? Math.round((attendedClasses / totalClasses) * 100) : 100;
    return {
      student,
      totalClasses,
      attendedClasses,
      percentage,
      isAtRisk: percentage < 75,
    };
  });

  const filteredStats = studentAttendanceStats.filter((stat) => {
    const matchesSearch =
      stat.student.fullName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      stat.student.rollNo.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesThreshold =
      filterThreshold === 'ALL' ||
      (filterThreshold === 'BELOW_75' && stat.isAtRisk) ||
      (filterThreshold === 'ABOVE_75' && !stat.isAtRisk);

    return matchesSearch && matchesThreshold;
  });

  const atRiskCount = studentAttendanceStats.filter((s) => s.isAtRisk).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Attendance Monitoring Center</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Subject-wise logs, 75% threshold compliance, and automated parent warning triggers
          </p>
        </div>

        {atRiskCount > 0 && (
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs font-bold shadow-2xs">
            <AlertTriangle className="w-4 h-4 text-rose-600" />
            <span>{atRiskCount} Students Below 75% Mandatory Attendance</span>
          </div>
        )}
      </div>

      {/* View Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab('STUDENT_ANALYTICS')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'STUDENT_ANALYTICS' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Student Attendance Roster ({students.length})
        </button>
        <button
          onClick={() => setActiveTab('SESSION_LOGS')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'SESSION_LOGS' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Lecture Session Logs ({attendanceSessions.length})
        </button>
      </div>

      {activeTab === 'STUDENT_ANALYTICS' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs flex flex-col sm:flex-row gap-3 items-center justify-between">
            <div className="relative w-full sm:w-80">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search Student by Name or Roll No..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none"
              />
            </div>

            <div className="flex items-center space-x-2 w-full sm:w-auto">
              <span className="text-xs text-slate-400 font-semibold">Filter:</span>
              <select
                value={filterThreshold}
                onChange={(e) => setFilterThreshold(e.target.value as any)}
                className="py-1.5 px-3 text-xs bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-700"
              >
                <option value="ALL">All Students</option>
                <option value="BELOW_75">At-Risk (&lt; 75% Attendance)</option>
                <option value="ABOVE_75">Eligible (&ge; 75% Attendance)</option>
              </select>
            </div>
          </div>

          {/* Student Stats Table */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="py-3 px-4">Student</th>
                    <th className="py-3 px-4">Roll Number</th>
                    <th className="py-3 px-4">Classes Attended / Total</th>
                    <th className="py-3 px-4">Attendance %</th>
                    <th className="py-3 px-4">Exam Eligibility</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredStats.map((stat) => (
                    <tr key={stat.student.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-4 font-bold text-slate-900 flex items-center space-x-2.5">
                        <img src={stat.student.photo} alt="" className="w-7 h-7 rounded-lg object-cover" />
                        <span>{stat.student.fullName}</span>
                      </td>
                      <td className="py-3 px-4 font-bold text-blue-700">{stat.student.rollNo}</td>
                      <td className="py-3 px-4 font-semibold text-slate-800">
                        {stat.attendedClasses} / {stat.totalClasses} Sessions
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <div className="w-24 bg-slate-200 rounded-full h-2 overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                stat.percentage >= 75 ? 'bg-emerald-500' : 'bg-rose-500'
                              }`}
                              style={{ width: `${stat.percentage}%` }}
                            />
                          </div>
                          <span className={`font-bold ${stat.percentage >= 75 ? 'text-emerald-700' : 'text-rose-700'}`}>
                            {stat.percentage}%
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        {stat.percentage >= 75 ? (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                            Eligible
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
                            Defaulter Warning
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-right">
                        {stat.isAtRisk && (
                          <button
                            onClick={() => alert(`Warning SMS & Email dispatched to Parent (${stat.student.parentPhone}) for ${stat.student.fullName}`)}
                            className="px-2.5 py-1 text-[11px] font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 rounded-lg border border-rose-200 transition-colors"
                          >
                            Send Alert
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'SESSION_LOGS' && (
        <div className="space-y-3">
          {attendanceSessions.map((sess) => {
            const sub = subjects.find((s) => s.id === sess.subjectId);
            const fac = faculty.find((f) => f.id === sess.facultyId);
            const div = divisions.find((d) => d.id === sess.divisionId);
            const presentCount = sess.records.filter((r) => r.status === 'Present' || r.status === 'Late').length;

            return (
              <div
                key={sess.id}
                className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs hover:shadow-md transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-xs text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                      {sub?.code}
                    </span>
                    <h4 className="font-bold text-sm text-slate-900">{sub?.name}</h4>
                    <span className="text-xs text-slate-400 font-medium">({div?.name})</span>
                  </div>
                  <p className="text-xs text-slate-600 mt-1 font-medium">
                    Topic Covered: <span className="text-slate-900 font-bold">{sess.topicCovered}</span>
                  </p>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Date: {sess.date} • Period {sess.period} • Instructor: {fac?.fullName}
                  </p>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <span className="text-xs font-extrabold text-slate-900">
                      {presentCount} / {sess.records.length} Present
                    </span>
                    <span className="block text-[10px] text-slate-500">
                      ({Math.round((presentCount / sess.records.length) * 100)}% Turnout)
                    </span>
                  </div>
                  <span className="px-2.5 py-1 text-xs font-bold rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200">
                    Logged
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
