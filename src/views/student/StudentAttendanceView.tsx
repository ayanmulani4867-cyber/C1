import React from 'react';
import { useErp } from '../../context/ErpContext';
import { CheckCircle2, AlertTriangle, Clock, Calendar, BookOpen, ShieldCheck } from 'lucide-react';

export const StudentAttendanceView: React.FC = () => {
  const { students, subjects, attendanceSessions, currentUser } = useErp();

  const myStudent = students.find((s) => s.id === currentUser.id) || students[0];

  // Calculate per-subject attendance
  const subjectStats = subjects.map((sub) => {
    let totalSubjectSessions = 0;
    let attendedSubjectSessions = 0;

    attendanceSessions.forEach((sess) => {
      if (sess.subjectId === sub.id) {
        const rec = sess.records.find((r) => r.studentId === myStudent?.id);
        if (rec) {
          totalSubjectSessions++;
          if (rec.status === 'Present' || rec.status === 'Late') {
            attendedSubjectSessions++;
          }
        }
      }
    });

    const percentage =
      totalSubjectSessions > 0 ? Math.round((attendedSubjectSessions / totalSubjectSessions) * 100) : 90;

    // Calculate required classes or safe to miss
    // Requirement is 75%
    // attended / total >= 0.75
    let message = '';
    if (percentage < 75) {
      // (attended + x) / (total + x) >= 0.75 -> attended + x >= 0.75*total + 0.75*x -> 0.25*x >= 0.75*total - attended
      const needed = Math.ceil((0.75 * totalSubjectSessions - attendedSubjectSessions) / 0.25);
      message = `Must attend next ${Math.max(1, needed)} classes continuously to reach 75% threshold.`;
    } else {
      // attended / (total + y) >= 0.75 -> attended >= 0.75*total + 0.75*y -> 0.75*y <= attended - 0.75*total
      const canMiss = Math.floor((attendedSubjectSessions - 0.75 * totalSubjectSessions) / 0.75);
      message =
        canMiss > 0
          ? `You have a safe attendance buffer to miss ${canMiss} upcoming lecture${canMiss > 1 ? 's' : ''}.`
          : 'Attendance is right at the 75% threshold. Do not miss upcoming classes.';
    }

    return {
      subject: sub,
      totalSubjectSessions,
      attendedSubjectSessions,
      percentage,
      message,
      isAtRisk: percentage < 75,
    };
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Attendance Analytics & Threshold Status</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Subject-wise attendance, lecture logs, and 75% examination eligibility compliance
          </p>
        </div>

        <div className="inline-flex items-center space-x-2 px-3 py-1.5 bg-blue-50 border border-blue-200 rounded-xl text-blue-800 text-xs font-bold shadow-2xs">
          <ShieldCheck className="w-4 h-4 text-blue-600" />
          <span>75% Mandatory Attendance Rule Enforced</span>
        </div>
      </div>

      {/* Subject Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {subjectStats.map((stat) => (
          <div
            key={stat.subject.id}
            className={`bg-white rounded-2xl border p-5 shadow-2xs space-y-4 ${
              stat.isAtRisk ? 'border-rose-300 ring-2 ring-rose-500/10' : 'border-slate-200'
            }`}
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="font-mono text-xs font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                  {stat.subject.code}
                </span>
                <h4 className="font-bold text-sm text-slate-900 mt-1.5">{stat.subject.name}</h4>
                <p className="text-xs text-slate-500">
                  Semester {stat.subject.semesterNumber} • {stat.subject.type}
                </p>
              </div>

              <div className="text-right">
                <span
                  className={`text-2xl font-extrabold block ${
                    stat.percentage >= 75 ? 'text-emerald-700' : 'text-rose-600'
                  }`}
                >
                  {stat.percentage}%
                </span>
                <span className="text-[10px] text-slate-400 font-semibold">
                  {stat.attendedSubjectSessions} / {stat.totalSubjectSessions} Attended
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="space-y-1.5">
              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    stat.percentage >= 75 ? 'bg-emerald-500' : 'bg-rose-500'
                  }`}
                  style={{ width: `${stat.percentage}%` }}
                />
              </div>
            </div>

            {/* Advice Box */}
            <div
              className={`p-3 rounded-xl text-xs font-medium ${
                stat.isAtRisk
                  ? 'bg-rose-50 text-rose-800 border border-rose-200'
                  : 'bg-emerald-50 text-emerald-800 border border-emerald-200'
              }`}
            >
              {stat.message}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
