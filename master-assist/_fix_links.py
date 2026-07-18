"""Fix all href="#" placeholders across every page."""
import os, re

BASE = r'C:/Users/Administrator/Desktop/WEBSITES/amin claude/master-assist'

# -----------------------------------------------------------
# 1. Simple single-line replacements (safe for all pages)
# -----------------------------------------------------------
SIMPLE = [
    # User-dropdown links
    ('href="#"><i class="fas fa-user"></i> My Profile</a>',            'href="profile.html"><i class="fas fa-user"></i> My Profile</a>'),
    ('href="#"><i class="fas fa-cog"></i> Settings</a>',               'href="settings.html"><i class="fas fa-cog"></i> Settings</a>'),
    ('href="#"><i class="fas fa-shield-alt"></i> Change Password</a>', 'href="settings.html"><i class="fas fa-shield-alt"></i> Change Password</a>'),

    # Approval submenu
    ('<li><a href="#">Pending Approval</a></li>', '<li><a href="approvals.html">Pending Approval</a></li>'),
    ('<li><a href="#">Approved</a></li>',          '<li><a href="approvals.html">Approved</a></li>'),
    ('<li><a href="#">Rejected</a></li>',          '<li><a href="approvals.html">Rejected</a></li>'),

    # Reports submenu
    ('<li><a href="#">Daily Sales</a></li>',      '<li><a href="reports.html">Daily Sales</a></li>'),
    ('<li><a href="#">Monthly Summary</a></li>',  '<li><a href="reports.html">Monthly Summary</a></li>'),
    ('<li><a href="#">Stock Report</a></li>',     '<li><a href="reports.html">Stock Report</a></li>'),
    ('<li><a href="#">Bill Wise Report</a></li>', '<li><a href="reports.html">Bill Wise Report</a></li>'),

    # Single-line compact sidebar items (non-welcome pages)
    ('<li><a href="#"><span class="menu-icon"><i class="fas fa-receipt"></i></span>Purchase Orders</a></li>',    '<li><a href="purchase_orders.html"><span class="menu-icon"><i class="fas fa-receipt"></i></span>Purchase Orders</a></li>'),
    ('<li><a href="#"><span class="menu-icon"><i class="fas fa-exchange-alt"></i></span>Returns</a></li>',       '<li><a href="returns.html"><span class="menu-icon"><i class="fas fa-exchange-alt"></i></span>Returns</a></li>'),
    ('<li><a href="#"><span class="menu-icon"><i class="fas fa-cash-register"></i></span>POS Sales</a></li>',   '<li><a href="pos_sales.html"><span class="menu-icon"><i class="fas fa-cash-register"></i></span>POS Sales</a></li>'),
    ('<li><a href="#"><span class="menu-icon"><i class="fas fa-boxes"></i></span>Inventory</a></li>',            '<li><a href="inventory.html"><span class="menu-icon"><i class="fas fa-boxes"></i></span>Inventory</a></li>'),
    ('<li><a href="#"><span class="menu-icon"><i class="fas fa-chart-bar"></i></span>Reports</a></li>',          '<li><a href="reports.html"><span class="menu-icon"><i class="fas fa-chart-bar"></i></span>Reports</a></li>'),
    ('<li><a href="#"><span class="menu-icon"><i class="fas fa-users"></i></span>User Management</a></li>',      '<li><a href="users.html"><span class="menu-icon"><i class="fas fa-users"></i></span>User Management</a></li>'),
    ('<li><a href="#"><span class="menu-icon"><i class="fas fa-building"></i></span>Centers</a></li>',           '<li><a href="centers.html"><span class="menu-icon"><i class="fas fa-building"></i></span>Centers</a></li>'),
    ('<li><a href="#"><span class="menu-icon"><i class="fas fa-cog"></i></span>Settings</a></li>',               '<li><a href="settings.html"><span class="menu-icon"><i class="fas fa-cog"></i></span>Settings</a></li>'),
    ('<li><a href="#"><span class="menu-icon"><i class="fas fa-history"></i></span>Audit Log</a></li>',          '<li><a href="settings.html"><span class="menu-icon"><i class="fas fa-history"></i></span>Audit Log</a></li>'),
    ('<li><a href="#"><span class="menu-icon"><i class="fas fa-tasks"></i></span>Approvals</a></li>',            '<li><a href="approvals.html"><span class="menu-icon"><i class="fas fa-tasks"></i></span>Approvals</a></li>'),
    ('<li><a href="#"><span class="menu-icon"><i class="fas fa-store"></i></span>Store Management</a></li>',     '<li><a href="centers.html"><span class="menu-icon"><i class="fas fa-store"></i></span>Store Management</a></li>'),
]

