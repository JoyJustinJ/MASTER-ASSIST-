"""
Update all original pages to use the new expanded sidebar.
Replaces everything between <aside class="ma-sidebar"...> and </aside> tags.
"""
import os, re

TARGET_DIR = os.path.dirname(os.path.abspath(__file__))

NEW_SIDEBAR = '''<aside class="ma-sidebar" id="sidebar">
  <div class="sidebar-section-title">Main Menu</div>
  <ul class="sidebar-menu"><li><a href="welcome.html"><span class="menu-icon"><i class="fas fa-th-large"></i></span>Dashboard</a></li></ul>
  <div class="sidebar-section-title">Sales</div>
  <ul class="sidebar-menu">
    <li><a href="new_sale.html"><span class="menu-icon"><i class="fas fa-shopping-cart"></i></span>New Sale</a></li>
    <li><a href="pos_sales.html"><span class="menu-icon"><i class="fas fa-cash-register"></i></span>POS Sales</a></li>
    <li><a href="booking_master.html"><span class="menu-icon"><i class="fas fa-calendar-check"></i></span>Bookings</a></li>
  </ul>
  <div class="sidebar-section-title">Bill Management</div>
  <ul class="sidebar-menu">
    <li><a href="bill_upload.html"><span class="menu-icon"><i class="fas fa-cloud-upload-alt"></i></span>Bill Upload<span class="badge-count">12</span></a></li>
    <li><a href="bills.html"><span class="menu-icon"><i class="fas fa-file-invoice"></i></span>All Bills</a></li>
    <li><a href="approvals.html"><span class="menu-icon"><i class="fas fa-tasks"></i></span>Approvals</a></li>
    <li><a href="purchase_orders.html"><span class="menu-icon"><i class="fas fa-receipt"></i></span>Purchase Orders</a></li>
    <li><a href="returns.html"><span class="menu-icon"><i class="fas fa-exchange-alt"></i></span>Returns</a></li>
    <li><a href="suppliers.html"><span class="menu-icon"><i class="fas fa-truck"></i></span>Suppliers</a></li>
    <li><a href="customers.html"><span class="menu-icon"><i class="fas fa-user-friends"></i></span>Customers</a></li>
  </ul>
  <div class="sidebar-section-title">Inventory</div>
  <ul class="sidebar-menu">
    <li><a href="inventory.html"><span class="menu-icon"><i class="fas fa-boxes"></i></span>Inventory</a></li>
    <li><a href="item_master.html"><span class="menu-icon"><i class="fas fa-cube"></i></span>Item Master</a></li>
    <li><a href="category_master.html"><span class="menu-icon"><i class="fas fa-tags"></i></span>Categories</a></li>
    <li><a href="brand_list.html"><span class="menu-icon"><i class="fas fa-trademark"></i></span>Brands</a></li>
    <li><a href="barcode_list.html"><span class="menu-icon"><i class="fas fa-barcode"></i></span>Barcodes</a></li>
    <li><a href="stock_transfer.html"><span class="menu-icon"><i class="fas fa-dolly"></i></span>Stock Transfer</a></li>
  </ul>
  <div class="sidebar-section-title">Finance</div>
  <ul class="sidebar-menu">
    <li><a href="expenses.html"><span class="menu-icon"><i class="fas fa-file-invoice-dollar"></i></span>Expenses</a></li>
    <li><a href="payments.html"><span class="menu-icon"><i class="fas fa-hand-holding-usd"></i></span>Payments</a></li>
    <li><a href="cashbook.html"><span class="menu-icon"><i class="fas fa-book"></i></span>Cashbook</a></li>
    <li><a href="tax_master.html"><span class="menu-icon"><i class="fas fa-percent"></i></span>Tax Master</a></li>
    <li><a href="coupon_master.html"><span class="menu-icon"><i class="fas fa-tag"></i></span>Coupons &amp; Offers</a></li>
    <li><a href="target_master.html"><span class="menu-icon"><i class="fas fa-bullseye"></i></span>Targets</a></li>
  </ul>
  <div class="sidebar-section-title">Reports</div>
  <ul class="sidebar-menu">
    <li><a href="reports.html"><span class="menu-icon"><i class="fas fa-chart-bar"></i></span>Sales Reports</a></li>
    <li><a href="gst_reports.html"><span class="menu-icon"><i class="fas fa-file-alt"></i></span>GST Reports</a></li>
    <li><a href="aging_report.html"><span class="menu-icon"><i class="fas fa-clock"></i></span>Aging Report</a></li>
    <li><a href="salesman_report.html"><span class="menu-icon"><i class="fas fa-user-tie"></i></span>Salesman Report</a></li>
  </ul>
  <div class="sidebar-section-title">Communication</div>
  <ul class="sidebar-menu"><li><a href="sms_email.html"><span class="menu-icon"><i class="fas fa-envelope"></i></span>SMS &amp; Email</a></li></ul>
  <div class="sidebar-section-title">Administration</div>
  <ul class="sidebar-menu">
    <li><a href="users.html"><span class="menu-icon"><i class="fas fa-users"></i></span>User Management</a></li>
    <li><a href="area_master.html"><span class="menu-icon"><i class="fas fa-map-marker-alt"></i></span>Area Master</a></li>
    <li><a href="centers.html"><span class="menu-icon"><i class="fas fa-building"></i></span>Centers</a></li>
    <li><a href="notifications.html"><span class="menu-icon"><i class="fas fa-bell"></i></span>Notifications</a></li>
    <li><a href="settings.html"><span class="menu-icon"><i class="fas fa-cog"></i></span>Settings</a></li>
    <li><a href="settings.html"><span class="menu-icon"><i class="fas fa-history"></i></span>Audit Log</a></li>
  </ul>
  <div class="sidebar-divider"></div>
  <ul class="sidebar-menu"><li><button onclick="window.location.href='index.html'"><span class="menu-icon"><i class="fas fa-sign-out-alt"></i></span>Logout</button></li></ul>
</aside>'''

