import React from 'react';
import { useErp } from '../../context/ErpContext';
import { formatINR } from '../../utils/formatters';
import {
  Users,
  GraduationCap,
  BookOpen,
  Receipt,
  CheckCircle2,
  AlertTriangle,
  FileCheck2,
  Megaphone,
  TrendingUp,
  ArrowUpRight,
  Shield,
  Layers,
  Building2,
  Clock,
  Award,
} from 'lucide-react';

interface AdminDashboardViewProps {
  setCurrentView: (view: string) => void;
}

export const AdminDashboardView: React.FC<AdminDashboardViewProps> = ({ setCurrentView }) => {
  const {
    students,
    faculty,
    departments,
    courses,
    attendanceSessions,
    feeLedgers,
    feePayments,
    leaves,
    certificates,
    grievances,
    notices,
  } = useErp();

  // Metrics
  const totalStudents = students.length;
  const totalFaculty = faculty.length;
  const totalDepts = departments.length;
  const totalCourses = courses.length;

  const totalFeeCollected = feePayments.reduce((acc, p) => acc + p.amount, 0);
  const totalFeePending = feeLedgers.reduce((acc, l) => acc + l.pendingAmount, 0);

  const pendingLeaves = leaves.filter((l) => l.status === 'Pending').length;
  const pendingCerts = certificates.filter((c) => c.status === 'Pending').length;
  const openGrievances = grievances.filter((g) => g.status === 'Open' || g.status === 'Under Investigation').length;

  // Calculate Average Attendance %
  let totalPresences = 0;
  let totalRecords = 0;
  attendanceSessions.forEach((sess) => {
    sess.records.forEach((rec) => {
      totalRecords++;
      if (rec.status === 'Present' || rec.status === 'Late') {
        totalPresences++;
      }
    });
  });
  const avgAttendance = totalRecords > 0 ? Math.round((totalPresences / totalRecords) * 100) : 89;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 animate-in fade-in duration-150">
      {/* Welcome Banner */}
      <div className="bg-slate-900 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden border border-slate-800">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 text-xs font-semibold border border-blue-400/30 mb-2">
              <Shield className="w-3.5 h-3.5" />
              <span>Institutional Executive Dashboard</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              Apex Institute of Technology & Science
            </h1>
            <p className="text-sm text-slate-300 mt-1 max-w-2xl">
              Academic Term 2025–2026 • Real-time operational overview across {totalDepts} academic departments and {totalStudents} enrolled students.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <button
              onClick={() => setCurrentView('students')}
              className="px-4 py-2 text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white rounded-xl shadow-md transition flex items-center space-x-1.5"
            >
              <GraduationCap className="w-4 h-4" />
              <span>Student Directory</span>
            </button>
            <button
              onClick={() => setCurrentView('fees')}
              className="px-4 py-2 text-xs font-bold bg-slate-800 hover:bg-slate-700 text-white rounded-xl border border-slate-700 transition flex items-center space-x-1.5"
            >
              <Receipt className="w-4 h-4" />
              <span>Fee Ledgers (INR)</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Students */}
        <div
          onClick={() => setCurrentView('students')}
          className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
              <GraduationCap className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full flex items-center border border-emerald-200">
              Active <ArrowUpRight className="w-3 h-3 ml-0.5" />
            </span>
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-black text-slate-900">{totalStudents}</h3>
            <p className="text-xs text-slate-500 font-medium mt-0.5">Enrolled Students</p>
          </div>
        </div>

        {/* Total Faculty */}
        <div
          onClick={() => setCurrentView('faculty')}
          className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
              <Users className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded-full border border-purple-200">
              {totalDepts} Departments
            </span>
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-black text-slate-900">{totalFaculty}</h3>
            <p className="text-xs text-slate-500 font-medium mt-0.5">Appointed Faculty</p>
          </div>
        </div>

        {/* Avg Attendance Rate */}
        <div
          onClick={() => setCurrentView('attendance')}
          className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full flex items-center border border-emerald-200">
              <TrendingUp className="w-3 h-3 mr-0.5" /> Optimal
            </span>
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-black text-slate-900">{avgAttendance}%</h3>
            <p className="text-xs text-slate-500 font-medium mt-0.5">Campus Attendance Rate</p>
          </div>
        </div>

        {/* Fee Collection in INR */}
        <div
          onClick={() => setCurrentView('fees')}
          className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
              <Receipt className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded-full border border-rose-200">
              {formatINR(totalFeePending)} Dues
            </span>
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-black text-emerald-700">
              {formatINR(totalFeeCollected)}
            </h3>
            <p className="text-xs text-slate-500 font-medium mt-0.5">Total Realized Fees</p>
          </div>
        </div>
      </div>

      {/* Actionable Pending Approvals Strip */}
      <div className="bg-slate-900 text-white rounded-2xl p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 border border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-sm text-white">Pending Executive Approvals</h4>
            <p className="text-xs text-slate-400">
              {pendingLeaves} leave requests • {pendingCerts} certificate applications • {openGrievances} open grievance tickets
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {pendingLeaves > 0 && (
            <button
              onClick={() => setCurrentView('leaves')}
              className="px-3 py-1.5 text-xs font-bold bg-amber-500 hover:bg-amber-600 text-slate-950 rounded-xl transition"
            >
              Leaves ({pendingLeaves})
            </button>
          )}
          {pendingCerts > 0 && (
            <button
              onClick={() => setCurrentView('certificates')}
              className="px-3 py-1.5 text-xs font-bold bg-blue-500 hover:bg-blue-600 text-white rounded-xl transition"
            >
              Certificates ({pendingCerts})
            </button>
          )}
          {openGrievances > 0 && (
            <button
              onClick={() => setCurrentView('grievances')}
              className="px-3 py-1.5 text-xs font-bold bg-rose-500 hover:bg-rose-600 text-white rounded-xl transition"
            >
              Grievances ({openGrievances})
            </button>
          )}
        </div>
      </div>

      {/* Department Distribution & Notices Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Department Overview */}
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
              <Building2 className="w-4 h-4 text-blue-600" />
              <span>Academic Departments & Faculty Roster</span>
            </h3>
            <button
              onClick={() => setCurrentView('departments')}
              className="text-xs text-blue-600 hover:text-blue-800 font-bold"
            >
              Manage Departments
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {departments.map((dept) => {
              const deptStudents = students.filter((s) => s.departmentId === dept.id).length;
              const deptFaculty = faculty.filter((f) => f.departmentId === dept.id).length;

              return (
                <div
                  key={dept.id}
                  className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-white hover:border-blue-300 hover:shadow-sm transition space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900 text-xs">{dept.name}</span>
                    <span className="font-mono text-[10px] font-bold text-blue-700 bg-blue-100 px-1.5 py-0.5 rounded">
                      {dept.code}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-500 pt-1 border-t border-slate-200/60">
                    <span>{deptStudents} Students Enrolled</span>
                    <span>{deptFaculty} Faculty Staff</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Notices Board */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
              <Megaphone className="w-4 h-4 text-amber-600" />
              <span>Campus Circulars</span>
            </h3>
            <button
              onClick={() => setCurrentView('notices')}
              className="text-xs text-amber-600 hover:text-amber-800 font-bold"
            >
              View All
            </button>
          </div>

          <div className="space-y-3">
            {notices.slice(0, 3).map((notice) => (
              <div key={notice.id} className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                <span className="text-[10px] font-bold uppercase text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-200">
                  {notice.category}
                </span>
                <h4 className="text-xs font-bold text-slate-900 line-clamp-1">{notice.title}</h4>
                <p className="text-[11px] text-slate-500 line-clamp-2">{notice.content}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
