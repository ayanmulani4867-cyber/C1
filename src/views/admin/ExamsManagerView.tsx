import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { BookOpen, Plus, Calendar, Award, CheckCircle2, Search, X } from 'lucide-react';
import { ExamSchedule, ExamResult } from '../../types';

export const ExamsManagerView: React.FC = () => {
  const { exams, examResults, subjects, courses, students, departments, addExam, recordExamMarks } = useErp();

  const [activeTab, setActiveTab] = useState<'SCHEDULE' | 'MARKS_ENTRY'>('SCHEDULE');
  const [selectedExamId, setSelectedExamId] = useState<string>(exams[0]?.id || 'exam-mid-4-dbms');
  const [showAddExamModal, setShowAddExamModal] = useState(false);

  // New Exam Form
  const [examForm, setExamForm] = useState({
    title: '',
    examType: 'Mid-Term' as ExamSchedule['examType'],
    courseId: courses[0]?.id || 'course-btech-cse',
    semesterNumber: 4,
    subjectId: subjects[0]?.id || 'sub-dbms',
    examDate: '2026-03-25',
    startTime: '10:00 AM',
    endTime: '01:00 PM',
    maxMarks: 50,
    passingMarks: 20,
    academicYear: '2025-2026',
    status: 'Scheduled' as ExamSchedule['status'],
  });

  const selectedExam = exams.find((e) => e.id === selectedExamId);
  const selectedSubject = subjects.find((s) => s.id === selectedExam?.subjectId);
  const existingResults = examResults.filter((r) => r.examScheduleId === selectedExamId);

  // Local state for editable marks
  const [marksState, setMarksState] = useState<{ [studentId: string]: number }>({});

  const handleCreateExam = (e: React.FormEvent) => {
    e.preventDefault();
    if (!examForm.title) return;
    addExam(examForm);
    setShowAddExamModal(false);
  };

  const handleSaveMarks = (studentId: string, studentRoll: string, studentName: string) => {
    const marks = marksState[studentId] ?? 40;
    const maxMarks = selectedExam?.maxMarks || 50;
    const percentage = (marks / maxMarks) * 100;
    let grade = 'B';
    let gradePoint = 8.0;
    if (percentage >= 90) {
      grade = 'A+';
      gradePoint = 10.0;
    } else if (percentage >= 80) {
      grade = 'A';
      gradePoint = 9.0;
    } else if (percentage >= 70) {
      grade = 'B+';
      gradePoint = 8.0;
    } else if (percentage >= 60) {
      grade = 'B';
      gradePoint = 7.0;
    } else if (percentage >= 50) {
      grade = 'C';
      gradePoint = 6.0;
    } else {
      grade = 'F';
      gradePoint = 0.0;
    }

    recordExamMarks({
      examScheduleId: selectedExamId,
      studentId,
      rollNo: studentRoll,
      studentName,
      subjectId: selectedExam?.subjectId || 'sub-dbms',
      marksObtained: marks,
      maxMarks,
      grade,
      gradePoint,
      isPass: marks >= (selectedExam?.passingMarks || 20),
      evaluatedBy: 'Prof. Arthur Sterling',
      evaluatedDate: new Date().toISOString().split('T')[0],
    });
    alert(`Marks recorded for ${studentName}: ${marks}/${maxMarks} (Grade: ${grade})`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Examinations & Grade Ledger</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Mid-term and End-semester evaluations, scheduling, and mark sheet compilation
          </p>
        </div>

        <button
          onClick={() => setShowAddExamModal(true)}
          className="px-4 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs transition-colors flex items-center space-x-1.5 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Schedule New Exam</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab('SCHEDULE')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'SCHEDULE' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Exam Timetable Schedules ({exams.length})
        </button>
        <button
          onClick={() => setActiveTab('MARKS_ENTRY')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'MARKS_ENTRY' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Marks Evaluation Entry Ledger
        </button>
      </div>

      {activeTab === 'SCHEDULE' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {exams.map((exam) => {
            const sub = subjects.find((s) => s.id === exam.subjectId);
            const course = courses.find((c) => c.id === exam.courseId);

            return (
              <div
                key={exam.id}
                className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200 uppercase">
                      {exam.examType}
                    </span>
                    <span className="text-[10px] font-bold text-slate-400 font-mono">{sub?.code}</span>
                  </div>

                  <h4 className="font-bold text-sm text-slate-900 mt-2.5">{exam.title}</h4>
                  <p className="text-xs text-slate-600 mt-0.5">{sub?.name}</p>

                  <div className="mt-4 bg-slate-50 p-3 rounded-xl space-y-1.5 text-xs text-slate-700">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Date & Time:</span>
                      <span className="font-bold text-slate-900">{exam.examDate} ({exam.startTime})</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Max / Pass Marks:</span>
                      <span className="font-semibold text-slate-900">{exam.maxMarks} / {exam.passingMarks}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Target Semester:</span>
                      <span className="font-semibold text-slate-900">Sem {exam.semesterNumber} ({course?.code})</span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                    {exam.status}
                  </span>
                  <button
                    onClick={() => {
                      setSelectedExamId(exam.id);
                      setActiveTab('MARKS_ENTRY');
                    }}
                    className="text-xs font-bold text-blue-600 hover:text-blue-700"
                  >
                    Enter Marks →
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {activeTab === 'MARKS_ENTRY' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs p-6 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <span className="text-xs font-bold text-slate-400 block uppercase">Selected Examination:</span>
              <h3 className="font-extrabold text-base text-slate-900">{selectedExam?.title}</h3>
              <p className="text-xs text-blue-700 font-semibold">
                {selectedSubject?.name} ({selectedSubject?.code}) • Max Marks: {selectedExam?.maxMarks}
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-slate-500">Switch Exam:</span>
              <select
                value={selectedExamId}
                onChange={(e) => setSelectedExamId(e.target.value)}
                className="py-1.5 px-3 text-xs bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-800"
              >
                {exams.map((e) => (
                  <option key={e.id} value={e.id}>
                    {e.title}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Student Marks Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3 px-4">Student</th>
                  <th className="py-3 px-4">Roll Number</th>
                  <th className="py-3 px-4">Marks Obtained (/{selectedExam?.maxMarks})</th>
                  <th className="py-3 px-4">Recorded Grade</th>
                  <th className="py-3 px-4">Pass Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {students.map((student) => {
                  const result = existingResults.find((r) => r.studentId === student.id);
                  const currentMark = marksState[student.id] ?? (result?.marksObtained ?? 42);

                  return (
                    <tr key={student.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-4 font-bold text-slate-900 flex items-center space-x-2.5">
                        <img src={student.photo} alt="" className="w-7 h-7 rounded-lg object-cover" />
                        <span>{student.fullName}</span>
                      </td>
                      <td className="py-3 px-4 font-bold text-blue-700">{student.rollNo}</td>
                      <td className="py-3 px-4">
                        <input
                          type="number"
                          min="0"
                          max={selectedExam?.maxMarks || 50}
                          value={currentMark}
                          onChange={(e) =>
                            setMarksState({
                              ...marksState,
                              [student.id]: Number(e.target.value),
                            })
                          }
                          className="w-20 px-2.5 py-1 text-xs bg-slate-50 border border-slate-200 rounded-lg font-bold text-slate-900 focus:bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded text-xs font-extrabold bg-blue-50 text-blue-800 border border-blue-200">
                          {result?.grade || (currentMark >= 40 ? 'A' : currentMark >= 30 ? 'B' : 'C')}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {currentMark >= (selectedExam?.passingMarks || 20) ? (
                          <span className="text-emerald-700 font-bold flex items-center space-x-1">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Passed</span>
                          </span>
                        ) : (
                          <span className="text-rose-600 font-bold">Failed</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => handleSaveMarks(student.id, student.rollNo, student.fullName)}
                          className="px-3 py-1 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                        >
                          Save
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Exam Modal */}
      {showAddExamModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-extrabold text-base text-slate-900">Schedule New Examination</h3>
              <button onClick={() => setShowAddExamModal(false)} className="p-1 text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreateExam} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Exam Title *</label>
                <input
                  type="text"
                  required
                  value={examForm.title}
                  onChange={(e) => setExamForm({ ...examForm, title: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="e.g. End-Term Theory Exam - Algorithms"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Exam Type</label>
                  <select
                    value={examForm.examType}
                    onChange={(e) => setExamForm({ ...examForm, examType: e.target.value as any })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  >
                    <option value="Mid-Term">Mid-Term</option>
                    <option value="End-Term">End-Term</option>
                    <option value="Quiz">Quiz</option>
                    <option value="Lab Practical">Lab Practical</option>
                  </select>
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Subject</label>
                  <select
                    value={examForm.subjectId}
                    onChange={(e) => setExamForm({ ...examForm, subjectId: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  >
                    {subjects.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name} ({s.code})
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Exam Date</label>
                  <input
                    type="date"
                    value={examForm.examDate}
                    onChange={(e) => setExamForm({ ...examForm, examDate: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Time Slot</label>
                  <input
                    type="text"
                    value={examForm.startTime}
                    onChange={(e) => setExamForm({ ...examForm, startTime: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                    placeholder="10:00 AM"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Max Marks</label>
                  <input
                    type="number"
                    value={examForm.maxMarks}
                    onChange={(e) => setExamForm({ ...examForm, maxMarks: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Passing Marks</label>
                  <input
                    type="number"
                    value={examForm.passingMarks}
                    onChange={(e) => setExamForm({ ...examForm, passingMarks: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddExamModal(false)}
                  className="px-4 py-2 font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs"
                >
                  Save Schedule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
