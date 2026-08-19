import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { CalendarDays, Clock, Building, User, Layers, Filter } from 'lucide-react';

export const TimetableManagerView: React.FC = () => {
  const { timetable, divisions, subjects, faculty } = useErp();

  const [selectedDivisionId, setSelectedDivisionId] = useState<string>(divisions[0]?.id || 'div-cse-4a');

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] as const;
  const periods = [1, 2, 3, 4, 5];

  const currentDiv = divisions.find((d) => d.id === selectedDivisionId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Institutional Timetable & Scheduling</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Slot matrix, faculty workloads, and classroom allocations
          </p>
        </div>

        {/* Division Selector */}
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold text-slate-500">Section:</span>
          <select
            value={selectedDivisionId}
            onChange={(e) => setSelectedDivisionId(e.target.value)}
            className="py-2 px-3 text-xs bg-white border border-slate-200 rounded-xl font-bold text-blue-700 shadow-2xs focus:outline-none"
          >
            {divisions.map((div) => (
              <option key={div.id} value={div.id}>
                {div.name} ({div.code}) • Room {div.roomNumber}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Class Meta Banner */}
      <div className="bg-gradient-to-r from-blue-900 to-indigo-900 text-white p-5 rounded-2xl shadow-md flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-white/20 text-blue-100 border border-white/20">
            Active Schedule
          </span>
          <h3 className="text-lg font-bold text-white mt-1">
            {currentDiv?.name} — Master Timetable
          </h3>
          <p className="text-xs text-blue-200 mt-0.5">
            Default Lecture Room: <strong>{currentDiv?.roomNumber}</strong> • Academic Year 2025–2026
          </p>
        </div>

        <div className="flex items-center space-x-4 text-xs font-semibold">
          <div className="bg-white/10 px-3 py-1.5 rounded-xl border border-white/10 text-center">
            <span className="block text-sm font-extrabold">5</span>
            <span className="text-[10px] text-blue-200">Periods / Day</span>
          </div>
          <div className="bg-white/10 px-3 py-1.5 rounded-xl border border-white/10 text-center">
            <span className="block text-sm font-extrabold">25</span>
            <span className="text-[10px] text-blue-200">Weekly Slots</span>
          </div>
        </div>
      </div>

      {/* Timetable Grid Matrix */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                <th className="py-3 px-4 w-32 border-r border-slate-200">Day / Period</th>
                <th className="py-3 px-4 border-r border-slate-200">
                  <div>Period 1</div>
                  <span className="text-[10px] text-slate-400 font-normal">09:00 - 09:55 AM</span>
                </th>
                <th className="py-3 px-4 border-r border-slate-200">
                  <div>Period 2</div>
                  <span className="text-[10px] text-slate-400 font-normal">10:00 - 10:55 AM</span>
                </th>
                <th className="py-3 px-4 border-r border-slate-200">
                  <div>Period 3</div>
                  <span className="text-[10px] text-slate-400 font-normal">11:15 - 12:10 PM</span>
                </th>
                <th className="py-3 px-4 border-r border-slate-200">
                  <div>Period 4</div>
                  <span className="text-[10px] text-slate-400 font-normal">01:00 - 01:55 PM</span>
                </th>
                <th className="py-3 px-4">
                  <div>Period 5</div>
                  <span className="text-[10px] text-slate-400 font-normal">02:00 - 02:55 PM</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {daysOfWeek.map((day) => (
                <tr key={day} className="hover:bg-slate-50/60 transition-colors">
                  <td className="py-4 px-4 font-bold text-slate-900 bg-slate-50/50 border-r border-slate-200">
                    {day}
                  </td>
                  {periods.map((periodNum) => {
                    const slot = timetable.find(
                      (t) => t.divisionId === selectedDivisionId && t.dayOfWeek === day && t.period === periodNum
                    );
                    const sub = subjects.find((s) => s.id === slot?.subjectId);
                    const fac = faculty.find((f) => f.id === slot?.facultyId);

                    return (
                      <td key={periodNum} className="p-2 border-r border-slate-100 align-top">
                        {slot ? (
                          <div className={`p-2.5 rounded-xl border transition-all ${
                            sub?.type === 'Practical'
                              ? 'bg-amber-50/70 border-amber-200/80 text-amber-950'
                              : 'bg-blue-50/70 border-blue-200/80 text-blue-950'
                          }`}>
                            <div className="flex items-center justify-between">
                              <span className="font-mono font-bold text-[10px] text-blue-700">
                                {sub?.code}
                              </span>
                              <span className="text-[9px] font-semibold text-slate-500 bg-white/70 px-1 rounded">
                                {slot.roomNumber}
                              </span>
                            </div>
                            <h5 className="font-bold text-[11px] mt-1 text-slate-900 line-clamp-1">
                              {sub?.name || 'Class Subject'}
                            </h5>
                            <p className="text-[10px] text-slate-600 mt-1 flex items-center space-x-1">
                              <User className="w-2.5 h-2.5 text-slate-400" />
                              <span className="truncate">{fac?.fullName || 'Faculty'}</span>
                            </p>
                          </div>
                        ) : (
                          <div className="p-3 text-center text-slate-300 font-medium text-[11px] bg-slate-50/30 rounded-xl border border-dashed border-slate-200">
                            Free Slot
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
