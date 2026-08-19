import React, { useState } from 'react';
import { ErpProvider, useErp } from './context/ErpContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { IdCardModal } from './components/IdCardModal';
import { CertificateModal } from './components/CertificateModal';
import { FeeReceiptModal } from './components/FeeReceiptModal';

// Admin Views
import { AdminDashboardView } from './views/admin/AdminDashboardView';
import { StudentsDirectoryView } from './views/admin/StudentsDirectoryView';
import { FacultyDirectoryView } from './views/admin/FacultyDirectoryView';
import { DepartmentsView } from './views/admin/DepartmentsView';
import { TimetableManagerView } from './views/admin/TimetableManagerView';
import { AttendanceCenterView } from './views/admin/AttendanceCenterView';
import { ExamsManagerView } from './views/admin/ExamsManagerView';
import { FeeManagementView } from './views/admin/FeeManagementView';
import { LeavesDeskView } from './views/admin/LeavesDeskView';
import { CertificatesDeskView } from './views/admin/CertificatesDeskView';
import { GrievancesDeskView } from './views/admin/GrievancesDeskView';
import { NoticesView } from './views/admin/NoticesView';
import { EventsView } from './views/admin/EventsView';

// Faculty Views
import { FacultyDashboardView } from './views/faculty/FacultyDashboardView';
import { MarkAttendanceView } from './views/faculty/MarkAttendanceView';
import { AssignmentsManagerView } from './views/faculty/AssignmentsManagerView';
import { StudyMaterialsView } from './views/faculty/StudyMaterialsView';
import { FacultyLeaveView } from './views/faculty/FacultyLeaveView';

// Student Views
import { StudentDashboardView } from './views/student/StudentDashboardView';
import { StudentAttendanceView } from './views/student/StudentAttendanceView';
import { StudentTimetableView } from './views/student/StudentTimetableView';
import { StudentAssignmentsView } from './views/student/StudentAssignmentsView';
import { StudentMaterialsView } from './views/student/StudentMaterialsView';
import { StudentResultsView } from './views/student/StudentResultsView';
import { StudentFeeView } from './views/student/StudentFeeView';
import { StudentServicesView } from './views/student/StudentServicesView';
import { StudentIdCardView } from './views/student/StudentIdCardView';

// Auth View
import { LoginView } from './views/auth/LoginView';

import { Student, CertificateRequest, FeePayment } from './types';

const AppContent: React.FC = () => {
  const { isAuthenticated, isAuthLoading, currentView, setCurrentView, currentUser, students } = useErp();

  // Modal states
  const [selectedStudentForIdCard, setSelectedStudentForIdCard] = useState<Student | null>(null);
  const [selectedCertificate, setSelectedCertificate] = useState<CertificateRequest | null>(null);
  const [selectedFeeReceipt, setSelectedFeeReceipt] = useState<FeePayment | null>(null);

  if (isAuthLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center text-white font-sans">
        <div className="w-10 h-10 border-3 border-blue-500/20 border-t-blue-500 rounded-full animate-spin mb-4" />
        <div className="text-xs font-semibold tracking-wider text-slate-300 uppercase">
          Verifying Verified ERP Session...
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginView />;
  }

  const activeStudent = students.find((s) => s.id === currentUser.id) || students[0];

  const renderActiveView = () => {
    switch (currentView) {
      // Admin Views
      case 'dashboard':
        return <AdminDashboardView setCurrentView={setCurrentView} />;
      case 'students':
      case 'my-classes':
        return <StudentsDirectoryView onOpenIdCard={(student) => setSelectedStudentForIdCard(student)} />;
      case 'faculty':
        return <FacultyDirectoryView />;
      case 'departments':
      case 'courses':
      case 'department-overview':
        return <DepartmentsView />;
      case 'timetable':
      case 'faculty-timetable':
        return <TimetableManagerView />;
      case 'attendance':
        return <AttendanceCenterView />;
      case 'exams':
      case 'student-performance':
        return <ExamsManagerView />;
      case 'fees':
        return <FeeManagementView onOpenReceipt={(payment) => setSelectedFeeReceipt(payment)} />;
      case 'leaves':
        return <LeavesDeskView />;
      case 'certificates':
        return <CertificatesDeskView onOpenCertificate={(cert) => setSelectedCertificate(cert)} />;
      case 'grievances':
        return <GrievancesDeskView />;
      case 'notices':
        return <NoticesView />;
      case 'events':
        return <EventsView />;

      // Faculty Views
      case 'faculty-dashboard':
        return <FacultyDashboardView setCurrentView={setCurrentView} />;
      case 'mark-attendance':
        return <MarkAttendanceView />;
      case 'assignments':
      case 'assignments-manager':
        return <AssignmentsManagerView />;
      case 'materials':
      case 'materials-manager':
        return <StudyMaterialsView />;
      case 'faculty-leave':
        return <FacultyLeaveView />;
      case 'faculty-id':
        return <StudentIdCardView onOpenModal={() => setSelectedStudentForIdCard(activeStudent)} />;

      // Student Views
      case 'student-dashboard':
        return (
          <StudentDashboardView
            setCurrentView={setCurrentView}
            onOpenIdCard={() => setSelectedStudentForIdCard(activeStudent)}
          />
        );
      case 'student-attendance':
        return <StudentAttendanceView />;
      case 'student-timetable':
        return <StudentTimetableView />;
      case 'student-assignments':
        return <StudentAssignmentsView />;
      case 'student-materials':
        return <StudentMaterialsView />;
      case 'student-results':
        return <StudentResultsView />;
      case 'student-fees':
        return <StudentFeeView onOpenReceipt={(payment) => setSelectedFeeReceipt(payment)} />;
      case 'student-services':
      case 'student-grievance':
        return <StudentServicesView onOpenCertificate={(cert) => setSelectedCertificate(cert)} />;
      case 'student-id-card':
        return <StudentIdCardView onOpenModal={() => setSelectedStudentForIdCard(activeStudent)} />;

      default:
        if (currentUser.role === 'STUDENT') {
          return (
            <StudentDashboardView
              setCurrentView={setCurrentView}
              onOpenIdCard={() => setSelectedStudentForIdCard(activeStudent)}
            />
          );
        }
        if (currentUser.role === 'FACULTY' || currentUser.role === 'HOD') {
          return <FacultyDashboardView setCurrentView={setCurrentView} />;
        }
        return <AdminDashboardView setCurrentView={setCurrentView} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans text-slate-900 antialiased selection:bg-blue-600 selection:text-white">
      {/* Top Navbar */}
      <Navbar
        currentView={currentView}
        setCurrentView={setCurrentView}
        onOpenIdCard={() => setSelectedStudentForIdCard(activeStudent)}
      />

      {/* Main Layout Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar currentView={currentView} setCurrentView={setCurrentView} />

        {/* Content Workspace */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {renderActiveView()}
        </main>
      </div>

      {/* Global Printable Modals */}
      {selectedStudentForIdCard && (
        <IdCardModal
          student={selectedStudentForIdCard}
          onClose={() => setSelectedStudentForIdCard(null)}
        />
      )}

      {selectedCertificate && (
        <CertificateModal
          certificate={selectedCertificate}
          onClose={() => setSelectedCertificate(null)}
        />
      )}

      {selectedFeeReceipt && (
        <FeeReceiptModal
          payment={selectedFeeReceipt}
          onClose={() => setSelectedFeeReceipt(null)}
        />
      )}
    </div>
  );
};

export default function App() {
  return (
    <ErpProvider>
      <AppContent />
    </ErpProvider>
  );
}
