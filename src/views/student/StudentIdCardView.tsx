import React from 'react';
import { useErp } from '../../context/ErpContext';
import { Sparkles, Printer, Download, QrCode, ShieldCheck } from 'lucide-react';

interface StudentIdCardViewProps {
  onOpenModal: () => void;
}

export const StudentIdCardView: React.FC<StudentIdCardViewProps> = ({ onOpenModal }) => {
  const { currentUser, students, divisions } = useErp();
  const myStudent = students.find((s) => s.id === currentUser.id) || students[0];
  const myDivision = divisions.find((d) => d.id === myStudent?.divisionId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Digital Student Identity Card</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            RFID & QR enabled official university student identification card
          </p>
        </div>

        <button
          onClick={onOpenModal}
          className="px-5 py-2.5 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-md transition-all flex items-center space-x-2 self-start sm:self-auto"
        >
          <Printer className="w-4 h-4" />
          <span>Generate / Print PVC Card</span>
        </button>
      </div>

      {/* Interactive Card Presentation */}
      <div className="flex justify-center p-6">
        <div className="w-full max-w-sm bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 rounded-3xl p-6 text-white shadow-2xl border border-blue-400/30 relative overflow-hidden space-y-6">
          <div className="absolute -right-12 -top-12 w-48 h-48 bg-blue-500/20 rounded-full blur-2xl" />

          {/* Header */}
          <div className="flex items-center space-x-3 border-b border-blue-800/60 pb-4">
            <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-black text-base shadow">
              A
            </div>
            <div>
              <h3 className="font-black text-sm tracking-wide">APEX INSTITUTE</h3>
              <p className="text-[10px] text-blue-300 font-semibold tracking-wider uppercase">
                Technology & Science • Student ID
              </p>
            </div>
          </div>

          {/* Body */}
          <div className="flex items-center space-x-4">
            <img
              src={myStudent.photo}
              alt=""
              className="w-24 h-28 rounded-2xl object-cover ring-2 ring-blue-400 shadow-md"
            />
            <div className="space-y-1">
              <h4 className="font-extrabold text-base text-white">{myStudent.fullName}</h4>
              <p className="text-xs font-mono font-bold text-blue-300">{myStudent.rollNo}</p>
              <p className="text-[11px] text-slate-300 font-medium">B.Tech - Computer Science</p>
              <p className="text-[11px] text-slate-300 font-medium">Batch {myStudent.batch} • Sem {myStudent.semesterNumber}</p>
              <span className="inline-block mt-1 px-2 py-0.5 rounded text-[9px] font-extrabold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                STATUS: ACTIVE
              </span>
            </div>
          </div>

          {/* Footer Bar */}
          <div className="pt-4 border-t border-blue-800/60 flex items-center justify-between text-[10px] text-slate-400">
            <div>
              <span className="block text-slate-500">VALID THRU:</span>
              <strong className="text-slate-200">MAY 2028</strong>
            </div>
            <div>
              <span className="block text-slate-500">BLOOD GROUP:</span>
              <strong className="text-slate-200">{myStudent.bloodGroup || 'O+'}</strong>
            </div>
            <div className="w-10 h-10 bg-white rounded-lg p-1 flex items-center justify-center">
              <QrCode className="w-full h-full text-slate-900" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
