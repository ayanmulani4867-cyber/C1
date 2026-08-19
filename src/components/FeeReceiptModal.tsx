import React from 'react';
import { FeePayment, Student } from '../types';
import { formatINR, formatIndianDate } from '../utils/formatters';
import { X, Printer, CheckCircle2, Receipt, Building2, ShieldCheck } from 'lucide-react';

interface FeeReceiptModalProps {
  payment: FeePayment;
  student?: Student;
  isOpen: boolean;
  onClose: () => void;
}

export const FeeReceiptModal: React.FC<FeeReceiptModalProps> = ({
  payment,
  student,
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-3 sm:p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-xl w-full overflow-hidden animate-in zoom-in-95 duration-150">
        {/* Top bar */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50">
          <div className="flex items-center space-x-2">
            <Receipt className="w-5 h-5 text-emerald-600" />
            <h3 className="font-bold text-sm text-slate-900">Official University Fee Receipt</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Receipt Sheet */}
        <div className="p-6 bg-slate-100 flex justify-center">
          <div
            id="printable-fee-receipt"
            className="w-full bg-white p-6 rounded-2xl shadow-md border border-slate-200 text-slate-900 space-y-4"
          >
            {/* Header */}
            <div className="text-center border-b border-slate-200 pb-3">
              <h2 className="font-black text-base text-slate-900 uppercase tracking-tight">
                Apex Institute of Technology & Science
              </h2>
              <p className="text-[11px] text-slate-500 font-medium">Bursar & Finance Division • Institutional Campus</p>
              <div className="mt-2 flex items-center justify-center space-x-2">
                <span className="px-3 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                  RECEIPT: {payment.receiptNumber}
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-100 text-blue-800 border border-blue-200">
                  PAID
                </span>
              </div>
            </div>

            {/* Student Details Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs bg-slate-50 p-4 rounded-xl border border-slate-200">
              <div>
                <span className="text-slate-400 font-medium block">Student Name:</span>
                <span className="font-bold text-slate-900">{student?.fullName || 'Rahul Sharma'}</span>
              </div>
              <div>
                <span className="text-slate-400 font-medium block">Roll Number:</span>
                <span className="font-mono font-bold text-slate-900">{student?.rollNo || '23CS101'}</span>
              </div>
              <div>
                <span className="text-slate-400 font-medium block">Course & Semester:</span>
                <span className="font-semibold text-slate-900">B.Tech CSE • Semester {payment.semesterNumber}</span>
              </div>
              <div>
                <span className="text-slate-400 font-medium block">Payment Method:</span>
                <span className="font-semibold text-blue-700">{payment.paymentMethod}</span>
              </div>
              <div>
                <span className="text-slate-400 font-medium block">Transaction / UTR ID:</span>
                <span className="font-mono font-semibold text-slate-700 text-[11px]">{payment.transactionId}</span>
              </div>
              <div>
                <span className="text-slate-400 font-medium block">Receipt Date:</span>
                <span className="font-semibold text-slate-900">{formatIndianDate(payment.paymentDate)}</span>
              </div>
            </div>

            {/* Breakdown Table in INR (₹) */}
            <div className="border border-slate-200 rounded-xl overflow-hidden">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-3">Fee Component Head</th>
                    <th className="py-2.5 px-3 text-right">Amount (₹)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  <tr>
                    <td className="py-2 px-3 text-slate-700">Tuition & Academic Training Fee</td>
                    <td className="py-2 px-3 text-right font-mono font-semibold text-slate-900">
                      {formatINR(payment.breakdown.tuition)}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2 px-3 text-slate-700">Laboratory, Computing & Workshop Fee</td>
                    <td className="py-2 px-3 text-right font-mono font-semibold text-slate-900">
                      {formatINR(payment.breakdown.lab)}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2 px-3 text-slate-700">Digital Library, Journals & E-Resources</td>
                    <td className="py-2 px-3 text-right font-mono font-semibold text-slate-900">
                      {formatINR(payment.breakdown.library)}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2 px-3 text-slate-700">University Examination & Evaluation Fee</td>
                    <td className="py-2 px-3 text-right font-mono font-semibold text-slate-900">
                      {formatINR(payment.breakdown.exam)}
                    </td>
                  </tr>
                </tbody>
                <tfoot className="bg-emerald-50/80 font-bold text-slate-900 border-t-2 border-emerald-200">
                  <tr>
                    <td className="py-2.5 px-3 text-emerald-950 font-bold">Total Amount Paid</td>
                    <td className="py-2.5 px-3 text-right text-sm font-mono font-bold text-emerald-900">
                      {formatINR(payment.amount)}
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>

            {/* Note & Auth Stamp */}
            <div className="flex items-center justify-between pt-3 border-t border-slate-200 text-[11px] text-slate-500">
              <div className="flex items-center space-x-1.5 text-emerald-700 font-semibold">
                <ShieldCheck className="w-4 h-4" />
                <span>Digitally Authenticated E-Receipt</span>
              </div>
              <span className="font-medium text-slate-400">Finance & Accounts Registrar</span>
            </div>
          </div>
        </div>

        {/* Modal Actions */}
        <div className="px-6 py-4 bg-white border-t border-slate-100 flex items-center justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900 rounded-xl hover:bg-slate-100 transition"
          >
            Close
          </button>
          <button
            onClick={handlePrint}
            className="px-5 py-2 text-xs font-bold text-white bg-slate-900 hover:bg-slate-800 rounded-xl shadow-md transition flex items-center space-x-1.5"
          >
            <Printer className="w-4 h-4" />
            <span>Print Receipt</span>
          </button>
        </div>
      </div>
    </div>
  );
};
