import React, { useState, useEffect } from 'react';
import { useErp } from '../context/ErpContext';
import { Student } from '../types';
import {
  User,
  GraduationCap,
  Users,
  MapPin,
  PhoneCall,
  KeyRound,
  FileText,
  CheckCircle2,
  Upload,
  Trash2,
  Eye,
  AlertCircle,
  ChevronRight,
  ChevronLeft,
  ArrowLeft,
  Save,
  Sparkles,
  RefreshCw,
  Copy,
  Check,
  ShieldCheck,
  Building2,
  BookOpen,
} from 'lucide-react';

interface StudentEnrollmentStudioProps {
  initialStudent?: Student | null;
  onClose: () => void;
  onSuccess?: (student: Student) => void;
}

const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
  'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
  'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Delhi NCR', 'Chandigarh'
];

export const StudentEnrollmentStudio: React.FC<StudentEnrollmentStudioProps> = ({
  initialStudent,
  onClose,
  onSuccess,
}) => {
  const { departments, courses, divisions, sessions, addStudent, updateStudent, students } = useErp();

  const isEditing = Boolean(initialStudent);
  const [currentStep, setCurrentStep] = useState(1);
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [isEnrolledSuccess, setIsEnrolledSuccess] = useState(false);
  const [enrolledStudentResult, setEnrolledStudentResult] = useState<Student | null>(null);

  // Form State
  const [formData, setFormData] = useState({
    // Step 1: Personal
    photo: initialStudent?.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200',
    firstName: initialStudent?.firstName || '',
    middleName: '',
    lastName: initialStudent?.lastName || '',
    dob: initialStudent?.dob || '2005-04-12',
    gender: (initialStudent?.gender || 'Male') as 'Male' | 'Female' | 'Other',
    bloodGroup: initialStudent?.bloodGroup || 'O+',
    personalEmail: initialStudent?.personalEmail || '',
    collegeEmail: initialStudent?.collegeEmail || '',
    mobile: initialStudent?.mobile || '',
    altMobile: '',
    nationality: 'Indian',
    identityType: 'Aadhaar / National ID',
    identityNumber: '',

    // Step 2: Academic
    studentId: initialStudent?.studentId || `STU-2025-0${100 + students.length + 1}`,
    enrollmentNo: initialStudent?.enrollmentNo || `EN25CSE00${100 + students.length + 1}`,
    admissionNo: initialStudent?.admissionNo || `ADM-2025-${9100 + students.length + 1}`,
    rollNo: initialStudent?.rollNo || `25CS${100 + students.length + 1}`,
    departmentId: initialStudent?.departmentId || departments[0]?.id || 'dept-cse',
    courseId: initialStudent?.courseId || courses[0]?.id || 'course-btech-cse',
    sessionId: 'sess-2025',
    semesterNumber: initialStudent?.semesterNumber || 1,
    divisionId: initialStudent?.divisionId || divisions[0]?.id || 'div-cse-4a',
    batch: initialStudent?.batch || '2025-2029',
    admissionDate: initialStudent?.admissionDate || new Date().toISOString().split('T')[0],
    status: (initialStudent?.status || 'Active') as 'Active' | 'Suspended' | 'Alumni' | 'On Leave',
    cgpa: initialStudent?.cgpa || 8.0,

    // Step 3: Parent/Guardian
    fatherName: initialStudent?.fatherName || '',
    motherName: initialStudent?.motherName || '',
    guardianName: '',
    guardianRelation: 'Father',
    guardianPhone: initialStudent?.parentPhone || '',
    guardianAltPhone: '',
    guardianEmail: '',
    guardianOccupation: 'Professional / Business',

    // Step 4: Address
    currAddressLine1: initialStudent?.currentAddress?.line1 || '',
    currAddressLine2: '',
    currCity: initialStudent?.currentAddress?.city || 'Bengaluru',
    currState: initialStudent?.currentAddress?.state || 'Karnataka',
    currPincode: initialStudent?.currentAddress?.pincode || '560064',
    sameAsCurrentAddress: true,
    permAddressLine1: '',
    permAddressLine2: '',
    permCity: 'Bengaluru',
    permState: 'Karnataka',
    permPincode: '560064',

    // Step 5: Emergency Contact
    emergencyName: initialStudent?.emergencyContact?.name || '',
    emergencyRelation: initialStudent?.emergencyContact?.relation || 'Parent',
    emergencyPhone: initialStudent?.emergencyContact?.phone || '',
    emergencyAltPhone: '',

    // Step 6: Login Account
    createLogin: true,
    username: initialStudent?.studentId ? initialStudent.studentId.toLowerCase() : `std_${100 + students.length + 1}`,
    tempPassword: 'Campus@' + Math.floor(1000 + Math.random() * 9000),
  });

  // Uploaded documents mock state
  const [documents, setDocuments] = useState<Array<{ name: string; type: string; size: string; status: 'Uploaded' | 'Verified' }>>([
    { name: '10th_Standard_Marksheet.pdf', type: 'PDF Document', size: '1.4 MB', status: 'Uploaded' },
    { name: '12th_Standard_Marksheet.pdf', type: 'PDF Document', size: '1.8 MB', status: 'Uploaded' },
    { name: 'Transfer_Certificate.pdf', type: 'PDF Document', size: '820 KB', status: 'Uploaded' },
  ]);

  // Sync auto emails if first & last name change and field is empty
  useEffect(() => {
    if (!isEditing && formData.firstName && formData.lastName) {
      const cleanFirst = formData.firstName.toLowerCase().replace(/[^a-z0-9]/g, '');
      const cleanLast = formData.lastName.toLowerCase().replace(/[^a-z0-9]/g, '');
      if (!formData.collegeEmail || formData.collegeEmail.includes('@student.apex.edu')) {
        setFormData((prev) => ({
          ...prev,
          collegeEmail: `${cleanFirst}.${cleanLast}@student.apex.edu`,
          username: `std.${cleanFirst}.${cleanLast}`.slice(0, 20),
        }));
      }
    }
  }, [formData.firstName, formData.lastName, isEditing]);

  // Sync courses based on selected department
  const filteredCourses = courses.filter((c) => c.departmentId === formData.departmentId);
  const filteredDivisions = divisions.filter((d) => d.departmentId === formData.departmentId);

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleCopy = (text: string, fieldName: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(fieldName);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 1:
        if (!formData.firstName.trim() || !formData.lastName.trim()) {
          alert('Please enter both First Name and Last Name.');
          return false;
        }
        if (!formData.mobile.trim()) {
          alert('Please provide a valid 10-digit mobile number for the student.');
          return false;
        }
        return true;
      case 2:
        if (!formData.studentId.trim() || !formData.rollNo.trim() || !formData.enrollmentNo.trim()) {
          alert('Student ID, Roll Number, and Enrollment Number are required academic identifiers.');
          return false;
        }
        return true;
      case 3:
        if (!formData.fatherName.trim() && !formData.motherName.trim() && !formData.guardianName.trim()) {
          alert("Please enter at least one Parent or Guardian's name.");
          return false;
        }
        if (!formData.guardianPhone.trim()) {
          alert('Please provide parent/guardian contact phone number.');
          return false;
        }
        return true;
      case 4:
        if (!formData.currAddressLine1.trim() || !formData.currCity.trim() || !formData.currPincode.trim()) {
          alert('Please provide complete current address (Line 1, City, and PIN code).');
          return false;
        }
        return true;
      case 5:
        if (!formData.emergencyName.trim() || !formData.emergencyPhone.trim()) {
          alert('Please provide Emergency Contact Name and Phone Number.');
          return false;
        }
        return true;
      default:
        return true;
    }
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, 8));
    }
  };

  const handlePrev = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const handleFinalSubmit = () => {
    if (!validateStep(1) || !validateStep(2) || !validateStep(3) || !validateStep(4) || !validateStep(5)) {
      return;
    }

    const studentPayload: any = {
      studentId: formData.studentId,
      rollNo: formData.rollNo,
      enrollmentNo: formData.enrollmentNo,
      admissionNo: formData.admissionNo,
      firstName: formData.firstName,
      lastName: formData.lastName,
      fullName: `${formData.firstName} ${formData.middleName ? formData.middleName + ' ' : ''}${formData.lastName}`,
      dob: formData.dob,
      gender: formData.gender,
      bloodGroup: formData.bloodGroup,
      collegeEmail: formData.collegeEmail || `${formData.firstName.toLowerCase()}.${formData.lastName.toLowerCase()}@student.apex.edu`,
      personalEmail: formData.personalEmail || `${formData.firstName.toLowerCase()}@gmail.com`,
      mobile: formData.mobile,
      departmentId: formData.departmentId,
      courseId: formData.courseId,
      semesterNumber: Number(formData.semesterNumber),
      divisionId: formData.divisionId,
      admissionDate: formData.admissionDate,
      batch: formData.batch,
      status: formData.status,
      photo: formData.photo,
      cgpa: Number(formData.cgpa) || 8.0,
      currentAddress: {
        line1: formData.currAddressLine1,
        city: formData.currCity,
        state: formData.currState,
        pincode: formData.currPincode,
      },
      fatherName: formData.fatherName || formData.guardianName,
      motherName: formData.motherName || 'N/A',
      parentPhone: formData.guardianPhone,
      emergencyContact: {
        name: formData.emergencyName || formData.fatherName,
        relation: formData.emergencyRelation || 'Parent',
        phone: formData.emergencyPhone || formData.guardianPhone,
      },
    };

    let resultStudent: Student;

    if (isEditing && initialStudent) {
      updateStudent(initialStudent.id, studentPayload);
      resultStudent = { ...initialStudent, ...studentPayload };
    } else {
      resultStudent = addStudent(studentPayload);
    }

    setEnrolledStudentResult(resultStudent);
    setIsEnrolledSuccess(true);

    if (onSuccess) {
      onSuccess(resultStudent);
    }
  };

  const stepsList = [
    { number: 1, title: 'Personal Info', desc: 'Identity & Details', icon: User },
    { number: 2, title: 'Academics', desc: 'Roll, Dept, Course', icon: GraduationCap },
    { number: 3, title: 'Parent/Guardian', desc: 'Family Contacts', icon: Users },
    { number: 4, title: 'Addresses', desc: 'Current & Permanent', icon: MapPin },
    { number: 5, title: 'Emergency', desc: 'Urgent Contact', icon: PhoneCall },
    { number: 6, title: 'ERP Account', desc: 'Login & App Credentials', icon: KeyRound },
    { number: 7, title: 'Documents', desc: 'Certificates & KYC', icon: FileText },
    { number: 8, title: 'Review & Submit', desc: 'Enrollment Dossier', icon: CheckCircle2 },
  ];

  if (isEnrolledSuccess && enrolledStudentResult) {
    return (
      <div className="fixed inset-0 z-50 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-xl w-full p-8 text-center animate-in zoom-in-95 duration-200">
          <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-5 shadow-sm ring-8 ring-emerald-50">
            <CheckCircle2 className="w-9 h-9" />
          </div>

          <h3 className="text-2xl font-bold text-slate-900 tracking-tight">
            {isEditing ? 'Student Record Updated' : 'Student Enrolled Successfully'}
          </h3>
          <p className="text-sm text-slate-600 mt-2 max-w-md mx-auto">
            {isEditing
              ? `The profile and academic dossier for ${enrolledStudentResult.fullName} has been updated.`
              : `Official academic record and credentials created for ${enrolledStudentResult.fullName}.`}
          </p>

          <div className="mt-6 bg-slate-50 border border-slate-200 rounded-xl p-5 text-left space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-200">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Student Full Name</span>
              <span className="text-sm font-bold text-slate-900">{enrolledStudentResult.fullName}</span>
            </div>
            <div className="flex items-center justify-between pb-2 border-b border-slate-200">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Student ID</span>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-mono font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                  {enrolledStudentResult.studentId}
                </span>
                <button
                  type="button"
                  onClick={() => handleCopy(enrolledStudentResult.studentId, 'studentId')}
                  className="text-slate-400 hover:text-slate-700 p-1"
                >
                  {copiedField === 'studentId' ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <div className="flex items-center justify-between pb-2 border-b border-slate-200">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Enrollment No.</span>
              <span className="text-sm font-mono font-medium text-slate-800">{enrolledStudentResult.enrollmentNo}</span>
            </div>
            <div className="flex items-center justify-between pb-2 border-b border-slate-200">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Roll Number</span>
              <span className="text-sm font-mono font-bold text-slate-900">{enrolledStudentResult.rollNo}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Android App Username</span>
              <span className="text-sm font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-semibold">
                {formData.username}
              </span>
            </div>
          </div>

          <div className="mt-8 flex items-center justify-center space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2.5 bg-blue-700 hover:bg-blue-800 text-white font-medium rounded-xl text-sm shadow-md transition-all flex items-center space-x-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Return to Student Directory</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-6xl my-auto flex flex-col max-h-[94vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-md">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">
                {isEditing ? `Edit Student Dossier — ${formData.firstName} ${formData.lastName}` : 'Enterprise Student Enrollment Studio'}
              </h2>
              <p className="text-xs text-slate-400">
                Apex Institute of Technology & Science • Knowledge City Campus • Academic Year 2025-2026
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-white px-3 py-1.5 rounded-lg text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 transition"
          >
            Cancel & Close
          </button>
        </div>

        {/* Step Navigation Bar */}
        <div className="bg-slate-50 border-b border-slate-200 px-6 py-3 overflow-x-auto">
          <div className="flex items-center space-x-2 min-w-max">
            {stepsList.map((st, index) => {
              const Icon = st.icon;
              const isActive = currentStep === st.number;
              const isPast = currentStep > st.number;
              return (
                <React.Fragment key={st.number}>
                  <button
                    type="button"
                    onClick={() => {
                      if (st.number < currentStep || validateStep(currentStep)) {
                        setCurrentStep(st.number);
                      }
                    }}
                    className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      isActive
                        ? 'bg-blue-700 text-white shadow-sm ring-2 ring-blue-600/30'
                        : isPast
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100'
                        : 'bg-white text-slate-500 border border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    <span
                      className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                        isActive
                          ? 'bg-white text-blue-700'
                          : isPast
                          ? 'bg-emerald-600 text-white'
                          : 'bg-slate-200 text-slate-700'
                      }`}
                    >
                      {isPast ? '✓' : st.number}
                    </span>
                    <span>{st.title}</span>
                  </button>
                  {index < stepsList.length - 1 && <span className="text-slate-300">›</span>}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Form Body Scroll Area */}
        <div className="flex-1 overflow-y-auto p-6 sm:p-8 bg-white">
          {/* STEP 1: PERSONAL INFORMATION */}
          {currentStep === 1 && (
            <div className="space-y-6 max-w-4xl mx-auto">
              <div className="border-b border-slate-200 pb-3">
                <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                  <User className="w-5 h-5 text-blue-600" />
                  <span>Step 1 — Personal & Identity Information</span>
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Enter student's legal name, primary contact details, and upload their official ID card photograph.
                </p>
              </div>

              {/* Profile Photo Uploader */}
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-6">
                <div className="relative group">
                  <img
                    src={formData.photo}
                    alt="Student Preview"
                    className="w-24 h-24 rounded-2xl object-cover border-2 border-blue-500 shadow-md bg-white"
                  />
                  <div className="absolute -bottom-2 -right-2 bg-blue-600 text-white p-1 rounded-full shadow">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                </div>
                <div className="flex-1 text-center sm:text-left space-y-1">
                  <h4 className="text-sm font-bold text-slate-900">Official Student ID Photograph</h4>
                  <p className="text-xs text-slate-500">
                    High resolution color photo with clear frontal face view. Formats: JPG, PNG, WEBP (Max 5MB).
                  </p>
                  <div className="pt-2 flex flex-wrap items-center justify-center sm:justify-start gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        const randomAvatars = [
                          'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200',
                          'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200',
                          'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200',
                          'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200',
                          'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200',
                        ];
                        const next = randomAvatars[Math.floor(Math.random() * randomAvatars.length)];
                        handleInputChange('photo', next);
                      }}
                      className="px-3 py-1.5 bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-lg shadow-sm flex items-center space-x-1.5 transition"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                      <span>Choose Sample Avatar</span>
                    </button>
                    <label className="cursor-pointer px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm flex items-center space-x-1.5 transition">
                      <Upload className="w-3.5 h-3.5" />
                      <span>Upload File</span>
                      <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) {
                            const reader = new FileReader();
                            reader.onloadend = () => {
                              if (reader.result) {
                                handleInputChange('photo', reader.result as string);
                              }
                            };
                            reader.readAsDataURL(file);
                          }
                        }}
                      />
                    </label>
                  </div>
                </div>
              </div>

              {/* Name Fields */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    First Name <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Rahul"
                    value={formData.firstName}
                    onChange={(e) => handleInputChange('firstName', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Middle Name</label>
                  <input
                    type="text"
                    placeholder="e.g. Kumar"
                    value={formData.middleName}
                    onChange={(e) => handleInputChange('middleName', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Last Name <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Verma"
                    value={formData.lastName}
                    onChange={(e) => handleInputChange('lastName', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                </div>
              </div>

              {/* DOB, Gender, Blood Group */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Date of Birth <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="date"
                    value={formData.dob}
                    onChange={(e) => handleInputChange('dob', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Gender <span className="text-rose-600">*</span>
                  </label>
                  <select
                    value={formData.gender}
                    onChange={(e) => handleInputChange('gender', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Blood Group</label>
                  <select
                    value={formData.bloodGroup}
                    onChange={(e) => handleInputChange('bloodGroup', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  >
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </select>
                </div>
              </div>

              {/* Contacts */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Primary Mobile Number (+91) <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="tel"
                    required
                    placeholder="+91 98450 12345"
                    value={formData.mobile}
                    onChange={(e) => handleInputChange('mobile', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                  <span className="text-[11px] text-slate-400 mt-0.5 block">10-digit Indian mobile number for OTP/SMS</span>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Alternate Mobile Number</label>
                  <input
                    type="tel"
                    placeholder="+91 98765 00000"
                    value={formData.altMobile}
                    onChange={(e) => handleInputChange('altMobile', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                </div>
              </div>

              {/* Emails */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Official College Email <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="email"
                    required
                    placeholder="firstname.lastname@student.apex.edu"
                    value={formData.collegeEmail}
                    onChange={(e) => handleInputChange('collegeEmail', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Personal Email Address</label>
                  <input
                    type="email"
                    placeholder="student.personal@gmail.com"
                    value={formData.personalEmail}
                    onChange={(e) => handleInputChange('personalEmail', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                </div>
              </div>

              {/* Nationality & Optional KYC */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Nationality</label>
                  <input
                    type="text"
                    value={formData.nationality}
                    onChange={(e) => handleInputChange('nationality', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Aadhaar / National ID (Optional)</label>
                  <input
                    type="text"
                    placeholder="e.g. XXXX-XXXX-9812"
                    value={formData.identityNumber}
                    onChange={(e) => handleInputChange('identityNumber', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                </div>
              </div>
            </div>
          )}

          {/* STEP 2: ACADEMIC INFORMATION */}
          {currentStep === 2 && (
            <div className="space-y-6 max-w-4xl mx-auto">
              <div className="border-b border-slate-200 pb-3">
                <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                  <GraduationCap className="w-5 h-5 text-blue-600" />
                  <span>Step 2 — Academic Enrollment & Class Allocation</span>
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Assign official registration numbers, academic department, course program, semester, and batch division.
                </p>
              </div>

              {/* Registration Numbers */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-slate-50 rounded-xl border border-slate-200">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Student ID <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.studentId}
                    onChange={(e) => handleInputChange('studentId', e.target.value)}
                    className="w-full px-3 py-1.5 text-sm font-mono font-bold bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Enrollment No. <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.enrollmentNo}
                    onChange={(e) => handleInputChange('enrollmentNo', e.target.value)}
                    className="w-full px-3 py-1.5 text-sm font-mono font-bold bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Roll Number <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.rollNo}
                    onChange={(e) => handleInputChange('rollNo', e.target.value)}
                    className="w-full px-3 py-1.5 text-sm font-mono font-bold bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Admission No.</label>
                  <input
                    type="text"
                    value={formData.admissionNo}
                    onChange={(e) => handleInputChange('admissionNo', e.target.value)}
                    className="w-full px-3 py-1.5 text-sm font-mono bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>

              {/* Department & Course Cascades */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Academic Department <span className="text-rose-600">*</span>
                  </label>
                  <select
                    value={formData.departmentId}
                    onChange={(e) => {
                      const newDeptId = e.target.value;
                      const deptCourses = courses.filter((c) => c.departmentId === newDeptId);
                      const deptDivs = divisions.filter((d) => d.departmentId === newDeptId);
                      setFormData((prev) => ({
                        ...prev,
                        departmentId: newDeptId,
                        courseId: deptCourses[0]?.id || prev.courseId,
                        divisionId: deptDivs[0]?.id || prev.divisionId,
                      }));
                    }}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  >
                    {departments.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.code} — {d.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Course Program <span className="text-rose-600">*</span>
                  </label>
                  <select
                    value={formData.courseId}
                    onChange={(e) => handleInputChange('courseId', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  >
                    {filteredCourses.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name} ({c.code})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Semester, Division, Session, Batch */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Current Semester <span className="text-rose-600">*</span>
                  </label>
                  <select
                    value={formData.semesterNumber}
                    onChange={(e) => handleInputChange('semesterNumber', Number(e.target.value))}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
                      <option key={s} value={s}>
                        Semester {s}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Class Section / Division</label>
                  <select
                    value={formData.divisionId}
                    onChange={(e) => handleInputChange('divisionId', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  >
                    {filteredDivisions.length > 0 ? (
                      filteredDivisions.map((div) => (
                        <option key={div.id} value={div.id}>
                          {div.name}
                        </option>
                      ))
                    ) : (
                      <option value="div-cse-4a">Section A</option>
                    )}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Batch Period</label>
                  <input
                    type="text"
                    placeholder="e.g. 2025-2029"
                    value={formData.batch}
                    onChange={(e) => handleInputChange('batch', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Admission Date</label>
                  <input
                    type="date"
                    value={formData.admissionDate}
                    onChange={(e) => handleInputChange('admissionDate', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>

              {/* Status & CGPA */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Academic Enrollment Status</label>
                  <select
                    value={formData.status}
                    onChange={(e) => handleInputChange('status', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  >
                    <option value="Active">Active (In Good Standing)</option>
                    <option value="On Leave">On Official Leave</option>
                    <option value="Suspended">Suspended</option>
                    <option value="Alumni">Graduated / Alumni</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Cumulative CGPA (10-Point Scale)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="10"
                    value={formData.cgpa}
                    onChange={(e) => handleInputChange('cgpa', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>
            </div>
          )}

          {/* STEP 3: PARENT / GUARDIAN */}
          {currentStep === 3 && (
            <div className="space-y-6 max-w-4xl mx-auto">
              <div className="border-b border-slate-200 pb-3">
                <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                  <Users className="w-5 h-5 text-blue-600" />
                  <span>Step 3 — Parent & Guardian Contact Information</span>
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Primary and emergency guardian credentials for official university notifications, marksheet dispatch, and fee reminders.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Father's Full Name <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Sanjay Verma"
                    value={formData.fatherName}
                    onChange={(e) => handleInputChange('fatherName', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Mother's Full Name</label>
                  <input
                    type="text"
                    placeholder="e.g. Sunita Verma"
                    value={formData.motherName}
                    onChange={(e) => handleInputChange('motherName', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Primary Guardian Phone (+91) <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="tel"
                    required
                    placeholder="+91 98450 99887"
                    value={formData.guardianPhone}
                    onChange={(e) => handleInputChange('guardianPhone', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Alternate Guardian Phone</label>
                  <input
                    type="tel"
                    placeholder="+91 98450 00000"
                    value={formData.guardianAltPhone}
                    onChange={(e) => handleInputChange('guardianAltPhone', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Guardian Email Address</label>
                  <input
                    type="email"
                    placeholder="parent.verma@gmail.com"
                    value={formData.guardianEmail}
                    onChange={(e) => handleInputChange('guardianEmail', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Guardian Profession / Occupation</label>
                  <input
                    type="text"
                    placeholder="e.g. Senior Software Architect / Govt Officer"
                    value={formData.guardianOccupation}
                    onChange={(e) => handleInputChange('guardianOccupation', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>
            </div>
          )}

          {/* STEP 4: ADDRESSES */}
          {currentStep === 4 && (
            <div className="space-y-6 max-w-4xl mx-auto">
              <div className="border-b border-slate-200 pb-3">
                <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                  <MapPin className="w-5 h-5 text-blue-600" />
                  <span>Step 4 — Residential Address (Current & Permanent)</span>
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Specify current local residence (campus hostel, PG, or city home) and permanent native address.
                </p>
              </div>

              {/* Current Address */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Current / Local Address</h4>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Address Line 1 <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="text"
                    placeholder="Flat / House No., Building Name, Street"
                    value={formData.currAddressLine1}
                    onChange={(e) => handleInputChange('currAddressLine1', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      City <span className="text-rose-600">*</span>
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Bengaluru"
                      value={formData.currCity}
                      onChange={(e) => handleInputChange('currCity', e.target.value)}
                      className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      State <span className="text-rose-600">*</span>
                    </label>
                    <select
                      value={formData.currState}
                      onChange={(e) => handleInputChange('currState', e.target.value)}
                      className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none"
                    >
                      {INDIAN_STATES.map((st) => (
                        <option key={st} value={st}>
                          {st}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      PIN Code <span className="text-rose-600">*</span>
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. 560064"
                      value={formData.currPincode}
                      onChange={(e) => handleInputChange('currPincode', e.target.value)}
                      className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Same as Current Checkbox */}
              <div className="flex items-center space-x-2 bg-blue-50 border border-blue-200 p-3 rounded-xl">
                <input
                  type="checkbox"
                  id="sameAddressCheck"
                  checked={formData.sameAsCurrentAddress}
                  onChange={(e) => handleInputChange('sameAsCurrentAddress', e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
                />
                <label htmlFor="sameAddressCheck" className="text-xs font-bold text-blue-900 cursor-pointer">
                  Permanent address is identical to current residential address
                </label>
              </div>

              {/* Permanent Address if different */}
              {!formData.sameAsCurrentAddress && (
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Permanent / Native Address</h4>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Address Line 1</label>
                    <input
                      type="text"
                      placeholder="Native home, Village / Town, Street"
                      value={formData.permAddressLine1}
                      onChange={(e) => handleInputChange('permAddressLine1', e.target.value)}
                      className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">City</label>
                      <input
                        type="text"
                        placeholder="e.g. Pune"
                        value={formData.permCity}
                        onChange={(e) => handleInputChange('permCity', e.target.value)}
                        className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">State</label>
                      <select
                        value={formData.permState}
                        onChange={(e) => handleInputChange('permState', e.target.value)}
                        className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none"
                      >
                        {INDIAN_STATES.map((st) => (
                          <option key={st} value={st}>
                            {st}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">PIN Code</label>
                      <input
                        type="text"
                        placeholder="e.g. 411007"
                        value={formData.permPincode}
                        onChange={(e) => handleInputChange('permPincode', e.target.value)}
                        className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* STEP 5: EMERGENCY CONTACT */}
          {currentStep === 5 && (
            <div className="space-y-6 max-w-4xl mx-auto">
              <div className="border-b border-slate-200 pb-3">
                <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                  <PhoneCall className="w-5 h-5 text-blue-600" />
                  <span>Step 5 — 24x7 Campus Emergency Contact</span>
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Required contact person for medical emergencies, campus safety alerts, and urgent university notices.
                </p>
              </div>

              <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
                <p className="text-xs text-rose-800 leading-relaxed">
                  This phone number is registered with the campus Health Center & Proctor Office for instant dispatch during urgent medical or security incidents.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Emergency Contact Name <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Sanjay Verma (Father)"
                    value={formData.emergencyName}
                    onChange={(e) => handleInputChange('emergencyName', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Relationship with Student <span className="text-rose-600">*</span>
                  </label>
                  <select
                    value={formData.emergencyRelation}
                    onChange={(e) => handleInputChange('emergencyRelation', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  >
                    <option value="Father">Father</option>
                    <option value="Mother">Mother</option>
                    <option value="Guardian">Local Guardian</option>
                    <option value="Sibling">Elder Brother / Sister</option>
                    <option value="Other">Other Relative</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Primary Emergency Phone (+91) <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="tel"
                    required
                    placeholder="+91 98450 12345"
                    value={formData.emergencyPhone}
                    onChange={(e) => handleInputChange('emergencyPhone', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Alternate Emergency Phone</label>
                  <input
                    type="tel"
                    placeholder="+91 98450 67890"
                    value={formData.emergencyAltPhone}
                    onChange={(e) => handleInputChange('emergencyAltPhone', e.target.value)}
                    className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>
            </div>
          )}

          {/* STEP 6: ERP & ANDROID APP ACCOUNT */}
          {currentStep === 6 && (
            <div className="space-y-6 max-w-4xl mx-auto">
              <div className="border-b border-slate-200 pb-3">
                <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                  <KeyRound className="w-5 h-5 text-blue-600" />
                  <span>Step 6 — Native Android Student App Login & Security Credentials</span>
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Configure secure authentication credentials that the student will use to log into the native Android application.
                </p>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-200">
                  <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Authentication Mechanism</span>
                  <span className="text-xs font-semibold text-emerald-700 bg-emerald-100 px-2.5 py-1 rounded-full border border-emerald-300">
                    Bcrypt Hash + JWT Token
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Android App Login Username / Handle <span className="text-rose-600">*</span>
                    </label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="text"
                        required
                        value={formData.username}
                        onChange={(e) => handleInputChange('username', e.target.value)}
                        className="w-full px-3.5 py-2 text-sm font-mono font-bold bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                      />
                      <button
                        type="button"
                        onClick={() => handleCopy(formData.username, 'username')}
                        className="p-2 text-slate-500 hover:text-slate-800 bg-white border border-slate-300 rounded-lg shadow-sm"
                        title="Copy Username"
                      >
                        {copiedField === 'username' ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>
                    <span className="text-[11px] text-slate-400 mt-0.5 block">Student can login with this username or their email.</span>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Temporary First-Login Password
                    </label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={formData.tempPassword}
                        onChange={(e) => handleInputChange('tempPassword', e.target.value)}
                        className="w-full px-3.5 py-2 text-sm font-mono font-bold bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-blue-700"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          const newPass = 'Campus@' + Math.floor(1000 + Math.random() * 9000);
                          handleInputChange('tempPassword', newPass);
                        }}
                        className="p-2 text-slate-500 hover:text-slate-800 bg-white border border-slate-300 rounded-lg shadow-sm"
                        title="Regenerate Password"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleCopy(formData.tempPassword, 'password')}
                        className="p-2 text-slate-500 hover:text-slate-800 bg-white border border-slate-300 rounded-lg shadow-sm"
                        title="Copy Password"
                      >
                        {copiedField === 'password' ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>
                    <span className="text-[11px] text-slate-400 mt-0.5 block">Student will be prompted to reset password on first launch.</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* STEP 7: DOCUMENTS & VERIFICATION */}
          {currentStep === 7 && (
            <div className="space-y-6 max-w-4xl mx-auto">
              <div className="border-b border-slate-200 pb-3">
                <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <span>Step 7 — Academic Documents & KYC Uploads</span>
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Upload verified certificates, marksheets, and official institution admission letters for compliance auditing.
                </p>
              </div>

              {/* Upload Dropzone */}
              <div className="border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-2xl p-6 text-center bg-slate-50 hover:bg-blue-50/40 transition cursor-pointer">
                <Upload className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <h4 className="text-sm font-bold text-slate-800">Upload Additional Document</h4>
                <p className="text-xs text-slate-500 mt-0.5">Drag & drop PDF, JPG, PNG files here, or browse from computer (Max 10MB)</p>
                <button
                  type="button"
                  onClick={() => {
                    const docName = prompt('Enter document title (e.g. Migration_Certificate.pdf):');
                    if (docName) {
                      setDocuments((prev) => [
                        ...prev,
                        { name: docName, type: 'PDF Document', size: '1.2 MB', status: 'Uploaded' },
                      ]);
                    }
                  }}
                  className="mt-3 px-4 py-1.5 bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-lg shadow-sm"
                >
                  Select File from Computer
                </button>
              </div>

              {/* Documents Table */}
              <div className="border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
                    <tr>
                      <th className="py-2.5 px-4">Document Title</th>
                      <th className="py-2.5 px-4">Type</th>
                      <th className="py-2.5 px-4">File Size</th>
                      <th className="py-2.5 px-4">Status</th>
                      <th className="py-2.5 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {documents.map((doc, idx) => (
                      <tr key={idx} className="hover:bg-slate-50">
                        <td className="py-2.5 px-4 font-semibold text-slate-900 flex items-center space-x-2">
                          <FileText className="w-4 h-4 text-blue-600" />
                          <span>{doc.name}</span>
                        </td>
                        <td className="py-2.5 px-4 text-slate-600">{doc.type}</td>
                        <td className="py-2.5 px-4 font-mono text-slate-500">{doc.size}</td>
                        <td className="py-2.5 px-4">
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700 border border-emerald-300">
                            {doc.status}
                          </span>
                        </td>
                        <td className="py-2.5 px-4 text-right">
                          <button
                            type="button"
                            onClick={() => setDocuments(documents.filter((_, i) => i !== idx))}
                            className="text-rose-600 hover:text-rose-800 p-1 hover:bg-rose-50 rounded"
                            title="Remove Document"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* STEP 8: REVIEW & ENROLL */}
          {currentStep === 8 && (
            <div className="space-y-6 max-w-4xl mx-auto">
              <div className="border-b border-slate-200 pb-3">
                <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  <span>Step 8 — Review & Finalize Enrollment</span>
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Please verify all student biographical, academic, contact, and credential information before finalizing registration.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* ID Card Snapshot */}
                <div className="bg-gradient-to-b from-blue-900 to-indigo-950 text-white rounded-2xl p-5 shadow-lg border border-blue-800 flex flex-col items-center text-center">
                  <span className="text-[10px] uppercase font-bold tracking-widest text-blue-300">APEX INSTITUTE OF TECHNOLOGY</span>
                  <img
                    src={formData.photo}
                    alt="Student"
                    className="w-20 h-20 rounded-xl object-cover border-2 border-white/80 my-3 shadow-md"
                  />
                  <h4 className="text-base font-bold text-white leading-tight">{formData.firstName} {formData.lastName}</h4>
                  <span className="text-xs text-blue-200 font-mono mt-0.5">{formData.rollNo}</span>

                  <div className="w-full bg-white/10 rounded-xl p-3 mt-4 text-left space-y-1.5 text-xs">
                    <div className="flex justify-between">
                      <span className="text-blue-300">Student ID:</span>
                      <span className="font-mono font-bold">{formData.studentId}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-300">Department:</span>
                      <span className="font-semibold">{departments.find((d) => d.id === formData.departmentId)?.code || 'CSE'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-300">Semester:</span>
                      <span>Semester {formData.semesterNumber}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-300">Blood Group:</span>
                      <span className="font-bold">{formData.bloodGroup}</span>
                    </div>
                  </div>
                </div>

                {/* Key Summary Cards */}
                <div className="md:col-span-2 space-y-4">
                  {/* Academic Profile */}
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
                    <h5 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-1.5">
                      <GraduationCap className="w-4 h-4 text-blue-600" />
                      <span>Academic Program & Class Allocation</span>
                    </h5>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div><span className="text-slate-500">Course:</span> <strong className="text-slate-900 block">{courses.find((c) => c.id === formData.courseId)?.name || 'B.Tech CSE'}</strong></div>
                      <div><span className="text-slate-500">Enrollment No:</span> <strong className="text-slate-900 block font-mono">{formData.enrollmentNo}</strong></div>
                      <div><span className="text-slate-500">Admission No:</span> <strong className="text-slate-900 block font-mono">{formData.admissionNo}</strong></div>
                      <div><span className="text-slate-500">Batch:</span> <strong className="text-slate-900 block">{formData.batch}</strong></div>
                    </div>
                  </div>

                  {/* Contact Summary */}
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
                    <h5 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-1.5">
                      <PhoneCall className="w-4 h-4 text-blue-600" />
                      <span>Communication & Guardian Coordinates</span>
                    </h5>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div><span className="text-slate-500">Student Phone:</span> <strong className="text-slate-900 block">{formData.mobile}</strong></div>
                      <div><span className="text-slate-500">College Email:</span> <strong className="text-slate-900 block font-mono">{formData.collegeEmail}</strong></div>
                      <div><span className="text-slate-500">Parent Name:</span> <strong className="text-slate-900 block">{formData.fatherName || formData.guardianName}</strong></div>
                      <div><span className="text-slate-500">Parent Phone:</span> <strong className="text-slate-900 block">{formData.guardianPhone}</strong></div>
                      <div className="col-span-2"><span className="text-slate-500">Address:</span> <strong className="text-slate-900 block">{formData.currAddressLine1}, {formData.currCity}, {formData.currState} - {formData.currPincode}</strong></div>
                    </div>
                  </div>

                  {/* App Credentials */}
                  <div className="bg-blue-50/70 p-4 rounded-xl border border-blue-200 space-y-1 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-blue-900 flex items-center space-x-1">
                        <KeyRound className="w-4 h-4 text-blue-700" />
                        <span>Android App Username</span>
                      </span>
                      <span className="font-mono font-bold text-blue-800 bg-white px-2 py-0.5 rounded border border-blue-200">
                        {formData.username}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 bg-slate-100 border-t border-slate-200 flex items-center justify-between">
          <div>
            {currentStep > 1 && (
              <button
                type="button"
                onClick={handlePrev}
                className="px-4 py-2 bg-white hover:bg-slate-50 text-slate-700 font-semibold rounded-xl text-xs border border-slate-300 shadow-sm flex items-center space-x-1.5 transition"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Previous Step</span>
              </button>
            )}
          </div>

          <div className="flex items-center space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-slate-600 hover:text-slate-800 text-xs font-semibold"
            >
              Cancel
            </button>

            {currentStep < 8 ? (
              <button
                type="button"
                onClick={handleNext}
                className="px-6 py-2 bg-blue-700 hover:bg-blue-800 text-white font-bold rounded-xl text-xs shadow-md flex items-center space-x-1.5 transition"
              >
                <span>Save & Continue</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleFinalSubmit}
                className="px-7 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs shadow-lg flex items-center space-x-2 transition ring-2 ring-emerald-500/30"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>{isEditing ? 'Update Student Record' : 'Complete & Enroll Student'}</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
