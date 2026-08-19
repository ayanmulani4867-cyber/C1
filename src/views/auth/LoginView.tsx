import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import {
  GraduationCap,
  Lock,
  User,
  Eye,
  EyeOff,
  ShieldCheck,
  ArrowRight,
  AlertCircle,
  KeyRound,
} from 'lucide-react';

export const LoginView: React.FC = () => {
  const { login } = useErp();

  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    if (!usernameOrEmail.trim()) {
      setErrorMessage('Please enter your institutional username or college email.');
      return;
    }
    if (!password) {
      setErrorMessage('Please enter your secure password.');
      return;
    }

    setIsLoading(true);
    const result = await login(usernameOrEmail.trim(), password);
    setIsLoading(false);

    if (!result.success) {
      setErrorMessage(result.error || 'Invalid credentials. Please verify your username and password.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden font-sans text-slate-100 selection:bg-blue-600 selection:text-white">
      {/* Background Decorative Gradient Orbs */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        {/* Institutional Crest & Brand */}
        <div className="flex justify-center">
          <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-700 to-indigo-600 text-white shadow-xl shadow-blue-500/25 ring-4 ring-blue-500/20">
            <GraduationCap className="w-9 h-9" />
          </div>
        </div>

        <div className="text-center mt-4">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Apex Institute of Technology & Science
          </h1>
          <p className="text-sm font-semibold text-blue-400 mt-1">
            Campus Connect Enterprise ERP • Production Sign-In
          </p>
          <p className="text-xs text-slate-400 mt-0.5">
            Academic Year 2025–2026 • Verified Access Portal
          </p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10 px-4 sm:px-0">
        <div className="bg-slate-800/90 backdrop-blur-xl border border-slate-700/80 rounded-3xl py-8 px-6 sm:px-10 shadow-2xl">
          {errorMessage && (
            <div className="mb-6 p-4 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs font-semibold flex items-center space-x-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-400" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleLoginSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                Institutional ID / Username / Email
              </label>
              <div className="relative rounded-2xl shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <User className="w-4 h-4" />
                </div>
                <input
                  id="input-username"
                  type="text"
                  value={usernameOrEmail}
                  onChange={(e) => setUsernameOrEmail(e.target.value)}
                  placeholder="e.g. admin or student / faculty ID"
                  className="block w-full pl-10 pr-4 py-3 bg-slate-900/80 border border-slate-700 rounded-2xl text-xs sm:text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                Password
              </label>
              <div className="relative rounded-2xl shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="input-password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="block w-full pl-10 pr-10 py-3 bg-slate-900/80 border border-slate-700 rounded-2xl text-xs sm:text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-200 cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs">
              <label className="flex items-center space-x-2 cursor-pointer text-slate-300">
                <input
                  type="checkbox"
                  defaultChecked
                  className="rounded border-slate-700 bg-slate-900 text-blue-600 focus:ring-blue-500"
                />
                <span>Remember session</span>
              </label>
              <span className="text-slate-400 font-medium">SSL 256-bit Secure</span>
            </div>

            <button
              id="btn-submit-login"
              type="submit"
              disabled={isLoading}
              className="w-full py-3.5 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-sm font-bold rounded-2xl shadow-lg shadow-blue-600/30 transition-all flex items-center justify-center space-x-2 disabled:opacity-70 cursor-pointer"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <span>Sign In to Institutional ERP</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Admin Credentials Info Card */}
          <div className="mt-6 pt-5 border-t border-slate-700/60">
            <div className="p-3.5 rounded-2xl bg-slate-900/90 border border-slate-700/60 text-xs flex items-start space-x-3">
              <div className="w-8 h-8 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center flex-shrink-0 mt-0.5">
                <KeyRound className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-slate-200">System Administrator Login:</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  ID: <code className="text-blue-400 font-bold bg-blue-950/60 px-1.5 py-0.5 rounded border border-blue-800/40">admin</code> &nbsp;•&nbsp; 
                  Password: <code className="text-blue-400 font-bold bg-blue-950/60 px-1.5 py-0.5 rounded border border-blue-800/40">admin</code>
                </p>
                <p className="text-[10px] text-slate-500 mt-1">
                  All faculty, staff, and student accounts are created & managed by the Administrator through the ERP.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Security Badges */}
        <div className="mt-6 text-center text-xs text-slate-500 flex items-center justify-center space-x-4">
          <div className="flex items-center space-x-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>PostgreSQL Database Active</span>
          </div>
          <span>•</span>
          <span>Indian Institute ERP Standard (₹ INR)</span>
        </div>
      </div>
    </div>
  );
};
