import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { Award, TrendingUp, BookOpen, CheckCircle2, FileText, Printer } from 'lucide-react';

export const StudentResultsView: React.FC = () => {
  const { students, subjects, exams, marks, currentUser } = useErp();

  const myStudent = students.find((s) => s.id === currentUser.id) || students[0];
  const [selectedSemester, setSelectedSemester] = useState<number>(myStudent?.semesterNumber || 4);

  // Filter marks for this student
  const myMarks = marks.filter((m) => m.studentId === myStudent?.id);

  // Group marks by exam
  const examResults = exams.map((exam) => {
    const examMarks = myMarks.filter((m) => m.examId === exam.id);
    return {
      exam,
      marks: examMarks,
    };
  });

  const handlePrintGradeCard = () => {
    window.print();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Academic Grade Cards & Results</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Semester-wise performance, SGPA, credits earned, and university evaluation breakdown
          </p>
        </div>

        <button
          onClick={handlePrintGradeCard}
          className="px-4 py-2 text-xs font-bold text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 rounded-xl shadow-xs transition-colors flex items-center space-x-1.5 self-start sm:self-auto"
        >
          <Printer className="w-4 h-4" />
          <span>Print Transcript</span>
        </button>
      </div>

      {/* Overview CGPA Card */}
      <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 rounded-3xl p-6 text-white shadow-lg grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="flex items-center space-x-4">
          <div className="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center font-extrabold text-blue-300">
            <Award className="w-7 h-7" />
          </div>
          <div>
            <span className="text-xs text-blue-200 uppercase font-bold tracking-wider">Cumulative GPA</span>
            <h3 className="text-3xl font-extrabold">{myStudent?.cgpa.toFixed(2)} / 10.0</h3>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center font-extrabold text-emerald-300">
            <TrendingUp className="w-7 h-7" />
          </div>
          <div>
            <span className="text-xs text-blue-200 uppercase font-bold tracking-wider">Latest SGPA</span>
            <h3 className="text-3xl font-extrabold">9.10 / 10.0</h3>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center font-extrabold text-amber-300">
            <CheckCircle2 className="w-7 h-7" />
          </div>
          <div>
            <span className="text-xs text-blue-200 uppercase font-bold tracking-wider">Total Credits Earned</span>
            <h3 className="text-3xl font-extrabold">84 Credits</h3>
          </div>
        </div>
      </div>

      {/* Detailed Marks Cards by Exam */}
      <div className="space-y-6">
        {examResults.map(({ exam, marks }) => (
          <div key={exam.id} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-2xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-blue-50 text-blue-800 border border-blue-200 uppercase">
                  {exam.examType}
                </span>
                <h3 className="font-extrabold text-base text-slate-900 mt-1">{exam.title}</h3>
                <p className="text-xs text-slate-500">
                  Academic Year: {exam.academicYear} • Weightage: {exam.weightagePercentage}%
                </p>
              </div>

              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-xl border border-emerald-200">
                Grade: A+ (Passed)
              </span>
            </div>

            {/* Marks Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="py-2.5 px-4">Subject</th>
                    <th className="py-2.5 px-4">Subject Code</th>
                    <th className="py-2.5 px-4 text-center">Max Marks</th>
                    <th className="py-2.5 px-4 text-center">Marks Scored</th>
                    <th className="py-2.5 px-4 text-center">Letter Grade</th>
                    <th className="py-2.5 px-4 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {subjects.map((sub) => {
                    const markEntry = marks.find((m) => m.subjectId === sub.id);
                    const scored = markEntry?.marksObtained ?? 88;
                    const maxMarks = markEntry?.maxMarks ?? exam.maxMarks;
                    const grade = markEntry?.gradeLetter ?? 'A';

                    return (
                      <tr key={sub.id} className="hover:bg-slate-50 transition-colors">
                        <td className="py-3 px-4 font-bold text-slate-900">{sub.name}</td>
                        <td className="py-3 px-4 font-mono font-bold text-blue-700">{sub.code}</td>
                        <td className="py-3 px-4 text-center text-slate-600 font-semibold">{maxMarks}</td>
                        <td className="py-3 px-4 text-center font-extrabold text-slate-900">{scored}</td>
                        <td className="py-3 px-4 text-center">
                          <span className="px-2 py-0.5 rounded font-extrabold text-xs bg-purple-50 text-purple-700 border border-purple-200">
                            {grade}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right font-bold text-emerald-700">PASS</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
