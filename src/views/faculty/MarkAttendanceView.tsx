import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { CheckCircle2, XCircle, Clock, Save, Sparkles, Check, Users } from 'lucide-react';
import { AttendanceStatus } from '../../types';

export const MarkAttendanceView: React.FC = () => {
  const { subjects, divisions, students, currentUser, recordAttendanceSession } = useErp();

  const [selectedSubjectId, setSelectedSubjectId] = useState<string>(subjects[0]?.id || 'sub-dbms');
  const [selectedDivisionId, setSelectedDivisionId] = useState<string>(divisions[0]?.id || 'div-cse-4a');
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [period, setPeriod] = useState<number>(2);
  const [topicCovered, setTopicCovered] = useState<string>('ACID Properties & Transaction Isolation Levels');

  // Attendance status mapping per student
  const [records, setRecords] = useState<{ [studentId: string]: { status: AttendanceStatus; remarks?: string } }>({});

  // Filter students belonging to this division
  const divisionStudents = students.filter((s) => s.divisionId === selectedDivisionId);

  // Initialize all to Present
  const handleMarkAll = (status: AttendanceStatus) => {
    const updated: { [id: string]: { status: AttendanceStatus } } = {};
    divisionStudents.forEach((s) => {
      updated[s.id] = { status };
    });
    setRecords(updated);
  };

  const setStudentStatus = (studentId: string, status: AttendanceStatus) => {
    setRecords((prev) => ({
      ...prev,
      [studentId]: {
        ...prev[studentId],
        status,
      },
    }));
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topicCovered) {
      alert('Please specify the topic covered in this lecture.');
      return;
    }

    const attendanceRecords = divisionStudents.map((s) => ({
      studentId: s.id,
      rollNo: s.rollNo,
      studentName: s.fullName,
      status: records[s.id]?.status || 'Present',
      remarks: records[s.id]?.remarks || '',
    }));

    recordAttendanceSession({
      subjectId: selectedSubjectId,
      divisionId: selectedDivisionId,
      facultyId: currentUser.id,
      date,
      period,
      topicCovered,
      records: attendanceRecords,
    });

    alert('Attendance recorded successfully! Absence SMS notifications dispatched.');
  };

  const presentCount = divisionStudents.filter((s) => (records[s.id]?.status || 'Present') === 'Present').length;
  const absentCount = divisionStudents.filter((s) => records[s.id]?.status === 'Absent').length;
  const lateCount = divisionStudents.filter((s) => records[s.id]?.status === 'Late').length;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Mark Lecture Attendance</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Log class roll-call, specify curriculum topics, and automate attendance alerts
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleMarkAll('Present')}
            className="px-3 py-1.5 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-xl transition-colors"
          >
            Mark All Present
          </button>
          <button
            onClick={() => handleMarkAll('Absent')}
            className="px-3 py-1.5 text-xs font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-xl transition-colors"
          >
            Mark All Absent
          </button>
        </div>
      </div>

      {/* Lecture Config Box */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs space-y-4 text-xs">
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div>
            <label className="font-bold text-slate-700 block mb-1">Subject</label>
            <select
              value={selectedSubjectId}
              onChange={(e) => setSelectedSubjectId(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-800"
            >
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.code})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="font-bold text-slate-700 block mb-1">Class Division</label>
            <select
              value={selectedDivisionId}
              onChange={(e) => setSelectedDivisionId(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-800"
            >
              {divisions.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.code})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="font-bold text-slate-700 block mb-1">Date</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
            />
          </div>

          <div>
            <label className="font-bold text-slate-700 block mb-1">Period</label>
            <select
              value={period}
              onChange={(e) => setPeriod(Number(e.target.value))}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-800"
            >
              {[1, 2, 3, 4, 5].map((p) => (
                <option key={p} value={p}>
                  Period {p}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="font-bold text-slate-700 block mb-1">Topic Covered in Lecture *</label>
          <input
            type="text"
            required
            value={topicCovered}
            onChange={(e) => setTopicCovered(e.target.value)}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-medium text-slate-900"
            placeholder="e.g. Relational Calculus, Query Optimization"
          />
        </div>
      </div>

      {/* Summary Counter */}
      <div className="flex items-center justify-between bg-slate-900 text-white p-4 rounded-2xl">
        <div className="flex items-center space-x-6 text-xs font-semibold">
          <span>
            Total: <strong>{divisionStudents.length}</strong>
          </span>
          <span className="text-emerald-400">
            Present: <strong>{presentCount}</strong>
          </span>
          <span className="text-rose-400">
            Absent: <strong>{absentCount}</strong>
          </span>
          <span className="text-amber-400">
            Late: <strong>{lateCount}</strong>
          </span>
        </div>

        <button
          onClick={handleSave}
          className="px-5 py-2 text-xs font-bold text-white bg-purple-600 hover:bg-purple-500 rounded-xl shadow-md flex items-center space-x-1.5 transition-colors"
        >
          <Save className="w-4 h-4" />
          <span>Save & Submit Roll Call</span>
        </button>
      </div>

      {/* Student Attendance List */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3 px-4">Student</th>
                <th className="py-3 px-4">Roll Number</th>
                <th className="py-3 px-4">Current CGPA</th>
                <th className="py-3 px-4 text-center">Attendance Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {divisionStudents.map((student) => {
                const currentStatus = records[student.id]?.status || 'Present';

                return (
                  <tr key={student.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4 font-bold text-slate-900 flex items-center space-x-2.5">
                      <img src={student.photo} alt="" className="w-8 h-8 rounded-xl object-cover" />
                      <span>{student.fullName}</span>
                    </td>
                    <td className="py-3 px-4 font-bold text-blue-700">{student.rollNo}</td>
                    <td className="py-3 px-4 font-semibold text-slate-700">{student.cgpa.toFixed(2)}</td>
                    <td className="py-3 px-4 text-center">
                      <div className="inline-flex items-center space-x-1 bg-slate-100 p-1 rounded-xl">
                        <button
                          type="button"
                          onClick={() => setStudentStatus(student.id, 'Present')}
                          className={`px-3 py-1 text-xs font-bold rounded-lg transition-all ${
                            currentStatus === 'Present'
                              ? 'bg-emerald-600 text-white shadow-xs'
                              : 'text-slate-600 hover:text-emerald-700'
                          }`}
                        >
                          Present
                        </button>
                        <button
                          type="button"
                          onClick={() => setStudentStatus(student.id, 'Late')}
                          className={`px-3 py-1 text-xs font-bold rounded-lg transition-all ${
                            currentStatus === 'Late'
                              ? 'bg-amber-500 text-white shadow-xs'
                              : 'text-slate-600 hover:text-amber-700'
                          }`}
                        >
                          Late
                        </button>
                        <button
                          type="button"
                          onClick={() => setStudentStatus(student.id, 'Absent')}
                          className={`px-3 py-1 text-xs font-bold rounded-lg transition-all ${
                            currentStatus === 'Absent'
                              ? 'bg-rose-600 text-white shadow-xs'
                              : 'text-slate-600 hover:text-rose-700'
                          }`}
                        >
                          Absent
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
