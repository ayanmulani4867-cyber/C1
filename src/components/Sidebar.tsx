import React from 'react';
import { useErp } from '../context/ErpContext';
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  BookOpen,
  CalendarDays,
  CheckCircle2,
  FileSpreadsheet,
  Receipt,
  FileText,
  AlertCircle,
  Megaphone,
  PartyPopper,
  FolderDown,
  FileCheck2,
  Award,
  CreditCard,
  Layers,
  ClipboardList,
  UserSquare2,
} from 'lucide-react';

interface SidebarProps {
  currentView?: string;
  setCurrentView?: (view: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView: propCurrentView, setCurrentView: propSetCurrentView }) => {
  const {
    currentUser,
    leaves,
    certificates,
    grievances,
    assignments,
    submissions,
    currentStudent,
    currentView: ctxCurrentView,
    setCurrentView: ctxSetCurrentView,
  } = useErp();

  const currentView = propCurrentView || ctxCurrentView;
  const setCurrentView = propSetCurrentView || ctxSetCurrentView;

  const pendingLeavesCount = leaves.filter((l) => l.status === 'Pending').length;
  const pendingCertsCount = certificates.filter((c) => c.status === 'Pending').length;
  const openGrievancesCount = grievances.filter((g) => g.status === 'Open' || g.status === 'Under Investigation').length;

  const role = currentUser.role;

  // Compute navigation items by role
  const getNavSections = () => {
    if (role === 'ADMIN') {
      return [
        {
          title: 'Main',
          items: [
            { id: 'dashboard', label: 'Admin Dashboard', icon: LayoutDashboard },
          ],
        },
        {
          title: 'Academics & Structure',
          items: [
            { id: 'departments', label: 'Departments & HODs', icon: Layers },
            { id: 'courses', label: 'Courses & Curriculum', icon: BookOpen },
            { id: 'timetable', label: 'Timetable Manager', icon: CalendarDays },
          ],
        },
        {
          title: 'People Directory',
          items: [
            { id: 'students', label: 'Student Directory', icon: GraduationCap },
            { id: 'faculty', label: 'Faculty Directory', icon: Users },
          ],
        },
        {
          title: 'Operations & Records',
          items: [
            { id: 'attendance', label: 'Attendance Center', icon: CheckCircle2 },
            { id: 'exams', label: 'Exams & Grades', icon: Award },
            { id: 'fees', label: 'Fee & Finance Mgmt', icon: Receipt },
          ],
        },
        {
          title: 'Requests & Services',
          items: [
            { id: 'leaves', label: 'Leave Approvals', icon: FileCheck2, badge: pendingLeavesCount > 0 ? pendingLeavesCount : undefined, badgeColor: 'bg-amber-500' },
            { id: 'certificates', label: 'Certificates Desk', icon: FileText, badge: pendingCertsCount > 0 ? pendingCertsCount : undefined, badgeColor: 'bg-blue-500' },
            { id: 'grievances', label: 'Grievances & Helpdesk', icon: AlertCircle, badge: openGrievancesCount > 0 ? openGrievancesCount : undefined, badgeColor: 'bg-rose-500' },
          ],
        },
        {
          title: 'Campus Life',
          items: [
            { id: 'notices', label: 'Notices & Circulars', icon: Megaphone },
            { id: 'events', label: 'Campus Events', icon: PartyPopper },
          ],
        },
      ];
    }

    if (role === 'HOD' || role === 'FACULTY') {
      return [
        {
          title: 'Academic Desk',
          items: [
            { id: 'faculty-dashboard', label: 'Faculty Workspace', icon: LayoutDashboard },
            { id: 'mark-attendance', label: 'Mark Attendance', icon: CheckCircle2 },
            { id: 'faculty-timetable', label: 'Teaching Schedule', icon: CalendarDays },
            { id: 'assignments-manager', label: 'Assignments & Grading', icon: ClipboardList },
            { id: 'materials-manager', label: 'Study Materials & Notes', icon: FolderDown },
          ],
        },
        {
          title: 'Class & Department',
          items: [
            { id: 'my-classes', label: 'My Classes & Students', icon: GraduationCap },
            { id: 'student-performance', label: 'Performance & Marks', icon: Award },
            ...(role === 'HOD'
              ? [
                  { id: 'department-overview', label: 'Department Overview', icon: Layers },
                  { id: 'leaves', label: 'Review Leaves', icon: FileCheck2, badge: pendingLeavesCount > 0 ? pendingLeavesCount : undefined, badgeColor: 'bg-amber-500' },
                ]
              : []),
          ],
        },
        {
          title: 'Personal & Services',
          items: [
            { id: 'faculty-leave', label: 'My Leave Applications', icon: FileCheck2 },
            { id: 'faculty-id', label: 'Digital Faculty Badge', icon: UserSquare2 },
            { id: 'notices', label: 'Campus Circulars', icon: Megaphone },
            { id: 'events', label: 'Events & Workshops', icon: PartyPopper },
          ],
        },
      ];
    }

    // STUDENT Role
    return [
      {
        title: 'Student Portal',
        items: [
          { id: 'student-dashboard', label: 'My Dashboard', icon: LayoutDashboard },
          { id: 'student-attendance', label: 'Attendance Tracker', icon: CheckCircle2 },
          { id: 'student-timetable', label: 'Class Timetable', icon: CalendarDays },
          { id: 'student-assignments', label: 'Assignments & Tasks', icon: ClipboardList },
          { id: 'student-materials', label: 'Study Materials & Syllabus', icon: FolderDown },
          { id: 'student-results', label: 'Exam Results & Grades', icon: Award },
        ],
      },
      {
        title: 'Finance & Services',
        items: [
          { id: 'student-fees', label: 'Fees & Online Payment', icon: CreditCard },
          { id: 'student-services', label: 'Apply Leave / Certificates', icon: FileText },
          { id: 'student-grievance', label: 'Student Grievance Box', icon: AlertCircle },
          { id: 'student-id-card', label: 'Digital Student ID Card', icon: UserSquare2 },
        ],
      },
      {
        title: 'Campus Buzz',
        items: [
          { id: 'notices', label: 'Notice Board', icon: Megaphone },
          { id: 'events', label: 'College Events & Fests', icon: PartyPopper },
        ],
      },
    ];
  };

  const sections = getNavSections();

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col flex-shrink-0 min-h-[calc(100vh-4rem)] border-r border-slate-800 selection:bg-blue-600">
      {/* Role Banner */}
      <div className="p-4 border-b border-slate-800/80 bg-slate-950/40">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <img
              src={currentUser.profileImage}
              alt=""
              className="w-10 h-10 rounded-xl object-cover ring-2 ring-blue-500/40"
            />
            <span className="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-emerald-500 border-2 border-slate-900 rounded-full" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-bold text-white truncate">{currentUser.fullName}</p>
            <p className="text-[11px] text-blue-400 font-medium tracking-wide">
              {currentUser.role === 'ADMIN'
                ? 'Institutional Director'
                : currentUser.role === 'HOD'
                ? 'Head of Department'
                : currentUser.role === 'FACULTY'
                ? 'Teaching Faculty'
                : `Student (${currentStudent?.rollNo || 'Enrolled'})`}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto p-3 space-y-5">
        {sections.map((section, idx) => (
          <div key={idx} className="space-y-1">
            <h4 className="px-3 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">
              {section.title}
            </h4>
            <div className="space-y-0.5 mt-1">
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = currentView === item.id;
                return (
                  <button
                    key={item.id}
                    id={`nav-link-${item.id}`}
                    onClick={() => setCurrentView(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all group ${
                      isActive
                        ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                        : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/70'
                    }`}
                  >
                    <div className="flex items-center space-x-2.5 min-w-0">
                      <Icon
                        className={`w-4 h-4 flex-shrink-0 transition-colors ${
                          isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'
                        }`}
                      />
                      <span className="truncate">{item.label}</span>
                    </div>

                    {item.badge !== undefined && (
                      <span
                        className={`ml-2 px-1.5 py-0.5 text-[10px] font-bold rounded-full text-white ${
                          item.badgeColor || 'bg-blue-500'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* System Status Footer */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/60">
        <div className="flex items-center justify-between text-[11px] text-slate-400">
          <div className="flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-medium">System Online</span>
          </div>
          <span className="font-mono text-[10px] text-slate-400">AY 2025-26</span>
        </div>
      </div>
    </aside>
  );
};
