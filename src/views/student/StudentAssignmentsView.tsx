import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { FileText, Upload, CheckCircle2, Clock, Calendar, AlertCircle, Award, X } from 'lucide-react';
import { Assignment } from '../../types';

export const StudentAssignmentsView: React.FC = () => {
  const { assignments, submissions, subjects, currentUser, students, submitAssignment } = useErp();

  const myStudent = students.find((s) => s.id === currentUser.id) || students[0];
  const myAssignments = assignments.filter((a) => a.divisionId === myStudent?.divisionId);

  // Upload modal state
  const [submittingAssignId, setSubmittingAssignId] = useState<string | null>(null);
  const [fileName, setFileName] = useState('Rahul_Verma_Assignment_Solution.pdf');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!submittingAssignId) return;

    submitAssignment({
      assignmentId: submittingAssignId,
      studentId: myStudent.id,
      rollNo: myStudent.rollNo,
      studentName: myStudent.fullName,
      submittedAt: new Date().toISOString().split('T')[0],
      fileUrl: 'https://apex.edu/submissions/rahul_solution.pdf',
      fileName: fileName,
      status: 'Submitted',
    });

    setSubmittingAssignId(null);
    alert('Assignment solution submitted successfully to instructor for grading!');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Assignments & Lab Exercises</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Submit coursework solutions, review faculty evaluations, and inspect awarded scores
          </p>
        </div>
      </div>

      {/* Assignments List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {myAssignments.map((assign) => {
          const sub = subjects.find((s) => s.id === assign.subjectId);
          const mySubmission = submissions.find(
            (s) => s.assignmentId === assign.id && s.studentId === myStudent.id
          );

          const isSubmitted = !!mySubmission;
          const isGraded = mySubmission?.status === 'Graded';

          return (
            <div
              key={assign.id}
              className={`bg-white rounded-2xl border p-5 shadow-2xs flex flex-col justify-between transition-all ${
                isGraded ? 'border-emerald-200' : isSubmitted ? 'border-blue-200' : 'border-slate-200'
              }`}
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                    {sub?.code}
                  </span>
                  <span className="text-xs font-bold text-slate-500">Max: {assign.totalMarks} Marks</span>
                </div>

                <h4 className="font-extrabold text-sm text-slate-900 mt-2.5">{assign.title}</h4>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">{assign.description}</p>

                <div className="mt-4 bg-slate-50 p-3 rounded-xl space-y-1 text-xs text-slate-600">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Assigned Date:</span>
                    <span>{assign.assignedDate}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400 font-bold text-rose-600">Submission Due:</span>
                    <span className="font-bold text-rose-600">{assign.dueDate}</span>
                  </div>
                </div>

                {/* Feedback Box if Graded */}
                {isGraded && (
                  <div className="mt-3 bg-emerald-50 border border-emerald-200 p-3 rounded-xl space-y-1 text-xs text-emerald-900">
                    <div className="flex justify-between items-center font-bold">
                      <span>Evaluated Score:</span>
                      <span className="text-sm">
                        {mySubmission.marksObtained} / {assign.totalMarks} Marks
                      </span>
                    </div>
                    {mySubmission.feedback && (
                      <p className="text-[11px] text-emerald-800 pt-1 border-t border-emerald-200">
                        Instructor Feedback: <em>"{mySubmission.feedback}"</em>
                      </p>
                    )}
                  </div>
                )}
              </div>

              {/* Action Button */}
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                {isGraded ? (
                  <span className="inline-flex items-center space-x-1 text-xs font-bold text-emerald-700">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Graded</span>
                  </span>
                ) : isSubmitted ? (
                  <span className="inline-flex items-center space-x-1 text-xs font-bold text-blue-700">
                    <Clock className="w-4 h-4" />
                    <span>Submitted (Awaiting Grade)</span>
                  </span>
                ) : (
                  <button
                    onClick={() => {
                      setSubmittingAssignId(assign.id);
                      setFileName(`${myStudent.fullName.replace(' ', '_')}_Assignment.pdf`);
                    }}
                    className="px-4 py-1.5 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs transition-colors flex items-center space-x-1.5"
                  >
                    <Upload className="w-3.5 h-3.5" />
                    <span>Submit Work</span>
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Submit Assignment Modal */}
      {submittingAssignId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-md w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-extrabold text-base text-slate-900">Upload Assignment Solution</h3>
              <button onClick={() => setSubmittingAssignId(null)} className="p-1 text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Attached Solution File</label>
                <input
                  type="text"
                  required
                  value={fileName}
                  onChange={(e) => setFileName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-mono text-slate-900"
                />
              </div>

              <div className="border-2 border-dashed border-slate-200 p-6 rounded-2xl text-center space-y-2 bg-slate-50">
                <FileText className="w-8 h-8 text-blue-600 mx-auto" />
                <p className="font-bold text-slate-800">PDF, ZIP, or DOC file selected</p>
                <p className="text-[10px] text-slate-400">File ready for upload to university LMS</p>
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setSubmittingAssignId(null)}
                  className="px-4 py-2 font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs"
                >
                  Confirm & Submit
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
