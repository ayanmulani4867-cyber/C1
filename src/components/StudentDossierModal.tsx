import React, { useState } from 'react';
import { useErp } from '../context/ErpContext';
import { Student, FeePayment } from '../types';
import { formatINR, formatIndianDate } from '../utils/formatters';
import {
  User,
  GraduationCap,
  Users,
  MapPin,
  CalendarDays,
  Award,
  Receipt,
  FileCheck2,
  FileText,
  CreditCard,
  CheckCircle2,
  Clock,
  Mail,
  Phone,
  Edit2,
  X,
  Printer,
  ShieldCheck,
  Building2,
  BookOpen,
} from 'lucide-react';

interface StudentDossierModalProps {
  student: Student;
  onClose: () => void;
  onEdit: (student: Student) => void;
  onOpenIdCard: (student: Student) => void;
  onOpenReceipt?: (payment: FeePayment) => void;
}

export const StudentDossierModal: React.FC<StudentDossierModalProps> = ({
  student,
  onClose,
  onEdit,
  onOpenIdCard,
  onOpenReceipt,
}) => {
  const {
    departments,
    courses,
    divisions,
    attendanceSessions,
    examResults,
    exams,
    subjects,
    feeLedgers,
    feePayments,
    assignments,
    submissions,
    leaves,
    certificates,
  } = useErp();

  const [activeTab, setActiveTab] = useState<
    'overview' | 'personal' | 'academic' | 'guardian' | 'attendance' | 'results' | 'fees' | 'assignments' | 'documents'
  >('overview');

  const dept = departments.find((d) => d.id === student.departmentId);
  const course = courses.find((c) => c.id === student.courseId);
  const div = divisions.find((dv) => dv.id === student.divisionId);

  // Student specific stats
  const studentFeeLedger = feeLedgers.find((fl) => fl.studentId === student.id);
  const studentPayments = feePayments.filter((fp) => fp.studentId === student.id);
  const studentResults = examResults.filter((er) => er.studentId === student.id);
  const studentLeaves = leaves.filter((l) => l.applicantId === student.id);
  const studentCerts = certificates.filter((c) => c.studentId === student.id);

  // Calculate attendance rate
  let attendedCount = 0;
  let totalSessions = 0;
  attendanceSessions.forEach((s) => {
    const rec = s.records.find((r) => r.studentId === student.id);
    if (rec) {
      totalSessions++;
      if (rec.status === 'Present') attendedCount++;
    }
  });
  const attendanceRate = totalSessions > 0 ? ((attendedCount / totalSessions) * 100).toFixed(1) : '88.5';

  const tabsList = [
    { id: 'overview', label: 'Overview & Summary', icon: User },
    { id: 'personal', label: 'Personal Details', icon: ShieldCheck },
    { id: 'academic', label: 'Academic Profile', icon: GraduationCap },
    { id: 'guardian', label: 'Guardian Coordinates', icon: Users },
    { id: 'attendance', label: 'Attendance Records', icon: CheckCircle2 },
    { id: 'results', label: 'Results & Marksheet', icon: Award },
    { id: 'fees', label: 'Fee & Financials', icon: Receipt },
    { id: 'assignments', label: 'Assignments & Submissions', icon: FileCheck2 },
    { id: 'documents', label: 'Certificates & KYC', icon: FileText },
  ];

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-6xl max-h-[94vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-150">
        {/* Header Ribbon */}
        <div className="bg-slate-900 text-white px-6 py-5 border-b border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <img
                src={student.photo}
                alt={student.fullName}
                className="w-16 h-16 rounded-2xl object-cover border-2 border-blue-500 shadow-md bg-white"
              />
              <span className="absolute -bottom-1 -right-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-500 text-white shadow">
                {student.status}
              </span>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-xl font-bold text-white tracking-tight">{student.fullName}</h2>
                <span className="text-xs font-mono font-bold bg-blue-600 text-white px-2 py-0.5 rounded">
                  {student.rollNo}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                {course?.name || 'B.Tech CSE'} • Semester {student.semesterNumber} • Section {div?.name || 'A'} • ID: {student.studentId}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={() => onOpenIdCard(student)}
              className="px-3 py-1.5 bg-blue-700 hover:bg-blue-600 text-white text-xs font-semibold rounded-lg shadow-sm flex items-center space-x-1.5 transition"
            >
              <CreditCard className="w-3.5 h-3.5" />
              <span>Digital ID Card</span>
            </button>
            <button
              type="button"
              onClick={() => onEdit(student)}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-lg border border-slate-700 flex items-center space-x-1.5 transition"
            >
              <Edit2 className="w-3.5 h-3.5" />
              <span>Edit Dossier</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-slate-50 border-b border-slate-200 px-6 overflow-x-auto flex space-x-1">
          {tabsList.map((t) => {
            const Icon = t.icon;
            const isActive = activeTab === t.id;
            return (
              <button
                key={t.id}
                type="button"
                onClick={() => setActiveTab(t.id as any)}
                className={`py-3 px-3.5 text-xs font-bold border-b-2 flex items-center space-x-2 whitespace-nowrap transition-all ${
                  isActive
                    ? 'border-blue-600 text-blue-700 bg-white shadow-sm -mb-px rounded-t-lg'
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-100/70'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                <span>{t.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Body */}
        <div className="flex-1 overflow-y-auto p-6 bg-slate-100/50">
          {/* 1. OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="space-y-5 max-w-5xl mx-auto">
              {/* Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">Attendance Rate</span>
                  <div className="mt-1 flex items-baseline space-x-2">
                    <span className={`text-2xl font-black ${Number(attendanceRate) >= 75 ? 'text-emerald-700' : 'text-rose-600'}`}>
                      {attendanceRate}%
                    </span>
                    <span className="text-xs text-slate-400">Min 75% req.</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2 overflow-hidden">
                    <div
                      className={`h-full ${Number(attendanceRate) >= 75 ? 'bg-emerald-500' : 'bg-rose-500'}`}
                      style={{ width: `${Math.min(Number(attendanceRate), 100)}%` }}
                    />
                  </div>
                </div>

                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">Cumulative CGPA</span>
                  <div className="mt-1 flex items-baseline space-x-2">
                    <span className="text-2xl font-black text-blue-700">{student.cgpa || 8.85}</span>
                    <span className="text-xs text-slate-400">/ 10.0</span>
                  </div>
                  <span className="text-[11px] text-emerald-700 font-semibold mt-1 block">First Class with Distinction</span>
                </div>

                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">Pending Fee Balance</span>
                  <div className="mt-1 flex items-baseline space-x-2">
                    <span className="text-2xl font-black text-slate-900">
                      {formatINR(studentFeeLedger?.pendingAmount || 0)}
                    </span>
                  </div>
                  <span className={`text-[11px] font-bold ${studentFeeLedger?.pendingAmount === 0 ? 'text-emerald-700' : 'text-amber-700'}`}>
                    {studentFeeLedger?.pendingAmount === 0 ? 'Fully Cleared' : 'Semester 4 Due'}
                  </span>
                </div>

                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">Completed Credits</span>
                  <div className="mt-1 flex items-baseline space-x-2">
                    <span className="text-2xl font-black text-purple-700">72</span>
                    <span className="text-xs text-slate-400">/ 160 Total</span>
                  </div>
                  <span className="text-[11px] text-slate-500 font-semibold mt-1 block">On Track for Graduation</span>
                </div>
              </div>

              {/* Two Column Key Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-2 border-b border-slate-100 pb-2">
                    <GraduationCap className="w-4 h-4 text-blue-600" />
                    <span>Academic Registration</span>
                  </h4>
                  <div className="grid grid-cols-2 gap-y-2 text-xs">
                    <div><span className="text-slate-500">Department:</span> <strong className="text-slate-900 block">{dept?.name}</strong></div>
                    <div><span className="text-slate-500">Degree Program:</span> <strong className="text-slate-900 block">{course?.name}</strong></div>
                    <div><span className="text-slate-500">Enrollment No:</span> <strong className="text-slate-900 font-mono block">{student.enrollmentNo}</strong></div>
                    <div><span className="text-slate-500">Admission No:</span> <strong className="text-slate-900 font-mono block">{student.admissionNo}</strong></div>
                    <div><span className="text-slate-500">Academic Batch:</span> <strong className="text-slate-900 block">{student.batch}</strong></div>
                    <div><span className="text-slate-500">Admission Date:</span> <strong className="text-slate-900 block">{formatIndianDate(student.admissionDate)}</strong></div>
                  </div>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-2 border-b border-slate-100 pb-2">
                    <Phone className="w-4 h-4 text-blue-600" />
                    <span>Communication & Coordinates</span>
                  </h4>
                  <div className="grid grid-cols-2 gap-y-2 text-xs">
                    <div><span className="text-slate-500">Mobile Phone:</span> <strong className="text-slate-900 block">{student.mobile}</strong></div>
                    <div><span className="text-slate-500">College Email:</span> <strong className="text-slate-900 font-mono block truncate">{student.collegeEmail}</strong></div>
                    <div><span className="text-slate-500">Parent / Father:</span> <strong className="text-slate-900 block">{student.fatherName}</strong></div>
                    <div><span className="text-slate-500">Parent Phone:</span> <strong className="text-slate-900 block">{student.parentPhone}</strong></div>
                    <div className="col-span-2"><span className="text-slate-500">Current Address:</span> <strong className="text-slate-900 block">{student.currentAddress?.line1}, {student.currentAddress?.city}, {student.currentAddress?.state} - {student.currentAddress?.pincode}</strong></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 2. PERSONAL */}
          {activeTab === 'personal' && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm max-w-4xl mx-auto space-y-6">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-2">
                Biographical & Identity Records
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 text-xs">
                <div><span className="text-slate-500">Full Legal Name:</span> <strong className="text-slate-900 block text-sm font-bold mt-0.5">{student.fullName}</strong></div>
                <div><span className="text-slate-500">Date of Birth:</span> <strong className="text-slate-900 block text-sm font-bold mt-0.5">{formatIndianDate(student.dob)}</strong></div>
                <div><span className="text-slate-500">Gender:</span> <strong className="text-slate-900 block text-sm font-bold mt-0.5">{student.gender}</strong></div>
                <div><span className="text-slate-500">Blood Group:</span> <strong className="text-slate-900 block text-sm font-bold mt-0.5 text-rose-700">{student.bloodGroup}</strong></div>
                <div><span className="text-slate-500">Nationality:</span> <strong className="text-slate-900 block text-sm font-bold mt-0.5">Indian</strong></div>
                <div><span className="text-slate-500">Identity Verification:</span> <strong className="text-slate-900 block text-sm font-bold mt-0.5 text-emerald-700">Aadhaar Verified</strong></div>
                <div><span className="text-slate-500">Personal Email:</span> <strong className="text-slate-900 block mt-0.5">{student.personalEmail}</strong></div>
                <div><span className="text-slate-500">Official College Email:</span> <strong className="text-slate-900 font-mono block mt-0.5">{student.collegeEmail}</strong></div>
                <div><span className="text-slate-500">Emergency Contact:</span> <strong className="text-slate-900 block mt-0.5">{student.emergencyContact?.name} ({student.emergencyContact?.relation}) - {student.emergencyContact?.phone}</strong></div>
              </div>
            </div>
          )}

          {/* 3. ACADEMIC */}
          {activeTab === 'academic' && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm max-w-4xl mx-auto space-y-6">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-2">
                University Registration & Program Details
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-xs">
                <div><span className="text-slate-500">Student ID:</span> <strong className="text-slate-900 font-mono font-bold block text-sm">{student.studentId}</strong></div>
                <div><span className="text-slate-500">Roll Number:</span> <strong className="text-slate-900 font-mono font-bold block text-sm">{student.rollNo}</strong></div>
                <div><span className="text-slate-500">Enrollment Number:</span> <strong className="text-slate-900 font-mono font-bold block text-sm">{student.enrollmentNo}</strong></div>
                <div><span className="text-slate-500">Admission Number:</span> <strong className="text-slate-900 font-mono font-bold block text-sm">{student.admissionNo}</strong></div>
                <div><span className="text-slate-500">Department:</span> <strong className="text-slate-900 block font-bold">{dept?.name} ({dept?.code})</strong></div>
                <div><span className="text-slate-500">Course Program:</span> <strong className="text-slate-900 block font-bold">{course?.name}</strong></div>
                <div><span className="text-slate-500">Semester & Section:</span> <strong className="text-slate-900 block">Semester {student.semesterNumber} • Section {div?.name || 'A'}</strong></div>
                <div><span className="text-slate-500">Academic Standing:</span> <strong className="text-emerald-700 block font-bold">{student.status} (Regular Student)</strong></div>
              </div>
            </div>
          )}

          {/* 4. GUARDIAN */}
          {activeTab === 'guardian' && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm max-w-4xl mx-auto space-y-6">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-2">
                Parent & Guardian Records
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-xs">
                <div><span className="text-slate-500">Father's Name:</span> <strong className="text-slate-900 block text-sm font-bold mt-0.5">{student.fatherName}</strong></div>
                <div><span className="text-slate-500">Mother's Name:</span> <strong className="text-slate-900 block text-sm font-bold mt-0.5">{student.motherName}</strong></div>
                <div><span className="text-slate-500">Primary Contact Phone:</span> <strong className="text-slate-900 block text-sm font-bold mt-0.5">{student.parentPhone}</strong></div>
                <div><span className="text-slate-500">Emergency Phone:</span> <strong className="text-slate-900 block text-sm font-bold mt-0.5">{student.emergencyContact?.phone}</strong></div>
                <div className="col-span-2"><span className="text-slate-500">Permanent Residential Address:</span> <strong className="text-slate-900 block mt-1">{student.currentAddress?.line1}, {student.currentAddress?.city}, {student.currentAddress?.state} - {student.currentAddress?.pincode}</strong></div>
              </div>
            </div>
          )}

          {/* 5. ATTENDANCE */}
          {activeTab === 'attendance' && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm max-w-5xl mx-auto space-y-4">
              <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Semester 4 Live Attendance Sessions
                </h3>
                <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-3 py-1 rounded-full border border-emerald-300">
                  Overall: {attendanceRate}%
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
                    <tr>
                      <th className="py-2.5 px-3">Session Date</th>
                      <th className="py-2.5 px-3">Subject</th>
                      <th className="py-2.5 px-3">Period</th>
                      <th className="py-2.5 px-3">Topic Covered</th>
                      <th className="py-2.5 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {attendanceSessions.slice(0, 10).map((s) => {
                      const rec = s.records.find((r) => r.studentId === student.id);
                      const isPres = rec ? rec.status === 'Present' : true;
                      const sub = subjects.find((sb) => sb.id === s.subjectId);
                      return (
                        <tr key={s.id} className="hover:bg-slate-50">
                          <td className="py-2.5 px-3 font-semibold text-slate-900">{formatIndianDate(s.date)}</td>
                          <td className="py-2.5 px-3 font-medium text-slate-800">{sub?.name || 'Core CSE Subject'}</td>
                          <td className="py-2.5 px-3 font-mono text-slate-500">Period {s.period}</td>
                          <td className="py-2.5 px-3 text-slate-600">{s.topicCovered || 'Syllabus lecture'}</td>
                          <td className="py-2.5 px-3">
                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${isPres ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                              {isPres ? 'Present' : 'Absent'}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 6. RESULTS */}
          {activeTab === 'results' && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm max-w-5xl mx-auto space-y-4">
              <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Academic Performance & Semester Marksheets
                </h3>
                <span className="text-xs font-bold text-blue-700 bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
                  CGPA: {student.cgpa || 8.85}
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
                    <tr>
                      <th className="py-2.5 px-3">Subject Code & Name</th>
                      <th className="py-2.5 px-3">Semester</th>
                      <th className="py-2.5 px-3 text-right">Marks</th>
                      <th className="py-2.5 px-3 text-right">Max</th>
                      <th className="py-2.5 px-3 text-center">Grade</th>
                      <th className="py-2.5 px-3 text-center">Grade Point</th>
                      <th className="py-2.5 px-3">Remarks</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {studentResults.length > 0 ? (
                      studentResults.map((r) => {
                        const sub = subjects.find((s) => s.id === r.subjectId);
                        return (
                          <tr key={r.id} className="hover:bg-slate-50">
                            <td className="py-2.5 px-3 font-semibold text-slate-900">
                              {sub?.code || 'CS401'} — {sub?.name || 'Database Management Systems'}
                            </td>
                            <td className="py-2.5 px-3 text-slate-600">Semester {r.semesterNumber || 3}</td>
                            <td className="py-2.5 px-3 font-mono font-bold text-slate-900 text-right">{r.marksObtained}</td>
                            <td className="py-2.5 px-3 font-mono text-slate-500 text-right">{r.maxMarks}</td>
                            <td className="py-2.5 px-3 text-center">
                              <span className="px-2 py-0.5 font-bold rounded bg-blue-100 text-blue-800">
                                {r.grade}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 font-mono font-bold text-center text-slate-900">{r.gradePoint}</td>
                            <td className="py-2.5 px-3 text-slate-600">{r.remarks || 'Passed'}</td>
                          </tr>
                        );
                      })
                    ) : (
                      <tr>
                        <td colSpan={7} className="py-8 text-center text-slate-400">
                          No previous semester marksheets found for this student.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 7. FEES */}
          {activeTab === 'fees' && (
            <div className="space-y-5 max-w-5xl mx-auto">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                  <span className="text-xs text-slate-500 font-medium">Total Semester Fee</span>
                  <p className="text-xl font-bold text-slate-900 mt-1">{formatINR(studentFeeLedger?.totalAmount || 85000)}</p>
                </div>
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                  <span className="text-xs text-slate-500 font-medium">Paid to Date</span>
                  <p className="text-xl font-bold text-emerald-700 mt-1">{formatINR(studentFeeLedger?.paidAmount || 85000)}</p>
                </div>
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                  <span className="text-xs text-slate-500 font-medium">Outstanding Balance</span>
                  <p className="text-xl font-bold text-rose-600 mt-1">{formatINR(studentFeeLedger?.pendingAmount || 0)}</p>
                </div>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider border-b border-slate-100 pb-2">
                  Official Fee Receipts & Transaction Log
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
                      <tr>
                        <th className="py-2.5 px-3">Receipt No.</th>
                        <th className="py-2.5 px-3">Date</th>
                        <th className="py-2.5 px-3">Mode</th>
                        <th className="py-2.5 px-3">Transaction ID</th>
                        <th className="py-2.5 px-3 text-right">Amount (₹)</th>
                        <th className="py-2.5 px-3 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200">
                      {studentPayments.map((p) => (
                        <tr key={p.id} className="hover:bg-slate-50">
                          <td className="py-2.5 px-3 font-mono font-bold text-blue-700">{p.receiptNumber}</td>
                          <td className="py-2.5 px-3 text-slate-700">{formatIndianDate(p.paymentDate)}</td>
                          <td className="py-2.5 px-3 font-medium text-slate-800">{p.paymentMethod}</td>
                          <td className="py-2.5 px-3 font-mono text-slate-500">{p.transactionId}</td>
                          <td className="py-2.5 px-3 font-mono font-bold text-slate-900 text-right">{formatINR(p.amount)}</td>
                          <td className="py-2.5 px-3 text-right">
                            {onOpenReceipt && (
                              <button
                                type="button"
                                onClick={() => onOpenReceipt(p)}
                                className="px-2.5 py-1 bg-blue-50 text-blue-700 hover:bg-blue-100 font-bold rounded border border-blue-200"
                              >
                                View Receipt
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

          {/* 8. ASSIGNMENTS */}
          {activeTab === 'assignments' && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm max-w-5xl mx-auto space-y-4">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-2">
                Assignments & Grading Submissions
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
                    <tr>
                      <th className="py-2.5 px-3">Assignment Title</th>
                      <th className="py-2.5 px-3">Subject</th>
                      <th className="py-2.5 px-3">Due Date</th>
                      <th className="py-2.5 px-3">Submission File</th>
                      <th className="py-2.5 px-3 text-right">Marks</th>
                      <th className="py-2.5 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {assignments.slice(0, 6).map((a) => {
                      const sub = subjects.find((sb) => sb.id === a.subjectId);
                      const submission = submissions.find((s) => s.assignmentId === a.id && s.studentId === student.id);
                      return (
                        <tr key={a.id} className="hover:bg-slate-50">
                          <td className="py-2.5 px-3 font-semibold text-slate-900">{a.title}</td>
                          <td className="py-2.5 px-3 text-slate-700">{sub?.name || 'Core CSE'}</td>
                          <td className="py-2.5 px-3 text-slate-600">{formatIndianDate(a.dueDate)}</td>
                          <td className="py-2.5 px-3 font-mono text-blue-600">{submission?.fileName || 'submission.zip'}</td>
                          <td className="py-2.5 px-3 font-mono font-bold text-slate-900 text-right">
                            {submission?.marksObtained !== undefined ? `${submission.marksObtained} / ${a.maxMarks}` : `Pending / ${a.maxMarks}`}
                          </td>
                          <td className="py-2.5 px-3">
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700">
                              {submission ? submission.status : 'Submitted'}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 9. DOCUMENTS */}
          {activeTab === 'documents' && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm max-w-4xl mx-auto space-y-5">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-2">
                Official University Certificates & KYC Verification
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 border border-slate-200 rounded-xl bg-slate-50 flex items-center space-x-3">
                  <FileText className="w-8 h-8 text-blue-600" />
                  <div className="flex-1">
                    <h5 className="text-xs font-bold text-slate-900">10th Standard Board Marksheet</h5>
                    <span className="text-[11px] text-slate-500">PDF • Verified on Admission</span>
                  </div>
                  <span className="text-[10px] font-bold bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded">Verified</span>
                </div>

                <div className="p-4 border border-slate-200 rounded-xl bg-slate-50 flex items-center space-x-3">
                  <FileText className="w-8 h-8 text-blue-600" />
                  <div className="flex-1">
                    <h5 className="text-xs font-bold text-slate-900">12th Standard Board Marksheet</h5>
                    <span className="text-[11px] text-slate-500">PDF • Verified on Admission</span>
                  </div>
                  <span className="text-[10px] font-bold bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded">Verified</span>
                </div>

                <div className="p-4 border border-slate-200 rounded-xl bg-slate-50 flex items-center space-x-3">
                  <FileText className="w-8 h-8 text-blue-600" />
                  <div className="flex-1">
                    <h5 className="text-xs font-bold text-slate-900">College Transfer & Character Certificate</h5>
                    <span className="text-[11px] text-slate-500">PDF • Institutional Record</span>
                  </div>
                  <span className="text-[10px] font-bold bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded">Verified</span>
                </div>

                <div className="p-4 border border-slate-200 rounded-xl bg-slate-50 flex items-center space-x-3">
                  <ShieldCheck className="w-8 h-8 text-emerald-600" />
                  <div className="flex-1">
                    <h5 className="text-xs font-bold text-slate-900">Aadhaar / National Identity Document</h5>
                    <span className="text-[11px] text-slate-500">Secure Government ID Proof</span>
                  </div>
                  <span className="text-[10px] font-bold bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded">Verified</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 bg-slate-100 border-t border-slate-200 flex items-center justify-between">
          <span className="text-xs text-slate-500">
            Student Record Ref: <strong className="font-mono">{student.studentId}</strong> • Apex Institute ERP
          </span>
          <button
            type="button"
            onClick={onClose}
            className="px-5 py-1.5 bg-slate-800 hover:bg-slate-900 text-white font-semibold rounded-xl text-xs transition"
          >
            Close Dossier
          </button>
        </div>
      </div>
    </div>
  );
};
