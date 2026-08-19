import React from 'react';
import { useErp } from '../../context/ErpContext';
import {
  CalendarDays,
  CheckCircle2,
  BookOpen,
  Users,
  FileText,
  Clock,
  ArrowRight,
  Sparkles,
  Layers,
} from 'lucide-react';

interface FacultyDashboardViewProps {
  setCurrentView: (view: string) => void;
}

export const FacultyDashboardView: React.FC<FacultyDashboardViewProps> = ({ setCurrentView }) => {
  const { currentUser, subjects, timetable, assignments, submissions, students, divisions } = useErp();

  // Faculty specific subjects
  const mySubjects = subjects.filter((s) => s.assignedFacultyIds?.includes(currentUser.id) || (s as any).facultyId === currentUser.id);

  // Today's classes from timetable (assuming Monday for demo or day based)
  const mySchedule = timetable.filter((t) => t.facultyId === currentUser.id);

  // Pending submissions to evaluate
  const myAssignments = assignments.filter((a) => a.facultyId === currentUser.id);
  const myAssignmentIds = myAssignments.map((a) => a.id);
  const pendingSubmissions = submissions.filter((s) => myAssignmentIds.includes(s.assignmentId) && s.status === 'Submitted');

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-purple-950 via-slate-900 to-indigo-950 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <img
              src={currentUser.photo || currentUser.profileImage || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200'}
              alt=""
              className="w-16 h-16 rounded-2xl object-cover ring-2 ring-purple-400 shadow-md"
            />
            <div>
              <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 text-[10px] font-bold uppercase tracking-wider mb-1">
                <Sparkles className="w-3 h-3" />
                <span>Faculty Academic Portal</span>
              </div>
              <h1 className="text-xl sm:text-2xl font-extrabold">{currentUser.fullName || currentUser.name}</h1>
              <p className="text-xs text-slate-300 mt-0.5">
                {currentUser.department || 'Computer Science & Engineering'} • Apex Institute of Technology & Science
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setCurrentView('mark-attendance')}
              className="px-4 py-2 text-xs font-bold bg-purple-600 hover:bg-purple-500 text-white rounded-xl shadow-md transition-all flex items-center space-x-1.5"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Mark Attendance</span>
            </button>
            <button
              onClick={() => setCurrentView('assignments')}
              className="px-4 py-2 text-xs font-bold bg-white/10 hover:bg-white/20 text-white rounded-xl border border-white/20 transition-all flex items-center space-x-1.5"
            >
              <FileText className="w-4 h-4" />
              <span>Assignments</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div
          onClick={() => setCurrentView('mark-attendance')}
          className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
              <BookOpen className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded-full">
              Assigned
            </span>
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-extrabold text-slate-900">{mySubjects.length}</h3>
            <p className="text-xs text-slate-500 font-medium mt-0.5">Courses & Subjects Taught</p>
          </div>
        </div>

        <div
          onClick={() => setCurrentView('assignments')}
          className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
              <FileText className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full">
              To Grade
            </span>
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-extrabold text-slate-900">{pendingSubmissions.length}</h3>
            <p className="text-xs text-slate-500 font-medium mt-0.5">Pending Student Submissions</p>
          </div>
        </div>

        <div
          onClick={() => setCurrentView('timetable')}
          className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
              <Clock className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full">
              Weekly
            </span>
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-extrabold text-slate-900">{mySchedule.length} Hours</h3>
            <p className="text-xs text-slate-500 font-medium mt-0.5">Weekly Lecture Workload</p>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Today's Lectures & Subjects */}
        <div className="lg:col-span-2 space-y-6">
          {/* Lecture Schedule */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-bold text-base text-slate-900">Assigned Lecture Timetable</h3>
                <p className="text-xs text-slate-500">Your scheduled classes across academic divisions</p>
              </div>
              <button
                onClick={() => setCurrentView('mark-attendance')}
                className="text-xs font-bold text-purple-600 hover:text-purple-700 flex items-center space-x-1"
              >
                <span>Record Attendance</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="space-y-2.5">
              {mySchedule.map((slot) => {
                const sub = subjects.find((s) => s.id === slot.subjectId);
                const div = divisions.find((d) => d.id === slot.divisionId);

                return (
                  <div
                    key={slot.id}
                    className="p-4 rounded-xl border border-slate-100 bg-slate-50/70 hover:bg-purple-50/50 hover:border-purple-200 transition-all flex items-center justify-between"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-xl bg-purple-100 text-purple-800 flex items-center justify-center font-extrabold text-xs">
                        P{slot.period}
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-xs font-bold text-purple-700">{sub?.code}</span>
                          <h4 className="font-bold text-sm text-slate-900">{sub?.name}</h4>
                        </div>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {slot.dayOfWeek} • {div?.name} • Room: <strong>{slot.roomNumber}</strong>
                        </p>
                      </div>
                    </div>

                    <button
                      onClick={() => setCurrentView('mark-attendance')}
                      className="px-3 py-1.5 text-xs font-bold text-purple-700 bg-purple-100 hover:bg-purple-200 rounded-xl transition-colors"
                    >
                      Mark Session
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Assigned Subjects */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs">
            <h3 className="font-bold text-base text-slate-900 mb-3">Teaching Courses</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {mySubjects.map((sub) => (
                <div key={sub.id} className="p-4 rounded-xl border border-slate-100 bg-slate-50 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-purple-700 bg-purple-100 px-2 py-0.5 rounded">
                      {sub.code}
                    </span>
                    <span className="text-xs font-bold text-slate-500">{sub.credits} Credits</span>
                  </div>
                  <h4 className="font-bold text-sm text-slate-900">{sub.name}</h4>
                  <p className="text-xs text-slate-500">Semester {sub.semesterNumber} • {sub.type}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right 1 Col: Quick Links */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs space-y-4">
            <h3 className="font-bold text-base text-slate-900">Faculty Action Center</h3>

            <div className="space-y-2">
              <button
                onClick={() => setCurrentView('materials')}
                className="w-full p-3 text-left rounded-xl bg-slate-50 hover:bg-purple-50 border border-slate-200/60 hover:border-purple-200 transition-all flex items-center justify-between group"
              >
                <div>
                  <h5 className="font-bold text-xs text-slate-900">Study Materials</h5>
                  <p className="text-[10px] text-slate-500">Upload notes, PPTs, and code labs</p>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-purple-600 transition-colors" />
              </button>

              <button
                onClick={() => setCurrentView('assignments')}
                className="w-full p-3 text-left rounded-xl bg-slate-50 hover:bg-purple-50 border border-slate-200/60 hover:border-purple-200 transition-all flex items-center justify-between group"
              >
                <div>
                  <h5 className="font-bold text-xs text-slate-900">Create Assignment</h5>
                  <p className="text-[10px] text-slate-500">Set deadlines & submission criteria</p>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-purple-600 transition-colors" />
              </button>

              <button
                onClick={() => setCurrentView('faculty-leave')}
                className="w-full p-3 text-left rounded-xl bg-slate-50 hover:bg-purple-50 border border-slate-200/60 hover:border-purple-200 transition-all flex items-center justify-between group"
              >
                <div>
                  <h5 className="font-bold text-xs text-slate-900">Apply for Leave</h5>
                  <p className="text-[10px] text-slate-500">Casual, duty, or medical leave request</p>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-purple-600 transition-colors" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
