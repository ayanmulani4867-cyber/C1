import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { Layers, Plus, BookOpen, Users, GraduationCap, X, Check } from 'lucide-react';

export const DepartmentsView: React.FC = () => {
  const { departments, courses, faculty, students, subjects, addDepartment, addCourse } = useErp();

  const [activeTab, setActiveTab] = useState<'DEPTS' | 'COURSES' | 'SUBJECTS'>('DEPTS');
  const [showAddDeptModal, setShowAddDeptModal] = useState(false);
  const [showAddCourseModal, setShowAddCourseModal] = useState(false);

  // New Dept Form
  const [deptForm, setDeptForm] = useState({
    name: '',
    code: '',
    description: '',
    hodName: '',
    establishedYear: 2020,
    color: '#2563eb',
  });

  // New Course Form
  const [courseForm, setCourseForm] = useState({
    name: '',
    code: '',
    departmentId: departments[0]?.id || 'dept-cse',
    durationYears: 4,
    totalSemesters: 8,
    degreeType: 'Undergraduate' as const,
    tuitionFeePerSem: 60000,
  });

  const handleCreateDept = (e: React.FormEvent) => {
    e.preventDefault();
    if (!deptForm.name || !deptForm.code) return;
    addDepartment({
      ...deptForm,
      isActive: true,
    });
    setShowAddDeptModal(false);
    setDeptForm({ name: '', code: '', description: '', hodName: '', establishedYear: 2020, color: '#2563eb' });
  };

  const handleCreateCourse = (e: React.FormEvent) => {
    e.preventDefault();
    if (!courseForm.name || !courseForm.code) return;
    addCourse({
      ...courseForm,
      isActive: true,
    });
    setShowAddCourseModal(false);
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Academic Structure & Curriculum</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Departments, Degree Programs, and Semester Curriculum
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowAddDeptModal(true)}
            className="px-3.5 py-2 text-xs font-bold text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 rounded-xl transition-colors flex items-center space-x-1.5 shadow-2xs"
          >
            <Plus className="w-4 h-4 text-blue-600" />
            <span>Add Department</span>
          </button>
          <button
            onClick={() => setShowAddCourseModal(true)}
            className="px-4 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs transition-colors flex items-center space-x-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>Add Degree Course</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab('DEPTS')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'DEPTS' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Departments ({departments.length})
        </button>
        <button
          onClick={() => setActiveTab('COURSES')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'COURSES' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Degree Programs ({courses.length})
        </button>
        <button
          onClick={() => setActiveTab('SUBJECTS')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'SUBJECTS' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Curriculum Subjects ({subjects.length})
        </button>
      </div>

      {/* Tab: Departments */}
      {activeTab === 'DEPTS' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {departments.map((dept) => {
            const deptFaculty = faculty.filter((f) => f.departmentId === dept.id);
            const deptStudents = students.filter((s) => s.departmentId === dept.id);
            const deptCourses = courses.filter((c) => c.departmentId === dept.id);

            return (
              <div
                key={dept.id}
                className="bg-white rounded-2xl border border-slate-200 p-6 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span
                      className="px-2.5 py-1 rounded-lg text-xs font-extrabold text-white tracking-wider"
                      style={{ backgroundColor: dept.color }}
                    >
                      {dept.code}
                    </span>
                    <span className="text-xs font-bold text-slate-400">Est. {dept.establishedYear}</span>
                  </div>

                  <h3 className="text-base font-extrabold text-slate-900 mt-3">{dept.name}</h3>
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">{dept.description}</p>

                  <div className="mt-4 p-3 bg-slate-50 rounded-xl border border-slate-100 space-y-1 text-xs">
                    <div className="text-slate-600">
                      HOD / Head of Department:{' '}
                      <strong className="text-slate-900">{dept.hodName || 'Dr. Arthur Sterling'}</strong>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 pt-4 mt-4 border-t border-slate-100 text-center text-xs">
                  <div className="bg-slate-50 p-2 rounded-xl">
                    <span className="font-extrabold text-slate-900 block text-sm">{deptCourses.length}</span>
                    <span className="text-[10px] text-slate-400 font-semibold">Programs</span>
                  </div>
                  <div className="bg-slate-50 p-2 rounded-xl">
                    <span className="font-extrabold text-slate-900 block text-sm">{deptFaculty.length}</span>
                    <span className="text-[10px] text-slate-400 font-semibold">Faculty</span>
                  </div>
                  <div className="bg-slate-50 p-2 rounded-xl">
                    <span className="font-extrabold text-slate-900 block text-sm">{deptStudents.length}</span>
                    <span className="text-[10px] text-slate-400 font-semibold">Students</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Tab: Courses */}
      {activeTab === 'COURSES' && (
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-2xs">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3 px-4">Program Name</th>
                  <th className="py-3 px-4">Code</th>
                  <th className="py-3 px-4">Department</th>
                  <th className="py-3 px-4">Duration / Sems</th>
                  <th className="py-3 px-4">Degree Level</th>
                  <th className="py-3 px-4">Tuition Fee / Sem</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {courses.map((course) => {
                  const dept = departments.find((d) => d.id === course.departmentId);
                  return (
                    <tr key={course.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-4 font-bold text-slate-900">{course.name}</td>
                      <td className="py-3 px-4 font-mono font-bold text-blue-700">{course.code}</td>
                      <td className="py-3 px-4 text-slate-700">{dept?.name || 'Department'}</td>
                      <td className="py-3 px-4 text-slate-700 font-medium">
                        {course.durationYears} Years ({course.totalSemesters} Semesters)
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-800 border border-blue-200">
                          {course.degreeType}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-bold text-slate-900">
                        ${course.tuitionFeePerSem.toLocaleString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab: Subjects */}
      {activeTab === 'SUBJECTS' && (
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-2xs">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3 px-4">Subject Name</th>
                  <th className="py-3 px-4">Code</th>
                  <th className="py-3 px-4">Credits</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Semester</th>
                  <th className="py-3 px-4">Assigned Faculty</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {subjects.map((sub) => {
                  const assignedFac = faculty.filter((f) => sub.assignedFacultyIds.includes(f.id));
                  return (
                    <tr key={sub.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-4 font-bold text-slate-900">{sub.name}</td>
                      <td className="py-3 px-4 font-mono font-bold text-blue-700">{sub.code}</td>
                      <td className="py-3 px-4 font-bold text-slate-800">{sub.credits} Credits</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          sub.type === 'Practical' ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800'
                        }`}>
                          {sub.type}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-700 font-medium">Semester {sub.semesterNumber}</td>
                      <td className="py-3 px-4 text-slate-700">
                        {assignedFac.map((f) => f.fullName).join(', ') || 'Staff Allocated'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Dept Modal */}
      {showAddDeptModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-extrabold text-base text-slate-900">Add Academic Department</h3>
              <button onClick={() => setShowAddDeptModal(false)} className="p-1 text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreateDept} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Department Name *</label>
                <input
                  type="text"
                  required
                  value={deptForm.name}
                  onChange={(e) => setDeptForm({ ...deptForm, name: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="e.g. Civil & Environmental Engineering"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Dept Code *</label>
                  <input
                    type="text"
                    required
                    value={deptForm.code}
                    onChange={(e) => setDeptForm({ ...deptForm, code: e.target.value.toUpperCase() })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                    placeholder="e.g. CIVIL"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Established Year</label>
                  <input
                    type="number"
                    value={deptForm.establishedYear}
                    onChange={(e) => setDeptForm({ ...deptForm, establishedYear: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Head of Department (HOD) Name</label>
                <input
                  type="text"
                  value={deptForm.hodName}
                  onChange={(e) => setDeptForm({ ...deptForm, hodName: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="Dr. Full Name"
                />
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Description</label>
                <textarea
                  rows={2}
                  value={deptForm.description}
                  onChange={(e) => setDeptForm({ ...deptForm, description: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddDeptModal(false)}
                  className="px-4 py-2 font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs"
                >
                  Save Department
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Course Modal */}
      {showAddCourseModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-extrabold text-base text-slate-900">Add Degree Program</h3>
              <button onClick={() => setShowAddCourseModal(false)} className="p-1 text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreateCourse} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Course / Degree Name *</label>
                <input
                  type="text"
                  required
                  value={courseForm.name}
                  onChange={(e) => setCourseForm({ ...courseForm, name: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="e.g. Master of Computer Applications (MCA)"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Course Code *</label>
                  <input
                    type="text"
                    required
                    value={courseForm.code}
                    onChange={(e) => setCourseForm({ ...courseForm, code: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                    placeholder="MCA"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Department</label>
                  <select
                    value={courseForm.departmentId}
                    onChange={(e) => setCourseForm({ ...courseForm, departmentId: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  >
                    {departments.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Duration (Years)</label>
                  <input
                    type="number"
                    value={courseForm.durationYears}
                    onChange={(e) => setCourseForm({ ...courseForm, durationYears: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Tuition Fee / Sem ($)</label>
                  <input
                    type="number"
                    value={courseForm.tuitionFeePerSem}
                    onChange={(e) => setCourseForm({ ...courseForm, tuitionFeePerSem: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddCourseModal(false)}
                  className="px-4 py-2 font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs"
                >
                  Save Program
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
