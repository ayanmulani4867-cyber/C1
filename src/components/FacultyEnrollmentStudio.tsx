import React, { useState } from 'react';
import { useErp } from '../context/ErpContext';
import { Faculty } from '../types';
import {
  User,
  Users,
  Building2,
  BookOpen,
  MapPin,
  PhoneCall,
  KeyRound,
  ShieldCheck,
  CheckCircle2,
  Upload,
  RefreshCw,
  Copy,
  Check,
  ChevronRight,
  ChevronLeft,
  X,
} from 'lucide-react';

interface FacultyEnrollmentStudioProps {
  initialFaculty?: Faculty | null;
  onClose: () => void;
  onSuccess?: (faculty: Faculty) => void;
}

export const FacultyEnrollmentStudio: React.FC<FacultyEnrollmentStudioProps> = ({
  initialFaculty,
  onClose,
  onSuccess,
}) => {
  const { departments, subjects, addFaculty, updateFaculty, faculty } = useErp();

  const isEditing = Boolean(initialFaculty);
  const [currentStep, setCurrentStep] = useState(1);
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    photo: initialFaculty?.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200',
    firstName: initialFaculty?.firstName || '',
    lastName: initialFaculty?.lastName || '',
    facultyId: initialFaculty?.facultyId || `FAC-CSE-0${faculty.length + 10}`,
    employeeId: initialFaculty?.employeeId || `EMP-${1090 + faculty.length + 1}`,
    departmentId: initialFaculty?.departmentId || departments[0]?.id || 'dept-cse',
    designation: (initialFaculty?.designation || 'Assistant Professor') as any,
    employmentType: (initialFaculty?.employmentType || 'Permanent') as any,
    dateOfJoining: initialFaculty?.dateOfJoining || new Date().toISOString().split('T')[0],
    qualification: initialFaculty?.qualification || 'Ph.D. in Computer Science (IIT Bombay)',
    specialization: initialFaculty?.specialization || 'Distributed Computing, Artificial Intelligence',
    experienceYears: initialFaculty?.experienceYears || 6,
    officialEmail: initialFaculty?.officialEmail || '',
    personalEmail: initialFaculty?.personalEmail || '',
    mobile: initialFaculty?.mobile || '+91 98450 91823',
    gender: (initialFaculty?.gender || 'Male') as any,
    bloodGroup: initialFaculty?.bloodGroup || 'O+',
    roomOffice: initialFaculty?.roomOffice || 'Cabin 304, Academic Block-B',
    status: (initialFaculty?.status || 'Active') as any,
    username: initialFaculty?.officialEmail
      ? initialFaculty.officialEmail.split('@')[0]
      : `fac_${faculty.length + 1}`,
    tempPassword: 'Faculty@' + Math.floor(1000 + Math.random() * 9000),
  });

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleCopy = (text: string, fieldName: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(fieldName);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }

    if (!formData.firstName || !formData.lastName) {
      setErrorMessage('Please fill out first name and last name.');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    const payload: any = {
      facultyId: formData.facultyId,
      employeeId: formData.employeeId,
      firstName: formData.firstName,
      lastName: formData.lastName,
      fullName: `Prof. ${formData.firstName} ${formData.lastName}`,
      dob: '1985-06-20',
      gender: formData.gender,
      bloodGroup: formData.bloodGroup,
      officialEmail:
        formData.officialEmail ||
        `${formData.firstName.toLowerCase()}.${formData.lastName.toLowerCase()}@apex.edu`,
      personalEmail:
        formData.personalEmail ||
        `${formData.firstName.toLowerCase()}@gmail.com`,
      mobile: formData.mobile,
      departmentId: formData.departmentId,
      designation: formData.designation,
      employmentType: formData.employmentType,
      dateOfJoining: formData.dateOfJoining,
      qualification: formData.qualification,
      specialization: formData.specialization,
      experienceYears: Number(formData.experienceYears),
      photo: formData.photo,
      status: formData.status,
      roomOffice: formData.roomOffice,
    };

    try {
      let resultFaculty: Faculty;

      if (isEditing && initialFaculty) {
        updateFaculty(initialFaculty.id, payload);
        resultFaculty = { ...initialFaculty, ...payload };
      } else {
        resultFaculty = await addFaculty(payload);
      }

      if (onSuccess) {
        onSuccess(resultFaculty);
      }

      onClose();
    } catch (error: any) {
      console.error('Faculty creation failed:', error);
      setErrorMessage(error?.message || 'Faculty could not be saved. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[94vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-150">

        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-purple-600 text-white flex items-center justify-center shadow-md">
              <Users className="w-6 h-6" />
            </div>

            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">
                {isEditing
                  ? `Edit Faculty Profile — Prof. ${formData.firstName} ${formData.lastName}`
                  : 'Faculty Onboarding & Academic Appointment'}
              </h2>

              <p className="text-xs text-slate-400">
                Apex Institute of Technology & Science • Faculty Affairs Desk
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-white px-3 py-1.5 rounded-lg text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 transition"
          >
            Cancel
          </button>
        </div>

        {/* Form Body */}
        <form
          onSubmit={handleSubmit}
          className="flex-1 overflow-y-auto p-6 sm:p-8 bg-white space-y-6"
        >

          {/* Photo & Basic Details */}
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-6">
            <img
              src={formData.photo}
              alt="Faculty Avatar"
              className="w-20 h-20 rounded-2xl object-cover border-2 border-purple-500 shadow-md bg-white"
            />

            <div className="flex-1 text-center sm:text-left space-y-1">
              <h4 className="text-sm font-bold text-slate-900">
                Faculty Official Photograph
              </h4>

              <p className="text-xs text-slate-500">
                Official image displayed on faculty directory and course assignments.
              </p>

              <div className="pt-2 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => {
                    const avatars = [
                      'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200',
                      'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=200',
                      'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=200',
                      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200',
                    ];

                    handleInputChange(
                      'photo',
                      avatars[Math.floor(Math.random() * avatars.length)]
                    );
                  }}
                  className="px-3 py-1 bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-lg shadow-sm flex items-center space-x-1"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>Choose Sample Photo</span>
                </button>
              </div>
            </div>
          </div>

          {/* Name & Identifiers */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">

            <div className="sm:col-span-2">
              <label className="block text-xs font-bold text-slate-700 mb-1">
                First Name <span className="text-rose-600">*</span>
              </label>

              <input
                type="text"
                required
                placeholder="e.g. Meenakshi"
                value={formData.firstName}
                onChange={(e) =>
                  handleInputChange('firstName', e.target.value)
                }
                className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Last Name <span className="text-rose-600">*</span>
              </label>

              <input
                type="text"
                required
                placeholder="e.g. Sundaram"
                value={formData.lastName}
                onChange={(e) =>
                  handleInputChange('lastName', e.target.value)
                }
                className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>
          </div>

          {/* Employee ID, Dept, Designation */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Employee ID <span className="text-rose-600">*</span>
              </label>

              <input
                type="text"
                required
                value={formData.employeeId}
                onChange={(e) =>
                  handleInputChange('employeeId', e.target.value)
                }
                className="w-full px-3.5 py-2 text-sm font-mono font-bold border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Department <span className="text-rose-600">*</span>
              </label>

              <select
                value={formData.departmentId}
                onChange={(e) =>
                  handleInputChange('departmentId', e.target.value)
                }
                className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
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
                Designation <span className="text-rose-600">*</span>
              </label>

              <select
                value={formData.designation}
                onChange={(e) =>
                  handleInputChange('designation', e.target.value)
                }
                className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
              >
                <option value="Professor & HOD">Professor & HOD</option>
                <option value="Professor">Professor</option>
                <option value="Associate Professor">
                  Associate Professor
                </option>
                <option value="Assistant Professor">
                  Assistant Professor
                </option>
                <option value="Visiting Faculty">Visiting Faculty</option>
              </select>
            </div>
          </div>

          {/* Academic Qualifications & Specialization */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Highest Qualification
              </label>

              <input
                type="text"
                placeholder="e.g. Ph.D. in Computer Science (IISc Bangalore)"
                value={formData.qualification}
                onChange={(e) =>
                  handleInputChange('qualification', e.target.value)
                }
                className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Research Specialization
              </label>

              <input
                type="text"
                placeholder="e.g. Cloud Security, Natural Language Processing"
                value={formData.specialization}
                onChange={(e) =>
                  handleInputChange('specialization', e.target.value)
                }
                className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>
          </div>

          {/* Contacts & Office */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Official Email <span className="text-rose-600">*</span>
              </label>

              <input
                type="email"
                required
                placeholder="name@apex.edu"
                value={formData.officialEmail}
                onChange={(e) =>
                  handleInputChange('officialEmail', e.target.value)
                }
                className="w-full px-3.5 py-2 text-sm font-mono border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Mobile (+91) <span className="text-rose-600">*</span>
              </label>

              <input
                type="tel"
                required
                placeholder="+91 98450 12345"
                value={formData.mobile}
                onChange={(e) =>
                  handleInputChange('mobile', e.target.value)
                }
                className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Faculty Cabin / Office Room
              </label>

              <input
                type="text"
                placeholder="e.g. Room 204, CSE Block"
                value={formData.roomOffice}
                onChange={(e) =>
                  handleInputChange('roomOffice', e.target.value)
                }
                className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>
          </div>

          {errorMessage && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs font-semibold text-red-700">
              {errorMessage}
            </div>
          )}

          {/* Footer Submit */}
          <div className="pt-4 border-t border-slate-200 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-slate-600 hover:text-slate-800 text-xs font-semibold disabled:opacity-50"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2.5 bg-purple-700 hover:bg-purple-800 text-white font-bold rounded-xl text-xs shadow-md flex items-center space-x-2 transition disabled:opacity-50"
            >
              {isSubmitting ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <CheckCircle2 className="w-4 h-4" />
              )}
              <span>
                {isSubmitting
                  ? 'Saving to Database...'
                  : isEditing
                  ? 'Update Faculty Profile'
                  : 'Complete Faculty Appointment'}
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
