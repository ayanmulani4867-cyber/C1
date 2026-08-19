import React from 'react';
import { useErp } from '../../context/ErpContext';
import { formatINR } from '../../utils/formatters';
import {
  CheckCircle2,
  AlertTriangle,
  Award,
  BookOpen,
  CalendarDays,
  Receipt,
  FileText,
  Clock,
  Sparkles,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';

interface StudentDashboardViewProps {
  setCurrentView: (view: string) => void;
  onOpenIdCard: () => void;
}

export const StudentDashboardView: React.FC<StudentDashboardViewProps> = ({ setCurrentView, onOpenIdCard }) => {
  const { currentUser, students, subjects, attendanceSessions, assignments, feeLedgers, notices, timetable, divisions } =
    useErp();

  const myStudent = students.find((s) => s.id === currentUser.id) || students[0];
  const myDivision = divisions.find((d) => d.id === myStudent?.divisionId);

  // Compute total attendance %
  let totalSessions = 0;
  let attendedSessions = 0;

  attendanceSessions.forEach((sess) => {
    const rec = sess.records.find((r) => r.studentId === myStudent?.id);
    if (rec) {
      totalSessions++;
      if (rec.status === 'Present' || rec.status === 'Late') {
        attendedSessions++;
      }
    }
  });

  const attendancePct = totalSessions > 0 ? Math.round((attendedSessions / totalSessions) * 100) : 92;
  const isAttendanceAtRisk = attendancePct < 75;

  // Fee ledger
  const myFeeLedger = feeLedgers.find((l) => l.studentId === myStudent?.id);

  // Pending assignments
  const pendingAssignments = assignments.filter((a) => a.divisionId === myStudent?.divisionId);

  // Today's classes
  const myTodayClasses = timetable.filter(
    (t) => t.divisionId === myStudent?.divisionId && t.dayOfWeek === 'Monday'
  );

  return (
    <div className="space-y-6">
      {/* Student Welcome Banner */}
      <div className="bg-gradient-to-r from-blue-950 via-slate-900 to-indigo-950 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <img
              src={myStudent?.photo || currentUser.photo}
              alt=""
              className="w-16 h-16 rounded-2xl object-cover ring-2 ring-blue-400 shadow-md"
            />
            <div>
              <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 text-[10px] font-bold uppercase tracking-wider mb-1">
                <Sparkles className="w-3 h-3" />
                <span>Student Academic Portal</span>
              </div>
              <h1 className="text-xl sm:text-2xl font-extrabold">{myStudent?.fullName}</h1>
              <p className="text-xs text-slate-300 mt-0.5">
                Roll No: <strong className="text-white">{myStudent?.rollNo}</strong> • Semester{' '}
                {myStudent?.semesterNumber} (Batch {myStudent?.batch})
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={onOpenIdCard}
              className="px-4 py-2 text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white rounded-xl shadow-md transition-all flex items-center space-x-1.5"
            >
              <Sparkles className="w-4 h-4" />
              <span>Digital ID Card</span>
            </button>
            <button
              onClick={() => setCurrentView('student-fees')}
              className="px-4 py-2 text-xs font-bold bg-white/10 hover:bg-white/20 text-white rounded-xl border border-white/20 transition-all flex items-center space-x-1.5"
            >
              <Receipt className="w-4 h-4" />
              <span>Pay Fees</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Attendance Percentage */}
        <div
          onClick={() => setCurrentView('student-attendance')}
          className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold ${
              isAttendanceAtRisk ? 'bg-rose-50 text-rose-600' : 'bg-emerald-50 text-emerald-600'
            }`}>
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
              isAttendanceAtRisk ? 'bg-rose-50 text-rose-700' : 'bg-emerald-50 text-emerald-700'
            }`}>
              {isAttendanceAtRisk ? 'At Risk (<75%)' : 'Eligible'}
            </span>
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-extrabold text-slate-900">{attendancePct}%</h3>
            <p className="text-xs text-slate-500 font-medium mt-0.5">Overall Class Attendance</p>
          </div>
        </div>

        {/* CGPA */}
        <div
          onClick={() => setCurrentView('student-results')}
          className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
              <Award className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded-full flex items-center">
              <TrendingUp className="w-3 h-3 mr-0.5" /> Grade A+
            </span>
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-extrabold text-slate-900">{myStudent?.cgpa.toFixed(2)}</h3>
            <p className="text-xs text-slate-500 font-medium mt-0.5">Cumulative Grade (CGPA)</p>
          </div>
        </div>

        {/* Pending Assignments */}
        <div
          onClick={() => setCurrentView('student-assignments')}
          className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
              <FileText className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full">
              Active Tasks
            </span>
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-extrabold text-slate-900">{pendingAssignments.length}</h3>
            <p className="text-xs text-slate-500 font-medium mt-0.5">Homework & Lab Deadlines</p>
          </div>
        </div>

        {/* Fee Status */}
        <div
          onClick={() => setCurrentView('student-fees')}
          className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
              <Receipt className="w-5 h-5" />
            </div>
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
              (myFeeLedger?.pendingAmount || 0) > 0 ? 'bg-amber-50 text-amber-700' : 'bg-emerald-50 text-emerald-700'
            }`}>
              {(myFeeLedger?.pendingAmount || 0) > 0 ? 'Due Pending' : 'Paid'}
            </span>
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-extrabold text-slate-900">
              {formatINR(myFeeLedger?.pendingAmount || 0)}
            </h3>
            <p className="text-xs text-slate-500 font-medium mt-0.5">Tuition Dues for Sem {myStudent?.semesterNumber}</p>
          </div>
        </div>
      </div>

      {/* Main Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Today's Schedule & Academic Feed */}
        <div className="lg:col-span-2 space-y-6">
          {/* Today's Lectures */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-bold text-base text-slate-900">Today's Class Timetable</h3>
                <p className="text-xs text-slate-500">Live lecture schedule for {myDivision?.name}</p>
              </div>
              <button
                onClick={() => setCurrentView('student-timetable')}
                className="text-xs font-bold text-blue-600 hover:text-blue-700 flex items-center space-x-1"
              >
                <span>Full Timetable</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="space-y-2.5">
              {myTodayClasses.map((slot) => {
                const sub = subjects.find((s) => s.id === slot.subjectId);

                return (
                  <div
                    key={slot.id}
                    className="p-3.5 rounded-xl border border-slate-100 bg-slate-50/80 flex items-center justify-between hover:bg-blue-50/60 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-9 h-9 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs">
                        P{slot.period}
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-xs font-bold text-blue-700">{sub?.code}</span>
                          <h4 className="font-bold text-xs text-slate-900">{sub?.name}</h4>
                        </div>
                        <p className="text-[11px] text-slate-500 mt-0.5">
                          Room: <strong>{slot.roomNumber}</strong> • {slot.startTime} - {slot.endTime}
                        </p>
                      </div>
                    </div>

                    <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold bg-white border border-slate-200 text-slate-700">
                      {sub?.type}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Quick Services Bar */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs">
            <h3 className="font-bold text-base text-slate-900 mb-3">Student Self-Service Desk</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                onClick={() => setCurrentView('student-services')}
                className="p-3.5 text-left rounded-xl bg-slate-50 hover:bg-blue-50 border border-slate-200/60 hover:border-blue-200 transition-all"
              >
                <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold mb-2">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
                <h5 className="font-bold text-xs text-slate-900">Apply for Leave</h5>
                <p className="text-[10px] text-slate-500">Submit absence application</p>
              </button>

              <button
                onClick={() => setCurrentView('student-services')}
                className="p-3.5 text-left rounded-xl bg-slate-50 hover:bg-blue-50 border border-slate-200/60 hover:border-blue-200 transition-all"
              >
                <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-bold mb-2">
                  <Award className="w-4 h-4" />
                </div>
                <h5 className="font-bold text-xs text-slate-900">Get Certificate</h5>
                <p className="text-[10px] text-slate-500">Bonafide / NOC issuance</p>
              </button>

              <button
                onClick={() => setCurrentView('student-services')}
                className="p-3.5 text-left rounded-xl bg-slate-50 hover:bg-blue-50 border border-slate-200/60 hover:border-blue-200 transition-all"
              >
                <div className="w-8 h-8 rounded-lg bg-rose-100 text-rose-700 flex items-center justify-center font-bold mb-2">
                  <AlertTriangle className="w-4 h-4" />
                </div>
                <h5 className="font-bold text-xs text-slate-900">File Grievance</h5>
                <p className="text-[10px] text-slate-500">Report campus complaint</p>
              </button>
            </div>
          </div>
        </div>

        {/* Right 1 Col: Notices Feed */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs">
            <h3 className="font-bold text-base text-slate-900 mb-3">Campus Announcements</h3>
            <div className="space-y-3">
              {notices.slice(0, 3).map((n) => (
                <div key={n.id} className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                  <span className="text-[9px] font-bold text-blue-700 bg-blue-100 px-2 py-0.5 rounded-full">
                    {n.category}
                  </span>
                  <h5 className="font-bold text-xs text-slate-900 line-clamp-1">{n.title}</h5>
                  <p className="text-[11px] text-slate-600 line-clamp-2">{n.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
