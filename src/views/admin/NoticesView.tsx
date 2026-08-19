import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { Megaphone, Plus, Pin, Trash2, Calendar, Tag, X } from 'lucide-react';
import { Notice } from '../../types';

export const NoticesView: React.FC = () => {
  const { notices, addNotice, deleteNotice, currentUser } = useErp();

  const [showAddModal, setShowAddModal] = useState(false);
  const [filterCategory, setFilterCategory] = useState<string>('ALL');

  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: 'Academic' as Notice['category'],
    targetAudience: 'All' as Notice['targetAudience'],
    priority: 'Normal' as Notice['priority'],
    isPinned: false,
    expiryDate: '2026-06-30',
  });

  const filteredNotices = notices.filter((n) => {
    return filterCategory === 'ALL' || n.category === filterCategory;
  });

  const handleCreateNotice = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title || !formData.content) return;

    addNotice({
      ...formData,
      publishedBy: currentUser.fullName || currentUser.name || 'Administration',
      publishedAt: new Date().toISOString().split('T')[0],
    });

    setShowAddModal(false);
    setFormData({
      title: '',
      content: '',
      category: 'Academic',
      targetAudience: 'All',
      priority: 'Normal',
      isPinned: false,
      expiryDate: '2026-06-30',
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Campus Notice Board & Circulars</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Broadcast official circulars, exam notifications, placement alerts, and holiday calendars
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs transition-colors flex items-center space-x-1.5 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Publish New Notice</span>
        </button>
      </div>

      {/* Category Filter Chips */}
      <div className="flex flex-wrap items-center gap-2">
        {['ALL', 'Academic', 'Examination', 'Fee', 'Placement', 'General', 'Sports'].map((cat) => (
          <button
            key={cat}
            onClick={() => setFilterCategory(cat)}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
              filterCategory === cat
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {cat === 'ALL' ? 'All Categories' : cat}
          </button>
        ))}
      </div>

      {/* Notices Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredNotices.map((notice) => (
          <div
            key={notice.id}
            className={`bg-white rounded-2xl border p-5 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between ${
              notice.isPinned ? 'border-amber-300 ring-2 ring-amber-500/10' : 'border-slate-200'
            }`}
          >
            <div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-50 text-blue-800 border border-blue-200">
                    {notice.category}
                  </span>
                  <span className="text-[10px] font-bold text-slate-400">Audience: {notice.targetAudience}</span>
                </div>

                {notice.isPinned && (
                  <span className="inline-flex items-center space-x-1 text-[10px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full">
                    <Pin className="w-3 h-3" />
                    <span>Pinned</span>
                  </span>
                )}
              </div>

              <h4 className="font-extrabold text-sm text-slate-900 mt-2.5">{notice.title}</h4>
              <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">{notice.content}</p>
            </div>

            <div className="flex items-center justify-between pt-4 mt-3 border-t border-slate-100 text-[11px] text-slate-400">
              <span>
                By <strong>{notice.publishedBy}</strong> • {notice.publishedAt}
              </span>
              <button
                onClick={() => deleteNotice(notice.id)}
                className="p-1 text-slate-400 hover:text-rose-600 rounded transition-colors"
                title="Delete Notice"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Publish Notice Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-extrabold text-base text-slate-900">Publish Campus Notice</h3>
              <button onClick={() => setShowAddModal(false)} className="p-1 text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreateNotice} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Notice Title *</label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="e.g. Schedule for Mid-Term Examinations Spring 2026"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Category</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value as any })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  >
                    <option value="Academic">Academic</option>
                    <option value="Examination">Examination</option>
                    <option value="Fee">Fee</option>
                    <option value="Placement">Placement</option>
                    <option value="General">General</option>
                    <option value="Sports">Sports</option>
                  </select>
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Target Audience</label>
                  <select
                    value={formData.targetAudience}
                    onChange={(e) => setFormData({ ...formData, targetAudience: e.target.value as any })}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  >
                    <option value="All">All Campus</option>
                    <option value="Students">Students Only</option>
                    <option value="Faculty">Faculty Only</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Notice Content *</label>
                <textarea
                  rows={4}
                  required
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl"
                  placeholder="Enter full circular details..."
                />
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="pin-notice"
                  checked={formData.isPinned}
                  onChange={(e) => setFormData({ ...formData, isPinned: e.target.checked })}
                  className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="pin-notice" className="font-semibold text-slate-700">
                  Pin this circular to top of dashboard
                </label>
              </div>
              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-xs"
                >
                  Publish Notice
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
