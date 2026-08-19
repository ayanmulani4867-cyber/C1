import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { CertificateRequest } from '../../types';
import { Award, CheckCircle2, XCircle, Printer, Eye, Sparkles, Clock, FileText } from 'lucide-react';

interface CertificatesDeskViewProps {
  onOpenCertificate: (certificate: CertificateRequest) => void;
}

export const CertificatesDeskView: React.FC<CertificatesDeskViewProps> = ({ onOpenCertificate }) => {
  const { certificates, updateCertificateStatus } = useErp();

  const [filterStatus, setFilterStatus] = useState<'ALL' | 'Pending' | 'Approved' | 'Issued' | 'Rejected'>('ALL');

  const filteredCertificates = certificates.filter((c) => {
    return filterStatus === 'ALL' || c.status === filterStatus;
  });

  const handleIssue = (cert: CertificateRequest) => {
    const certNum = `AITS/CERT/${new Date().getFullYear()}/${Math.floor(1000 + Math.random() * 9000)}`;
    updateCertificateStatus(cert.id, 'Issued', certNum);
    alert(`Certificate #${certNum} generated & issued to ${cert.studentName}!`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Certificate Generation & Issuance Desk</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Issue official Bonafide, Character, NOC, and Course Completion certificates with digital seals
          </p>
        </div>

        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value as any)}
          className="py-1.5 px-3 text-xs bg-white border border-slate-200 rounded-xl font-bold text-slate-700 shadow-2xs self-start sm:self-auto"
        >
          <option value="ALL">All Certificates</option>
          <option value="Pending">Pending Applications</option>
          <option value="Issued">Issued & Verified</option>
        </select>
      </div>

      {/* Grid of Certificates */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredCertificates.map((cert) => {
          const isIssued = cert.status === 'Issued';
          const isPending = cert.status === 'Pending';

          return (
            <div
              key={cert.id}
              className={`bg-white rounded-2xl border p-5 shadow-2xs flex flex-col justify-between transition-all ${
                isPending ? 'border-blue-300 ring-2 ring-blue-500/10' : 'border-slate-200'
              }`}
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Award className="w-5 h-5 text-amber-600" />
                    <span className="font-extrabold text-sm text-slate-900">{cert.certificateType}</span>
                  </div>

                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold ${
                      isIssued
                        ? 'bg-emerald-100 text-emerald-800'
                        : cert.status === 'Rejected'
                        ? 'bg-rose-100 text-rose-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {cert.status}
                  </span>
                </div>

                <div className="mt-3">
                  <h4 className="font-bold text-sm text-slate-900">{cert.studentName}</h4>
                  <p className="text-xs text-blue-700 font-semibold">
                    Roll No: {cert.rollNo} • {cert.departmentName}
                  </p>
                </div>

                <div className="mt-3 p-3 bg-slate-50 rounded-xl space-y-1.5 text-xs text-slate-700">
                  <div>
                    <span className="text-slate-400 font-medium">Application Purpose:</span>{' '}
                    <span className="text-slate-800 font-semibold">{cert.purpose}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium">Applied On:</span>{' '}
                    <span className="text-slate-600">{cert.appliedDate}</span>
                  </div>
                  {cert.certificateNumber && (
                    <div className="pt-1 border-t border-slate-200 text-emerald-700 font-mono font-bold text-[11px]">
                      Cert ID: {cert.certificateNumber}
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end space-x-2 pt-4 mt-3 border-t border-slate-100">
                {isIssued ? (
                  <button
                    onClick={() => onOpenCertificate(cert)}
                    className="px-4 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs flex items-center space-x-1.5 transition-colors"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>View / Print Certificate</span>
                  </button>
                ) : (
                  <>
                    <button
                      onClick={() => updateCertificateStatus(cert.id, 'Rejected')}
                      className="px-3 py-1.5 text-xs font-bold text-rose-600 hover:bg-rose-50 border border-rose-200 rounded-xl transition-colors"
                    >
                      Reject
                    </button>
                    <button
                      onClick={() => handleIssue(cert)}
                      className="px-4 py-1.5 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-xs flex items-center space-x-1.5 transition-colors"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Issue Certificate</span>
                    </button>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
