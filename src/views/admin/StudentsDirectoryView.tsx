import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { Student } from '../../types';
import { StudentEnrollmentStudio } from '../../components/StudentEnrollmentStudio';
import { StudentDossierModal } from '../../components/StudentDossierModal';
import {
  GraduationCap,
  Plus,
  Search,
  Filter,
  Eye,
  Trash2,
  Edit2,
  Mail,
  Phone,
  CreditCard,
  Building2,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Download,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
} from 'lucide-react';

interface StudentsDirectoryViewProps {
  onOpenIdCard: (student: Student) => void;
}

export const StudentsDirectoryView: React.FC<StudentsDirectoryViewProps> = ({ onOpenIdCard }) => {
  const { students, departments, courses, divisions, deleteStudent, updateStudent } = useErp();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDept, setSelectedDept] = useState<string>('ALL');
  const [selectedSem, setSelectedSem] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;

  // Enrollment Studio and Dossier states
  const [showEnrollmentStudio, setShowEnrollmentStudio] = useState(false);
  const [studentToEdit, setStudentToEdit] = useState<Student | null>(null);
  const [selectedDossierStudent, setSelectedDossierStudent] = useState<Student | null>(null);

  // Filtered Students
  const filteredStudents = students.filter((s) => {
    const matchesSearch =
      s.fullName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.rollNo.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.studentId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.enrollmentNo.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.collegeEmail.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.mobile.includes(searchQuery);

    const matchesDept = selectedDept === 'ALL' || s.departmentId === selectedDept;
    const matchesSem = selectedSem === 'ALL' || String(s.semesterNumber) === selectedSem;
    const matchesStatus = selectedStatus === 'ALL' || s.status === selectedStatus;

    return matchesSearch && matchesDept && matchesSem && matchesStatus;
  });

  const totalPages = Math.ceil(filteredStudents.length / itemsPerPage) || 1;
  const paginatedStudents = filteredStudents.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handleExportCSV = () => {
    const headers = 'Student ID,Roll No,Enrollment No,Full Name,Department,Course,Semester,Email,Phone,CGPA,Status\n';
    const rows = filteredStudents
      .map((s) => {
        const d = departments.find((dept) => dept.id === s.departmentId)?.code || 'CSE';
        const c = courses.find((crs) => crs.id === s.courseId)?.code || 'B.Tech';
        return `"${s.studentId}","${s.rollNo}","${s.enrollmentNo}","${s.fullName}","${d}","${c}",${s.semesterNumber},"${s.collegeEmail}","${s.mobile}",${s.cgpa},"${s.status}"`;
      })
      .join('\n');

    const blob = new Blob([headers + rows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `Students_Directory_Export_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="w-12 h-12 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-md">
            <GraduationCap className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Institutional Student Directory</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Comprehensive student master database, academic credentials, and official enrollment dossiers.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            type="button"
            onClick={handleExportCSV}
            className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs border border-slate-200 flex items-center space-x-1.5 transition"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setStudentToEdit(null);
              setShowEnrollmentStudio(true);
            }}
            className="px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white font-bold rounded-xl text-xs shadow-md flex items-center space-x-2 transition"
          >
            <Plus className="w-4 h-4" />
            <span>Enroll New Student</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {/* Search */}
        <div className="lg:col-span-2 relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by Name, Roll No, Student ID, Email..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full pl-9 pr-4 py-2 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>

        {/* Department Filter */}
        <div>
          <select
            value={selectedDept}
            onChange={(e) => {
              setSelectedDept(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none bg-white text-slate-700"
          >
            <option value="ALL">All Departments</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>
                {d.code} — {d.name}
              </option>
            ))}
          </select>
        </div>

        {/* Semester Filter */}
        <div>
          <select
            value={selectedSem}
            onChange={(e) => {
              setSelectedSem(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none bg-white text-slate-700"
          >
            <option value="ALL">All Semesters</option>
            {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
              <option key={s} value={String(s)}>
                Semester {s}
              </option>
            ))}
          </select>
        </div>

        {/* Status Filter */}
        <div>
          <select
            value={selectedStatus}
            onChange={(e) => {
              setSelectedStatus(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none bg-white text-slate-700"
          >
            <option value="ALL">All Statuses</option>
            <option value="Active">Active</option>
            <option value="On Leave">On Leave</option>
            <option value="Suspended">Suspended</option>
            <option value="Alumni">Alumni</option>
          </select>
        </div>
      </div>

      {/* Directory Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-3.5 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Registered Students</span>
            <span className="text-xs font-semibold bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
              {filteredStudents.length} Students
            </span>
          </div>
          <span className="text-[11px] text-slate-400">
            Showing {(currentPage - 1) * itemsPerPage + 1}–{Math.min(currentPage * itemsPerPage, filteredStudents.length)} of {filteredStudents.length}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Student</th>
                <th className="py-3 px-3">Student ID</th>
                <th className="py-3 px-3">Enrollment No.</th>
                <th className="py-3 px-3">Roll No.</th>
                <th className="py-3 px-3">Department & Course</th>
                <th className="py-3 px-3 text-center">Sem / Section</th>
                <th className="py-3 px-3">Mobile & Email</th>
                <th className="py-3 px-3 text-center">CGPA</th>
                <th className="py-3 px-3 text-center">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {paginatedStudents.length > 0 ? (
                paginatedStudents.map((s) => {
                  const dept = departments.find((d) => d.id === s.departmentId);
                  const crs = courses.find((c) => c.id === s.courseId);
                  const div = divisions.find((dv) => dv.id === s.divisionId);

                  return (
                    <tr key={s.id} className="hover:bg-blue-50/40 transition">
                      {/* Photo & Name */}
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-3">
                          <img
                            src={s.photo}
                            alt={s.fullName}
                            className="w-10 h-10 rounded-xl object-cover border border-slate-200 shadow-sm"
                          />
                          <div>
                            <span className="font-bold text-slate-900 block">{s.fullName}</span>
                            <span className="text-[11px] text-slate-400 block">{s.batch}</span>
                          </div>
                        </div>
                      </td>

                      {/* Student ID */}
                      <td className="py-3 px-3 font-mono font-bold text-blue-700">{s.studentId}</td>

                      {/* Enrollment No */}
                      <td className="py-3 px-3 font-mono text-slate-700">{s.enrollmentNo}</td>

                      {/* Roll No */}
                      <td className="py-3 px-3 font-mono font-bold text-slate-900">{s.rollNo}</td>

                      {/* Dept & Course */}
                      <td className="py-3 px-3">
                        <span className="font-bold text-slate-800 block">{dept?.code || 'CSE'}</span>
                        <span className="text-[11px] text-slate-500 block truncate max-w-[140px]">{crs?.name || 'B.Tech'}</span>
                      </td>

                      {/* Sem & Section */}
                      <td className="py-3 px-3 text-center">
                        <span className="font-semibold text-slate-800 block">Sem {s.semesterNumber}</span>
                        <span className="text-[10px] text-slate-400">{div?.name || 'Sec A'}</span>
                      </td>

                      {/* Mobile & Email */}
                      <td className="py-3 px-3">
                        <span className="text-slate-800 block font-medium">{s.mobile}</span>
                        <span className="text-[11px] font-mono text-slate-400 block truncate max-w-[150px]">{s.collegeEmail}</span>
                      </td>

                      {/* CGPA */}
                      <td className="py-3 px-3 text-center">
                        <span className="font-mono font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                          {s.cgpa || 8.5}
                        </span>
                      </td>

                      {/* Status */}
                      <td className="py-3 px-3 text-center">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                            s.status === 'Active'
                              ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                              : s.status === 'On Leave'
                              ? 'bg-amber-100 text-amber-800 border border-amber-200'
                              : 'bg-rose-100 text-rose-800 border border-rose-200'
                          }`}
                        >
                          {s.status}
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-1.5">
                          <button
                            type="button"
                            onClick={() => setSelectedDossierStudent(s)}
                            className="p-1.5 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition"
                            title="View Full Dossier"
                          >
                            <Eye className="w-4 h-4" />
                          </button>

                          <button
                            type="button"
                            onClick={() => {
                              setStudentToEdit(s);
                              setShowEnrollmentStudio(true);
                            }}
                            className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition"
                            title="Edit Student"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>

                          <button
                            type="button"
                            onClick={() => onOpenIdCard(s)}
                            className="p-1.5 text-purple-600 hover:text-purple-800 hover:bg-purple-50 rounded-lg transition"
                            title="Digital ID Card"
                          >
                            <CreditCard className="w-4 h-4" />
                          </button>

                          <button
                            type="button"
                            onClick={() => {
                              if (confirm(`Are you sure you want to delete student ${s.fullName} (${s.rollNo})?`)) {
                                deleteStudent(s.id);
                              }
                            }}
                            className="p-1.5 text-rose-600 hover:text-rose-800 hover:bg-rose-50 rounded-lg transition"
                            title="Delete Student"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-slate-400">
                    <GraduationCap className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                    <p className="font-semibold text-slate-600">No student records found matching your filters.</p>
                    <p className="text-xs text-slate-400 mt-1">Try resetting the search bar or changing department filters.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        {totalPages > 1 && (
          <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
            <span className="text-xs text-slate-500">
              Page {currentPage} of {totalPages}
            </span>
            <div className="flex items-center space-x-2">
              <button
                type="button"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                className="px-3 py-1 bg-white border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 disabled:opacity-40 hover:bg-slate-50 transition"
              >
                Previous
              </button>
              <button
                type="button"
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                className="px-3 py-1 bg-white border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 disabled:opacity-40 hover:bg-slate-50 transition"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Multi-Step Enrollment Studio Modal */}
      {showEnrollmentStudio && (
        <StudentEnrollmentStudio
          initialStudent={studentToEdit}
          onClose={() => {
            setShowEnrollmentStudio(false);
            setStudentToEdit(null);
          }}
          onSuccess={() => {
            setShowEnrollmentStudio(false);
            setStudentToEdit(null);
          }}
        />
      )}

      {/* Student Dossier Modal */}
      {selectedDossierStudent && (
        <StudentDossierModal
          student={selectedDossierStudent}
          onClose={() => setSelectedDossierStudent(null)}
          onEdit={(st) => {
            setSelectedDossierStudent(null);
            setStudentToEdit(st);
            setShowEnrollmentStudio(true);
          }}
          onOpenIdCard={(st) => {
            setSelectedDossierStudent(null);
            onOpenIdCard(st);
          }}
        />
      )}
    </div>
  );
};
