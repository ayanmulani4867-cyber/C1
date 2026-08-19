import React, { useState } from 'react';
import { useErp } from '../context/ErpContext';
import { CommandPaletteModal } from './CommandPaletteModal';
import {
  GraduationCap,
  Bell,
  CheckCheck,
  RotateCcw,
  Shield,
  UserCheck,
  BookOpen,
  User,
  LogOut,
  ChevronDown,
  Sparkles,
  Building2,
  Search,
  Users,
} from 'lucide-react';

interface NavbarProps {
  currentView?: string;
  setCurrentView?: (view: string) => void;
  onOpenIdCard?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentView: propCurrentView, setCurrentView: propSetCurrentView, onOpenIdCard }) => {
  const {
    currentUser,
    logout,
    notifications,
    markNotificationRead,
    markAllNotificationsRead,
    resetToFactoryDefaults,
    currentView: ctxCurrentView,
    setCurrentView: ctxSetCurrentView,
    availableUsers,
    switchUser,
  } = useErp();

  const currentView = propCurrentView || ctxCurrentView;
  const setCurrentView = propSetCurrentView || ctxSetCurrentView;

  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showRoleSwitcher, setShowRoleSwitcher] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [isCommandOpen, setIsCommandOpen] = useState(false);

  const unreadNotifs = notifications.filter((n) => !n.isRead);

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'ADMIN':
        return { label: 'Admin / Director', bg: 'bg-rose-100 text-rose-800 border-rose-200', icon: Shield };
      case 'HOD':
        return { label: 'HOD / Dept Head', bg: 'bg-purple-100 text-purple-800 border-purple-200', icon: UserCheck };
      case 'FACULTY':
        return { label: 'Faculty / Professor', bg: 'bg-blue-100 text-blue-800 border-blue-200', icon: BookOpen };
      case 'STUDENT':
        return { label: 'Student Portal', bg: 'bg-emerald-100 text-emerald-800 border-emerald-200', icon: GraduationCap };
      default:
        return { label: role, bg: 'bg-slate-100 text-slate-800 border-slate-200', icon: User };
    }
  };

  const badgeInfo = getRoleBadge(currentUser.role);
  const BadgeIcon = badgeInfo.icon;

  return (
    <>
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-2xs">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Brand & Institution Info */}
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-600 text-white shadow-md shadow-blue-500/20">
                <GraduationCap className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-extrabold text-lg text-slate-900 tracking-tight">Campus Connect</span>
                  <span className="hidden md:inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200/60">
                    ERP Production
                  </span>
                </div>
                <p className="text-xs text-slate-500 hidden sm:block font-medium">Apex Institute of Technology & Science (AITS)</p>
              </div>
            </div>

            {/* Quick Command Search Bar Button */}
            <button
              id="btn-quick-search-palette"
              onClick={() => setIsCommandOpen(true)}
              className="hidden md:flex items-center space-x-2 px-3.5 py-1.5 bg-slate-100/80 hover:bg-slate-100 border border-slate-200 rounded-xl text-slate-500 text-xs transition-colors group cursor-pointer max-w-xs w-full lg:w-64"
            >
              <Search className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600 transition-colors" />
              <span className="flex-1 text-left">Quick search or navigate...</span>
              <kbd className="hidden lg:inline-flex items-center px-1.5 py-0.5 text-[10px] font-mono font-medium text-slate-400 bg-white border border-slate-200 rounded">
                ⌘K
              </kbd>
            </button>

            {/* Institutional Status Info */}
            <div className="hidden 2xl:flex items-center space-x-3 px-3 py-1.5 bg-slate-50 rounded-xl border border-slate-200/80 text-xs text-slate-600">
              <div className="flex items-center space-x-1.5 font-semibold text-slate-700">
                <Building2 className="w-3.5 h-3.5 text-blue-600" />
                <span>Campus Portal</span>
              </div>
              <span className="text-slate-300">•</span>
              <span>Academic Year 2025–2026</span>
              <span className="text-slate-300">•</span>
              <span className="inline-flex items-center text-emerald-600 font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse" />
                PostgreSQL Sync
              </span>
            </div>

            {/* Right Actions */}
            <div className="flex items-center space-x-2 sm:space-x-3">
              {/* Quick Search icon on mobile */}
              <button
                onClick={() => setIsCommandOpen(true)}
                className="md:hidden p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
                title="Search"
              >
                <Search className="w-5 h-5" />
              </button>

              {/* Active Role Indicator & Quick Switcher Button */}
              <button
                id="btn-switch-role-menu"
                onClick={() => setShowRoleSwitcher(!showRoleSwitcher)}
                className={`hidden sm:flex items-center space-x-1.5 px-3 py-1 rounded-full border text-xs font-semibold hover:opacity-90 transition-opacity cursor-pointer ${badgeInfo.bg}`}
                title="Click to Switch Demo Account"
              >
                <BadgeIcon className="w-3.5 h-3.5" />
                <span>{badgeInfo.label}</span>
                <ChevronDown className="w-3 h-3 opacity-60" />
              </button>

              {/* Quick ID Card Modal Button (Student or Faculty) */}
              {onOpenIdCard && (currentUser.role === 'STUDENT' || currentUser.role === 'FACULTY' || currentUser.role === 'HOD') && (
                <button
                  id="btn-digital-id-card"
                  onClick={onOpenIdCard}
                  title="View Digital ID Card"
                  className="hidden md:flex items-center space-x-1 px-3 py-1.5 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors cursor-pointer"
                >
                  <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                  <span>Digital ID</span>
                </button>
              )}

              {/* Notifications Dropdown */}
              <div className="relative">
                <button
                  id="btn-notifications-toggle"
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="relative p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors focus:outline-none cursor-pointer"
                  aria-label="Notifications"
                >
                  <Bell className="w-5 h-5" />
                  {unreadNotifs.length > 0 && (
                    <span className="absolute top-1 right-1 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold text-white bg-rose-500 rounded-full ring-2 ring-white animate-pulse">
                      {unreadNotifs.length}
                    </span>
                  )}
                </button>

                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-2xl shadow-xl border border-slate-200 py-2 z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150">
                    <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-100">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-sm text-slate-800">Notifications</span>
                        <span className="px-2 py-0.5 text-[11px] font-bold bg-slate-100 text-slate-600 rounded-full">
                          {notifications.length}
                        </span>
                      </div>
                      {unreadNotifs.length > 0 && (
                        <button
                          onClick={markAllNotificationsRead}
                          className="text-xs text-blue-600 hover:text-blue-700 font-medium flex items-center space-x-1 cursor-pointer"
                        >
                          <CheckCheck className="w-3.5 h-3.5" />
                          <span>Mark all read</span>
                        </button>
                      )}
                    </div>

                    <div className="max-h-80 overflow-y-auto divide-y divide-slate-100">
                      {notifications.length === 0 ? (
                        <div className="px-4 py-8 text-center text-slate-400 text-xs">
                          No notifications to display
                        </div>
                      ) : (
                        notifications.map((notif) => (
                          <div
                            key={notif.id}
                            onClick={() => {
                              markNotificationRead(notif.id);
                              if (notif.link) {
                                setCurrentView(notif.link);
                                setShowNotifications(false);
                              }
                            }}
                            className={`p-3 text-left transition-colors cursor-pointer hover:bg-slate-50 flex items-start space-x-3 ${
                              !notif.isRead ? 'bg-blue-50/50' : ''
                            }`}
                          >
                            <div className={`mt-0.5 w-2 h-2 rounded-full flex-shrink-0 ${!notif.isRead ? 'bg-blue-600' : 'bg-slate-300'}`} />
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between">
                                <p className="text-xs font-semibold text-slate-800 truncate">{notif.title}</p>
                                <span className="text-[10px] text-slate-400">{notif.createdAt}</span>
                              </div>
                              <p className="text-xs text-slate-600 mt-0.5 line-clamp-2">{notif.message}</p>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Reset Database Button */}
              <button
                id="btn-reset-demo"
                onClick={() => setShowResetConfirm(true)}
                title="Reset Sample ERP Data"
                className="p-2 rounded-xl text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
              >
                <RotateCcw className="w-4 h-4" />
              </button>

              {/* User Profile Menu */}
              <div className="relative">
                <button
                  id="btn-user-avatar-menu"
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-2 p-1.5 rounded-xl hover:bg-slate-100 transition-colors cursor-pointer"
                >
                  <img
                    src={currentUser.profileImage}
                    alt={currentUser.fullName}
                    className="w-8 h-8 rounded-lg object-cover ring-1 ring-slate-200 shadow-2xs"
                  />
                  <div className="hidden xl:block text-left">
                    <p className="text-xs font-bold text-slate-800 leading-tight truncate max-w-[120px]">
                      {currentUser.firstName} {currentUser.lastName}
                    </p>
                    <p className="text-[10px] text-slate-500 capitalize">{currentUser.role.toLowerCase()}</p>
                  </div>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400 hidden xl:block" />
                </button>

                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-64 bg-white rounded-2xl shadow-xl border border-slate-200 py-2 z-50 animate-in fade-in duration-150">
                    <div className="px-4 py-3 border-b border-slate-100">
                      <p className="text-xs font-bold text-slate-900">{currentUser.fullName}</p>
                      <p className="text-xs text-slate-500 truncate">{currentUser.email}</p>
                      <div className="mt-2 inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700">
                        Role: {currentUser.role}
                      </div>
                    </div>

                    <div className="p-2 space-y-1">
                      <button
                        onClick={() => {
                          setShowUserMenu(false);
                          setShowRoleSwitcher(true);
                        }}
                        className="w-full text-left px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-xl flex items-center space-x-2 transition-colors cursor-pointer"
                      >
                        <Users className="w-4 h-4 text-blue-600" />
                        <span>Switch User Account</span>
                      </button>

                      <button
                        id="btn-navbar-logout"
                        onClick={() => {
                          setShowUserMenu(false);
                          logout();
                        }}
                        className="w-full text-left px-3 py-2 text-xs font-bold text-rose-600 hover:bg-rose-50 rounded-xl flex items-center space-x-2 transition-colors cursor-pointer"
                      >
                        <LogOut className="w-4 h-4" />
                        <span>Sign Out from ERP</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Role Switcher Modal */}
        {showRoleSwitcher && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
            <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 animate-in zoom-in-95 duration-150 max-h-[85vh] flex flex-col">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center space-x-2">
                  <div className="p-2 bg-blue-50 text-blue-600 rounded-xl">
                    <Users className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-900">Switch Demo Account</h3>
                    <p className="text-xs text-slate-500">Instantly switch between roles and personas</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowRoleSwitcher(false)}
                  className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
                >
                  ✕
                </button>
              </div>

              <div className="overflow-y-auto divide-y divide-slate-100 my-3 flex-1">
                {availableUsers.map((u) => {
                  const isCurrent = u.id === currentUser.id;
                  const roleBadge = getRoleBadge(u.role);
                  return (
                    <button
                      key={u.id}
                      onClick={() => {
                        switchUser(u.id);
                        setShowRoleSwitcher(false);
                      }}
                      className={`w-full text-left p-3 rounded-xl flex items-center justify-between transition-colors cursor-pointer ${
                        isCurrent ? 'bg-blue-50/80 border border-blue-200' : 'hover:bg-slate-50'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <img
                          src={u.profileImage}
                          alt={u.fullName}
                          className="w-10 h-10 rounded-xl object-cover ring-1 ring-slate-200"
                        />
                        <div>
                          <p className="text-xs font-bold text-slate-900">{u.fullName}</p>
                          <p className="text-[11px] text-slate-500">{u.email}</p>
                        </div>
                      </div>
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded-md border ${roleBadge.bg}`}>
                        {u.role}
                      </span>
                    </button>
                  );
                })}
              </div>

              <div className="pt-2 border-t border-slate-100 text-right">
                <button
                  onClick={() => setShowRoleSwitcher(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Reset Confirmation Modal */}
        {showResetConfirm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
            <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-md w-full p-6 text-center animate-in zoom-in-95 duration-150">
              <div className="w-12 h-12 rounded-2xl bg-rose-100 text-rose-600 mx-auto flex items-center justify-center mb-4">
                <RotateCcw className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900">Reset Demo Database?</h3>
              <p className="text-xs text-slate-500 mt-2">
                This will restore all departments, courses, faculty, students, attendance, fee records, and timetable slots to default sample values.
              </p>
              <div className="mt-6 flex items-center justify-center space-x-3">
                <button
                  onClick={() => setShowResetConfirm(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  id="btn-confirm-reset"
                  onClick={() => {
                    resetToFactoryDefaults();
                    setShowResetConfirm(false);
                  }}
                  className="px-4 py-2 text-xs font-semibold text-white bg-rose-600 hover:bg-rose-700 rounded-xl shadow-xs transition-colors cursor-pointer"
                >
                  Confirm Reset
                </button>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Global Command Palette */}
      <CommandPaletteModal
        isOpen={isCommandOpen}
        onClose={() => setIsCommandOpen(false)}
        onNavigate={(view) => setCurrentView(view)}
        onOpenIdCard={onOpenIdCard}
      />
    </>
  );
};

