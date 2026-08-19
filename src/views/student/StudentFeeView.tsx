import React, { useState } from 'react';
import { useErp } from '../../context/ErpContext';
import { FeePayment } from '../../types';
import { formatINR, formatIndianDate } from '../../utils/formatters';
import { Receipt, CreditCard, CheckCircle2, Clock, Download, Eye, Sparkles, X, ShieldCheck, QrCode } from 'lucide-react';

interface StudentFeeViewProps {
  onOpenReceipt: (payment: FeePayment) => void;
}

export const StudentFeeView: React.FC<StudentFeeViewProps> = ({ onOpenReceipt }) => {
  const { students, feeLedgers, feePayments, currentUser, recordFeePayment } = useErp();

  const myStudent = students.find((s) => s.id === currentUser.id) || students[0];
  const myLedger = feeLedgers.find((l) => l.studentId === myStudent?.id);
  const myPayments = feePayments.filter((p) => p.studentId === myStudent?.id);

  // Pay online modal
  const [showPayModal, setShowPayModal] = useState(false);
  const [payAmount, setPayAmount] = useState<number>(myLedger?.pendingAmount || 25000);
  const [paymentMode, setPaymentMode] = useState<FeePayment['paymentMethod']>('UPI');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleOnlinePay = (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);

    setTimeout(() => {
      const receiptNo = `RCP-2026-${Math.floor(100000 + Math.random() * 900000)}`;
      const transactionId = `UPI_${Date.now()}_${Math.floor(1000 + Math.random() * 9000)}`;

      recordFeePayment({
        studentId: myStudent.id,
        semesterNumber: myStudent.semesterNumber,
        amount: Number(payAmount),
        paymentMethod: paymentMode,
        transactionId: transactionId,
        receiptNumber: receiptNo,
        paymentDate: new Date().toISOString().split('T')[0],
        breakdown: {
          tuition: Math.round(Number(payAmount) * 0.7),
          lab: Math.round(Number(payAmount) * 0.15),
          library: Math.round(Number(payAmount) * 0.05),
          exam: Math.round(Number(payAmount) * 0.1),
        },
      });

      setIsProcessing(false);
      setShowPayModal(false);
    }, 1000);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Student Fee Account & Payment Portal</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Tuition fee ledger, online UPI / Net Banking payment, and official fee receipts.
          </p>
        </div>

        {(myLedger?.pendingAmount || 0) > 0 && (
          <button
            onClick={() => {
              setPayAmount(myLedger?.pendingAmount || 25000);
              setShowPayModal(true);
            }}
            className="px-5 py-2.5 text-xs font-bold text-white bg-blue-700 hover:bg-blue-800 rounded-xl shadow-md transition flex items-center space-x-2 self-start sm:self-auto"
          >
            <CreditCard className="w-4 h-4" />
            <span>Pay Dues Online ({formatINR(myLedger?.pendingAmount || 0)})</span>
          </button>
        )}
      </div>

      {/* Fee Balance Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Billed Fees (Year)</span>
          <h3 className="text-2xl font-black text-slate-900 mt-2">
            {formatINR(myLedger?.totalAmount || 120000)}
          </h3>
          <p className="text-[11px] text-slate-500 mt-1">Academic Year 2025–2026</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <span className="text-xs font-bold text-emerald-700 uppercase tracking-wider">Total Amount Paid</span>
          <h3 className="text-2xl font-black text-emerald-700 mt-2">
            {formatINR(myLedger?.paidAmount || 95000)}
          </h3>
          <p className="text-[11px] text-slate-500 mt-1">Verified with Bursar Office</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <span className="text-xs font-bold text-amber-700 uppercase tracking-wider">Outstanding Balance</span>
          <h3 className="text-2xl font-black text-amber-700 mt-2">
            {formatINR(myLedger?.pendingAmount || 0)}
          </h3>
          <p className="text-[11px] text-slate-500 mt-1">
            {(myLedger?.pendingAmount || 0) === 0 ? 'No Dues Pending ✓' : 'Due for Semester 4'}
          </p>
        </div>
      </div>

      {/* Payment History & Receipts */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden space-y-3 p-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
            <Receipt className="w-4 h-4 text-emerald-600" />
            <span>Official Payment Receipts & Transaction Records</span>
          </h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Receipt Number</th>
                <th className="py-2.5 px-3">Payment Date</th>
                <th className="py-2.5 px-3">Payment Mode</th>
                <th className="py-2.5 px-3">Transaction ID</th>
                <th className="py-2.5 px-3 text-right">Amount (₹)</th>
                <th className="py-2.5 px-3 text-right">Download / View</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {myPayments.length > 0 ? (
                myPayments.map((payment) => (
                  <tr key={payment.id} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 font-mono font-bold text-blue-700">{payment.receiptNumber}</td>
                    <td className="py-2.5 px-3 text-slate-700">{formatIndianDate(payment.paymentDate)}</td>
                    <td className="py-2.5 px-3 font-medium text-slate-800">{payment.paymentMethod}</td>
                    <td className="py-2.5 px-3 font-mono text-slate-500 text-[11px]">{payment.transactionId}</td>
                    <td className="py-2.5 px-3 font-mono font-bold text-slate-900 text-right">
                      {formatINR(payment.amount)}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <button
                        onClick={() => onOpenReceipt(payment)}
                        className="px-3 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-bold rounded-lg border border-emerald-200 transition inline-flex items-center space-x-1"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>View Receipt</span>
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-400">
                    No payment history recorded yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Online Pay Modal */}
      {showPayModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-md w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <QrCode className="w-5 h-5 text-blue-600" />
                <h3 className="font-bold text-base text-slate-900">Instant Online Fee Payment</h3>
              </div>
              <button
                onClick={() => setShowPayModal(false)}
                className="p-1 text-slate-400 hover:text-slate-700 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleOnlinePay} className="space-y-4 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Amount to Pay (INR ₹) *</label>
                <input
                  type="number"
                  required
                  min={1}
                  value={payAmount}
                  onChange={(e) => setPayAmount(Number(e.target.value))}
                  className="w-full px-3.5 py-2 font-mono font-bold text-slate-900 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-base"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Payment Gateway / Method *</label>
                <select
                  value={paymentMode}
                  onChange={(e) => setPaymentMode(e.target.value as any)}
                  className="w-full px-3.5 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none font-semibold text-slate-800"
                >
                  <option value="UPI">UPI (Google Pay / PhonePe / Paytm / BHIM)</option>
                  <option value="Net Banking">Net Banking (HDFC, SBI, ICICI, Axis)</option>
                  <option value="Credit Card">Debit / Credit Card</option>
                </select>
              </div>

              <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl flex items-center space-x-2 text-[11px] text-blue-800 font-medium">
                <ShieldCheck className="w-5 h-5 flex-shrink-0 text-blue-600" />
                <span>Encrypted 256-bit Institutional Gateway. Official e-Receipt is generated instantly.</span>
              </div>

              <div className="pt-3 border-t border-slate-200 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowPayModal(false)}
                  className="px-4 py-2 text-slate-600 hover:text-slate-800 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isProcessing}
                  className="px-5 py-2 bg-blue-700 hover:bg-blue-800 text-white font-bold rounded-xl shadow-md transition disabled:opacity-50"
                >
                  {isProcessing ? 'Processing Payment...' : `Pay ${formatINR(payAmount)}`}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
