import React, { useState } from 'react';
import { Student, Faculty } from '../types';
import { X, Printer, Download, Sparkles, ShieldCheck, QrCode, Phone, Mail, MapPin, Building, Calendar } from 'lucide-react';

interface IdCardModalProps {
  student?: Student;
  faculty?: Faculty;
  departmentName?: string;
  courseName?: string;
  isOpen: boolean;
  onClose: () => void;
}

export const IdCardModal: React.FC<IdCardModalProps> = ({
  student,
  faculty,
  departmentName = 'Computer Science & Engineering',
  courseName = 'Bachelor of Technology',
  isOpen,
  onClose,
}) => {
  const [side, setSide] = useState<'FRONT' | 'BACK'>('FRONT');

  if (!isOpen) return null;

  const isStudent = !!student;
  const personName = student?.fullName || faculty?.fullName || 'Academic Member';
  const personId = student?.studentId || faculty?.facultyId || 'ID-0000';
  const rollOrEmp = student?.rollNo || faculty?.employeeId || 'REF-001';
  const photo = student?.photo || faculty?.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200';
  const blood = student?.bloodGroup || faculty?.bloodGroup || 'O+';
  const email = student?.collegeEmail || faculty?.officialEmail || 'info@apex.edu';
  const mobile = student?.mobile || faculty?.mobile || '+1 (555) 000-0000';
  const validity = isStudent ? '2023 - 2027' : 'PERMANENT';

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-lg w-full overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-blue-600" />
            <h3 className="font-extrabold text-sm text-slate-900">
              Official Digital Identity Card
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* View Toggle */}
        <div className="px-6 pt-4 flex items-center justify-center space-x-2">
          <button
            onClick={() => setSide('FRONT')}
            className={`px-4 py-1.5 text-xs font-bold rounded-xl transition-all ${
              side === 'FRONT'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Front Side
          </button>
          <button
            onClick={() => setSide('BACK')}
            className={`px-4 py-1.5 text-xs font-bold rounded-xl transition-all ${
              side === 'BACK'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Back Side
          </button>
        </div>

        {/* Printable PVC ID Card Preview */}
        <div className="p-6 flex justify-center">
          <div
            id="printable-id-card"
            className="w-80 h-[480px] rounded-2xl shadow-xl overflow-hidden border border-slate-300 relative flex flex-col justify-between bg-white select-none transition-all"
            style={{
              backgroundImage: 'radial-gradient(circle at 100% 0%, rgba(37,99,235,0.05) 0%, rgba(255,255,255,1) 70%)',
            }}
          >
            {side === 'FRONT' ? (
              <>
                {/* ID Card Header */}
                <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-blue-800 text-white p-3.5 text-center relative overflow-hidden">
                  <div className="absolute -right-6 -bottom-6 w-20 h-20 bg-blue-500/20 rounded-full blur-sm" />
                  <p className="text-[9px] font-extrabold tracking-widest text-blue-200 uppercase">
                    Apex Institute of Technology
                  </p>
                  <p className="text-[12px] font-extrabold tracking-tight text-white mt-0.5">
                    CAMPUS IDENTITY CARD
                  </p>
                  <span className="inline-block mt-1 px-2 py-0.5 text-[8px] font-bold uppercase tracking-wider rounded bg-white/20 text-white border border-white/30">
                    {isStudent ? 'STUDENT' : 'FACULTY'}
                  </span>
                </div>

                {/* Photo & Hologram */}
                <div className="px-4 pt-4 flex flex-col items-center">
                  <div className="relative">
                    <img
                      src={photo}
                      alt={personName}
                      className="w-24 h-28 object-cover rounded-xl border-2 border-blue-600 shadow-md"
                    />
                    <div className="absolute -bottom-2 -right-2 bg-amber-400 text-amber-950 p-1 rounded-full shadow border border-white">
                      <ShieldCheck className="w-3.5 h-3.5" />
                    </div>
                  </div>

                  {/* Name & Role */}
                  <h4 className="mt-3 font-extrabold text-sm text-slate-900 text-center leading-tight">
                    {personName}
                  </h4>
                  <p className="text-[10px] font-bold text-blue-700 mt-0.5">
                    {isStudent ? `Roll No: ${rollOrEmp}` : faculty?.designation}
                  </p>
                </div>

                {/* Details Table */}
                <div className="px-5 py-2 space-y-1 text-[11px] text-slate-700">
                  <div className="flex justify-between border-b border-slate-100 py-0.5">
                    <span className="text-slate-400 font-medium">ID Number:</span>
                    <span className="font-bold text-slate-900">{personId}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-100 py-0.5">
                    <span className="text-slate-400 font-medium">Department:</span>
                    <span className="font-semibold text-slate-900 truncate max-w-[150px]">{departmentName}</span>
                  </div>
                  {isStudent && (
                    <div className="flex justify-between border-b border-slate-100 py-0.5">
                      <span className="text-slate-400 font-medium">Batch / Sem:</span>
                      <span className="font-semibold text-slate-900">{student?.batch} (Sem {student?.semesterNumber})</span>
                    </div>
                  )}
                  <div className="flex justify-between border-b border-slate-100 py-0.5">
                    <span className="text-slate-400 font-medium">Blood Group:</span>
                    <span className="font-bold text-rose-600">{blood}</span>
                  </div>
                  <div className="flex justify-between py-0.5">
                    <span className="text-slate-400 font-medium">Validity:</span>
                    <span className="font-semibold text-slate-900">{validity}</span>
                  </div>
                </div>

                {/* Barcode & Signature */}
                <div className="px-5 pb-3 pt-1 border-t border-slate-100 flex items-center justify-between bg-slate-50/80">
                  <div className="flex flex-col">
                    {/* Simulated Barcode */}
                    <div className="flex items-center space-x-[2px] h-6">
                      {[12, 18, 8, 22, 14, 20, 10, 16, 24, 8, 18, 14, 22, 10, 16, 12, 20, 14, 8, 18].map((h, i) => (
                        <div
                          key={i}
                          className="w-[2px] bg-slate-800"
                          style={{ height: `${h}px` }}
                        />
                      ))}
                    </div>
                    <span className="text-[8px] font-mono text-slate-500 mt-0.5 tracking-wider">{personId}</span>
                  </div>

                  <div className="text-right">
                    <div className="font-serif italic text-[11px] text-blue-950 font-bold border-b border-slate-400 pb-0.5 px-1">
                      Robert Vance
                    </div>
                    <span className="text-[7px] uppercase font-bold text-slate-400 tracking-wider">
                      Registrar Sign
                    </span>
                  </div>
                </div>
              </>
            ) : (
              <>
                {/* Back Side */}
                <div className="bg-slate-900 text-white p-3 text-center">
                  <p className="text-[9px] font-extrabold tracking-widest text-slate-400 uppercase">
                    Institutional Terms & Emergency
                  </p>
                </div>

                <div className="p-4 space-y-3 flex-1 flex flex-col justify-between">
                  <div className="space-y-2 text-[10px] text-slate-600 leading-relaxed">
                    <p>• This identity card is property of Apex Institute of Technology & Science.</p>
                    <p>• Must be produced upon demand by security and academic personnel.</p>
                    <p>• If lost or found, please return to the Office of the Registrar, Admin Block.</p>
                  </div>

                  {/* Contact info */}
                  <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200 space-y-1 text-[10px]">
                    <div className="flex items-center space-x-1.5 text-slate-700">
                      <Phone className="w-3 h-3 text-blue-600" />
                      <span>{mobile}</span>
                    </div>
                    <div className="flex items-center space-x-1.5 text-slate-700">
                      <Mail className="w-3 h-3 text-blue-600" />
                      <span className="truncate">{email}</span>
                    </div>
                    <div className="flex items-start space-x-1.5 text-slate-700">
                      <MapPin className="w-3 h-3 text-blue-600 flex-shrink-0 mt-0.5" />
                      <span className="truncate">Apex Campus, Silicon Highway, CA</span>
                    </div>
                  </div>

                  {/* QR Code */}
                  <div className="flex items-center justify-center flex-col pt-1">
                    <div className="p-2 bg-white rounded-xl border border-slate-200 shadow-2xs">
                      {/* SVG QR Code Simulation */}
                      <svg className="w-16 h-16 text-slate-900" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M2 2h8v8H2V2zm2 2v4h4V4H4zm-2 10h8v8H2v-8zm2 2v4h4v-4H4zm10-14h8v8h-8V2zm2 2v4h4V4h-4zm2 10h-2v2h2v-2zm-2 4h2v2h-2v-2zm4-4h2v4h-2v-4zm0 6h2v2h-2v-2zm-6-2h2v2h-2v-2zm2-2h2v2h-2v-2z" />
                      </svg>
                    </div>
                    <span className="text-[8px] font-mono text-slate-400 mt-1">Scan for verification</span>
                  </div>
                </div>

                <div className="bg-blue-900 text-blue-200 text-center py-1.5 text-[8px] font-semibold">
                  www.apex.edu • helpdesk@apex.edu
                </div>
              </>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
          <span className="text-xs text-slate-500">Official Secure ID Pass</span>
          <div className="flex items-center space-x-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-100 border border-slate-200 rounded-xl transition-colors"
            >
              Close
            </button>
            <button
              onClick={handlePrint}
              className="px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs flex items-center space-x-1.5 transition-colors"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print ID Card</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
