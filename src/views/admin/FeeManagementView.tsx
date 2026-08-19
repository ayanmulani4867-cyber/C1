import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { FeePayment } from '../../types';
import { formatINR, formatIndianDate } from '../../utils/formatters';
import {
  Receipt,
  Plus,
  CheckCircle2,
  AlertCircle,
  Search,
  Filter,
  Printer,
  CreditCard,
  X,
  Download,
  Building2,
  QrCode,
  Landmark,
  Wallet,
  Clock,
  Sparkles,
} from 'lucide-react';

interface FeeManagementViewProps {
  onOpenReceipt: (payment: FeePayment) => void;
}

export const FeeManagementView: React.FC<FeeManagementViewProps> = ({ onOpenReceipt }) => {
  const { students, feeLedgers, feePayments, recordFeePayment, departments, courses } = useErp();

  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'ALL' | 'Paid' | 'Partial' | 'Pending' | 'Overdue'>('ALL');
  const [selectedSem, setSelectedSem] = useState<string>('ALL');
  const [showCollectModal, setShowCollectModal] = useState(false);
  const [selectedStudentForPay, setSelectedStudentForPay] = useState<string>(students[0]?.id || '');

  const [paymentForm, setPaymentForm] = useState({
    amount: 65000,
    semesterNumber: 4,
    paymentMethod: 'UPI' as FeePayment['paymentMethod'],
    transactionId: `UPI-${Date.now().toString().slice(-8)}`,
    remarks: 'Semester 4 Regular Tuition & Exam Fee',
  });

  const totalBilled = feeLedgers.reduce((acc, l) => acc + l.totalAmount, 0);
  const totalCollected = feeLedgers.reduce((acc, l) => acc + l.paidAmount, 0);
  const totalPending = feeLedgers.reduce((acc, l) => acc + l.pendingAmount, 0);

  const filteredLedgers = feeLedgers.filter((ledger) => {
    const student = students.find((s) => s.id === ledger.studentId);
    const matchesSearch =
      student?.fullName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      student?.rollNo.toLowerCase().includes(searchQuery.toLowerCase()) ||
      student?.studentId.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus = filterStatus === 'ALL' || ledger.status === filterStatus;
    const matchesSem = selectedSem === 'ALL' || String(ledger.semesterNumber) === selectedSem;

    return matchesSearch && matchesStatus && matchesSem;
  });

  const handleRecordPayment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStudentForPay || paymentForm.amount <= 0) return;

    const receiptNum = `RCP-2026-${1000 + feePayments.length + 1}`;
    recordFeePayment({
      studentId: selectedStudentForPay,
      semesterNumber: paymentForm.semesterNumber,
      amount: Number(paymentForm.amount),
      paymentMethod: paymentForm.paymentMethod,
      transactionId: paymentForm.transactionId || `TXN-${Date.now()}`,
      receiptNumber: receiptNum,
      paymentDate: new Date().toISOString().split('T')[0],
      breakdown: {
        tuition: Math.round(Number(paymentForm.amount) * 0.7),
        lab: Math.round(Number(paymentForm.amount) * 0.15),
        library: Math.round(Number(paymentForm.amount) * 0.05),
        exam: Math.round(Number(paymentForm.amount) * 0.1),
      },
    });

    setShowCollectModal(false);
  };

  const handleExportCSV = () => {
    const headers = 'Roll No,Student Name,Semester,Total Billed (INR),Paid (INR),Pending (INR),Status\n';
    const rows = filteredLedgers
      .map((l) => {
        const s = students.find((st) => st.id === l.studentId);
        return `"${s?.rollNo}","${s?.fullName}",${l.semesterNumber},${l.totalAmount},${l.paidAmount},${l.pendingAmount},"${l.status}"`;
      })
      .join('\n');

    const blob = new Blob([headers + rows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `Fee_Ledger_Export_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="w-12 h-12 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-md">
            <Receipt className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Accounts & Fee Management Desk</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Tuition billing, student ledger reconciliation, fee collections (UPI/NEFT/DD/Cash), and official receipts.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            type="button"
            onClick={handleExportCSV}
            className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs border border-slate-200 flex items-center space-x-1.5 transition"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Ledger CSV</span>
          </button>

          <button
            type="button"
            onClick={() => setShowCollectModal(true)}
            className="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl text-xs shadow-md flex items-center space-x-2 transition"
          >
            <Plus className="w-4 h-4" />
            <span>Collect Fee / Record Payment</span>
          </button>
        </div>
      </div>

      {/* Financial KPIs in INR (₹) */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Billed Tuition</span>
            <span className="text-xs font-bold text-slate-400">Term 2025–26</span>
          </div>
          <h3 className="text-2xl font-black text-slate-900 mt-2">{formatINR(totalBilled)}</h3>
          <span className="text-xs text-slate-400 mt-1 block">Across all active department programs</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-emerald-700 uppercase tracking-wider">Total Collected</span>
            <span className="text-xs font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded">
              {totalBilled > 0 ? Math.round((totalCollected / totalBilled) * 100) : 0}% Realized
            </span>
          </div>
          <h3 className="text-2xl font-black text-emerald-700 mt-2">{formatINR(totalCollected)}</h3>
          <span className="text-xs text-emerald-600 mt-1 block">Reconciled in University Account</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-rose-600 uppercase tracking-wider">Outstanding Dues</span>
            <span className="text-xs font-bold bg-rose-100 text-rose-800 px-2 py-0.5 rounded">Pending</span>
          </div>
          <h3 className="text-2xl font-black text-rose-600 mt-2">{formatINR(totalPending)}</h3>
          <span className="text-xs text-rose-500 mt-1 block">Pending student recovery</span>
        </div>
      </div>

      {/* Search & Filter */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by Student Name, Roll No, Student ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
          />
        </div>

        <div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as any)}
            className="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none bg-white text-slate-700"
          >
            <option value="ALL">All Payment Statuses</option>
            <option value="Paid">Fully Paid</option>
            <option value="Partial">Partial Payment</option>
            <option value="Pending">Payment Pending</option>
            <option value="Overdue">Overdue Dues</option>
          </select>
        </div>

        <div>
          <select
            value={selectedSem}
            onChange={(e) => setSelectedSem(e.target.value)}
            className="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none bg-white text-slate-700"
          >
            <option value="ALL">All Semesters</option>
            {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
              <option key={s} value={String(s)}>
                Semester {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Student Fee Ledger Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-3.5 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Active Student Ledgers ({filteredLedgers.length})
          </span>
          <span className="text-xs text-slate-400 font-mono">Currency: INR (₹)</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Student Name</th>
                <th className="py-3 px-3">Roll No.</th>
                <th className="py-3 px-3">Semester</th>
                <th className="py-3 px-3 text-right">Total Billed</th>
                <th className="py-3 px-3 text-right">Amount Paid</th>
                <th className="py-3 px-3 text-right">Pending Balance</th>
                <th className="py-3 px-3 text-center">Status</th>
                <th className="py-3 px-4 text-right">Receipt / Collection</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {filteredLedgers.length > 0 ? (
                filteredLedgers.map((ledger) => {
                  const student = students.find((s) => s.id === ledger.studentId);
                  const payment = feePayments.find((p) => p.studentId === ledger.studentId);

                  return (
                    <tr key={ledger.id} className="hover:bg-emerald-50/30 transition">
                      <td className="py-3 px-4 font-bold text-slate-900 flex items-center space-x-3">
                        <img src={student?.photo} alt="" className="w-8 h-8 rounded-xl object-cover border border-slate-200" />
                        <div>
                          <span>{student?.fullName || 'Student'}</span>
                          <span className="text-[10px] text-slate-400 block font-mono">{student?.studentId}</span>
                        </div>
                      </td>
                      <td className="py-3 px-3 font-mono font-bold text-blue-700">{student?.rollNo}</td>
                      <td className="py-3 px-3 font-medium text-slate-700">Sem {ledger.semesterNumber}</td>
                      <td className="py-3 px-3 font-semibold text-slate-900 text-right">{formatINR(ledger.totalAmount)}</td>
                      <td className="py-3 px-3 font-bold text-emerald-700 text-right">{formatINR(ledger.paidAmount)}</td>
                      <td className="py-3 px-3 font-bold text-rose-600 text-right">{formatINR(ledger.pendingAmount)}</td>
                      <td className="py-3 px-3 text-center">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                            ledger.status === 'Paid'
                              ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                              : ledger.status === 'Partial'
                              ? 'bg-blue-100 text-blue-800 border border-blue-200'
                              : 'bg-rose-100 text-rose-800 border border-rose-200'
                          }`}
                        >
                          {ledger.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        {payment ? (
                          <button
                            type="button"
                            onClick={() => onOpenReceipt(payment)}
                            className="px-3 py-1 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-lg border border-emerald-200 transition inline-flex items-center space-x-1"
                          >
                            <Receipt className="w-3.5 h-3.5" />
                            <span>Receipt</span>
                          </button>
                        ) : (
                          <button
                            type="button"
                            onClick={() => {
                              setSelectedStudentForPay(ledger.studentId);
                              setPaymentForm({
                                ...paymentForm,
                                amount: ledger.pendingAmount,
                                semesterNumber: ledger.semesterNumber,
                              });
                              setShowCollectModal(true);
                            }}
                            className="px-3 py-1 text-xs font-bold text-white bg-emerald-700 hover:bg-emerald-800 rounded-lg shadow-xs transition"
                          >
                            Collect Dues
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    No fee ledgers matching your search criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Record Fee Payment Modal */}
      {showCollectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <Receipt className="w-5 h-5 text-emerald-600" />
                <h3 className="font-bold text-base text-slate-900">Record Fee Collection & Issue Receipt</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowCollectModal(false)}
                className="p-1 text-slate-400 hover:text-slate-700 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleRecordPayment} className="space-y-4 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Select Student *</label>
                <select
                  value={selectedStudentForPay}
                  onChange={(e) => setSelectedStudentForPay(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl font-bold text-slate-800 focus:ring-2 focus:ring-emerald-500 outline-none"
                >
                  {students.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.fullName} ({s.rollNo} • Sem {s.semesterNumber})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Amount to Collect (₹) *</label>
                  <input
                    type="number"
                    required
                    min={1}
                    value={paymentForm.amount}
                    onChange={(e) => setPaymentForm({ ...paymentForm, amount: Number(e.target.value) })}
                    className="w-full px-3 py-2 font-mono font-bold text-slate-900 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
                  />
                </div>

                <div>
                  <label className="font-bold text-slate-700 block mb-1">Academic Semester *</label>
                  <select
                    value={paymentForm.semesterNumber}
                    onChange={(e) => setPaymentForm({ ...paymentForm, semesterNumber: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8].map((sem) => (
                      <option key={sem} value={sem}>
                        Semester {sem}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Payment Mode *</label>
                  <select
                    value={paymentForm.paymentMethod}
                    onChange={(e) => setPaymentForm({ ...paymentForm, paymentMethod: e.target.value as any })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none font-semibold text-slate-800"
                  >
                    <option value="UPI">UPI / QR Code</option>
                    <option value="Net Banking">Net Banking / NEFT / RTGS</option>
                    <option value="Demand Draft">Demand Draft (DD)</option>
                    <option value="Cash">Cash at University Counter</option>
                    <option value="Credit Card">Credit / Debit Card</option>
                  </select>
                </div>

                <div>
                  <label className="font-bold text-slate-700 block mb-1">Transaction Ref / UTR *</label>
                  <input
                    type="text"
                    required
                    value={paymentForm.transactionId}
                    onChange={(e) => setPaymentForm({ ...paymentForm, transactionId: e.target.value })}
                    className="w-full px-3 py-2 font-mono text-slate-900 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Payment Remarks / Head</label>
                <input
                  type="text"
                  value={paymentForm.remarks}
                  onChange={(e) => setPaymentForm({ ...paymentForm, remarks: e.target.value })}
                  placeholder="e.g. Regular Semester 4 Tuition & Examination Fee"
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
                />
              </div>

              <div className="pt-3 border-t border-slate-200 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowCollectModal(false)}
                  className="px-4 py-2 text-slate-600 hover:text-slate-800 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow-md transition"
                >
                  Issue Official Receipt
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
