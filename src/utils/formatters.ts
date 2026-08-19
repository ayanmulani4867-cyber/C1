/**
 * Enterprise Indian College ERP Formatting Utilities
 */

/**
 * Formats a numeric amount to Indian Rupee standard format (e.g. ₹1,25,000 or ₹45,000)
 */
export function formatINR(amount: number | string | null | undefined): string {
  if (amount === null || amount === undefined || isNaN(Number(amount))) {
    return '₹0';
  }
  const num = Math.round(Number(amount));
  const formatted = num.toLocaleString('en-IN');
  return `₹${formatted}`;
}

/**
 * Formats large amounts in Indian numbering system (Lakhs, Crores, Thousands)
 */
export function formatINRLarge(amount: number | string | null | undefined): string {
  if (amount === null || amount === undefined || isNaN(Number(amount))) {
    return '₹0';
  }
  const num = Number(amount);
  if (num >= 10000000) {
    return `₹${(num / 10000000).toFixed(2)} Cr`;
  }
  if (num >= 100000) {
    return `₹${(num / 100000).toFixed(2)} L`;
  }
  if (num >= 1000) {
    return `₹${(num / 1000).toFixed(1)} K`;
  }
  return `₹${num.toLocaleString('en-IN')}`;
}

/**
 * Format Indian Phone Numbers (+91 98765 43210)
 */
export function formatIndianPhone(phone: string | undefined): string {
  if (!phone) return '+91 98765 43210';
  const clean = phone.replace(/\D/g, '');
  if (clean.length === 10) {
    return `+91 ${clean.slice(0, 5)} ${clean.slice(5)}`;
  }
  if (clean.length === 12 && clean.startsWith('91')) {
    return `+91 ${clean.slice(2, 7)} ${clean.slice(7)}`;
  }
  return phone;
}

/**
 * Formats standard ISO or date string to Indian academic date (e.g. 15-Aug-2025 or 15/08/2025)
 */
export function formatIndianDate(dateStr: string | Date | undefined, withTime: boolean = false): string {
  if (!dateStr) return 'N/A';
  try {
    const d = typeof dateStr === 'string' ? new Date(dateStr) : dateStr;
    if (isNaN(d.getTime())) return String(dateStr);
    
    const options: Intl.DateTimeFormatOptions = {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      ...(withTime ? { hour: '2-digit', minute: '2-digit', hour12: true } : {}),
    };
    return d.toLocaleDateString('en-IN', options);
  } catch {
    return String(dateStr);
  }
}
