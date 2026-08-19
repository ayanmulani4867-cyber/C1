import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { BookOpen, Plus, Download, FileText, FileCode, Presentation, X } from 'lucide-react';
import { StudyMaterial } from '../../types';

export const StudyMaterialsView: React.FC = () => {
  const { studyMaterials, subjects, currentUser, addStudyMaterial } = useErp();

  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedSubjectFilter, setSelectedSubjectFilter] = useState<string>('ALL');

  const [form, setForm] = useState({
    title: '',
    description: '',
    subjectId: subjects[0]?.id || 'sub-dbms',
    unitNumber: 1,
    fileType: 'PDF' as StudyMaterial['fileType'],
    fileUrl: 'https://apex.edu/materials/lecture-notes.pdf',
    fileSizeBytes: 3450000,
  });

  const filteredMaterials = studyMaterials.filter((m) => {
    return selectedSubjectFilter === 'ALL' || m.subjectId === selectedSubjectFilter;
  });

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title) return;

    addStudyMaterial({
      ...form,
      uploadedBy: currentUser.fullName || currentUser.name || 'Faculty',
      uploadedAt: new Date().toISOString().split('T')[0],
      downloadCount: 0,
    });

    setShowUploadModal(false);
  };

  const getIcon = (type: StudyMaterial['fileType']) => {
    switch (type) {
      case 'PDF':
        return <FileText className="w-6 h-6 text-rose-600" />;
      case 'PPT':
        return <Presentation className="w-6 h-6 text-amber-600" />;
      case 'Code':
        return <FileCode className="w-6 h-6 text-blue-600" />;
      default:
        return <FileText className="w-6 h-6 text-slate-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Academic Study Material Repository</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Unit-wise lecture notes, slide presentations, question banks, and source code packages
          </p>
        </div>

        <button
          onClick={() => setShowUploadModal(true)}
          className="px-4 py-2 text-xs font-bold text-white bg-purple-600 hover:bg-purple-700 rounded-xl shadow-xs transition-colors flex items-center space-x-1.5 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Upload Study Material</span>
        </button>
      </div>

      {/* Subject Filter Bar */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2">
        <button
          onClick={() => setSelectedSubjectFilter('ALL')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
            selectedSubjectFilter === 'ALL'
              ? 'bg-purple-600 text-white shadow-xs'
              : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
          }`}
        >
          All Subjects
        </button>
        {subjects.map((sub) => (
          <button
            key={sub.id}
            onClick={() => setSelectedSubjectFilter(sub.id)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
              selectedSubjectFilter === sub.id
                ? 'bg-purple-600 text-white shadow-xs'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {sub.code} - {sub.name}
          </button>
        ))}
      </div>

      {/* Materials Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredMaterials.map((material) => {
          const sub = subjects.find((s) => s.id === material.subjectId);

          return (
            <div
              key={material.id}
              className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">{getIcon(material.fileType)}</div>
                    <div>
                      <span className="font-mono text-[10px] font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
                        {sub?.code}
                      </span>
                      <span className="ml-2 text-xs font-semibold text-slate-500">Unit {material.unitNumber}</span>
                    </div>
                  </div>
                  <span className="text-[10px] font-bold text-slate-400">
                    {(material.fileSizeBytes / (1024 * 1024)).toFixed(1)} MB
                  </span>
                </div>

                <h4 className="font-bold text-sm text-slate-900 mt-3">{material.title}</h4>
                <p className="text-xs text-slate-600 mt-1 line-clamp-2">{material.description}</p>
              </div>

              <div className="pt-4 mt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] text-slate-400">By {material.uploadedBy}</span>
                <a
                  href={material.fileUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3 py-1.5 text-xs font-bold text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-xl transition-colors inline-flex items-center space-x-1"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download</span>
                </a>
              </div>
            </div>
          );
        })}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-extrabold text-base text-slate-900">Upload Learning Resource</h3>
              <button onClick={() => setShowUploadModal(false)} className="p-1 text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleUpload} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Resource Title *</label>
                <input
                  type="text"
                  required
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="e.g. Unit 3 - B-Trees, Hashing & Storage Architecture"
                />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Subject</label>
                  <select
                    value={form.subjectId}
                    onChange={(e) => setForm({ ...form, subjectId: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  >
                    {subjects.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Unit Number</label>
                  <select
                    value={form.unitNumber}
                    onChange={(e) => setForm({ ...form, unitNumber: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  >
                    {[1, 2, 3, 4, 5, 6].map((u) => (
                      <option key={u} value={u}>
                        Unit {u}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Format</label>
                  <select
                    value={form.fileType}
                    onChange={(e) => setForm({ ...form, fileType: e.target.value as any })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  >
                    <option value="PDF">PDF Notes</option>
                    <option value="PPT">PowerPoint Slides</option>
                    <option value="Code">Source Code</option>
                    <option value="DOC">Word Document</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Topic Summary</label>
                <textarea
                  rows={2}
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-bold text-white bg-purple-600 hover:bg-purple-700 rounded-xl shadow-xs"
                >
                  Publish Resource
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
