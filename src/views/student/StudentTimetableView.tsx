import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { CalendarDays, Clock, User, Building } from 'lucide-react';

export const StudentTimetableView: React.FC = () => {
  const { timetable, students, subjects, faculty, currentUser } = useErp();

  const myStudent = students.find((s) => s.id === currentUser.id) || students[0];
  const [selectedDay, setSelectedDay] = useState<string>('Monday');

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] as const;
  const periods = [1, 2, 3, 4, 5];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Class Timetable & Lecture Schedule</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Weekly slot matrix for Batch {myStudent?.batch} • Semester {myStudent?.semesterNumber}
          </p>
        </div>

        <div className="flex items-center space-x-1.5 bg-slate-100 p-1 rounded-xl">
          {daysOfWeek.map((day) => (
            <button
              key={day}
              onClick={() => setSelectedDay(day)}
              className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-all ${
                selectedDay === day ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-200'
              }`}
            >
              {day.slice(0, 3)}
            </button>
          ))}
        </div>
      </div>

      {/* Selected Day View */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs space-y-4">
        <h3 className="text-base font-extrabold text-slate-900 flex items-center space-x-2">
          <CalendarDays className="w-5 h-5 text-blue-600" />
          <span>{selectedDay}'s Class Schedule</span>
        </h3>

        <div className="space-y-3">
          {periods.map((periodNum) => {
            const slot = timetable.find(
              (t) => t.divisionId === myStudent?.divisionId && t.dayOfWeek === selectedDay && t.period === periodNum
            );
            const sub = subjects.find((s) => s.id === slot?.subjectId);
            const fac = faculty.find((f) => f.id === slot?.facultyId);

            return (
              <div
                key={periodNum}
                className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                  slot
                    ? sub?.type === 'Practical'
                      ? 'bg-amber-50/60 border-amber-200'
                      : 'bg-blue-50/60 border-blue-200'
                    : 'bg-slate-50/50 border-slate-200'
                }`}
              >
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 rounded-xl bg-white border border-slate-200 text-slate-900 flex flex-col items-center justify-center font-extrabold shadow-2xs flex-shrink-0">
                    <span className="text-xs text-blue-600">P{periodNum}</span>
                    <span className="text-[9px] text-slate-400 font-semibold">{slot?.startTime || '09:00'}</span>
                  </div>

                  <div>
                    {slot ? (
                      <>
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-xs font-bold text-blue-700 bg-white px-2 py-0.5 rounded border border-blue-200">
                            {sub?.code}
                          </span>
                          <h4 className="font-bold text-sm text-slate-900">{sub?.name}</h4>
                        </div>
                        <p className="text-xs text-slate-600 mt-1 flex items-center space-x-3">
                          <span>Instructor: <strong>{fac?.fullName}</strong></span>
                          <span>•</span>
                          <span>Room: <strong>{slot.roomNumber}</strong></span>
                        </p>
                      </>
                    ) : (
                      <div className="text-xs font-semibold text-slate-400 italic">
                        Free Period / Self Study / Library
                      </div>
                    )}
                  </div>
                </div>

                {slot && (
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-white text-slate-700 border border-slate-200 self-start sm:self-auto">
                    {sub?.type} Lecture
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
