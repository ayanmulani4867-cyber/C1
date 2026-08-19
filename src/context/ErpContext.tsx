import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  User,
  Role,
  Department,
  Course,
  AcademicSession,
  Semester,
  ClassDivision,
  Subject,
  Student,
  Faculty,
  TimetableSlot,
  AttendanceSession,
  Assignment,
  AssignmentSubmission,
  StudyMaterial,
  Exam,
  ExamResult,
  FeeStructure,
  StudentFeeLedger,
  FeePayment,
  LeaveRequest,
  CertificateRequest,
  GrievanceComplaint,
  Notice,
  CampusEvent,
  AppNotification,
} from '../types';
import {
  INITIAL_USERS,
  INITIAL_DEPARTMENTS,
  INITIAL_COURSES,
  INITIAL_SESSIONS,
  INITIAL_SEMESTERS,
  INITIAL_DIVISIONS,
  INITIAL_SUBJECTS,
  INITIAL_FACULTY,
  INITIAL_STUDENTS,
  INITIAL_TIMETABLE,
  INITIAL_ATTENDANCE_SESSIONS,
  INITIAL_ASSIGNMENTS,
  INITIAL_SUBMISSIONS,
  INITIAL_STUDY_MATERIALS,
  INITIAL_EXAMS,
  INITIAL_EXAM_RESULTS,
  INITIAL_FEE_STRUCTURES,
  INITIAL_STUDENT_FEE_LEDGER,
  INITIAL_FEE_PAYMENTS,
  INITIAL_LEAVES,
  INITIAL_CERTIFICATE_REQUESTS,
  INITIAL_GRIEVANCES,
  INITIAL_NOTICES,
  INITIAL_EVENTS,
  INITIAL_NOTIFICATIONS,
} from '../data/initialData';

import { formatINR } from '../utils/formatters';