# Pages that already have new sidebar (skip them)
SKIP = {
    'new_sale.html','item_master.html','category_master.html','brand_list.html',
    'tax_master.html','coupon_master.html','target_master.html','gst_reports.html',
    'cashbook.html','salesman_report.html','aging_report.html','sms_email.html',
    'area_master.html','barcode_list.html','booking_master.html','index.html',
}

# Active class maps: filename -> sidebar href that should get "active" class
ACTIVE_MAP = {
    'welcome.html': 'welcome.html',
    'bill_upload.html': 'bill_upload.html',
    'bills.html': 'bills.html',
    'approvals.html': 'approvals.html',
    'purchase_orders.html': 'purchase_orders.html',
    'returns.html': 'returns.html',
    'suppliers.html': 'suppliers.html',
    'customers.html': 'customers.html',
    'pos_sales.html': 'pos_sales.html',
    'inventory.html': 'inventory.html',
    'stock_transfer.html': 'stock_transfer.html',
    'reports.html': 'reports.html',
    'expenses.html': 'expenses.html',
    'payments.html': 'payments.html',
    'users.html': 'users.html',
    'centers.html': 'centers.html',
    'notifications.html': 'notifications.html',
    'settings.html': 'settings.html',
    'profile.html': None,
}

updated = []
skipped = []
errors = []

for fname in sorted(os.listdir(TARGET_DIR)):
    if not fname.endswith('.html'):
        continue
    if fname in SKIP:
        skipped.append(fname)
        continue
    if fname not in ACTIVE_MAP:
        skipped.append(fname)
        continue

    fpath = os.path.join(TARGET_DIR, fname)
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            html = f.read()

        # Replace aside block
        pattern = r'<aside class="ma-sidebar"[^>]*>.*?</aside>'
        new_sidebar = NEW_SIDEBAR

        # Add active class to matching link
        active_href = ACTIVE_MAP.get(fname)
        if active_href:
            new_sidebar = new_sidebar.replace(
                f'href="{active_href}"',
                f'href="{active_href}" class="active"',
                1  # only first occurrence
            )

        new_html, count = re.subn(pattern, new_sidebar, html, flags=re.DOTALL)
        if count == 0:
            errors.append(f'{fname}: no <aside> found')
            continue

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_html)
        updated.append(fname)
    except Exception as e:
        errors.append(f'{fname}: {e}')

print(f'Updated: {len(updated)}')
for f in updated:
    print(f'  OK  {f}')
print(f'\nSkipped: {len(skipped)}')
print(f'Errors: {len(errors)}')
for e in errors:
    print(f'  ERR {e}')
