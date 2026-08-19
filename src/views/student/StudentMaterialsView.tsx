import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { BookOpen, Download, FileText, FileCode, Presentation, Search } from 'lucide-react';
import { StudyMaterial } from '../../types';

export const StudentMaterialsView: React.FC = () => {
  const { studyMaterials, subjects } = useErp();

  const [selectedSubjectFilter, setSelectedSubjectFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredMaterials = studyMaterials.filter((m) => {
    const matchesSub = selectedSubjectFilter === 'ALL' || m.subjectId === selectedSubjectFilter;
    const matchesSearch =
      m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSub && matchesSearch;
  });

  const getIcon = (type: StudyMaterial['fileType']) => {
    switch (type) {
      case 'PDF':
        return <FileText className="w-5 h-5 text-rose-600" />;
      case 'PPT':
        return <Presentation className="w-5 h-5 text-amber-600" />;
      case 'Code':
        return <FileCode className="w-5 h-5 text-blue-600" />;
      default:
        return <FileText className="w-5 h-5 text-slate-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Study Materials & Lecture Notes</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Unit-wise curated lecture notes, presentation slides, reference code, and past year papers
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2">
        <button
          onClick={() => setSelectedSubjectFilter('ALL')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
            selectedSubjectFilter === 'ALL'
              ? 'bg-blue-600 text-white shadow-xs'
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
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {sub.code} - {sub.name}
          </button>
        ))}
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredMaterials.map((mat) => {
          const sub = subjects.find((s) => s.id === mat.subjectId);

          return (
            <div
              key={mat.id}
              className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2.5">
                    <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">{getIcon(mat.fileType)}</div>
                    <div>
                      <span className="font-mono text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                        {sub?.code}
                      </span>
                      <span className="ml-2 text-xs font-semibold text-slate-500">Unit {mat.unitNumber}</span>
                    </div>
                  </div>
                  <span className="text-[10px] font-bold text-slate-400">
                    {(mat.fileSizeBytes / (1024 * 1024)).toFixed(1)} MB
                  </span>
                </div>

                <h4 className="font-extrabold text-sm text-slate-900 mt-3">{mat.title}</h4>
                <p className="text-xs text-slate-600 mt-1 line-clamp-2">{mat.description}</p>
              </div>

              <div className="pt-4 mt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] text-slate-400">By {mat.uploadedBy}</span>
                <a
                  href={mat.fileUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3.5 py-1.5 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs transition-colors inline-flex items-center space-x-1.5"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download</span>
                </a>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