interface ErpContextType {
  isAuthenticated: boolean;
  login: (usernameOrEmail: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  currentUser: User;
  switchUser: (userId: string) => void;
  availableUsers: User[];

  currentView: string;
  setCurrentView: (view: string) => void;
  
  // Entities
  departments: Department[];
  courses: Course[];
  sessions: AcademicSession[];
  semesters: Semester[];
  divisions: ClassDivision[];
  subjects: Subject[];
  students: Student[];
  faculty: Faculty[];
  timetable: TimetableSlot[];
  attendanceSessions: AttendanceSession[];
  assignments: Assignment[];
  submissions: AssignmentSubmission[];
  materials: StudyMaterial[];
  studyMaterials: StudyMaterial[]; // Compatibility alias
  exams: Exam[];
  examResults: ExamResult[];
  marks: ExamResult[]; // Alias for examResults
  feeStructures: FeeStructure[];
  feeLedgers: StudentFeeLedger[];
  feePayments: FeePayment[];
  leaves: LeaveRequest[];
  certificates: CertificateRequest[];
  grievances: GrievanceComplaint[];
  notices: Notice[];
  events: CampusEvent[];
  notifications: AppNotification[];

  // Active student/faculty entity for current user
  currentStudent: Student | undefined;
  currentFaculty: Faculty | undefined;

  // Actions
  addStudent: (student: Omit<Student, 'id' | 'userId'>) => Promise<Student>;
  updateStudent: (id: string, updates: Partial<Student>) => void;
  deleteStudent: (id: string) => void;

  addFaculty: (faculty: Omit<Faculty, 'id' | 'userId'>) => Promise<Faculty>;
  updateFaculty: (id: string, updates: Partial<Faculty>) => void;
  deleteFaculty: (id: string) => void;

  addDepartment: (dept: Omit<Department, 'id'>) => void;
  addCourse: (course: Omit<Course, 'id'>) => void;
  addSubject: (subject: Omit<Subject, 'id'>) => void;

  saveAttendanceSession: (session: Omit<AttendanceSession, 'id' | 'createdAt'>) => void;
  recordAttendanceSession: (session: Omit<AttendanceSession, 'id' | 'createdAt'>) => void; // Compatibility alias
  
  addAssignment: (assignment: Omit<Assignment, 'id' | 'createdAt'>) => void;
  submitAssignment: (assignmentIdOrPayload: any, submissionData?: any) => void;
  gradeSubmission: (submissionId: string, marks: number, feedback: string) => void;

  addStudyMaterial: (mat: Omit<StudyMaterial, 'id' | 'uploadedAt'>) => void;

  addExam: (exam: Omit<Exam, 'id'> | any) => void;
  saveExamResults: (results: Omit<ExamResult, 'id'>[]) => void;
  recordExamMarks: (result: any) => void;

  payStudentFee: (payment: { studentId: string; amount: number; paymentMethod: any; semesterNumber: number; breakdown?: any; transactionId?: string; receiptNumber?: string; paymentDate?: string; remarks?: string }) => FeePayment;
  recordFeePayment: (payment: { studentId: string; amount: number; paymentMethod: any; semesterNumber: number; breakdown?: any; transactionId?: string; receiptNumber?: string; paymentDate?: string; remarks?: string }) => FeePayment;

  applyLeave: (leave: Omit<LeaveRequest, 'id' | 'applicantId' | 'applicantRole' | 'applicantName' | 'departmentId' | 'status' | 'appliedAt'>) => void;
  applyForLeave: (leave: any) => void; // Compatibility alias
  reviewLeave: (leaveId: string, status: 'Approved' | 'Rejected', remarks: string) => void;
  updateLeaveStatus: (leaveId: string, status: 'Approved' | 'Rejected', reviewerName?: string, remarks?: string) => void; // Compatibility alias

  requestCertificate: (certificateTypeOrPayload: any, purpose?: string) => void;
  issueCertificate: (certId: string) => void;
  rejectCertificate: (certId: string) => void;
  updateCertificateStatus: (certId: string, status: 'Approved' | 'Issued' | 'Rejected', certNum?: string) => void; // Compatibility alias

  submitGrievance: (data: { category: any; title: string; description: string; priority: any }) => void;
  fileGrievance: (data: any) => void; // Compatibility alias
  resolveGrievance: (id: string, notes: string, status: 'Resolved' | 'Closed' | 'Under Investigation') => void;
  updateGrievanceStatus: (id: string, status: 'Resolved' | 'Closed' | 'Under Investigation', notes?: string) => void; // Compatibility alias

  publishNotice: (notice: Omit<Notice, 'id' | 'publishedAt' | 'authorName' | 'authorRole'>) => void;
  addNotice: (notice: any) => void;
  deleteNotice: (id: string) => void;

  addEvent: (event: any) => void;
  toggleEventRegister: (eventId: string) => void;
  registerForEvent: (eventId: string) => void;
  markNotificationRead: (id: string) => void;
  markAllNotificationsRead: () => void;

  resetToFactoryDefaults: () => void;
}

const ErpContext = createContext<ErpContextType | null>(null);

const STORAGE_PREFIX = 'CAMPUS_CONNECT_ERP_';

function loadStored<T>(key: string, fallback: T): T {
  try {
    const item = localStorage.getItem(STORAGE_PREFIX + key);
    return item ? JSON.parse(item) : fallback;
  } catch (e) {
    console.error('Failed to load ' + key + ' from localStorage', e);
    return fallback;
  }
}

export const ErpProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [availableUsers, setAvailableUsers] = useState<User[]>(() => loadStored('availableUsers', INITIAL_USERS));
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => loadStored('isAuthenticated', false));
  const [currentUserId, setCurrentUserId] = useState<string>(() => loadStored('currentUserId', 'u-admin-1'));
  const [currentView, setCurrentView] = useState<string>(() => {
    const storedView = loadStored('currentView', '');
    if (storedView) return storedView;
    const initialUser = INITIAL_USERS.find((u) => u.id === 'u-admin-1');
    if (initialUser?.role === 'STUDENT') return 'student-dashboard';
    if (initialUser?.role === 'FACULTY' || initialUser?.role === 'HOD') return 'faculty-dashboard';
    return 'dashboard';
  });
  
  const [departments, setDepartments] = useState<Department[]>(() => loadStored('departments', INITIAL_DEPARTMENTS));
  const [courses, setCourses] = useState<Course[]>(() => loadStored('courses', INITIAL_COURSES));
  const [sessions] = useState<AcademicSession[]>(INITIAL_SESSIONS);
  const [semesters] = useState<Semester[]>(INITIAL_SEMESTERS);
  const [divisions, setDivisions] = useState<ClassDivision[]>(() => loadStored('divisions', INITIAL_DIVISIONS));
  const [subjects, setSubjects] = useState<Subject[]>(() => loadStored('subjects', INITIAL_SUBJECTS));
  const [students, setStudents] = useState<Student[]>(() => loadStored('students', INITIAL_STUDENTS));
  const [faculty, setFaculty] = useState<Faculty[]>(() => loadStored('faculty', INITIAL_FACULTY));
  const [timetable, setTimetable] = useState<TimetableSlot[]>(() => loadStored('timetable', INITIAL_TIMETABLE));
  const [attendanceSessions, setAttendanceSessions] = useState<AttendanceSession[]>(() => loadStored('attendance', INITIAL_ATTENDANCE_SESSIONS));
  const [assignments, setAssignments] = useState<Assignment[]>(() => loadStored('assignments', INITIAL_ASSIGNMENTS));
  const [submissions, setSubmissions] = useState<AssignmentSubmission[]>(() => loadStored('submissions', INITIAL_SUBMISSIONS));
  const [materials, setMaterials] = useState<StudyMaterial[]>(() => loadStored('materials', INITIAL_STUDY_MATERIALS));
  const [exams, setExams] = useState<Exam[]>(() => loadStored('exams', INITIAL_EXAMS));
  const [examResults, setExamResults] = useState<ExamResult[]>(() => loadStored('examResults', INITIAL_EXAM_RESULTS));
  const [feeStructures, setFeeStructures] = useState<FeeStructure[]>(() => loadStored('feeStructures', INITIAL_FEE_STRUCTURES));
  const [feeLedgers, setFeeLedgers] = useState<StudentFeeLedger[]>(() => loadStored('feeLedgers', INITIAL_STUDENT_FEE_LEDGER));
  const [feePayments, setFeePayments] = useState<FeePayment[]>(() => loadStored('feePayments', INITIAL_FEE_PAYMENTS));
  const [leaves, setLeaves] = useState<LeaveRequest[]>(() => loadStored('leaves', INITIAL_LEAVES));
  const [certificates, setCertificates] = useState<CertificateRequest[]>(() => loadStored('certificates', INITIAL_CERTIFICATE_REQUESTS));
  const [grievances, setGrievances] = useState<GrievanceComplaint[]>(() => loadStored('grievances', INITIAL_GRIEVANCES));
  const [notices, setNotices] = useState<Notice[]>(() => loadStored('notices', INITIAL_NOTICES));
  const [events, setEvents] = useState<CampusEvent[]>(() => loadStored('events', INITIAL_EVENTS));
  const [notifications, setNotifications] = useState<AppNotification[]>(() => loadStored('notifications', INITIAL_NOTIFICATIONS));

  // Sync to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'isAuthenticated', JSON.stringify(isAuthenticated));
  }, [isAuthenticated]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'currentUserId', JSON.stringify(currentUserId));
  }, [currentUserId]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'availableUsers', JSON.stringify(availableUsers));
  }, [availableUsers]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'currentView', JSON.stringify(currentView));
  }, [currentView]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'students', JSON.stringify(students));
  }, [students]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'faculty', JSON.stringify(faculty));
  }, [faculty]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'attendance', JSON.stringify(attendanceSessions));
  }, [attendanceSessions]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'assignments', JSON.stringify(assignments));
  }, [assignments]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'submissions', JSON.stringify(submissions));
  }, [submissions]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'feeLedgers', JSON.stringify(feeLedgers));
  }, [feeLedgers]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'feePayments', JSON.stringify(feePayments));
  }, [feePayments]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'leaves', JSON.stringify(leaves));
  }, [leaves]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'certificates', JSON.stringify(certificates));
  }, [certificates]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'grievances', JSON.stringify(grievances));
  }, [grievances]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'notices', JSON.stringify(notices));
  }, [notices]);

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + 'materials', JSON.stringify(materials));
  }, [materials]);

  const rawCurrentUser = availableUsers.find((u) => u.id === currentUserId) || availableUsers[0];
  const currentUser: User = {
    ...rawCurrentUser,
    name: rawCurrentUser?.name || rawCurrentUser?.fullName || `${rawCurrentUser?.firstName || ''} ${rawCurrentUser?.lastName || ''}`.trim(),
    photo: rawCurrentUser?.photo || rawCurrentUser?.profileImage || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200',
    department: rawCurrentUser?.department || departments.find((d) => d.id === rawCurrentUser?.departmentId)?.name || 'Computer Science & Engineering',
  };
  const currentStudent = students.find((s) => s.userId === currentUser.id || s.id === currentUser.id);
  const currentFaculty = faculty.find((f) => f.userId === currentUser.id || f.id === currentUser.id);

  const login = async (usernameOrEmail: string, pass: string): Promise<{ success: boolean; error?: string }> => {
    const input = usernameOrEmail.toLowerCase().trim();
    const cleanPass = pass.trim();

    // Check for standard admin login credentials
    if (input === 'admin' || input === 'admin@apex.edu') {
      const adminUser = availableUsers.find((u) => u.role === 'ADMIN') || {
        id: 'u-admin-1',
        username: 'admin',
        email: 'admin@apex.edu',
        role: 'ADMIN' as const,
        firstName: 'System',
        lastName: 'Administrator',
        fullName: 'Administrator (ERP Director)',
        phone: '+91 98765 43210',
        profileImage: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=200&auto=format&fit=crop&q=80',
      };

      if (cleanPass !== 'admin' && cleanPass !== 'admin123' && cleanPass !== 'password') {
        return { success: false, error: 'Incorrect administrator password. Please use password "admin".' };
      }

      setCurrentUserId(adminUser.id);
      setIsAuthenticated(true);
      setCurrentView('dashboard');
      return { success: true };
    }
    
    // Find matching user by email, username, roll number or studentId
    let matchedUser = availableUsers.find(
      (u) => u.email.toLowerCase() === input || u.username.toLowerCase() === input
    );

    if (!matchedUser) {
      // Check if it matches an existing student
      const matchedStudent = students.find(
        (s) =>
          s.collegeEmail.toLowerCase() === input ||
          s.personalEmail.toLowerCase() === input ||
          s.rollNo.toLowerCase() === input ||
          s.studentId.toLowerCase() === input
      );
      if (matchedStudent) {
        matchedUser = availableUsers.find((u) => u.id === matchedStudent.userId);
        if (!matchedUser) {
          // Dynamically construct user if missing
          matchedUser = {
            id: matchedStudent.userId || `u-${matchedStudent.id}`,
            username: matchedStudent.rollNo.toLowerCase(),
            email: matchedStudent.collegeEmail,
            role: 'STUDENT',
            firstName: matchedStudent.firstName,
            lastName: matchedStudent.lastName,
            fullName: matchedStudent.fullName,
            phone: matchedStudent.mobile,
            profileImage: matchedStudent.photo || 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200&auto=format&fit=crop&q=80',
            departmentId: matchedStudent.departmentId,
          };
          setAvailableUsers((prev) => [...prev, matchedUser!]);
        }
      }
    }

    if (!matchedUser) {
      // Check if it matches faculty
      const matchedFac = faculty.find(
        (f) =>
          f.officialEmail.toLowerCase() === input ||
          f.personalEmail.toLowerCase() === input ||
          f.facultyId.toLowerCase() === input ||
          f.employeeId.toLowerCase() === input
      );
      if (matchedFac) {
        matchedUser = availableUsers.find((u) => u.id === matchedFac.userId);
        if (!matchedUser) {
          // Dynamically construct user if missing
          matchedUser = {
            id: matchedFac.userId || `u-${matchedFac.id}`,
            username: matchedFac.facultyId.toLowerCase(),
            email: matchedFac.officialEmail,
            role: matchedFac.designation.includes('HOD') || matchedFac.designation.includes('Head') ? 'HOD' : 'FACULTY',
            firstName: matchedFac.firstName,
            lastName: matchedFac.lastName,
            fullName: matchedFac.fullName,
            phone: matchedFac.mobile,
            profileImage: matchedFac.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80',
            departmentId: matchedFac.departmentId,
          };
          setAvailableUsers((prev) => [...prev, matchedUser!]);
        }
      }
    }

    if (!matchedUser) {
      return { success: false, error: 'User account not found. Please contact the administrator or verify your ID/email.' };
    }

    // Role-based password check
    if (cleanPass.length < 3) {
      return { success: false, error: 'Password must be at least 3 characters.' };
    }

    setCurrentUserId(matchedUser.id);
    setIsAuthenticated(true);

    if (matchedUser.role === 'ADMIN') {
      setCurrentView('dashboard');
    } else if (matchedUser.role === 'HOD' || matchedUser.role === 'FACULTY') {
      setCurrentView('faculty-dashboard');
    } else if (matchedUser.role === 'STUDENT') {
      setCurrentView('student-dashboard');
    }

    return { success: true };
  };

  const logout = () => {
    setIsAuthenticated(false);
    setCurrentUserId('');
  };

  const switchUser = (userId: string) => {
    setCurrentUserId(userId);
    const targetUser = availableUsers.find((u) => u.id === userId);
    if (targetUser) {
      if (targetUser.role === 'ADMIN') {
        setCurrentView('dashboard');
      } else if (targetUser.role === 'HOD' || targetUser.role === 'FACULTY') {
        setCurrentView('faculty-dashboard');
      } else if (targetUser.role === 'STUDENT') {
        setCurrentView('student-dashboard');
      }
    }
  };

  const getAuthHeaders = (): Record<string, string> => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('CAMPUS_CONNECT_ERP_token') || sessionStorage.getItem('token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    } catch {
      // Ignore
    }
    return headers;
  };

  const addStudent = async (studentData: Omit<Student, 'id' | 'userId'>): Promise<Student> => {
    let savedStudent: Student;

    try {
      const response = await fetch('/api/admin/students', {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify(studentData),
      });

      const data = await response.json();

      if (!response.ok || !data.success || !data.student) {
        throw new Error(data.message || data.error || 'Student could not be saved to the database.');
      }

      const rawStu = data.student;
      const studentIdStr = String(rawStu.id || rawStu.student_id || rawStu.studentId || `stu-${Date.now()}`);
      const userIdStr = String(rawStu.user_id || rawStu.userId || data.credentials?.user_id || data.user_id || `u-${studentIdStr}`);

      savedStudent = {
        ...studentData,
        id: studentIdStr,
        userId: userIdStr,
        studentId: rawStu.student_id || rawStu.studentId || studentData.studentId || `STU-${Date.now()}`,
        enrollmentNo: rawStu.enrollment_no || rawStu.enrollmentNumber || studentData.enrollmentNo || `ENR-${Date.now()}`,
        admissionNo: rawStu.admission_no || rawStu.admissionNumber || studentData.admissionNo || `ADM-${Date.now()}`,
        rollNo: rawStu.roll_no || rawStu.rollNumber || studentData.rollNo || `ROLL-${Date.now()}`,
      };

      const newUser: User = {
        id: userIdStr,
        username: data.credentials?.username || data.credentials?.email || savedStudent.collegeEmail,
        email: data.credentials?.email || savedStudent.collegeEmail,
        role: 'STUDENT',
        firstName: savedStudent.firstName,
        lastName: savedStudent.lastName,
        fullName: savedStudent.fullName,
        name: savedStudent.fullName,
        phone: savedStudent.mobile,
        profileImage: savedStudent.photo || 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200&auto=format&fit=crop&q=80',
        photo: savedStudent.photo || 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200&auto=format&fit=crop&q=80',
        departmentId: savedStudent.departmentId,
      };

      setAvailableUsers((prev) => [...prev.filter((u) => u.id !== newUser.id), newUser]);
    } catch (err: any) {
      console.warn('Backend student creation warning, persisting locally:', err);
      const localId = `stu-${Date.now()}`;
      const localUserId = `u-${localId}`;
      savedStudent = {
        ...studentData,
        id: localId,
        userId: localUserId,
        studentId: studentData.studentId || `STU-${Date.now()}`,
        enrollmentNo: studentData.enrollmentNo || `ENR-${Date.now()}`,
        admissionNo: studentData.admissionNo || `ADM-${Date.now()}`,
        rollNo: studentData.rollNo || `ROLL-${Date.now()}`,
      };
      const newUser: User = {
        id: localUserId,
        username: savedStudent.collegeEmail,
        email: savedStudent.collegeEmail,
        role: 'STUDENT',
        firstName: savedStudent.firstName,
        lastName: savedStudent.lastName,
        fullName: savedStudent.fullName,
        name: savedStudent.fullName,
        phone: savedStudent.mobile,
        profileImage: savedStudent.photo || 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200&auto=format&fit=crop&q=80',
        photo: savedStudent.photo || 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200&auto=format&fit=crop&q=80',
        departmentId: savedStudent.departmentId,
      };
      setAvailableUsers((prev) => [...prev, newUser]);
    }

    setStudents((prev) => [savedStudent, ...prev.filter((s) => s.id !== savedStudent.id)]);

    const newLedger: StudentFeeLedger = {
      id: `ledger-${savedStudent.id}`,
      studentId: savedStudent.id,
      semesterNumber: savedStudent.semesterNumber,
      totalAmount: 85000,
      paidAmount: 0,
      discount: 0,
      pendingAmount: 85000,
      status: 'Pending',
      dueDate: '2026-09-01',
    };

    setFeeLedgers((prev) => [...prev.filter((l) => l.studentId !== savedStudent.id), newLedger]);

    return savedStudent;
  };

  const updateStudent = (id: string, updates: Partial<Student>) => {
    setStudents((prev) => prev.map((s) => (s.id === id ? { ...s, ...updates } : s)));
  };

  const deleteStudent = (id: string) => {
    setStudents((prev) => prev.filter((s) => s.id !== id));
    setAvailableUsers((prev) => prev.filter((u) => u.id !== `u-${id}`));
  };

  const addFaculty = async (facultyData: Omit<Faculty, 'id' | 'userId'>): Promise<Faculty> => {
    let savedFaculty: Faculty;

    try {
      const response = await fetch('/api/admin/faculty', {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify(facultyData),
      });

      const data = await response.json();

      if (!response.ok || !data.success || !data.faculty) {
        throw new Error(data.message || data.error || 'Faculty could not be saved to the database.');
      }

      const rawFac = data.faculty;
      const facultyIdStr = String(rawFac.id || rawFac.faculty_id || rawFac.facultyId || `fac-${Date.now()}`);
      const userIdStr = String(rawFac.user_id || rawFac.userId || data.credentials?.user_id || data.user_id || `u-${facultyIdStr}`);

      savedFaculty = {
        ...facultyData,
        id: facultyIdStr,
        userId: userIdStr,
        facultyId: rawFac.faculty_id || rawFac.facultyId || facultyData.facultyId || `FAC-${Date.now()}`,
        employeeId: rawFac.employee_id || rawFac.employeeId || facultyData.employeeId || `EMP-${Date.now()}`,
      };

      const isHod =
        savedFaculty.designation.includes('HOD') ||
        savedFaculty.designation.includes('Head') ||
        data.credentials?.role === 'HOD';

      const newUser: User = {
        id: userIdStr,
        username: data.credentials?.username || data.credentials?.email || savedFaculty.officialEmail,
        email: data.credentials?.email || savedFaculty.officialEmail,
        role: isHod ? 'HOD' : 'FACULTY',
        firstName: savedFaculty.firstName,
        lastName: savedFaculty.lastName,
        fullName: savedFaculty.fullName,
        name: savedFaculty.fullName,
        phone: savedFaculty.mobile,
        profileImage: savedFaculty.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80',
        photo: savedFaculty.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80',
        departmentId: savedFaculty.departmentId,
      };

      setAvailableUsers((prev) => [...prev.filter((u) => u.id !== newUser.id), newUser]);
    } catch (err: any) {
      console.warn('Backend faculty creation failed/offline, persisting locally:', err);
      const localId = `fac-${Date.now()}`;
      const localUserId = `u-${localId}`;
      savedFaculty = {
        ...facultyData,
        id: localId,
        userId: localUserId,
        facultyId: facultyData.facultyId || `FAC-${Date.now()}`,
        employeeId: facultyData.employeeId || `EMP-${Date.now()}`,
      };

      const isHod =
        savedFaculty.designation.includes('HOD') ||
        savedFaculty.designation.includes('Head');

      const newUser: User = {
        id: localUserId,
        username: savedFaculty.officialEmail,
        email: savedFaculty.officialEmail,
        role: isHod ? 'HOD' : 'FACULTY',
        firstName: savedFaculty.firstName,
        lastName: savedFaculty.lastName,
        fullName: savedFaculty.fullName,
        name: savedFaculty.fullName,
        phone: savedFaculty.mobile,
        profileImage: savedFaculty.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80',
        photo: savedFaculty.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80',
        departmentId: savedFaculty.departmentId,
      };

      setAvailableUsers((prev) => [...prev, newUser]);
    }

    setFaculty((prev) => [savedFaculty, ...prev.filter((f) => f.id !== savedFaculty.id)]);

    return savedFaculty;
  };

  const updateFaculty = (id: string, updates: Partial<Faculty>) => {
    setFaculty((prev) => prev.map((f) => (f.id === id ? { ...f, ...updates } : f)));
  };

  const deleteFaculty = (id: string) => {
    setFaculty((prev) => prev.filter((f) => f.id !== id));
    setAvailableUsers((prev) => prev.filter((u) => u.id !== `u-${id}`));
  };

  const addDepartment = (dept: Omit<Department, 'id'>) => {
    const newDept: Department = { ...dept, id: `dept-${Date.now()}` };
    setDepartments((prev) => [...prev, newDept]);
  };

  const addCourse = (course: Omit<Course, 'id'>) => {
    const newCourse: Course = { ...course, id: `course-${Date.now()}` };
    setCourses((prev) => [...prev, newCourse]);
  };

  const addSubject = (subject: Omit<Subject, 'id'>) => {
    const newSubject: Subject = { ...subject, id: `sub-${Date.now()}` };
    setSubjects((prev) => [...prev, newSubject]);
  };

  const saveAttendanceSession = (sessionData: Omit<AttendanceSession, 'id' | 'createdAt'>) => {
    const newSession: AttendanceSession = {
      ...sessionData,
      id: `att-sess-${Date.now()}`,
      createdAt: new Date().toISOString(),
    };
    setAttendanceSessions((prev) => [newSession, ...prev]);

    // Send notifications to absent students
    newSession.records.forEach((record) => {
      if (record.status === 'Absent') {
        const student = students.find((s) => s.id === record.studentId);
        const subject = subjects.find((sub) => sub.id === sessionData.subjectId);
        if (student) {
          setNotifications((prev) => [
            {
              id: `notif-${Date.now()}-${student.id}`,
              userId: student.userId,
              title: 'Absence Recorded',
              message: `You were marked absent in ${subject?.name || 'Class'} on ${sessionData.date}.`,
              type: 'attendance',
              isRead: false,
              createdAt: 'Just now',
            },
            ...prev,
          ]);
        }
      }
    });
  };

  const addAssignment = (asg: Omit<Assignment, 'id' | 'createdAt'>) => {
    const newAsg: Assignment = {
      ...asg,
      id: `asg-${Date.now()}`,
      createdAt: new Date().toISOString().split('T')[0],
    };
    setAssignments((prev) => [newAsg, ...prev]);

    // Broadcast notification to students
    const targetStudents = students.filter((s) => s.divisionId === asg.divisionId);
    targetStudents.forEach((st) => {
      setNotifications((prev) => [
        {
          id: `notif-asg-${Date.now()}-${st.id}`,
          userId: st.userId,
          title: 'New Assignment Published',
          message: `${newAsg.title} - Due ${newAsg.dueDate}`,
          type: 'assignment',
          isRead: false,
          createdAt: 'Just now',
          link: 'assignments',
        },
        ...prev,
      ]);
    });
  };

  const submitAssignment = (
    param1: string | { assignmentId: string; fileName?: string; fileSize?: string; notes?: string; [key: string]: any },
    param2?: { fileName?: string; fileSize?: string; notes?: string; [key: string]: any }
  ) => {
    let assignmentId = '';
    let fileName = 'solution.pdf';
    let fileSize = '1.2 MB';
    let notes: string | undefined = undefined;

    if (typeof param1 === 'object' && param1 !== null) {
      assignmentId = param1.assignmentId;
      fileName = param1.fileName || 'solution.pdf';
      fileSize = param1.fileSize || '1.2 MB';
      notes = param1.notes;
    } else {
      assignmentId = String(param1);
      if (param2) {
        fileName = param2.fileName || 'solution.pdf';
        fileSize = param2.fileSize || '1.2 MB';
        notes = param2.notes;
      }
    }

    const studentId = currentStudent?.id || students[0]?.id || 'stu-2025-0101';
    const existingIndex = submissions.findIndex(
      (s) => s.assignmentId === assignmentId && s.studentId === studentId
    );
    const newSub: AssignmentSubmission = {
      id: existingIndex >= 0 ? submissions[existingIndex].id : `sub-${Date.now()}`,
      assignmentId,
      studentId,
      submittedAt: new Date().toISOString(),
      fileName,
      fileSize,
      notes,
      status: 'Submitted',
    };

    if (existingIndex >= 0) {
      setSubmissions((prev) => {
        const next = [...prev];
        next[existingIndex] = newSub;
        return next;
      });
    } else {
      setSubmissions((prev) => [newSub, ...prev]);
    }
  };

  const gradeSubmission = (submissionId: string, marks: number, feedback: string) => {
    setSubmissions((prev) =>
      prev.map((sub) =>
        sub.id === submissionId
          ? {
              ...sub,
              marksObtained: marks,
              feedback,
              status: 'Graded',
            }
          : sub
      )
    );

    const sub = submissions.find((s) => s.id === submissionId);
    if (sub) {
      const student = students.find((st) => st.id === sub.studentId);
      const asg = assignments.find((a) => a.id === sub.assignmentId);
      if (student && asg) {
        setNotifications((prev) => [
          {
            id: `notif-grade-${Date.now()}`,
            userId: student.userId,
            title: 'Assignment Graded',
            message: `Your submission for "${asg.title}" has been graded: ${marks}/${asg.maxMarks} marks.`,
            type: 'assignment',
            isRead: false,
            createdAt: 'Just now',
            link: 'assignments',
          },
          ...prev,
        ]);
      }
    }
  };

  const addStudyMaterial = (mat: Omit<StudyMaterial, 'id' | 'uploadedAt'>) => {
    const newMat: StudyMaterial = {
      ...mat,
      id: `mat-${Date.now()}`,
      uploadedAt: new Date().toISOString().split('T')[0],
    };
    setMaterials((prev) => [newMat, ...prev]);
  };

  const addExam = (exam: Omit<Exam, 'id'>) => {
    const newExam: Exam = {
      ...exam,
      id: `exam-${Date.now()}`,
    };
    setExams((prev) => [...prev, newExam]);
  };

  const saveExamResults = (newResults: Omit<ExamResult, 'id'>[]) => {
    const mapped = newResults.map((r) => ({
      ...r,
      id: `res-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
    }));
    setExamResults((prev) => [...prev, ...mapped]);
  };

  const recordExamMarks = (resultData: any) => {
    const newResult: ExamResult = {
      id: `res-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
      examId: resultData.examScheduleId || resultData.examId,
      examScheduleId: resultData.examScheduleId || resultData.examId,
      studentId: resultData.studentId,
      rollNo: resultData.rollNo,
      studentName: resultData.studentName,
      subjectId: resultData.subjectId,
      semesterNumber: resultData.semesterNumber || 4,
      marksObtained: resultData.marksObtained,
      maxMarks: resultData.maxMarks || 50,
      grade: resultData.grade || 'B',
      gradePoint: resultData.gradePoint || 8.0,
      isPass: resultData.isPass ?? true,
      remarks: resultData.remarks || 'Evaluated',
      evaluatedBy: resultData.evaluatedBy || currentUser.fullName,
      evaluatedDate: resultData.evaluatedDate || new Date().toISOString().split('T')[0],
    };
    setExamResults((prev) => {
      const filtered = prev.filter(
        (r) =>
          !(
            (r.examScheduleId === newResult.examScheduleId || r.examId === newResult.examId) &&
            r.studentId === newResult.studentId
          )
      );
      return [...filtered, newResult];
    });
  };

  const payStudentFee = (paymentData: {
    studentId: string;
    amount: number;
    paymentMethod: any;
    semesterNumber: number;
    breakdown?: any;
    transactionId?: string;
    receiptNumber?: string;
    paymentDate?: string;
    remarks?: string;
  }): FeePayment => {
    const receiptNumber = paymentData.receiptNumber || `RCPT-${new Date().getFullYear()}-${Math.floor(10000 + Math.random() * 90000)}`;
    const transactionId = paymentData.transactionId || `TXN_${Date.now()}_${Math.random().toString(36).substring(2, 8).toUpperCase()}`;

    const newPayment: FeePayment = {
      id: `pay-${Date.now()}`,
      studentId: paymentData.studentId,
      receiptNumber,
      amount: paymentData.amount,
      paymentDate: paymentData.paymentDate || new Date().toISOString().split('T')[0],
      paymentMethod: paymentData.paymentMethod,
      transactionId,
      semesterNumber: paymentData.semesterNumber,
      breakdown: paymentData.breakdown || {
        tuitionFee: paymentData.amount,
        developmentFee: 0,
        examFee: 0,
        libraryFee: 0,
        labFee: 0,
      },
      status: 'Completed',
      remarks: paymentData.remarks,
    };

    setFeePayments((prev) => [newPayment, ...prev]);

    // Update Student Fee Ledger
    setFeeLedgers((prev) =>
      prev.map((ledger) => {
        if (ledger.studentId === paymentData.studentId && ledger.semesterNumber === paymentData.semesterNumber) {
          const newPaid = ledger.paidAmount + paymentData.amount;
          const newPending = Math.max(0, ledger.totalAmount - ledger.discount - newPaid);
          return {
            ...ledger,
            paidAmount: newPaid,
            pendingAmount: newPending,
            status: newPending === 0 ? 'Paid' : 'Partial',
          };
        }
        return ledger;
      })
    );

    // Notification
    const student = students.find((s) => s.id === paymentData.studentId);
    if (student) {
      setNotifications((prev) => [
        {
          id: `notif-fee-${Date.now()}`,
          userId: student.userId,
          title: 'Fee Payment Successful',
          message: `Received ${formatINR(paymentData.amount)} for Semester ${paymentData.semesterNumber}. Receipt: ${receiptNumber}`,
          type: 'fee',
          isRead: false,
          createdAt: 'Just now',
          link: 'fees',
        },
        ...prev,
      ]);
    }

    return newPayment;
  };

  const recordFeePayment = (paymentData: {
    studentId: string;
    amount: number;
    paymentMethod: any;
    semesterNumber: number;
    breakdown?: any;
    transactionId?: string;
    receiptNumber?: string;
    paymentDate?: string;
    remarks?: string;
  }): FeePayment => {
    return payStudentFee(paymentData);
  };

  const applyLeave = (leaveData: Omit<LeaveRequest, 'id' | 'applicantId' | 'applicantRole' | 'applicantName' | 'departmentId' | 'status' | 'appliedAt'>) => {
    const isStudent = currentUser.role === 'STUDENT';
    const applicantName = isStudent ? (currentStudent?.fullName || currentUser.fullName) : (currentFaculty?.fullName || currentUser.fullName);
    const departmentId = isStudent ? (currentStudent?.departmentId || 'dept-cse') : (currentFaculty?.departmentId || 'dept-cse');
    const applicantId = isStudent ? (currentStudent?.id || currentUser.id) : (currentFaculty?.id || currentUser.id);

    const newLeave: LeaveRequest = {
      ...leaveData,
      id: `leave-${Date.now()}`,
      applicantId,
      applicantRole: isStudent ? 'STUDENT' : 'FACULTY',
      applicantName,
      departmentId,
      status: 'Pending',
      appliedAt: new Date().toISOString().split('T')[0],
    };
    setLeaves((prev) => [newLeave, ...prev]);
  };

  const reviewLeave = (leaveId: string, status: 'Approved' | 'Rejected', remarks: string) => {
    setLeaves((prev) =>
      prev.map((l) =>
        l.id === leaveId
          ? {
              ...l,
              status,
              reviewerRemarks: remarks,
              reviewedBy: currentUser.fullName,
            }
          : l
      )
    );
  };

  const updateLeaveStatus = (leaveId: string, status: 'Approved' | 'Rejected', reviewerName?: string, remarks?: string) => {
    setLeaves((prev) =>
      prev.map((l) =>
        l.id === leaveId
          ? {
              ...l,
              status,
              reviewerRemarks: remarks || `${status} by administration`,
              reviewedBy: reviewerName || currentUser.fullName,
            }
          : l
      )
    );
  };

  const applyForLeave = (leaveData: any) => {
    applyLeave(leaveData);
  };

  const requestCertificate = (certificateTypeOrPayload: any, purposeParam?: string) => {
    let certType = 'Bonafide Certificate';
    let purpose = 'Official Verification';

    if (typeof certificateTypeOrPayload === 'object' && certificateTypeOrPayload !== null) {
      certType = certificateTypeOrPayload.certificateType || certificateTypeOrPayload.type || 'Bonafide Certificate';
      purpose = certificateTypeOrPayload.purpose || 'Official Verification';
    } else if (typeof certificateTypeOrPayload === 'string') {
      certType = certificateTypeOrPayload;
      if (purposeParam) purpose = purposeParam;
    }

    const student = currentStudent || students[0];
    const dept = departments.find((d) => d.id === student?.departmentId);
    const newReq: CertificateRequest = {
      id: `cert-${Date.now()}`,
      studentId: student?.id || 'stu-2025-0101',
      studentName: student?.fullName || currentUser.fullName,
      rollNo: student?.rollNo || '22CS101',
      departmentName: dept?.name || 'Computer Science & Engineering',
      certificateType: certType as any,
      purpose,
      status: 'Pending',
      appliedAt: new Date().toISOString().split('T')[0],
    };
    setCertificates((prev) => [newReq, ...prev]);
  };

  const issueCertificate = (certId: string, customCertNum?: string) => {
    const certNumber = customCertNum || `AITS/CERT/${new Date().getFullYear()}/${Math.floor(1000 + Math.random() * 9000)}`;
    setCertificates((prev) =>
      prev.map((c) =>
        c.id === certId
          ? {
              ...c,
              status: 'Issued',
              certificateNumber: certNumber,
              issuedDate: new Date().toISOString().split('T')[0],
            }
          : c
      )
    );

    const cert = certificates.find((c) => c.id === certId);
    if (cert) {
      const student = students.find((s) => s.id === cert.studentId);
      if (student) {
        setNotifications((prev) => [
          {
            id: `notif-cert-${Date.now()}`,
            userId: student.userId,
            title: 'Certificate Issued',
            message: `Your ${cert.certificateType} is ready for download. Number: ${certNumber}`,
            type: 'general',
            isRead: false,
            createdAt: 'Just now',
            link: 'services',
          },
          ...prev,
        ]);
      }
    }
  };

  const rejectCertificate = (certId: string) => {
    setCertificates((prev) =>
      prev.map((c) => (c.id === certId ? { ...c, status: 'Rejected' } : c))
    );
  };

  const updateCertificateStatus = (certId: string, status: 'Approved' | 'Issued' | 'Rejected', certNum?: string) => {
    if (status === 'Issued' || status === 'Approved') {
      issueCertificate(certId, certNum);
    } else {
      rejectCertificate(certId);
    }
  };

  const submitGrievance = (data: any) => {
    const isStudent = currentUser.role === 'STUDENT';
    const submitterName = data.submittedByName || data.submitterName || (isStudent ? (currentStudent?.fullName || currentUser.fullName) : (currentFaculty?.fullName || currentUser.fullName));
    const submitterId = data.submittedById || data.submitterId || (isStudent ? (currentStudent?.id || currentUser.id) : (currentFaculty?.id || currentUser.id));

    const newGrv: GrievanceComplaint = {
      id: `grv-${Date.now()}`,
      ticketNumber: `TKT-${new Date().getFullYear()}-${Math.floor(100 + Math.random() * 900)}`,
      submitterId,
      submitterName,
      submitterRole: isStudent ? 'STUDENT' : 'FACULTY',
      category: data.category || 'Academic & Curriculum',
      title: data.title || data.subject || 'Campus Grievance',
      description: data.description || '',
      priority: data.priority || 'Medium',
      status: 'Open',
      createdAt: new Date().toISOString().split('T')[0],
    };
    setGrievances((prev) => [newGrv, ...prev]);
  };

  const fileGrievance = (data: any) => {
    submitGrievance(data);
  };

  const resolveGrievance = (id: string, notes: string, status: 'Resolved' | 'Closed' | 'Under Investigation') => {
    setGrievances((prev) =>
      prev.map((g) =>
        g.id === id
          ? {
              ...g,
              status,
              resolutionNotes: notes,
              resolvedAt: status === 'Resolved' ? new Date().toISOString().split('T')[0] : g.resolvedAt,
            }
          : g
      )
    );
  };

  const updateGrievanceStatus = (id: string, status: 'Resolved' | 'Closed' | 'Under Investigation', notes?: string) => {
    resolveGrievance(id, notes || 'Resolved by administration', status);
  };

  const publishNotice = (noticeData: Omit<Notice, 'id' | 'publishedAt' | 'authorName' | 'authorRole'>) => {
    const newNotice: Notice = {
      ...noticeData,
      id: `not-${Date.now()}`,
      publishedAt: new Date().toISOString().split('T')[0],
      authorName: currentUser.fullName,
      authorRole: currentUser.role === 'ADMIN' ? 'Administration' : 'Faculty / HOD',
    };
    setNotices((prev) => [newNotice, ...prev]);
  };

  const addNotice = (noticeData: any) => {
    const newNotice: Notice = {
      id: `not-${Date.now()}`,
      title: noticeData.title || '',
      content: noticeData.content || '',
      category: noticeData.category || 'General',
      targetAudience: noticeData.targetAudience || 'All',
      priority: noticeData.priority || 'Normal',
      isPinned: !!noticeData.isPinned,
      publishedAt: noticeData.publishedAt || new Date().toISOString().split('T')[0],
      publishedBy: noticeData.publishedBy || currentUser.fullName,
      expiryDate: noticeData.expiryDate,
      authorName: noticeData.publishedBy || currentUser.fullName,
      authorRole: currentUser.role === 'ADMIN' ? 'Administration' : 'Faculty / HOD',
    };
    setNotices((prev) => [newNotice, ...prev]);
  };

  const deleteNotice = (id: string) => {
    setNotices((prev) => prev.filter((n) => n.id !== id));
  };

  const addEvent = (eventData: any) => {
    const newEvent: CampusEvent = {
      id: `ev-${Date.now()}`,
      title: eventData.title || '',
      description: eventData.description || '',
      category: eventData.category || 'Technical Symposium',
      eventType: eventData.eventType || 'Technical',
      startDate: eventData.startDate || new Date().toISOString().split('T')[0],
      endDate: eventData.endDate || new Date().toISOString().split('T')[0],
      time: eventData.time || '10:00 AM',
      venue: eventData.venue || 'Campus Auditorium',
      organizer: eventData.organizer || 'College Management',
      bannerColor: eventData.bannerColor || 'from-blue-600 to-indigo-700',
      bannerImage: eventData.bannerImage || 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=600&auto=format&fit=crop&q=80',
      maxParticipants: eventData.maxParticipants || 300,
      registrationDeadline: eventData.registrationDeadline || '2026-12-31',
      isRegistrationOpen: eventData.isRegistrationOpen ?? true,
      registeredParticipants: eventData.registeredParticipants || [currentUser.id],
      isRegistered: true,
    };
    setEvents((prev) => [newEvent, ...prev]);
  };

  const registerForEvent = (eventId: string) => {
    setEvents((prev) =>
      prev.map((e) => {
        if (e.id === eventId) {
          const currentList = e.registeredParticipants || [];
          const already = currentList.includes(currentUser.id);
          const updated = already
            ? currentList.filter((uid) => uid !== currentUser.id)
            : [...currentList, currentUser.id];
          return {
            ...e,
            registeredParticipants: updated,
            isRegistered: !already,
          };
        }
        return e;
      })
    );
  };

  const toggleEventRegister = (eventId: string) => {
    registerForEvent(eventId);
  };

  const markNotificationRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, isRead: true } : n))
    );
  };

  const markAllNotificationsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, isRead: true })));
  };

  const resetToFactoryDefaults = () => {
    localStorage.clear();
    setDepartments(INITIAL_DEPARTMENTS);
    setCourses(INITIAL_COURSES);
    setDivisions(INITIAL_DIVISIONS);
    setSubjects(INITIAL_SUBJECTS);
    setStudents(INITIAL_STUDENTS);
    setFaculty(INITIAL_FACULTY);
    setTimetable(INITIAL_TIMETABLE);
    setAttendanceSessions(INITIAL_ATTENDANCE_SESSIONS);
    setAssignments(INITIAL_ASSIGNMENTS);
    setSubmissions(INITIAL_SUBMISSIONS);
    setMaterials(INITIAL_STUDY_MATERIALS);
    setExams(INITIAL_EXAMS);
    setExamResults(INITIAL_EXAM_RESULTS);
    setFeeStructures(INITIAL_FEE_STRUCTURES);
    setFeeLedgers(INITIAL_STUDENT_FEE_LEDGER);
    setFeePayments(INITIAL_FEE_PAYMENTS);
    setLeaves(INITIAL_LEAVES);
    setCertificates(INITIAL_CERTIFICATE_REQUESTS);
    setGrievances(INITIAL_GRIEVANCES);
    setNotices(INITIAL_NOTICES);
    setEvents(INITIAL_EVENTS);
    setNotifications(INITIAL_NOTIFICATIONS);
    setCurrentUserId('u-admin-1');
  };

  return (
    <ErpContext.Provider
      value={{
        isAuthenticated,
        login,
        logout,
        currentUser,
        switchUser,
        availableUsers,
        currentView,
        setCurrentView,
        departments,
        courses,
        sessions,
        semesters,
        divisions,
        subjects,
        students,
        faculty,
        timetable,
        attendanceSessions,
        assignments,
        submissions,
        materials,
        studyMaterials: materials,
        exams,
        examResults,
        marks: examResults,
        feeStructures,
        feeLedgers,
        feePayments,
        leaves,
        certificates,
        grievances,
        notices,
        events,
        notifications,
        currentStudent,
        currentFaculty,
        addStudent,
        updateStudent,
        deleteStudent,
        addFaculty,
        updateFaculty,
        deleteFaculty,
        addDepartment,
        addCourse,
        addSubject,
        saveAttendanceSession,
        recordAttendanceSession: saveAttendanceSession,
        addAssignment,
        submitAssignment,
        gradeSubmission,
        addStudyMaterial,
        addExam,
        saveExamResults,
        recordExamMarks,
        payStudentFee,
        recordFeePayment,
        applyLeave,
        applyForLeave,
        reviewLeave,
        updateLeaveStatus,
        requestCertificate,
        issueCertificate,
        rejectCertificate,
        updateCertificateStatus,
        submitGrievance,
        fileGrievance,
        resolveGrievance,
        updateGrievanceStatus,
        publishNotice,
        addNotice,
        deleteNotice,
        addEvent,
        toggleEventRegister,
        registerForEvent,
        markNotificationRead,
        markAllNotificationsRead,
        resetToFactoryDefaults,
      }}
    >
      {children}
    </ErpContext.Provider>
  );
};

export const useErp = () => {
  const context = useContext(ErpContext);
  if (!context) {
    throw new Error('useErp must be used within an ErpProvider');
  }
  return context;
};
