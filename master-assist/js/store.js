/**
 * Master Assist — Shared Data Store
 * Single source of truth for all application data.
 * All pages read/write through this store via localStorage.
 */
const MA = (function () {

  // ─── helpers ────────────────────────────────────────────────────────────────
  function load(key, def) {
    try {
      const raw = localStorage.getItem('ma_' + key);
      return raw ? JSON.parse(raw) : def;
    } catch (e) { return def; }
  }
  function save(key, val) {
    try { localStorage.setItem('ma_' + key, JSON.stringify(val)); } catch (e) {}
    return val;
  }
  function nextId(arr) {
    return arr.length ? Math.max(...arr.map(r => r.id || 0)) + 1 : 1;
  }
  function today() {
    return new Date().toISOString().slice(0, 10);
  }
  function fmt(n) {
    return '₹' + Number(n).toLocaleString('en-IN');
  }

  // ─── seed data ──────────────────────────────────────────────────────────────
  const SEED = {

    company: {
      name: 'Master Assist',
      tagline: 'ERP-23',
      gstin: '',
      pan: '',
      phone: '',
      email: '',
      address: '',
      invoicePrefix: 'BILL-',
      invoiceStart: 1,
      gstDefault: '18',
      approvalThreshold: 10000,
      autoApproveBelow: 1000,
      maxFileSizeMB: 10,
      sessionTimeout: 30,
      maxLoginAttempts: 5,
      passwordMinLength: 8,
      retainBackupDays: 30,
    },

    users: [
      { id: 1, name: 'Administrator', username: 'admin', mobile: '', email: '', role: 'Admin', pos: 'All POS', lastLogin: '', status: 'active' },
    ],

    centers: [],
    pos: [],

    suppliers: [],
    customers: [],

    categories: [
      { id: 1, name: 'Grocery', parent: '', gst: '0', status: 'active', desc: '', color: 0 },
      { id: 2, name: 'Electronics', parent: '', gst: '18', status: 'active', desc: '', color: 3 },
      { id: 3, name: 'Clothing', parent: '', gst: '12', status: 'active', desc: '', color: 1 },
      { id: 4, name: 'FMCG', parent: '', gst: '18', status: 'active', desc: '', color: 2 },
      { id: 5, name: 'Pharma', parent: '', gst: '12', status: 'active', desc: '', color: 4 },
    ],

    brands: [
      { id: 1, name: 'Generic / Local', country: 'India', web: '', items: 0, status: 'active', desc: '', pi: 2 },
    ],

    taxes: [
      { id: 1, name: 'GST 0%',  rate: 0,  cgst: 0,   sgst: 0,   igst: 0,  cess: 0,  hsn: '', apply: 'Fresh produce, essentials', status: 'active' },
      { id: 2, name: 'GST 5%',  rate: 5,  cgst: 2.5, sgst: 2.5, igst: 5,  cess: 0,  hsn: '', apply: 'Edible oils, basic food',  status: 'active' },
      { id: 3, name: 'GST 12%', rate: 12, cgst: 6,   sgst: 6,   igst: 12, cess: 0,  hsn: '', apply: 'Processed foods, clothing', status: 'active' },
      { id: 4, name: 'GST 18%', rate: 18, cgst: 9,   sgst: 9,   igst: 18, cess: 0,  hsn: '', apply: 'Electronics, services',    status: 'active' },
      { id: 5, name: 'GST 28%', rate: 28, cgst: 14,  sgst: 14,  igst: 28, cess: 0,  hsn: '', apply: 'Luxury goods',             status: 'active' },
    ],

    items: [],

    bills: [],
    purchaseOrders: [],
    returns: [],

    sales: [],
    posTerminals: [],

    payments: [],
    expenses: [],
    ledger: [],

    inventory: [],
    stockTransfers: [],

    coupons: [],
    targets: [],
    bookings: [],
    areas: [],

    notifications: [],
    auditLog: [],

    smsTemplates: [
      { id: 1, key: 'sale_receipt',    name: 'Sale Receipt',       type: 'sms',   trigger: 'auto', status: 'active', body: 'Dear {customer_name}, Thank you for your purchase of {amount} at {store_name}. Bill No: {bill_no}. Date: {date}. - Team {store_name}' },
      { id: 2, key: 'payment_received',name: 'Payment Received',   type: 'sms',   trigger: 'auto', status: 'active', body: 'Dear {customer_name}, We received your payment of {amount} on {date} against {bill_no}. Thank you! - Team {store_name}' },
      { id: 3, key: 'due_reminder',    name: 'Due Reminder',       type: 'sms',   trigger: 'manual', status: 'active', body: 'Dear {customer_name}, Rs. {amount} is due on your account. Please clear at the earliest. Contact: {phone} - {store_name}' },
      { id: 4, key: 'otp',             name: 'OTP / Login',        type: 'sms',   trigger: 'auto', status: 'active', body: 'Your {store_name} OTP is {otp}. Valid for 5 minutes. Do not share. - Team {store_name}' },
      { id: 5, key: 'promo_offer',     name: 'Promotional Offer',  type: 'sms',   trigger: 'manual', status: 'active', body: 'Hi {customer_name}! Special offer at {store_name}. Use code: {code} for {discount} off. Valid till {expiry}. Reply STOP to unsubscribe.' },
      { id: 6, key: 'invoice_email',   name: 'Invoice Email',      type: 'email', trigger: 'auto', status: 'active', body: 'Subject: Invoice #{bill_no} from {store_name}\n\nDear {customer_name},\n\nPlease find your invoice details below.\nAmount: {amount}\nDate: {date}\n\nThank you for shopping with us!\n\nTeam {store_name}' },
      { id: 7, key: 'welcome_customer',name: 'Welcome Customer',   type: 'email', trigger: 'auto', status: 'active', body: 'Subject: Welcome to {store_name}!\n\nDear {customer_name},\n\nWelcome! Your account is active.\nLogin: {phone}\n\nEnjoy shopping!\n\nTeam {store_name}' },
    ],

    smsSendLog: [],
    gstFilingHistory: [],

    settings: {
      appearance: { theme: 'light', primaryColor: '#696cff', sidebarCollapsed: false },
      notifications: { billUpload: true, billApproval: true, lowStock: true, paymentReminder: true, emailDigest: false },
    },
  };

  // ─── initialise store (seed only if empty) ───────────────────────────────────
  function init() {
    Object.keys(SEED).forEach(function (key) {
      if (localStorage.getItem('ma_' + key) === null) {
        save(key, SEED[key]);
      }
    });
  }

  // ─── generic CRUD ──────────────────────────────────────────────────────────
  function getAll(key) { return load(key, []); }
  function getOne(key, id) { return getAll(key).find(function (r) { return r.id === id; }) || null; }
  function set(key, val) { return save(key, val); }

  function upsert(key, record) {
    const arr = getAll(key);
    const idx = arr.findIndex(function (r) { return r.id === record.id; });
    if (idx >= 0) { arr[idx] = record; } else { record.id = record.id || nextId(arr); arr.push(record); }
    save(key, arr);
    return record;
  }

  function remove(key, id) {
    const arr = getAll(key).filter(function (r) { return r.id !== id; });
    save(key, arr);
  }

  // ─── company settings ───────────────────────────────────────────────────────
  function getCompany() { return load('company', SEED.company); }
  function setCompany(obj) { return save('company', Object.assign(getCompany(), obj)); }

  // ─── notifications helpers ─────────────────────────────────────────────────
  function getUnreadCount() {
    return getAll('notifications').filter(function (n) { return n.unread; }).length;
  }
  function getPendingBillCount() {
    return getAll('bills').filter(function (b) { return b.status === 'pending'; }).length;
  }

  // ─── audit log helper ──────────────────────────────────────────────────────
  function addAudit(action, user) {
    const log = getAll('auditLog');
    log.unshift({ id: nextId(log), action: action, user: user || 'admin', time: new Date().toISOString(), ip: '' });
    if (log.length > 500) log.length = 500;
    save('auditLog', log);
  }

  // ─── dashboard summary ─────────────────────────────────────────────────────
  function dashStats() {
    const bills = getAll('bills');
    const sales = getAll('sales');
    const todaySales = sales.filter(function (s) { return s.date === today(); })
      .reduce(function (a, s) { return a + (s.total || 0); }, 0);
    return {
      totalBills:    bills.length,
      pending:       bills.filter(function (b) { return b.status === 'pending'; }).length,
      approved:      bills.filter(function (b) { return b.status === 'approved'; }).length,
      rejected:      bills.filter(function (b) { return b.status === 'rejected'; }).length,
      activePOS:     getAll('posTerminals').filter(function (p) { return p.status === 'active'; }).length,
      todaySales:    todaySales,
    };
  }

  // ─── public API ─────────────────────────────────────────────────────────────
  return {
    init:             init,
    load:             load,
    save:             save,
    nextId:           nextId,
    today:            today,
    fmt:              fmt,
    getAll:           getAll,
    getOne:           getOne,
    set:              set,
    upsert:           upsert,
    remove:           remove,
    getCompany:       getCompany,
    setCompany:       setCompany,
    getUnreadCount:   getUnreadCount,
    getPendingBillCount: getPendingBillCount,
    addAudit:         addAudit,
    dashStats:        dashStats,
    SEED:             SEED,
  };

})();

// Auto-init on load
MA.init();
