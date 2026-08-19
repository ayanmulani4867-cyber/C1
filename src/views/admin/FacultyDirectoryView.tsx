import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { Faculty } from '../../types';
import { FacultyEnrollmentStudio } from '../../components/FacultyEnrollmentStudio';
import {
  Users,
  Plus,
  Search,
  Mail,
  Phone,
  Building,
  GraduationCap,
  Sparkles,
  Edit2,
  Trash2,
  X,
  Award,
  Download,
  Building2,
  BookOpen,
} from 'lucide-react';

interface FacultyDirectoryViewProps {
  onOpenIdCard?: (faculty: Faculty) => void;
}

export const FacultyDirectoryView: React.FC<FacultyDirectoryViewProps> = () => {
  const { faculty, departments, deleteFaculty } = useErp();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDept, setSelectedDept] = useState<string>('ALL');
  const [selectedDesignation, setSelectedDesignation] = useState<string>('ALL');
  const [showStudio, setShowStudio] = useState(false);
  const [facultyToEdit, setFacultyToEdit] = useState<Faculty | null>(null);

  const filteredFaculty = faculty.filter((f) => {
    const matchesSearch =
      f.fullName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.officialEmail.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.facultyId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.employeeId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.specialization.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesDept = selectedDept === 'ALL' || f.departmentId === selectedDept;
    const matchesDesignation = selectedDesignation === 'ALL' || f.designation === selectedDesignation;

    return matchesSearch && matchesDept && matchesDesignation;
  });

  const handleExportCSV = () => {
    const headers = 'Employee ID,Faculty ID,Full Name,Department,Designation,Qualification,Email,Mobile,Office\n';
    const rows = filteredFaculty
      .map((f) => {
        const d = departments.find((dept) => dept.id === f.departmentId)?.code || 'CSE';
        return `"${f.employeeId}","${f.facultyId}","${f.fullName}","${d}","${f.designation}","${f.qualification}","${f.officialEmail}","${f.mobile}","${f.roomOffice}"`;
      })
      .join('\n');

    const blob = new Blob([headers + rows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `Faculty_Directory_Export_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="w-12 h-12 rounded-xl bg-purple-600 text-white flex items-center justify-center shadow-md">
            <Users className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Institutional Faculty & Staff Directory</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Professors, Associate Professors, Assistant Professors, and Department Heads.
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
              setFacultyToEdit(null);
              setShowStudio(true);
            }}
            className="px-4 py-2 bg-purple-700 hover:bg-purple-800 text-white font-bold rounded-xl text-xs shadow-md flex items-center space-x-2 transition"
          >
            <Plus className="w-4 h-4" />
            <span>Add New Faculty</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by Faculty Name, Employee ID, Specialization..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none"
          />
        </div>

        <div>
          <select
            value={selectedDept}
            onChange={(e) => setSelectedDept(e.target.value)}
            className="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none bg-white text-slate-700"
          >
            <option value="ALL">All Academic Departments</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>
                {d.code} — {d.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <select
            value={selectedDesignation}
            onChange={(e) => setSelectedDesignation(e.target.value)}
            className="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none bg-white text-slate-700"
          >
            <option value="ALL">All Academic Designations</option>
            <option value="Professor & HOD">Professor & HOD</option>
            <option value="Professor">Professor</option>
            <option value="Associate Professor">Associate Professor</option>
            <option value="Assistant Professor">Assistant Professor</option>
            <option value="Visiting Faculty">Visiting Faculty</option>
          </select>
        </div>
      </div>

      {/* Faculty Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredFaculty.length > 0 ? (
          filteredFaculty.map((f) => {
            const dept = departments.find((d) => d.id === f.departmentId);
            return (
              <div
                key={f.id}
                className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition p-5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3.5">
                      <img
                        src={f.photo}
                        alt={f.fullName}
                        className="w-14 h-14 rounded-2xl object-cover border-2 border-purple-500 shadow-sm bg-slate-100"
                      />
                      <div>
                        <h3 className="text-sm font-bold text-slate-900 leading-snug">{f.fullName}</h3>
                        <span className="text-[11px] font-semibold text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200 mt-1 inline-block">
                          {f.designation}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 space-y-2 text-xs text-slate-600 border-t border-slate-100 pt-3">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Department:</span>
                      <span className="font-bold text-slate-800">{dept?.name || 'Computer Science'}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Employee ID:</span>
                      <span className="font-mono font-bold text-slate-900">{f.employeeId}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Official Email:</span>
                      <span className="font-mono text-slate-800 truncate max-w-[180px]">{f.officialEmail}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Phone:</span>
                      <span className="font-medium text-slate-800">{f.mobile}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Specialization:</span>
                      <span className="text-slate-700 font-medium text-right max-w-[170px] truncate">{f.specialization}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Office Cabin:</span>
                      <span className="text-slate-700 text-right">{f.roomOffice}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
                  <button
                    type="button"
                    onClick={() => {
                      setFacultyToEdit(f);
                      setShowStudio(true);
                    }}
                    className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg text-xs flex items-center space-x-1.5 transition"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                    <span>Edit Profile</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      if (confirm(`Remove faculty member ${f.fullName} (${f.employeeId})?`)) {
                        deleteFaculty(f.id);
                      }
                    }}
                    className="p-1.5 text-rose-600 hover:text-rose-800 hover:bg-rose-50 rounded-lg transition"
                    title="Delete Faculty"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })
        ) : (
          <div className="col-span-full py-12 text-center text-slate-400 bg-white rounded-2xl border border-slate-200">
            <Users className="w-10 h-10 mx-auto mb-2 text-slate-300" />
            <p className="font-semibold text-slate-600">No faculty records found matching your filters.</p>
          </div>
        )}
      </div>

      {/* Multi-Step Studio Modal */}
      {showStudio && (
        <FacultyEnrollmentStudio
          initialFaculty={facultyToEdit}
          onClose={() => {
            setShowStudio(false);
            setFacultyToEdit(null);
          }}
          onSuccess={() => {
            setShowStudio(false);
            setFacultyToEdit(null);
          }}
        />
      )}
    </div>
  );
};
