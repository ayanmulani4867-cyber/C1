export type Role = 'ADMIN' | 'HOD' | 'FACULTY' | 'STUDENT';

export interface User {
  id: string;
  username: string;
  email: string;
  role: Role;
  firstName: string;
  lastName: string;
  fullName: string;
  name?: string;
  phone?: string;
  profileImage: string;
  photo?: string;
  departmentId?: string;
  department?: string;
}

export interface Department {
  id: string;
  name: string;
  code: string;
  description: string;
  hodFacultyId?: string;
  hodName?: string;
  establishedYear: number;
  isActive: boolean;
  color: string;
}

export interface Course {
  id: string;
  name: string;
  code: string;
  departmentId: string;
  durationYears: number;
  totalSemesters: number;
  degreeType: 'Undergraduate' | 'Postgraduate' | 'Diploma';
  isActive: boolean;
  tuitionFeePerSem: number;
}

export interface AcademicSession {
  id: string;
  name: string; // e.g. "2025-2026"
  startYear: number;
  endYear: number;
  isCurrent: boolean;
}

export interface Semester {
  id: string;
  number: number;
  name: string;
  isActive: boolean;
}

export interface ClassDivision {
  id: string;
  name: string; // e.g. "Section A"
  code: string; // e.g. "CSE-4A"
  departmentId: string;
  courseId: string;
  semesterId: string;
  sessionId: string;
  roomNumber: string;
  classTeacherFacultyId?: string;
}

export interface Subject {
  id: string;
  name: string;
  code: string;
  credits: number;
  type: 'Theory' | 'Practical' | 'Elective' | 'Seminar';
  departmentId: string;
  courseId: string;
  semesterNumber: number;
  assignedFacultyIds: string[];
  syllabus?: string;
}

export interface Student {
  id: string;
  userId: string;
  studentId: string; // e.g. STU-2025-0101
  rollNo: string; // e.g. 22CS101
  enrollmentNo: string;
  admissionNo: string;
  firstName: string;
  lastName: string;
  fullName: string;
  dob: string;
  gender: 'Male' | 'Female' | 'Other';
  bloodGroup: string;
  collegeEmail: string;
  personalEmail: string;
  mobile: string;
  departmentId: string;
  courseId: string;
  semesterNumber: number;
  divisionId: string;
  admissionDate: string;
  batch: string; // e.g. "2022-2026"
  status: 'Active' | 'Suspended' | 'Alumni' | 'On Leave';
  photo: string;
  cgpa: number;
  currentAddress: {
    line1: string;
    city: string;
    state: string;
    pincode: string;
  };
  fatherName: string;
  motherName: string;
  parentPhone: string;
  emergencyContact: {
    name: string;
    relation: string;
    phone: string;
  };
}

export interface Faculty {
  id: string;
  userId: string;
  facultyId: string; // e.g. FAC-CSE-012
  employeeId: string; // e.g. EMP-1092
  firstName: string;
  lastName: string;
  fullName: string;
  dob: string;
  gender: 'Male' | 'Female' | 'Other';
  bloodGroup: string;
  officialEmail: string;
  personalEmail: string;
  mobile: string;
  departmentId: string;
  designation: 'Professor & HOD' | 'Professor' | 'Associate Professor' | 'Assistant Professor' | 'Visiting Faculty';
  employmentType: 'Permanent' | 'Contract' | 'Adjunct';
  dateOfJoining: string;
  qualification: string;
  specialization: string;
  experienceYears: number;
  photo: string;
  status: 'Active' | 'On Leave' | 'Resigned';
  roomOffice: string;
}

export interface TimetableSlot {
  id: string;
  divisionId: string;
  dayOfWeek: 'Monday' | 'Tuesday' | 'Wednesday' | 'Thursday' | 'Friday' | 'Saturday';
  period: number; // 1 to 6
  startTime: string;
  endTime: string;
  subjectId: string;
  facultyId: string;
  roomNumber: string;
}

export interface AttendanceRecordItem {
  studentId: string;
  status: 'Present' | 'Absent' | 'Late' | 'Excused';
  remarks?: string;
}

export interface AttendanceSession {
  id: string;
  divisionId: string;
  subjectId: string;
  facultyId: string;
  date: string;
  period: number;
  topicCovered: string;
  records: AttendanceRecordItem[];
  createdAt: string;
}

export interface Assignment {
  id: string;
  title: string;
  description: string;
  subjectId: string;
  divisionId: string;
  facultyId: string;
  dueDate: string;
  maxMarks: number;
  attachmentName?: string;
  attachmentSize?: string;
  createdAt: string;
}

export interface AssignmentSubmission {
  id: string;
  assignmentId: string;
  studentId: string;
  submittedAt: string;
  fileName: string;
  fileSize: string;
  notes?: string;
  marksObtained?: number;
  feedback?: string;
  status: 'Submitted' | 'Graded' | 'Late';
}

export interface StudyMaterial {
  id: string;
  title: string;
  description: string;
  subjectId: string;
  facultyId: string;
  unit: string;
  fileType: 'PDF' | 'PPT' | 'DOC' | 'ZIP' | 'LINK' | 'Code';
  fileName: string;
  fileSize: string;
  uploadedAt: string;
}

