import React from 'react';
import { CertificateRequest, Student } from '../types';
import { X, Printer, Download, Award, ShieldCheck, CheckCircle2 } from 'lucide-react';

interface CertificateModalProps {
  certificate: CertificateRequest;
  student?: Student;
  isOpen: boolean;
  onClose: () => void;
}

export const CertificateModal: React.FC<CertificateModalProps> = ({
  certificate,
  student,
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  const certNumber = certificate.certificateNumber || 'AITS/CERT/2026/0412';
  const issueDate = certificate.issuedDate || new Date().toISOString().split('T')[0];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/75 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-2xl w-full overflow-hidden animate-in zoom-in-95 duration-150">
        {/* Modal Top Bar */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50">
          <div className="flex items-center space-x-2">
            <Award className="w-5 h-5 text-amber-600" />
            <h3 className="font-extrabold text-sm text-slate-900">
              Institutional Certificate Preview
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Certificate Paper */}
        <div className="p-8 bg-slate-100 flex justify-center">
          <div
            id="printable-certificate"
            className="w-full bg-white p-8 rounded-xl shadow-lg border-8 border-double border-amber-800/30 relative text-slate-900"
            style={{
              backgroundImage: 'radial-gradient(circle at center, rgba(251, 191, 36, 0.03) 0%, rgba(255,255,255,1) 100%)',
            }}
          >
            {/* Watermark */}
            <div className="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none select-none">
              <Award className="w-96 h-96 text-slate-900" />
            </div>

            {/* Certificate Header */}
            <div className="text-center border-b-2 border-amber-900/40 pb-4">
              <div className="flex items-center justify-center space-x-2 mb-1">
                <div className="w-8 h-8 rounded-full bg-blue-900 text-white flex items-center justify-center font-bold text-xs">
                  AITS
                </div>
                <h1 className="text-xl font-extrabold tracking-tight text-blue-950 uppercase font-serif">
                  Apex Institute of Technology & Science
                </h1>
              </div>
              <p className="text-[11px] text-slate-600 uppercase tracking-widest font-medium">
                Accredited by National Board of Accreditation • Established 1996
              </p>
              <p className="text-[10px] text-slate-500 mt-0.5">
                Campus: Silicon Highway, Tech Corridor, California • www.apex.edu
              </p>
            </div>

            {/* Reference & Date */}
            <div className="flex justify-between items-center text-xs font-mono text-slate-600 my-4 px-2">
              <span>Ref No: <strong>{certNumber}</strong></span>
              <span>Date: <strong>{issueDate}</strong></span>
            </div>

            {/* Title */}
            <div className="text-center my-6">
              <h2 className="text-xl font-bold uppercase tracking-wide text-amber-950 font-serif border-b inline-block px-6 pb-1 border-amber-600">
                {certificate.certificateType}
              </h2>
            </div>

            {/* Body */}
            <div className="px-4 text-sm leading-relaxed text-slate-800 space-y-4 font-serif text-justify">
              <p>
                This is to certify that <strong>{certificate.studentName}</strong>, bearing Roll Number{' '}
                <strong>{certificate.rollNo}</strong> and Enrollment ID{' '}
                <strong>{student?.enrollmentNo || 'EN23CSE00101'}</strong>, is a bonafide student of this institution,
                currently enrolled in the Department of <strong>{certificate.departmentName}</strong> for the 4-year
                degree program in <strong>Bachelor of Technology (Computer Science)</strong> (Batch: {student?.batch || '2023-2027'}).
              </p>

              <p>
                According to the records maintained by the university, their conduct and character have been found to be{' '}
                <strong>Exemplary</strong>.
              </p>

              <p>
                This certificate is being issued on their formal request for the specific purpose of:{' '}
                <em>"{certificate.purpose}"</em>.
              </p>
            </div>

            {/* Signatures & Seal */}
            <div className="mt-12 pt-6 flex items-end justify-between px-6 border-t border-slate-200">
              <div className="text-center">
                <div className="w-20 h-20 rounded-full border-2 border-dashed border-amber-800/40 flex items-center justify-center p-1 mx-auto text-[9px] font-bold text-amber-900 uppercase">
                  Institutional Seal
                </div>
              </div>

              <div className="text-center">
                <p className="font-serif italic text-base font-bold text-blue-950">Arthur Sterling</p>
                <div className="w-36 border-b border-slate-900 my-1" />
                <p className="text-xs font-bold text-slate-800">Head of Department</p>
                <p className="text-[10px] text-slate-500">Dept of Computer Science</p>
              </div>

              <div className="text-center">
                <p className="font-serif italic text-base font-bold text-blue-950">Dr. Robert Vance</p>
                <div className="w-36 border-b border-slate-900 my-1" />
                <p className="text-xs font-bold text-slate-800">Registrar & Director</p>
                <p className="text-[10px] text-slate-500">Apex Institute of Tech</p>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Actions */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs text-emerald-700 font-semibold">
            <CheckCircle2 className="w-4 h-4" />
            <span>Digitally Verified & Stamped</span>
          </div>
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
              <span>Print Official Certificate</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
