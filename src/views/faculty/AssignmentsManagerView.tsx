import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { FileText, Plus, CheckCircle2, Clock, Calendar, Users, Eye, X, Award } from 'lucide-react';
import { Assignment } from '../../types';

export const AssignmentsManagerView: React.FC = () => {
  const { assignments, submissions, subjects, currentUser, addAssignment, gradeSubmission } = useErp();

  const [activeTab, setActiveTab] = useState<'ASSIGNMENTS' | 'SUBMISSIONS'>('ASSIGNMENTS');
  const [selectedAssignmentId, setSelectedAssignmentId] = useState<string>(assignments[0]?.id || 'assign-dbms-1');
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Grading Modal State
  const [gradingSubmissionId, setGradingSubmissionId] = useState<string | null>(null);
  const [gradeMarks, setGradeMarks] = useState<number>(18);
  const [gradeFeedback, setGradeFeedback] = useState<string>('Excellent query optimization and thorough ER diagram.');

  // Create Assignment Form
  const [form, setForm] = useState({
    title: '',
    description: '',
    subjectId: subjects[0]?.id || 'sub-dbms',
    divisionId: 'div-cse-4a',
    dueDate: '2026-03-30',
    totalMarks: 20,
  });

  const myAssignments = assignments.filter((a) => a.facultyId === currentUser.id);
  const selectedAssignment = assignments.find((a) => a.id === selectedAssignmentId);
  const assignmentSubmissions = submissions.filter((s) => s.assignmentId === selectedAssignmentId);

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title) return;

    addAssignment({
      ...form,
      facultyId: currentUser.id,
      assignedDate: new Date().toISOString().split('T')[0],
      attachmentUrl: 'https://apex.edu/materials/assignment-brief.pdf',
    });

    setShowCreateModal(false);
  };

  const handleGrade = (e: React.FormEvent) => {
    e.preventDefault();
    if (!gradingSubmissionId) return;

    gradeSubmission(gradingSubmissionId, Number(gradeMarks), gradeFeedback);
    setGradingSubmissionId(null);
    alert('Submission evaluated and grade recorded!');
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Assignments & Evaluation Lab</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Assign homework tasks, track student file submissions, and provide structured grading
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 text-xs font-bold text-white bg-purple-600 hover:bg-purple-700 rounded-xl shadow-xs transition-colors flex items-center space-x-1.5 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Create New Assignment</span>
        </button>
      </div>

      {/* View Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab('ASSIGNMENTS')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'ASSIGNMENTS' ? 'bg-purple-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          My Assignments ({myAssignments.length})
        </button>
        <button
          onClick={() => setActiveTab('SUBMISSIONS')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'SUBMISSIONS' ? 'bg-purple-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Student Submissions ({assignmentSubmissions.length})
        </button>
      </div>

      {activeTab === 'ASSIGNMENTS' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {myAssignments.map((assign) => {
            const sub = subjects.find((s) => s.id === assign.subjectId);
            const subs = submissions.filter((s) => s.assignmentId === assign.id);
            const gradedCount = subs.filter((s) => s.status === 'Graded').length;

            return (
              <div
                key={assign.id}
                className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
                      {sub?.code}
                    </span>
                    <span className="text-xs font-bold text-slate-500">Max: {assign.totalMarks} Marks</span>
                  </div>

                  <h4 className="font-extrabold text-sm text-slate-900 mt-2.5">{assign.title}</h4>
                  <p className="text-xs text-slate-600 mt-1 line-clamp-2 leading-relaxed">{assign.description}</p>

                  <div className="mt-4 bg-slate-50 p-3 rounded-xl space-y-1 text-xs text-slate-600">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Assigned Date:</span>
                      <span>{assign.assignedDate}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400 font-semibold text-rose-600">Submission Due:</span>
                      <span className="font-bold text-rose-600">{assign.dueDate}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-700">
                    {subs.length} Submissions ({gradedCount} Evaluated)
                  </span>

                  <button
                    onClick={() => {
                      setSelectedAssignmentId(assign.id);
                      setActiveTab('SUBMISSIONS');
                    }}
                    className="text-xs font-bold text-purple-600 hover:text-purple-700"
                  >
                    View & Grade →
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {activeTab === 'SUBMISSIONS' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs p-6 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <span className="text-xs font-bold text-slate-400 block uppercase">Evaluating Assignment:</span>
              <h3 className="font-extrabold text-base text-slate-900">{selectedAssignment?.title}</h3>
              <p className="text-xs text-purple-700 font-semibold">
                Total Marks: {selectedAssignment?.totalMarks} • Due Date: {selectedAssignment?.dueDate}
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-slate-500">Switch Task:</span>
              <select
                value={selectedAssignmentId}
                onChange={(e) => setSelectedAssignmentId(e.target.value)}
                className="py-1.5 px-3 text-xs bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-800"
              >
                {myAssignments.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.title}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Submissions List */}
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3 px-4">Student</th>
                  <th className="py-3 px-4">Roll Number</th>
                  <th className="py-3 px-4">Submitted File</th>
                  <th className="py-3 px-4">Submission Date</th>
                  <th className="py-3 px-4">Score</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {assignmentSubmissions.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-slate-400">
                      No submissions uploaded for this task yet.
                    </td>
                  </tr>
                ) : (
                  assignmentSubmissions.map((subm) => (
                    <tr key={subm.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-4 font-bold text-slate-900">{subm.studentName}</td>
                      <td className="py-3 px-4 font-bold text-blue-700">{subm.rollNo}</td>
                      <td className="py-3 px-4">
                        <a
                          href={subm.fileUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="font-mono text-blue-600 underline font-semibold"
                        >
                          {subm.fileName}
                        </a>
                      </td>
                      <td className="py-3 px-4 text-slate-600">{subm.submittedAt}</td>
                      <td className="py-3 px-4">
                        {subm.marksObtained !== undefined ? (
                          <span className="font-extrabold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                            {subm.marksObtained} / {selectedAssignment?.totalMarks}
                          </span>
                        ) : (
                          <span className="text-amber-600 font-bold">Pending Review</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => {
                            setGradingSubmissionId(subm.id);
                            setGradeMarks(subm.marksObtained ?? 18);
                            setGradeFeedback(subm.feedback ?? '');
                          }}
                          className="px-3 py-1 text-xs font-bold text-white bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
                        >
                          {subm.status === 'Graded' ? 'Re-evaluate' : 'Grade Submission'}
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create Assignment Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-extrabold text-base text-slate-900">Create Academic Assignment</h3>
              <button onClick={() => setShowCreateModal(false)} className="p-1 text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Title *</label>
                <input
                  type="text"
                  required
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="e.g. Lab Exercise 3: B-Tree & Indexing Simulation"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Subject</label>
                  <select
                    value={form.subjectId}
                    onChange={(e) => setForm({ ...form, subjectId: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  >
                    {subjects.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name} ({s.code})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Max Marks</label>
                  <input
                    type="number"
                    value={form.totalMarks}
                    onChange={(e) => setForm({ ...form, totalMarks: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Submission Deadline</label>
                <input
                  type="date"
                  value={form.dueDate}
                  onChange={(e) => setForm({ ...form, dueDate: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                />
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Description & Guidelines</label>
                <textarea
                  rows={3}
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="State requirements, submission format, and rubric..."
                />
              </div>
              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-bold text-white bg-purple-600 hover:bg-purple-700 rounded-xl shadow-xs"
                >
                  Post Assignment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Grade Modal */}
      {gradingSubmissionId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-md w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-extrabold text-base text-slate-900">Score & Feedback</h3>
              <button onClick={() => setGradingSubmissionId(null)} className="p-1 text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleGrade} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">
                  Marks Awarded (out of {selectedAssignment?.totalMarks || 20}) *
                </label>
                <input
                  type="number"
                  min="0"
                  max={selectedAssignment?.totalMarks || 20}
                  required
                  value={gradeMarks}
                  onChange={(e) => setGradeMarks(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-900"
                />
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Faculty Evaluation Remarks</label>
                <textarea
                  rows={3}
                  value={gradeFeedback}
                  onChange={(e) => setGradeFeedback(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="Provide constructive feedback for student..."
                />
              </div>
              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setGradingSubmissionId(null)}
                  className="px-4 py-2 font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-bold text-white bg-purple-600 hover:bg-purple-700 rounded-xl shadow-xs"
                >
                  Submit Score
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