export interface Exam {
  id: string;
  name?: string;
  title?: string;
  examType: 'Mid-Term 1' | 'Mid-Term 2' | 'Semester End Exam' | 'Practical / Lab' | 'Mid-Term' | 'Final' | string;
  semesterNumber: number;
  subjectId: string;
  departmentId?: string;
  courseId?: string;
  date?: string;
  examDate?: string;
  time?: string;
  startTime?: string;
  endTime?: string;
  maxMarks: number;
  passingMarks: number;
  venue?: string;
  academicYear?: string;
  status?: 'Scheduled' | 'Completed' | 'Cancelled' | string;
}

export interface ExamResult {
  id: string;
  examId?: string;
  examScheduleId?: string;
  studentId: string;
  rollNo?: string;
  studentName?: string;
  subjectId: string;
  semesterNumber?: number;
  marksObtained: number;
  maxMarks: number;
  grade: 'O' | 'A+' | 'A' | 'B+' | 'B' | 'C' | 'P' | 'F' | string;
  gradePoint: number;
  isPass?: boolean;
  remarks?: string;
  evaluatedBy?: string;
  evaluatedDate?: string;
}

export interface FeeStructure {
  id: string;
  courseId: string;
  semesterNumber: number;
  tuitionFee: number;
  developmentFee: number;
  libraryFee: number;
  labFee: number;
  examFee: number;
  totalAmount: number;
  dueDate: string;
}

export interface StudentFeeLedger {
  id: string;
  studentId: string;
  semesterNumber: number;
  totalAmount: number;
  paidAmount: number;
  discount: number;
  pendingAmount: number;
  status: 'Paid' | 'Partial' | 'Pending' | 'Overdue';
  dueDate: string;
}

export interface FeePayment {
  id: string;
  studentId: string;
  receiptNumber: string;
  amount: number;
  paymentDate: string;
  paymentMethod: 'Online UPI' | 'Net Banking' | 'Credit/Debit Card' | 'Bank DD' | 'Cash' | any;
  transactionId: string;
  semesterNumber: number;
  breakdown: {
    tuition?: number;
    lab?: number;
    library?: number;
    exam?: number;
    [key: string]: any;
  };
  status: 'Completed' | 'Pending' | 'Failed';
  remarks?: string;
}

export interface LeaveRequest {
  id: string;
  applicantId: string;
  applicantRole: 'STUDENT' | 'FACULTY';
  applicantType?: 'STUDENT' | 'FACULTY';
  applicantName: string;
  departmentId: string;
  leaveType: 'Casual' | 'Medical' | 'Duty / On-Duty' | 'Emergency' | 'Maternity/Paternity';
  startDate: string;
  endDate: string;
  totalDays: number;
  reason: string;
  documentName?: string;
  status: 'Pending' | 'Approved' | 'Rejected';
  appliedAt: string;
  reviewedBy?: string;
  reviewerRemarks?: string;
}

export interface CertificateRequest {
  id: string;
  studentId: string;
  studentName: string;
  rollNo: string;
  departmentName: string;
  certificateType: 'Bonafide Certificate' | 'Character Certificate' | 'Transfer Certificate (TC)' | 'No Objection Certificate (NOC)' | 'Course Completion Certificate';
  purpose: string;
  status: 'Pending' | 'Approved' | 'Issued' | 'Rejected';
  certificateNumber?: string;
  issuedDate?: string;
  appliedAt: string;
}

export interface GrievanceComplaint {
  id: string;
  ticketNumber: string;
  submitterId: string;
  submitterName: string;
  submitterRole: 'STUDENT' | 'FACULTY';
  category: 'Academic & Curriculum' | 'Hostel & Mess' | 'Fees & Accounts' | 'Library & Infrastructure' | 'Ragging & Harassment' | 'IT & Wi-Fi';
  title: string;
  description: string;
  priority: 'Low' | 'Medium' | 'High' | 'Urgent';
  status: 'Open' | 'Under Investigation' | 'Resolved' | 'Closed';
  resolutionNotes?: string;
  createdAt: string;
  resolvedAt?: string;
}

export interface Notice {
  id: string;
  title: string;
  content: string;
  category: 'Academic' | 'Examination' | 'Admission' | 'Event' | 'Holiday' | 'General' | string;
  targetAudience: 'All' | 'Students' | 'Faculty' | 'HODs' | string;
  departmentId?: string;
  departmentCode?: string;
  priority?: 'Low' | 'Normal' | 'High' | 'Urgent' | string;
  isPinned: boolean;
  publishedAt: string;
  publishedBy?: string;
  expiryDate?: string;
  authorName: string;
  authorRole: string;
}

export interface CampusEvent {
  id: string;
  title: string;
  description: string;
  category: 'Technical Symposium' | 'Cultural Fest' | 'Sports Tournament' | 'Industry Workshop' | 'Guest Lecture' | string;
  eventType?: 'Technical' | 'Cultural' | 'Sports' | 'Academic' | 'Workshop' | 'Seminar' | string;
  startDate: string;
  endDate: string;
  time?: string;
  venue: string;
  organizer: string;
  bannerColor?: string;
  bannerImage?: string;
  maxParticipants?: number;
  registrationDeadline?: string;
  isRegistrationOpen?: boolean;
  registeredParticipants?: string[];
  isRegistered?: boolean;
}

export type AttendanceStatus = 'Present' | 'Absent' | 'Late' | 'Excused';
export type LeaveApplication = LeaveRequest;
export type GrievanceTicket = GrievanceComplaint;
export type ExamSchedule = Exam;

export interface AppNotification {
  id: string;
  userId: string;
  title: string;
  message: string;
  link?: string;
  isRead: boolean;
  createdAt: string;
  type: 'attendance' | 'exam' | 'fee' | 'leave' | 'notice' | 'assignment' | 'general';
}
