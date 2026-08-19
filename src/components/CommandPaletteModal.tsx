import React, { useState, useEffect, useMemo } from 'react';
import { useErp } from '../context/ErpContext';
import {
  Search,
  LayoutDashboard,
  Users,
  GraduationCap,
  BookOpen,
  CalendarDays,
  CheckCircle2,
  Receipt,
  FileCheck2,
  FileText,
  AlertCircle,
  Megaphone,
  PartyPopper,
  UserCheck,
  Shield,
  Sparkles,
  ArrowRight,
  X,
  CreditCard,
  Building2,
} from 'lucide-react';

interface CommandPaletteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (view: string) => void;
  onOpenIdCard?: () => void;
}

export const CommandPaletteModal: React.FC<CommandPaletteModalProps> = ({
  isOpen,
  onClose,
  onNavigate,
  onOpenIdCard,
}) => {
  const { students, faculty, currentUser, switchUser, users } = useErp();
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Close on Escape or shortcut Cmd+K / Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (isOpen) {
          onClose();
        }
      } else if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Reset query on open
  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  // Search items list
  const searchResults = useMemo(() => {
    const q = query.toLowerCase().trim();
    const results: Array<{
      id: string;
      title: string;
      subtitle: string;
      category: 'Navigation' | 'Students' | 'Faculty' | 'Quick Actions' | 'Switch Account';
      icon: any;
      action: () => void;
    }> = [];

    // 1. Navigation items
    const navItems = [
      { id: 'nav-admin-dash', title: 'Admin Dashboard', subtitle: 'Executive overview, stats & key metrics', view: 'dashboard', icon: LayoutDashboard, category: 'Navigation' as const },
      { id: 'nav-students', title: 'Student Directory & Admissions', subtitle: 'All enrolled students, dossiers & roll numbers', view: 'students', icon: GraduationCap, category: 'Navigation' as const },
      { id: 'nav-faculty', title: 'Faculty & Staff Directory', subtitle: 'Professors, HODs, employee IDs & departments', view: 'faculty', icon: Users, category: 'Navigation' as const },
      { id: 'nav-departments', title: 'Departments & HODs', subtitle: 'CSE, ECE, ME, MBA academic units', view: 'departments', icon: Building2, category: 'Navigation' as const },
      { id: 'nav-timetable', title: 'Timetable & Class Schedules', subtitle: 'Weekly schedules, periods & room allocations', view: 'timetable', icon: CalendarDays, category: 'Navigation' as const },
      { id: 'nav-attendance', title: 'Attendance Center', subtitle: 'Session logs, absent tracking & aggregate %', view: 'attendance', icon: CheckCircle2, category: 'Navigation' as const },
      { id: 'nav-fees', title: 'Fee Management & Ledgers', subtitle: 'Tuition fees, dues, discounts & receipts', view: 'fees', icon: Receipt, category: 'Navigation' as const },
      { id: 'nav-leaves', title: 'Leave Approvals Desk', subtitle: 'Duty and medical leaves review', view: 'leaves', icon: FileCheck2, category: 'Navigation' as const },
      { id: 'nav-certs', title: 'Certificates Desk', subtitle: 'Bonafide, NOC & Character certificate requests', view: 'certificates', icon: FileText, category: 'Navigation' as const },
      { id: 'nav-grievance', title: 'Grievances & Helpdesk', subtitle: 'Campus complaints & resolution tracking', view: 'grievances', icon: AlertCircle, category: 'Navigation' as const },
      { id: 'nav-notices', title: 'Notices & Circulars', subtitle: 'Official college announcements and pinned circulars', view: 'notices', icon: Megaphone, category: 'Navigation' as const },
      { id: 'nav-events', title: 'Campus Events & Workshops', subtitle: 'Hackathons, symposiums and placement drives', view: 'events', icon: PartyPopper, category: 'Navigation' as const },
      { id: 'nav-faculty-workspace', title: 'Faculty Workspace & Grading', subtitle: 'Mark attendance, assignments & upload materials', view: 'faculty-dashboard', icon: BookOpen, category: 'Navigation' as const },
      { id: 'nav-student-portal', title: 'Student Academic Portal', subtitle: 'My timetable, fee status, marks & digital ID', view: 'student-dashboard', icon: Sparkles, category: 'Navigation' as const },
    ];

    navItems.forEach((item) => {
      if (!q || item.title.toLowerCase().includes(q) || item.subtitle.toLowerCase().includes(q)) {
        results.push({
          id: item.id,
          title: item.title,
          subtitle: item.subtitle,
          category: item.category,
          icon: item.icon,
          action: () => {
            onNavigate(item.view);
            onClose();
          },
        });
      }
    });

    // 2. Students search
    students.forEach((s) => {
      if (
        !q ||
        s.fullName.toLowerCase().includes(q) ||
        s.rollNo?.toLowerCase().includes(q) ||
        s.studentId.toLowerCase().includes(q) ||
        s.collegeEmail.toLowerCase().includes(q)
      ) {
        results.push({
          id: `stu-${s.id}`,
          title: `${s.fullName} (${s.rollNo})`,
          subtitle: `Semester ${s.semesterNumber} • ${s.studentId} • ${s.collegeEmail}`,
          category: 'Students',
          icon: GraduationCap,
          action: () => {
            onNavigate('students');
            onClose();
          },
        });
      }
    });

    // 3. Faculty search
    faculty.forEach((f) => {
      if (
        !q ||
        f.fullName.toLowerCase().includes(q) ||
        f.employeeId.toLowerCase().includes(q) ||
        f.designation.toLowerCase().includes(q) ||
        f.officialEmail.toLowerCase().includes(q)
      ) {
        results.push({
          id: `fac-${f.id}`,
          title: f.fullName,
          subtitle: `${f.designation} • ${f.employeeId} • ${f.officialEmail}`,
          category: 'Faculty',
          icon: Users,
          action: () => {
            onNavigate('faculty');
            onClose();
          },
        });
      }
    });

    // 4. Quick Actions
    if (onOpenIdCard) {
      results.push({
        id: 'qa-id-card',
        title: 'Generate Digital ID Card',
        subtitle: 'View, flip and print student or faculty NFC badge',
        category: 'Quick Actions',
        icon: Sparkles,
        action: () => {
          onOpenIdCard();
          onClose();
        },
      });
    }

    return results.slice(0, 15);
  }, [query, students, faculty, onNavigate, onClose, onOpenIdCard]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-start justify-center pt-16 sm:pt-24 px-4 pb-6">
      <div
        className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Header */}
        <div className="relative flex items-center border-b border-slate-200 px-4 py-3 bg-slate-50/70">
          <Search className="w-5 h-5 text-slate-400 mr-3 shrink-0" />
          <input
            type="text"
            placeholder="Type a screen, student name, roll no, faculty or action... (Press Esc to close)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            className="w-full bg-transparent border-0 text-slate-900 placeholder-slate-400 text-sm sm:text-base focus:ring-0 focus:outline-hidden"
          />
          {query && (
            <button
              onClick={() => setQuery('')}
              className="p-1 text-slate-400 hover:text-slate-600 rounded-md"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <div className="hidden sm:flex items-center space-x-1 ml-2 text-[11px] text-slate-400 bg-white border border-slate-200 px-1.5 py-0.5 rounded">
            <kbd className="font-mono">ESC</kbd>
          </div>
        </div>

        {/* Results List */}
        <div className="max-h-[60vh] overflow-y-auto p-2 divide-y divide-slate-100">
          {searchResults.length === 0 ? (
            <div className="py-12 text-center text-slate-500">
              <Search className="w-8 h-8 mx-auto text-slate-300 mb-2" />
              <p className="text-sm font-medium">No matches found for "{query}"</p>
              <p className="text-xs text-slate-400 mt-1">Try searching for "Attendance", "Rahul", "CSE", or "Fees"</p>
            </div>
          ) : (
            searchResults.map((item, idx) => {
              const Icon = item.icon;
              const isSelected = idx === selectedIndex;
              return (
                <button
                  key={item.id}
                  onClick={item.action}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`w-full flex items-center justify-between p-3 rounded-xl text-left transition-all ${
                    isSelected ? 'bg-blue-50 text-blue-900' : 'hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <div className="flex items-center space-x-3 min-w-0">
                    <div
                      className={`p-2 rounded-lg shrink-0 ${
                        isSelected ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="truncate">
                      <div className="text-sm font-semibold text-slate-900 truncate flex items-center space-x-2">
                        <span>{item.title}</span>
                        <span
                          className={`text-[10px] px-1.5 py-0.2 rounded font-medium ${
                            item.category === 'Navigation'
                              ? 'bg-purple-100 text-purple-700'
                              : item.category === 'Students'
                              ? 'bg-emerald-100 text-emerald-700'
                              : item.category === 'Faculty'
                              ? 'bg-blue-100 text-blue-700'
                              : 'bg-amber-100 text-amber-700'
                          }`}
                        >
                          {item.category}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 truncate">{item.subtitle}</p>
                    </div>
                  </div>
                  <ArrowRight
                    className={`w-4 h-4 shrink-0 transition-transform ${
                      isSelected ? 'text-blue-600 translate-x-1' : 'text-slate-300'
                    }`}
                  />
                </button>
              );
            })
          )}
        </div>

        {/* Footer info */}
        <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center space-x-2">
            <span>Press <kbd className="px-1 py-0.5 bg-white border border-slate-300 rounded font-mono text-[10px]">Enter</kbd> to select</span>
            <span>•</span>
            <span><kbd className="px-1 py-0.5 bg-white border border-slate-300 rounded font-mono text-[10px]">Esc</kbd> to close</span>
          </div>
          <span className="font-semibold text-blue-600">Campus Connect ERP Command</span>
        </div>
      </div>
    </div>
  );
};