# -----------------------------------------------------------
# 2. Multiline regex replacements (for welcome.html style sidebar)
#    Pattern: <a href="#">  ...icon+label...  </a>
# -----------------------------------------------------------
def make_multi(icon_class, label, dest):
    """Return (pattern, replacement) that fixes a multiline sidebar href."""
    pat = (
        r'<a href="#">(\s*'
        r'<span class="menu-icon"><i class="fas ' + re.escape(icon_class) + r'"></i></span>\s*'
        + re.escape(label) + r'\s*)</a>'
    )
    rep = r'<a href="' + dest + r'">\1</a>'
    return pat, rep

MULTILINE = [
    make_multi('fa-receipt',      'Purchase Orders',  'purchase_orders.html'),
    make_multi('fa-exchange-alt', 'Returns',          'returns.html'),
    make_multi('fa-cash-register','POS Sales',        'pos_sales.html'),
    make_multi('fa-boxes',        'Inventory',        'inventory.html'),
    make_multi('fa-store',        'Store Management', 'centers.html'),
    make_multi('fa-chart-bar',    'Reports',          'reports.html'),
    make_multi('fa-users',        'User Management',  'users.html'),
    make_multi('fa-building',     'Centers',          'centers.html'),
    make_multi('fa-cog',          'Settings',         'settings.html'),
    make_multi('fa-history',      'Audit Log',        'settings.html'),
]

# Quick-tile hrefs in welcome.html (match on inner icon class + label)
QUICK_TILES = [
    ('fa-tasks',        'Approvals',  'approvals.html'),
    ('fa-cash-register','POS Sales',  'pos_sales.html'),
    ('fa-chart-bar',    'Reports',    'reports.html'),
    ('fa-boxes',        'Inventory',  'inventory.html'),
]

def fix_quick_tile(content, icon_cls, label, dest):
    pat = (
        r'<a href="#" class="quick-tile">(\s*'
        r'<div[^>]*><i class="fas ' + re.escape(icon_cls) + r'"></i></div>\s*'
        r'<div class="quick-tile-label">' + re.escape(label) + r'</div>\s*)</a>'
    )
    return re.sub(pat, r'<a href="' + dest + r'" class="quick-tile">\1</a>', content)

# -----------------------------------------------------------
# 3. Apply to all HTML files
# -----------------------------------------------------------
changed = []
for fname in sorted(os.listdir(BASE)):
    if not fname.endswith('.html') or fname.startswith('_'):
        continue
    fpath = os.path.join(BASE, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        original = f.read()
    content = original

    # Simple replacements
    for old, new in SIMPLE:
        content = content.replace(old, new)

    # Multiline regex
    for pat, rep in MULTILINE:
        content = re.sub(pat, rep, content)

    # Quick tiles
    for icon_cls, label, dest in QUICK_TILES:
        content = fix_quick_tile(content, icon_cls, label, dest)

    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        changed.append(fname)

print('Fixed files:', changed if changed else 'none')

# Verify remaining href="#" (excluding settings.html panel nav which is intentional)
print('\nRemaining href="#" per file:')
for fname in sorted(os.listdir(BASE)):
    if not fname.endswith('.html') or fname.startswith('_'):
        continue
    fpath = os.path.join(BASE, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    hits = [(i+1, l.strip()) for i, l in enumerate(lines) if 'href="#"' in l]
    if hits:
        print(f'\n  {fname}:')
        for ln, text in hits:
            print(f'    L{ln}: {text[:90]}')
