import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { FileCheck2, Award, ShieldAlert, Plus, CheckCircle2, Clock, X, Eye } from 'lucide-react';
import { LeaveApplication, CertificateRequest, GrievanceTicket } from '../../types';

interface StudentServicesViewProps {
  onOpenCertificate: (certificate: CertificateRequest) => void;
}

export const StudentServicesView: React.FC<StudentServicesViewProps> = ({ onOpenCertificate }) => {
  const {
    currentUser,
    students,
    leaves,
    certificates,
    grievances,
    applyForLeave,
    requestCertificate,
    fileGrievance,
  } = useErp();

  const myStudent = students.find((s) => s.id === currentUser.id) || students[0];

  const [activeTab, setActiveTab] = useState<'LEAVES' | 'CERTIFICATES' | 'GRIEVANCES'>('LEAVES');

  // Modal States
  const [showLeaveModal, setShowLeaveModal] = useState(false);
  const [showCertModal, setShowCertModal] = useState(false);
  const [showGrievanceModal, setShowGrievanceModal] = useState(false);

  // Form states
  const [leaveForm, setLeaveForm] = useState({
    leaveType: 'Medical' as LeaveApplication['leaveType'],
    startDate: '2026-03-25',
    endDate: '2026-03-27',
    totalDays: 3,
    reason: '',
  });

  const [certForm, setCertForm] = useState({
    certificateType: 'Bonafide Certificate' as CertificateRequest['certificateType'],
    purpose: '',
  });

  const [grievanceForm, setGrievanceForm] = useState({
    category: 'Academic' as GrievanceTicket['category'],
    priority: 'Medium' as GrievanceTicket['priority'],
    subject: '',
    description: '',
  });

  // Filtered student records
  const myLeaves = leaves.filter((l) => l.applicantId === myStudent?.id || l.applicantName === myStudent?.fullName);
  const myCertificates = certificates.filter((c) => c.studentId === myStudent?.id || c.studentName === myStudent?.fullName);
  const myGrievances = grievances.filter((g) => g.submitterId === myStudent?.id || (g as any).submittedById === myStudent?.id || g.submitterName === myStudent?.fullName);

  const handleLeaveSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!leaveForm.reason) return;

    applyForLeave({
      applicantId: myStudent.id,
      applicantName: myStudent.fullName,
      applicantType: 'STUDENT',
      rollOrEmpNo: myStudent.rollNo,
      departmentName: 'Computer Science & Engineering',
      leaveType: leaveForm.leaveType,
      startDate: leaveForm.startDate,
      endDate: leaveForm.endDate,
      totalDays: Number(leaveForm.totalDays),
      reason: leaveForm.reason,
      appliedDate: new Date().toISOString().split('T')[0],
      status: 'Pending',
    });

    setShowLeaveModal(false);
    setLeaveForm({ leaveType: 'Medical', startDate: '2026-03-25', endDate: '2026-03-27', totalDays: 3, reason: '' });
    alert('Leave application forwarded to Dean and Proctor.');
  };

  const handleCertSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!certForm.purpose) return;

    requestCertificate({
      studentId: myStudent.id,
      rollNo: myStudent.rollNo,
      studentName: myStudent.fullName,
      departmentName: 'Computer Science & Engineering',
      certificateType: certForm.certificateType,
      purpose: certForm.purpose,
      appliedDate: new Date().toISOString().split('T')[0],
      status: 'Pending',
    });

    setShowCertModal(false);
    setCertForm({ certificateType: 'Bonafide Certificate', purpose: '' });
    alert('Certificate application submitted to Registrar Office.');
  };

  const handleGrievanceSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!grievanceForm.subject || !grievanceForm.description) return;

    fileGrievance({
      submittedById: myStudent.id,
      submittedByName: myStudent.fullName,
      submittedByRole: 'Student',
      category: grievanceForm.category,
      priority: grievanceForm.priority,
      subject: grievanceForm.subject,
      description: grievanceForm.description,
      submittedAt: new Date().toISOString().split('T')[0],
      status: 'Open',
    });

    setShowGrievanceModal(false);
    setGrievanceForm({ category: 'Academic', priority: 'Medium', subject: '', description: '' });
    alert('Grievance ticket filed. Campus Disciplinary / Welfare committee notified.');
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Student Self-Service Desk</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Absence leaves, bonafide/NOC certificates, and confidential grievance redressal
          </p>
        </div>

        {/* Action Button depending on tab */}
        {activeTab === 'LEAVES' && (
          <button
            onClick={() => setShowLeaveModal(true)}
            className="px-4 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs transition-colors flex items-center space-x-1.5 self-start sm:self-auto"
          >
            <Plus className="w-4 h-4" />
            <span>Apply for Leave</span>
          </button>
        )}
        {activeTab === 'CERTIFICATES' && (
          <button
            onClick={() => setShowCertModal(true)}
            className="px-4 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs transition-colors flex items-center space-x-1.5 self-start sm:self-auto"
          >
            <Plus className="w-4 h-4" />
            <span>Request Certificate</span>
          </button>
        )}
        {activeTab === 'GRIEVANCES' && (
          <button
            onClick={() => setShowGrievanceModal(true)}
            className="px-4 py-2 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 rounded-xl shadow-xs transition-colors flex items-center space-x-1.5 self-start sm:self-auto"
          >
            <Plus className="w-4 h-4" />
            <span>File Grievance Ticket</span>
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab('LEAVES')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'LEAVES' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Leave Applications ({myLeaves.length})
        </button>
        <button
          onClick={() => setActiveTab('CERTIFICATES')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'CERTIFICATES' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Certificates & Letters ({myCertificates.length})
        </button>
        <button
          onClick={() => setActiveTab('GRIEVANCES')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'GRIEVANCES' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Grievances & Redressal ({myGrievances.length})
        </button>
      </div>

      {/* Tab 1: Leaves */}
      {activeTab === 'LEAVES' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {myLeaves.length === 0 ? (
            <div className="col-span-2 bg-white rounded-2xl border border-slate-200 p-8 text-center text-slate-400 text-xs">
              No leave applications submitted yet.
            </div>
          ) : (
            myLeaves.map((leave) => (
              <div key={leave.id} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-extrabold text-xs text-blue-800 bg-blue-100 px-2.5 py-0.5 rounded-full">
                    {leave.leaveType} Leave
                  </span>
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                      leave.status === 'Approved'
                        ? 'bg-emerald-100 text-emerald-800'
                        : leave.status === 'Rejected'
                        ? 'bg-rose-100 text-rose-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {leave.status}
                  </span>
                </div>

                <div className="text-xs text-slate-700 space-y-1">
                  <div>
                    Dates: <strong>{leave.startDate}</strong> to <strong>{leave.endDate}</strong> ({leave.totalDays} Days)
                  </div>
                  <div>
                    Reason: <em>"{leave.reason}"</em>
                  </div>
                  {leave.reviewerRemarks && (
                    <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-100">
                      Dean Remarks: <strong>{leave.reviewerRemarks}</strong>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab 2: Certificates */}
      {activeTab === 'CERTIFICATES' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {myCertificates.length === 0 ? (
            <div className="col-span-2 bg-white rounded-2xl border border-slate-200 p-8 text-center text-slate-400 text-xs">
              No certificates requested yet.
            </div>
          ) : (
            myCertificates.map((cert) => {
              const isIssued = cert.status === 'Issued';

              return (
                <div
                  key={cert.id}
                  className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs flex flex-col justify-between"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-extrabold text-sm text-slate-900">{cert.certificateType}</span>
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          isIssued ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {cert.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600">
                      Purpose: <strong>{cert.purpose}</strong>
                    </p>
                    <p className="text-[11px] text-slate-400">Applied On: {cert.appliedDate}</p>
                  </div>

                  {isIssued && (
                    <div className="pt-3 mt-3 border-t border-slate-100 flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-emerald-700">{cert.certificateNumber}</span>
                      <button
                        onClick={() => onOpenCertificate(cert)}
                        className="px-3 py-1.5 text-xs font-bold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-xl transition-colors inline-flex items-center space-x-1"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>View / Print Certificate</span>
                      </button>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Tab 3: Grievances */}
      {activeTab === 'GRIEVANCES' && (
        <div className="space-y-3">
          {myGrievances.length === 0 ? (
            <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center text-slate-400 text-xs">
              No grievances filed. Campus is peaceful!
            </div>
          ) : (
            myGrievances.map((g) => (
              <div key={g.id} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
                      {g.ticketNumber}
                    </span>
                    <span className="font-bold text-xs text-slate-700">{g.category}</span>
                  </div>
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                      g.status === 'Resolved' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {g.status}
                  </span>
                </div>
                <h4 className="font-bold text-sm text-slate-900">{g.subject}</h4>
                <p className="text-xs text-slate-600">{g.description}</p>
                {g.resolutionNotes && (
                  <div className="bg-emerald-50 border border-emerald-200 p-2.5 rounded-xl text-xs text-emerald-900 mt-2">
                    <span className="font-bold block">Resolution Action:</span>
                    {g.resolutionNotes}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Modals */}
      {showLeaveModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-md w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <h3 className="font-extrabold text-base text-slate-900">Student Leave Application</h3>
            <form onSubmit={handleLeaveSubmit} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Reason Category</label>
                <select
                  value={leaveForm.leaveType}
                  onChange={(e) => setLeaveForm({ ...leaveForm, leaveType: e.target.value as any })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-800"
                >
                  <option value="Medical">Medical / Sick Leave</option>
                  <option value="Casual">Casual / Family Function</option>
                  <option value="Duty">On-Duty / Hackathon / Sports</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Start Date</label>
                  <input
                    type="date"
                    value={leaveForm.startDate}
                    onChange={(e) => setLeaveForm({ ...leaveForm, startDate: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">End Date</label>
                  <input
                    type="date"
                    value={leaveForm.endDate}
                    onChange={(e) => setLeaveForm({ ...leaveForm, endDate: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Explanation of Absence *</label>
                <textarea
                  rows={3}
                  required
                  value={leaveForm.reason}
                  onChange={(e) => setLeaveForm({ ...leaveForm, reason: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="Detail your medical reason or official event participation..."
                />
              </div>
              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowLeaveModal(false)}
                  className="px-4 py-2 font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs"
                >
                  Submit Application
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showCertModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-md w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <h3 className="font-extrabold text-base text-slate-900">Request Official Certificate</h3>
            <form onSubmit={handleCertSubmit} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Certificate Type</label>
                <select
                  value={certForm.certificateType}
                  onChange={(e) => setCertForm({ ...certForm, certificateType: e.target.value as any })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-800"
                >
                  <option value="Bonafide Certificate">Bonafide Certificate</option>
                  <option value="Character Certificate">Character Certificate</option>
                  <option value="No Objection Certificate (NOC)">No Objection Certificate (NOC)</option>
                  <option value="Course Completion Certificate">Course Completion Certificate</option>
                </select>
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Purpose / Requirement Reason *</label>
                <input
                  type="text"
                  required
                  value={certForm.purpose}
                  onChange={(e) => setCertForm({ ...certForm, purpose: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="e.g. Passport Application / Internship Verification / Bank Loan"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCertModal(false)}
                  className="px-4 py-2 font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs"
                >
                  Submit Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showGrievanceModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-md w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <h3 className="font-extrabold text-base text-slate-900">File Confidential Grievance</h3>
            <form onSubmit={handleGrievanceSubmit} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Category</label>
                  <select
                    value={grievanceForm.category}
                    onChange={(e) => setGrievanceForm({ ...grievanceForm, category: e.target.value as any })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-800"
                  >
                    <option value="Academic">Academic</option>
                    <option value="Hostel">Hostel & Mess</option>
                    <option value="Infrastructure">Infrastructure</option>
                    <option value="Anti-Ragging">Anti-Ragging</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Priority</label>
                  <select
                    value={grievanceForm.priority}
                    onChange={(e) => setGrievanceForm({ ...grievanceForm, priority: e.target.value as any })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-800"
                  >
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                    <option value="Urgent">Urgent</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Subject / Issue Summary *</label>
                <input
                  type="text"
                  required
                  value={grievanceForm.subject}
                  onChange={(e) => setGrievanceForm({ ...grievanceForm, subject: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="e.g. Library WiFi Connectivity in Study Hall"
                />
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Detailed Description *</label>
                <textarea
                  rows={3}
                  required
                  value={grievanceForm.description}
                  onChange={(e) => setGrievanceForm({ ...grievanceForm, description: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="Provide precise details of the issue..."
                />
              </div>
              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowGrievanceModal(false)}
                  className="px-4 py-2 font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-bold text-white bg-rose-600 hover:bg-rose-700 rounded-xl shadow-xs"
                >
                  File Ticket
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
