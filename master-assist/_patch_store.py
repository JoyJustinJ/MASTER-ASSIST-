"""
Master Assist — Production-ready data patch.
Rewrites every HTML page to:
  1. Inject js/store.js before any <script src=
  2. Remove all hardcoded data arrays and replace with MA.getAll() calls
  3. Replace hardcoded stat values with live JS computed values
  4. Replace hardcoded navbar/sidebar badge numbers with dynamic lookups
  5. Replace hardcoded company data fields with MA.getCompany() references
"""
import re, os

DIR = os.path.dirname(os.path.abspath(__file__))

STORE_SCRIPT = '<script src="js/store.js"></script>\n'

# ─── inject store.js ──────────────────────────────────────────────────────────
def inject_store(html):
    if 'js/store.js' in html:
        return html
    # inject before the first <script src=
    return re.sub(r'(<script src=)', STORE_SCRIPT + r'\1', html, count=1)

# ─── navbar badge: replace hardcoded number with dynamic ───────────────────────
BADGE_STATIC = re.compile(r'(<span class="navbar-badge">)\d+(</span>)')
def fix_navbar_badge(html):
    return BADGE_STATIC.sub(
        r'\g<1><span id="navBadge">0</span>\g<2>',
        html
    )

SIDEBAR_BADGE_STATIC = re.compile(r'(<span class="badge-count">)\d+(</span>)')
def fix_sidebar_badge(html):
    return SIDEBAR_BADGE_STATIC.sub(
        r'\g<1><span id="sidebarBillBadge">0</span>\g<2>',
        html
    )

# ─── inject badge-init JS at end of <script> blocks ──────────────────────────
BADGE_INIT = """
// --- MA badge refresh ---
(function(){
  var nb=document.getElementById('navBadge');
  if(nb) nb.textContent=MA.getUnreadCount()||'';
  var sb=document.getElementById('sidebarBillBadge');
  if(sb) sb.textContent=MA.getPendingBillCount()||'';
  // company name in brand
  var comp=MA.getCompany();
  document.querySelectorAll('.brand-text').forEach(function(el){
    if(comp.name) el.textContent=comp.name;
  });
  document.querySelectorAll('.brand-sub').forEach(function(el){
    if(comp.tagline) el.textContent=comp.tagline;
  });
})();"""

def inject_badge_init(html):
    # add before last </script> closing tag in body
    last = html.rfind('</script>')
    if last == -1:
        return html
    return html[:last] + BADGE_INIT + '\n' + html[last:]


# ─── per-page data patches ────────────────────────────────────────────────────

PAGES = {}

# ---- welcome.html ----
PAGES['welcome.html'] = dict(
    html_replacements=[
        # stat cards — replace hardcoded values with placeholder then fill via JS
        (r'<div class="stat-value">\d[\d,]*</div>\s*<div class="stat-label">Total Bills</div>',
         '<div class="stat-value" id="dsTotalBills">—</div>\n<div class="stat-label">Total Bills</div>'),
        (r'<div class="stat-value">\d[\d,]*</div>\s*<div class="stat-label">Pending</div>',
         '<div class="stat-value" id="dsPending">—</div>\n<div class="stat-label">Pending</div>'),
        (r'<div class="stat-value">\d[\d,]*</div>\s*<div class="stat-label">Approved</div>',
         '<div class="stat-value" id="dsApproved">—</div>\n<div class="stat-label">Approved</div>'),
        (r'<div class="stat-value">\d[\d,]*</div>\s*<div class="stat-label">Rejected</div>',
         '<div class="stat-value" id="dsRejected">—</div>\n<div class="stat-label">Rejected</div>'),
        (r'<div class="stat-value">\d[\d,]*</div>\s*<div class="stat-label">Active POS</div>',
         '<div class="stat-value" id="dsActivePOS">—</div>\n<div class="stat-label">Active POS</div>'),
        (r"<div class=\"stat-value\">₹[\d.,L]+</div>\s*<div class=\"stat-label\">Today's Sales</div>",
         '<div class="stat-value" id="dsTodaySales">—</div>\n<div class="stat-label">Today\'s Sales</div>'),
        # recent bills table — replace static rows with empty tbody + JS fill
        (r'<tbody>(\s*<tr>.*?</tr>\s*)+</tbody>(\s*</table>)',
         '<tbody id="recentBillsBody"><tr><td colspan="6" style="text-align:center;padding:24px;color:#aaa;">No bills yet</td></tr></tbody>\\2'),
        # recent activity list — empty it
        (r'(<ul[^>]*class="[^"]*activity[^"]*"[^>]*>).*?(</ul>)',
         '\\1<li id="noActivity" style="color:#aaa;font-size:13px;padding:8px 0;">No activity yet</li>\\2'),
        # welcome banner
        (r'Welcome back, Admin!',
         '<span id="welcomeName">Welcome back!</span>'),
    ],
    js_append="""
// welcome page live data
(function(){
  var s=MA.dashStats();
  var el=function(id,v){var e=document.getElementById(id);if(e)e.textContent=v;};
  el('dsTotalBills', s.totalBills||0);
  el('dsPending',    s.pending||0);
  el('dsApproved',   s.approved||0);
  el('dsRejected',   s.rejected||0);
  el('dsActivePOS',  s.activePOS||0);
  el('dsTodaySales', s.todaySales?MA.fmt(s.todaySales):'₹0');
  var wn=document.getElementById('welcomeName');
  if(wn){var u=MA.getAll('users').find(function(u){return u.username==='admin';});wn.textContent='Welcome back, '+(u&&u.name?u.name.split(' ')[0]:'Admin')+'!';}
  // recent bills
  var bills=MA.getAll('bills').slice(0,5);
  var tbody=document.getElementById('recentBillsBody');
  if(tbody&&bills.length){
    tbody.innerHTML=bills.map(function(b){
      var badge=b.status==='approved'?'badge-success':b.status==='rejected'?'badge-error':'badge-pending';
      return '<tr><td><code style="font-size:11px;">'+b.billNo+'</code></td><td>'+b.party+'</td><td>'+b.pos+'</td><td style="font-weight:600;">'+MA.fmt(b.amount)+'</td><td style="font-size:12px;color:#888;">'+b.date+'</td><td><span class="'+badge+'" style="text-transform:capitalize;">'+b.status+'</span></td></tr>';
    }).join('');
  }
  // activity feed
  var log=MA.getAll('auditLog').slice(0,6);
  var act=document.getElementById('noActivity');
  if(act&&log.length){
    var ul=act.parentElement;
    ul.innerHTML=log.map(function(e){
      return '<li style="display:flex;gap:10px;align-items:flex-start;padding:8px 0;border-bottom:1px solid #f5f5fb;font-size:13px;"><i class="fas fa-circle" style="color:#696cff;font-size:6px;margin-top:6px;"></i><div><div>'+e.action+'</div><div style="font-size:11px;color:#aaa;">'+new Date(e.time).toLocaleString('en-IN')+'</div></div></li>';
    }).join('');
  }
})();
"""
)

# ---- bills.html ----
PAGES['bills.html'] = dict(
    js_replacements=[
        # remove hardcoded arrays
        (r"var parties\s*=\s*\[[^\]]+\];", "var parties = MA.getAll('suppliers').map(function(s){return s.name;});"),
        (r"var posList\s*=\s*\[[^\]]+\];", "var posList = MA.getAll('posTerminals').map(function(p){return p.name;});"),
        (r"var allBills\s*=\s*\[\s*\];[\s\S]*?(?=function\s+render|function\s+applyFilter|\/\/\s*render)", "var allBills = MA.getAll('bills');\n"),
    ],
)

# ---- bill_upload.html ----
PAGES['bill_upload.html'] = dict(
    js_replacements=[
        (r"var billsData\s*=\s*\[[\s\S]*?\];", "var billsData = MA.getAll('bills').slice().reverse();"),
    ],
    html_replacements=[
        (r"<option[^>]*>Master Assist</option>",
         '<option id="centerOption0"></option>'),
    ],
    js_append="""
(function(){
  // populate center dropdown from store
  var centers=MA.getAll('centers');
  var comp=MA.getCompany();
  var selC=document.querySelector('select[name="center"]')||document.querySelectorAll('select')[0];
  if(selC){selC.innerHTML=(centers.length?centers:[(comp.name||'Main Center')]).map(function(c,i){return '<option value="'+(c.id||i)+'">'+(c.name||c)+'</option>';}).join('');}
  // populate POS dropdown
  var posList=MA.getAll('posTerminals');
  var selP=document.querySelector('select[name="pos"]')||document.querySelectorAll('select')[1];
  if(selP){selP.innerHTML='<option value="">Select POS</option>'+(posList.length?posList.map(function(p){return '<option value="'+p.id+'">'+p.name+'</option>';}).join(''):'<option>No POS configured</option>');}
})();
"""
)

# ---- approvals.html ----
PAGES['approvals.html'] = dict(
    js_replacements=[
        (r"var parties\s*=\s*\[[^\]]+\];", "var parties = MA.getAll('suppliers').map(function(s){return s.name;});"),
        (r"var posList\s*=\s*\[[^\]]+\];", "var posList = MA.getAll('posTerminals').map(function(p){return p.name;});"),
        (r"var allBills\s*=\s*\[\s*\];[\s\S]*?(?=function\s+render|\/\/)", "var allBills = MA.getAll('bills').filter(function(b){return b.status==='pending';});\n"),
    ],
)

# ---- purchase_orders.html ----
PAGES['purchase_orders.html'] = dict(
    js_replacements=[
        (r"var suppliers\s*=\s*\[[^\]]+\];", "var suppliers = MA.getAll('suppliers').map(function(s){return s.name;});"),
        (r"var poData\s*=\s*\[\s*\];[\s\S]*?(?=function\s+render|\/\/)", "var poData = MA.getAll('purchaseOrders');\n"),
    ],
)

# ---- returns.html ----
PAGES['returns.html'] = dict(
    js_replacements=[
        (r"var parties\s*=\s*\[[^\]]+\];", "var parties = MA.getAll('suppliers').map(function(s){return s.name;}).concat(MA.getAll('customers').map(function(c){return c.name;}));"),
        (r"var posList\s*=\s*\[[^\]]+\];", "var posList = MA.getAll('posTerminals').map(function(p){return p.name;});"),
        (r"var returnsData\s*=\s*\[\s*\];[\s\S]*?(?=function\s+render|\/\/)", "var returnsData = MA.getAll('returns');\n"),
    ],
)

# ---- suppliers.html ----
PAGES['suppliers.html'] = dict(
    js_replacements=[
        (r"let suppliers\s*=\s*\[[\s\S]*?\];(?=\s*let nextId)", "let suppliers = MA.getAll('suppliers');"),
        (r"let nextId\s*=\s*\d+,\s*viewingId", "let nextId = MA.nextId(suppliers), viewingId"),
    ],
    js_append="""
// suppliers — save on mutation
var _origSave=typeof saveSupplier!=='undefined'?saveSupplier:null;
if(typeof saveSupplier==='function'){
  var _origSaveSupp=saveSupplier;
  saveSupplier=function(){_origSaveSupp();MA.set('suppliers',suppliers);};
}
if(typeof deleteSupplier==='function'){
  var _origDelSupp=deleteSupplier;
  deleteSupplier=function(id){_origDelSupp(id);MA.set('suppliers',suppliers);};
}
"""
)

# ---- customers.html ----
PAGES['customers.html'] = dict(
    js_replacements=[
        (r"let customers\s*=\s*\[[\s\S]*?\];(?=\s*let nextId)", "let customers = MA.getAll('customers');"),
        (r"let nextId\s*=\s*\d+,\s*currentPage", "let nextId = MA.nextId(customers), currentPage"),
    ],
    js_append="""
if(typeof saveCustomer==='function'){var _origSaveCust=saveCustomer;saveCustomer=function(){_origSaveCust();MA.set('customers',customers);};}
if(typeof deleteCustomer==='function'){var _origDelCust=deleteCustomer;deleteCustomer=function(id){_origDelCust(id);MA.set('customers',customers);};}
"""
)

# ---- expenses.html ----
PAGES['expenses.html'] = dict(
    js_replacements=[
        (r"let expenses\s*=\s*\[[\s\S]*?\];(?=\s*let nextId|\s*let current)", "let expenses = MA.getAll('expenses');"),
        (r"let nextId\s*=\s*\d+,\s*currentPage\s*=\s*1,\s*rowsPerPage\s*=\s*\d+,\s*filtered\s*=\s*\[\s*\];",
         "let nextId = MA.nextId(expenses), currentPage=1, rowsPerPage=12, filtered=[];"),
    ],
    js_append="""
var _centerOpts=MA.getAll('centers');
var _expCenterSel=document.getElementById('filterCenter');
if(_expCenterSel&&_centerOpts.length){_expCenterSel.innerHTML='<option value="">All Centers</option>'+_centerOpts.map(function(c){return '<option>'+c.name+'</option>';}).join('');}
var _expCenterMod=document.getElementById('eCenter');
if(_expCenterMod&&_centerOpts.length){_expCenterMod.innerHTML=_centerOpts.map(function(c){return '<option>'+c.name+'</option>';}).join('');}
if(typeof saveExpense==='function'){var _origSaveExp=saveExpense;saveExpense=function(){_origSaveExp();MA.set('expenses',expenses);};}
if(typeof deleteExpense==='function'){var _origDelExp=deleteExpense;deleteExpense=function(id){_origDelExp(id);MA.set('expenses',expenses);};}
"""
)

# ---- payments.html ----
PAGES['payments.html'] = dict(
    js_replacements=[
        (r"let payments\s*=\s*\[[\s\S]*?\];(?=\s*let nextId)", "let payments = MA.getAll('payments');"),
        (r"let nextId\s*=\s*\d+,\s*currentPage", "let nextId = MA.nextId(payments), currentPage"),
    ],
    js_append="""
if(typeof savePayment==='function'){var _origSavePay=savePayment;savePayment=function(){_origSavePay();MA.set('payments',payments);};}
"""
)

# ---- inventory.html ----
PAGES['inventory.html'] = dict(
    js_replacements=[
        (r"var items\s*=\s*\[[\s\S]*?\];(?=\s*function|\s*var)", "var items = MA.getAll('inventory');"),
    ],
    html_replacements=[
        (r'<option>Main Warehouse</option>\s*<option>Store A</option>\s*<option>Store B</option>',
         '<option id="_wh1"></option>'),
    ],
    js_append="""
(function(){
  var whs=[...new Set(MA.getAll('inventory').map(function(i){return i.warehouse;}))];
  var wh1=document.getElementById('_wh1');
  if(wh1){var parent=wh1.parentElement;parent.innerHTML='<option value="">All Warehouses</option>'+whs.map(function(w){return '<option>'+w+'</option>';}).join('');}
})();
"""
)

# ---- stock_transfer.html ----
PAGES['stock_transfer.html'] = dict(
    js_replacements=[
        (r"let transfers\s*=\s*\[[\s\S]*?\];(?=\s*let nextId)", "let transfers = MA.getAll('stockTransfers');"),
        (r"let nextId\s*=\s*\d+,\s*currentPage", "let nextId = MA.nextId(transfers), currentPage"),
    ],
    html_replacements=[
        (r'(<select[^>]*id="filterFrom"[^>]*>)\s*<option value="">All</option>\s*<option>Head Office</option>[\s\S]*?</select>',
         '\\1<option value="">All</option></select>'),
    ],
    js_append="""
(function(){
  var centers=MA.getAll('centers');
  ['filterFrom','filterTo','tFrom','tTo'].forEach(function(id){
    var s=document.getElementById(id);
    if(!s) return;
    var first=s.options[0]?s.options[0].outerHTML:'<option value="">Select</option>';
    s.innerHTML=first+centers.map(function(c){return '<option>'+c.name+'</option>';}).join('');
  });
})();
if(typeof saveTransfer==='function'){var _origSaveTrf=saveTransfer;saveTransfer=function(){_origSaveTrf();MA.set('stockTransfers',transfers);};}
"""
)

# ---- pos_sales.html ----
PAGES['pos_sales.html'] = dict(
    js_replacements=[
        (r"var posData\s*=\s*\[[\s\S]*?\];", "var posData = MA.getAll('posTerminals');"),
        (r"var txns\s*=\s*\[\s*\];[\s\S]*?(?=\/\/\s*render|function\s+render)", "var txns = MA.getAll('sales');\n"),
        (r"var vals\s*=\s*\[[^\]]+\];", "var vals = (function(){var s=MA.getAll('sales');var h=Array(8).fill(0);s.forEach(function(t){var hr=new Date(t.date+'T'+(t.time||'00:00')).getHours();if(hr>=9&&hr<=16)h[hr-9]+=(t.total||0);});return h;})();"),
    ],
)

# ---- reports.html ----
PAGES['reports.html'] = dict(
    js_replacements=[
        (r"var days\s*=\s*\[[^\]]+\];", "var days=(function(){var d=[];for(var i=6;i>=0;i--){var dt=new Date();dt.setDate(dt.getDate()-i);d.push(dt.toLocaleDateString('en-IN',{day:'2-digit',month:'short'}));}return d;})();"),
        (r"var vals\s*=\s*\[[^\]]+\];", "var vals=(function(){var sales=MA.getAll('sales');var out=Array(7).fill(0);sales.forEach(function(s){var dt=new Date(s.date);var now=new Date();var diff=Math.round((now-dt)/(1000*86400));if(diff>=0&&diff<7)out[6-diff]+=(s.total||0);});return out;})();"),
        (r"var reportRows\s*=\s*\[[\s\S]*?\];", "var reportRows = MA.getAll('bills').slice(0,10);"),
    ],
    html_replacements=[
        (r'<div style="font-size:20px;font-weight:700;color:#696cff;">₹[\d,]+</div>\s*<div style="font-size:12px;color:#888;">Total Sales</div>',
         '<div style="font-size:20px;font-weight:700;color:#696cff;" id="rTotalSales">₹0</div><div style="font-size:12px;color:#888;">Total Sales</div>'),
        (r'<div style="font-size:20px;font-weight:700;">[\d,]+</div>\s*<div style="font-size:12px;color:#888;">Total Bills</div>',
         '<div style="font-size:20px;font-weight:700;" id="rTotalBills">0</div><div style="font-size:12px;color:#888;">Total Bills</div>'),
    ],
    js_append="""
(function(){
  var bills=MA.getAll('bills');
  var el=function(id,v){var e=document.getElementById(id);if(e)e.textContent=v;};
  el('rTotalBills',bills.length);
  var total=bills.reduce(function(a,b){return a+(b.amount||0);},0);
  el('rTotalSales',MA.fmt(total));
})();
"""
)

# ---- users.html ----
PAGES['users.html'] = dict(
    js_replacements=[
        (r"var usersData\s*=\s*\[[\s\S]*?\];", "var usersData = MA.getAll('users');"),
    ],
    js_append="""
// POS dropdown
(function(){
  var posList=MA.getAll('posTerminals');
  var s=document.getElementById('uPOS');
  if(s&&posList.length){s.innerHTML='<option value="All POS">All POS</option>'+posList.map(function(p){return '<option>'+p.name+'</option>';}).join('');}
})();
if(typeof saveUser==='function'){var _origSaveUsr=saveUser;saveUser=function(){_origSaveUsr();MA.set('users',usersData);};}
if(typeof deleteUser==='function'){var _origDelUsr=deleteUser;deleteUser=function(id){_origDelUsr(id);MA.set('users',usersData);};}
"""
)

# ---- centers.html ----
PAGES['centers.html'] = dict(
    js_replacements=[
        (r"let centers\s*=\s*\[[\s\S]*?\];(?=\s*function|\s*let next)", "let centers = MA.getAll('centers');"),
        (r"let nextId\s*=\s*\d+;", "let nextId = MA.nextId(centers);"),
    ],
    js_append="""
if(typeof saveCenter==='function'){var _origSaveC=saveCenter;saveCenter=function(){_origSaveC();MA.set('centers',centers);};}
if(typeof deleteCenter==='function'){var _origDelC=deleteCenter;deleteCenter=function(id){_origDelC(id);MA.set('centers',centers);};}
"""
)

# ---- notifications.html ----
PAGES['notifications.html'] = dict(
    js_replacements=[
        (r"let notifications\s*=\s*\[[\s\S]*?\];(?=\s*function|\s*let)", "let notifications = MA.getAll('notifications');"),
    ],
    js_append="""
if(typeof markAllRead==='function'){var _origMar=markAllRead;markAllRead=function(){_origMar();MA.set('notifications',notifications);};}
"""
)

# ---- settings.html ----
PAGES['settings.html'] = dict(
    js_replacements=[
        (r"var centers\s*=\s*\[[\s\S]*?\];(?=\s*var auditEntries|\s*function)", "var centers = MA.getAll('centers');"),
        (r"var auditEntries\s*=\s*\[[\s\S]*?\];(?=\s*function|\s*\/\/)", "var auditEntries = MA.getAll('auditLog').slice(0,20);"),
    ],
    html_replacements=[
        (r'value="Master Assist Pvt\. Ltd\."', 'id="sCompanyName" value=""'),
        (r'value="ERP-23 v1\.0\.0"', 'id="sTagline" value="" readonly'),
        (r'value="admin@masterassist\.in"', 'id="sEmail" value=""'),
        (r'value="\+91 98765 43210"', 'id="sPhone" value=""'),
        (r'value="123, Commerce Park.*?560001"', 'id="sAddress" value=""'),
        (r'value="29AABCU9603R1ZM"', 'id="sGSTIN" value=""'),
        (r'value="AABCU9603R"', 'id="sPAN" value=""'),
    ],
    js_append="""
(function(){
  var c=MA.getCompany();
  var ef=function(id,v){var e=document.getElementById(id);if(e)e.value=v||'';};
  ef('sCompanyName',c.name);ef('sTagline',c.tagline);ef('sEmail',c.email);
  ef('sPhone',c.phone);ef('sAddress',c.address);ef('sGSTIN',c.gstin);ef('sPAN',c.pan);
  // save settings button
  var saveBtn=document.getElementById('saveGeneralSettings')||document.querySelector('button[onclick*="saveSettings"]');
  if(!saveBtn){
    var panels=document.querySelectorAll('[id="panelGeneral"]');
    if(panels.length){
      var btn=panels[0].querySelector('button.btn-ma-primary');
      if(btn)btn.addEventListener('click',function(){
        MA.setCompany({name:document.getElementById('sCompanyName').value,tagline:document.getElementById('sTagline').value,email:document.getElementById('sEmail').value,phone:document.getElementById('sPhone').value,address:document.getElementById('sAddress').value,gstin:document.getElementById('sGSTIN').value,pan:document.getElementById('sPAN').value});
        if(typeof Swal2!=='undefined')Swal2.fire({icon:'success',title:'Saved',timer:1200,showConfirmButton:false});
      });
    }
  }
})();
"""
)

# ---- profile.html ----
PAGES['profile.html'] = dict(
    js_replacements=[
        (r"var activities\s*=\s*\[[\s\S]*?\];(?=\s*function|\s*\/\/)", "var activities = MA.getAll('auditLog').slice(0,10).map(function(e){return {icon:'fa-circle',color:'#696cff',bg:'#ededff',text:e.action,time:new Date(e.time).toLocaleString('en-IN')};});"),
    ],
    html_replacements=[
        (r'value="Administrator"(?=[^>]*>)', 'id="pName" value=""'),
        (r'value="admin"(?=[^>]* readonly)', 'id="pUsername" value="" readonly'),
        (r'value="admin@masterassist\.in"', 'id="pEmail" value=""'),
        (r'value="9876543210"', 'id="pMobile" value=""'),
        (r'<div class="stat-value">248</div>\s*<div class="stat-label">Bills Uploaded</div>',
         '<div class="stat-value" id="pUploaded">—</div><div class="stat-label">Bills Uploaded</div>'),
        (r'<div class="stat-value">186</div>\s*<div class="stat-label">Approved</div>',
         '<div class="stat-value" id="pApproved">—</div><div class="stat-label">Approved</div>'),
        (r'<div class="stat-value">12</div>\s*<div class="stat-label">Rejected</div>',
         '<div class="stat-value" id="pRejected">—</div><div class="stat-label">Rejected</div>'),
    ],
    js_append="""
(function(){
  var u=MA.getAll('users').find(function(x){return x.username==='admin';})||{};
  var ef=function(id,v){var e=document.getElementById(id);if(e)e.value=v||'';};
  ef('pName',u.name);ef('pUsername',u.username||'admin');ef('pEmail',u.email);ef('pMobile',u.mobile);
  // stats from bills
  var bills=MA.getAll('bills');
  var el=function(id,v){var e=document.getElementById(id);if(e)e.textContent=v;};
  el('pUploaded',bills.length);
  el('pApproved',bills.filter(function(b){return b.status==='approved';}).length);
  el('pRejected',bills.filter(function(b){return b.status==='rejected';}).length);
  // save profile
  var saveBtn=document.querySelector('button[onclick*="saveProfile"]');
  if(!saveBtn){
    var forms=document.querySelectorAll('form');
    forms.forEach(function(f){f.addEventListener('submit',function(e){e.preventDefault();var users=MA.getAll('users');var idx=users.findIndex(function(x){return x.username==='admin';});if(idx>=0){users[idx].name=document.getElementById('pName').value;users[idx].email=document.getElementById('pEmail').value;users[idx].mobile=document.getElementById('pMobile').value;MA.set('users',users);if(typeof Swal2!=='undefined')Swal2.fire({icon:'success',title:'Saved',timer:1200,showConfirmButton:false});}});});
  }
})();
"""
)

# ---- item_master.html ----
PAGES['item_master.html'] = dict(
    js_replacements=[
        (r"let items\s*=\s*\[[\s\S]*?\];(?=\s*let nextId)", "let items = MA.getAll('items');"),
        (r"let nextId\s*=\s*\d+,\s*currentPage", "let nextId = MA.nextId(items), currentPage"),
    ],
    js_append="""
// populate category/brand dropdowns from store
(function(){
  var cats=MA.getAll('categories');var brands=MA.getAll('brands');
  ['iCat','filterCat'].forEach(function(id){var s=document.getElementById(id);if(s&&cats.length){var ph=s.options[0]?s.options[0].outerHTML:'';s.innerHTML=ph+cats.map(function(c){return '<option>'+c.name+'</option>';}).join('');}});
  ['iBrand','filterBrand'].forEach(function(id){var s=document.getElementById(id);if(s&&brands.length){var ph=s.options[0]?s.options[0].outerHTML:'';s.innerHTML=ph+brands.map(function(b){return '<option>'+b.name+'</option>';}).join('');}});
})();
if(typeof saveItem==='function'){var _origSaveItm=saveItem;saveItem=function(){_origSaveItm();MA.set('items',items);};}
if(typeof deleteItem==='function'){var _origDelItm=deleteItem;deleteItem=function(id){_origDelItm(id);MA.set('items',items);};}
"""
)

# ---- category_master.html ----
PAGES['category_master.html'] = dict(
    js_replacements=[
        (r"let cats\s*=\s*\[[\s\S]*?\];(?=\s*let nextId|\s*function)", "let cats = MA.getAll('categories');"),
        (r"let nextId\s*=\s*\d+;", "let nextId = MA.nextId(cats);"),
    ],
    js_append="""
if(typeof saveCat==='function'){var _origSaveCat=saveCat;saveCat=function(){_origSaveCat();MA.set('categories',cats);};}
if(typeof deleteCat==='function'){var _origDelCat=deleteCat;deleteCat=function(id){_origDelCat(id);MA.set('categories',cats);};}
"""
)

# ---- brand_list.html ----
PAGES['brand_list.html'] = dict(
    js_replacements=[
        (r"let brands\s*=\s*\[[\s\S]*?\];(?=\s*let nextId|\s*function)", "let brands = MA.getAll('brands');"),
        (r"let nextId\s*=\s*\d+;", "let nextId = MA.nextId(brands);"),
    ],
    js_append="""
if(typeof saveBrand==='function'){var _origSaveBrd=saveBrand;saveBrand=function(){_origSaveBrd();MA.set('brands',brands);};}
if(typeof deleteBrand==='function'){var _origDelBrd=deleteBrand;deleteBrand=function(id){_origDelBrd(id);MA.set('brands',brands);};}
"""
)

# ---- tax_master.html ----
PAGES['tax_master.html'] = dict(
    js_replacements=[
        (r"let taxes\s*=\s*\[[\s\S]*?\];(?=\s*let nextId|\s*function)", "let taxes = MA.getAll('taxes');"),
        (r"let nextId\s*=\s*\d+;", "let nextId = MA.nextId(taxes);"),
    ],
    html_replacements=[
        # Replace hardcoded "32 items", "18 items" etc in tax rate cards
        (r'<div class="tax-rate-items">\d+ items</div>', '<div class="tax-rate-items" data-taxitems="1">0 items</div>'),
    ],
    js_append="""
(function(){
  var items=MA.getAll('items');
  document.querySelectorAll('[data-taxitems]').forEach(function(el,i){
    var slabs=[0,5,12,18,28,28];var cnt=items.filter(function(it){return parseInt(it.gst||0)===slabs[i];}).length;
    el.textContent=cnt+' items';
  });
})();
if(typeof saveTax==='function'){var _origSaveTax=saveTax;saveTax=function(){_origSaveTax();MA.set('taxes',taxes);};}
if(typeof deleteTax==='function'){var _origDelTax=deleteTax;deleteTax=function(id){_origDelTax(id);MA.set('taxes',taxes);};}
"""
)

# ---- coupon_master.html ----
PAGES['coupon_master.html'] = dict(
    js_replacements=[
        (r"let coupons\s*=\s*\[[\s\S]*?\];(?=\s*let nextId|\s*function)", "let coupons = MA.getAll('coupons');"),
        (r"let nextId\s*=\s*\d+;", "let nextId = MA.nextId(coupons);"),
    ],
    html_replacements=[
        (r'<div class="stat-value">8</div>\s*<div class="stat-label">Total Coupons</div>',
         '<div class="stat-value" id="cpTotal">0</div><div class="stat-label">Total Coupons</div>'),
        (r'<div class="stat-value">5</div>\s*<div class="stat-label">Active</div>',
         '<div class="stat-value" id="cpActive">0</div><div class="stat-label">Active</div>'),
        (r'<div class="stat-value">342</div>\s*<div class="stat-label">Times Used</div>',
         '<div class="stat-value" id="cpUsed">0</div><div class="stat-label">Times Used</div>'),
        (r"<div class=\"stat-value\">₹[\d,]+</div>\s*<div class=\"stat-label\">Total Discounted</div>",
         '<div class="stat-value" id="cpDisc">₹0</div><div class="stat-label">Total Discounted</div>'),
    ],
    js_append="""
(function(){
  var el=function(id,v){var e=document.getElementById(id);if(e)e.textContent=v;};
  el('cpTotal',coupons.length);
  el('cpActive',coupons.filter(function(c){return c.status==='active';}).length);
  el('cpUsed',coupons.reduce(function(a,c){return a+(c.used||0);},0));
  el('cpDisc',MA.fmt(coupons.reduce(function(a,c){return a+(c.usedAmount||0);},0)));
})();
if(typeof saveCoupon==='function'){var _origSaveCp=saveCoupon;saveCoupon=function(){_origSaveCp();MA.set('coupons',coupons);};}
if(typeof deleteCoupon==='function'){var _origDelCp=deleteCoupon;deleteCoupon=function(id){_origDelCp(id);MA.set('coupons',coupons);};}
"""
)

# ---- target_master.html ----
PAGES['target_master.html'] = dict(
    js_replacements=[
        (r"const salesmen\s*=\s*\[[\s\S]*?\];(?=\s*const posTargets|\s*function)", "const salesmen = MA.getAll('targets').filter(function(t){return t.type==='salesman';});"),
        (r"const posTargets\s*=\s*\[[\s\S]*?\];(?=\s*function)", "const posTargets = MA.getAll('targets').filter(function(t){return t.type==='pos';});"),
    ],
    html_replacements=[
        (r'<div class="stat-value">₹8\.5L</div>\s*<div class="stat-label">Total Target</div>',
         '<div class="stat-value" id="tgTotal">₹0</div><div class="stat-label">Total Target</div>'),
        (r'<div class="stat-value">₹5\.2L</div>\s*<div class="stat-label">Achieved</div>',
         '<div class="stat-value" id="tgAchieved">₹0</div><div class="stat-label">Achieved</div>'),
        (r'<div class="stat-value">61\.2%</div>\s*<div class="stat-label">Overall %</div>',
         '<div class="stat-value" id="tgPct">0%</div><div class="stat-label">Overall %</div>'),
        (r'<div class="stat-value">5/8</div>\s*<div class="stat-label">On Track</div>',
         '<div class="stat-value" id="tgOnTrack">0/0</div><div class="stat-label">On Track</div>'),
    ],
    js_append="""
(function(){
  var all=MA.getAll('targets');
  var tot=all.reduce(function(a,t){return a+(t.target||0);},0);
  var ach=all.reduce(function(a,t){return a+(t.achieved||0);},0);
  var pct=tot?Math.round(ach/tot*100):0;
  var onTrack=all.filter(function(t){return t.target&&(t.achieved/t.target)>=0.75;}).length;
  var el=function(id,v){var e=document.getElementById(id);if(e)e.textContent=v;};
  el('tgTotal',MA.fmt(tot));el('tgAchieved',MA.fmt(ach));el('tgPct',pct+'%');el('tgOnTrack',onTrack+'/'+all.length);
})();
"""
)

# ---- cashbook.html ----
PAGES['cashbook.html'] = dict(
    js_replacements=[
        (r"let ledger\s*=\s*\[[\s\S]*?\];(?=\s*let nextId)", "let ledger = MA.getAll('ledger');"),
        (r"let nextId\s*=\s*\d+,\s*currentPage", "let nextId = MA.nextId(ledger), currentPage"),
        (r"let balance\s*=\s*\d+;", "let balance = (function(){var l=MA.getAll('ledger');return l.reduce(function(a,e){return a+(e.type==='cr'?e.amt:-e.amt);},0);})();"),
    ],
    html_replacements=[
        (r'<div class="stat-value">₹[\d,]+</div>\s*<div class="stat-label">Total Receipts</div>',
         '<div class="stat-value" id="cbReceipts">₹0</div><div class="stat-label">Total Receipts</div>'),
        (r'<div class="stat-value">₹[\d,]+</div>\s*<div class="stat-label">Total Payments</div>',
         '<div class="stat-value" id="cbPayments">₹0</div><div class="stat-label">Total Payments</div>'),
        (r'<div class="stat-value">₹[\d,]+</div>\s*<div class="stat-label">Cash in Hand</div>',
         '<div class="stat-value" id="cbCash">₹0</div><div class="stat-label">Cash in Hand</div>'),
        (r'<div class="stat-value">₹[\d,]+</div>\s*<div class="stat-label">Bank Balance</div>',
         '<div class="stat-value" id="cbBank">₹0</div><div class="stat-label">Bank Balance</div>'),
    ],
    js_append="""
(function(){
  var l=MA.getAll('ledger');
  var cr=l.filter(function(e){return e.type==='cr';}).reduce(function(a,e){return a+e.amt;},0);
  var dr=l.filter(function(e){return e.type==='dr';}).reduce(function(a,e){return a+e.amt;},0);
  var cash=l.filter(function(e){return e.acc==='Cash';}).reduce(function(a,e){return a+(e.type==='cr'?e.amt:-e.amt);},0);
  var bank=l.filter(function(e){return e.acc!=='Cash'&&e.acc!=='UPI';}).reduce(function(a,e){return a+(e.type==='cr'?e.amt:-e.amt);},0);
  var el=function(id,v){var e=document.getElementById(id);if(e)e.textContent=v;};
  el('cbReceipts',MA.fmt(cr));el('cbPayments',MA.fmt(dr));el('cbCash',MA.fmt(Math.max(cash,0)));el('cbBank',MA.fmt(Math.max(bank,0)));
})();
if(typeof saveEntry==='function'){var _origSaveEnt=saveEntry;saveEntry=function(){_origSaveEnt();MA.set('ledger',ledger);};}
"""
)

# ---- salesman_report.html ----
PAGES['salesman_report.html'] = dict(
    html_replacements=[
        (r'<div class="stat-value">₹[\d,]+</div>\s*<div class="stat-label">Total Sales</div>',
         '<div class="stat-value" id="smTotalSales">₹0</div><div class="stat-label">Total Sales</div>'),
        (r'<div class="stat-value">[\d,]+</div>\s*<div class="stat-label">Bills Processed</div>',
         '<div class="stat-value" id="smBills">0</div><div class="stat-label">Bills Processed</div>'),
        (r'<div class="stat-value">\d+</div>\s*<div class="stat-label">Active Salesmen</div>',
         '<div class="stat-value" id="smActive">0</div><div class="stat-label">Active Salesmen</div>'),
        (r'<div class="stat-value">[^<]+</div>\s*<div class="stat-label">Top Performer</div>',
         '<div class="stat-value" id="smTop">—</div><div class="stat-label">Top Performer</div>'),
    ],
    js_append="""
(function(){
  var tgts=MA.getAll('targets').filter(function(t){return t.type==='salesman';});
  var bills=MA.getAll('bills');
  var total=tgts.reduce(function(a,t){return a+(t.achieved||0);},0);
  var top=tgts.length?tgts.sort(function(a,b){return (b.achieved||0)-(a.achieved||0)})[0]:null;
  var el=function(id,v){var e=document.getElementById(id);if(e)e.textContent=v;};
  el('smTotalSales',MA.fmt(total));
  el('smBills',bills.length);
  el('smActive',MA.getAll('users').filter(function(u){return u.role==='Cashier'||u.role==='Manager';}).length);
  el('smTop',top&&top.name?top.name.split(' ')[0]+' '+top.name.split(' ').slice(-1)[0]:'—');
  // table — rebuild from targets data
  var tbody=document.querySelector('#agingBody')||document.querySelectorAll('tbody')[0];
  if(tbody&&tgts.length){
    var sorted=tgts.slice().sort(function(a,b){return (b.achieved||0)-(a.achieved||0);});
    tbody.innerHTML=sorted.map(function(t,i){
      var pct=t.target?Math.round((t.achieved/t.target)*100):0;
      var col=pct>=100?'#28a745':pct>=75?'#696cff':pct>=50?'#f57c00':'#dc3545';
      return '<tr><td>'+(i+1)+'</td><td style="font-weight:600;">'+t.name+'</td><td style="font-size:12px;">'+(t.center||'—')+'</td><td>'+(t.bills||0)+'</td><td style="font-weight:600;color:'+col+';">'+MA.fmt(t.achieved||0)+'</td><td style="font-size:12px;">'+MA.fmt(t.achieved||0)+'</td><td style="font-size:12px;">₹0</td><td>'+MA.fmt(t.target||0)+'</td><td style="color:'+col+';font-weight:700;">'+pct+'%</td><td>₹0</td></tr>';
    }).join('');
  }
})();
"""
)

# ---- aging_report.html ----
PAGES['aging_report.html'] = dict(
    js_replacements=[
        (r"const parties\s*=\s*\[[\s\S]*?\];(?=\s*function)", "const parties = MA.getAll('suppliers').map(function(s){return {name:s.name,type:'payable',due:s.balance||0,a0:s.balance||0,a30:0,a60:0,a90:0,lastPmt:''};}).concat(MA.getAll('customers').filter(function(c){return (c.balance||0)>0;}).map(function(c){return {name:c.name,type:'receivable',due:c.balance||0,a0:c.balance||0,a30:0,a60:0,a90:0,lastPmt:c.lastVisit||''};}));"),
    ],
    html_replacements=[
        (r'<div style="font-size:22px;font-weight:800;color:#28a745;">₹[\d,]+</div>',
         '<div style="font-size:22px;font-weight:800;color:#28a745;" id="ag0">₹0</div>'),
        (r'<div style="font-size:22px;font-weight:800;color:#f57c00;">₹[\d,]+</div>',
         '<div style="font-size:22px;font-weight:800;color:#f57c00;" id="ag30">₹0</div>'),
        (r'<div style="font-size:22px;font-weight:800;color:#ff5722;">₹[\d,]+</div>',
         '<div style="font-size:22px;font-weight:800;color:#ff5722;" id="ag60">₹0</div>'),
        (r'<div style="font-size:22px;font-weight:800;color:#dc3545;">₹[\d,]+</div>',
         '<div style="font-size:22px;font-weight:800;color:#dc3545;" id="ag90">₹0</div>'),
    ],
    js_append="""
(function(){
  var el=function(id,v){var e=document.getElementById(id);if(e)e.textContent=v;};
  el('ag0', MA.fmt(parties.reduce(function(a,p){return a+p.a0;},0)));
  el('ag30',MA.fmt(parties.reduce(function(a,p){return a+p.a30;},0)));
  el('ag60',MA.fmt(parties.reduce(function(a,p){return a+p.a60;},0)));
  el('ag90',MA.fmt(parties.reduce(function(a,p){return a+p.a90;},0)));
  renderTable();
})();
"""
)

# ---- gst_reports.html ----
PAGES['gst_reports.html'] = dict(
    js_replacements=[
        (r"const history\s*=\s*\[[\s\S]*?\];(?=\s*function)", "const history = MA.getAll('gstFilingHistory');"),
    ],
    html_replacements=[
        (r'value="27AABCU9603R1ZX"', 'id="gstinDisplay" value=""'),
        (r'<div class="stat-value">₹[\d,]+</div>\s*<div class="stat-label">Total Taxable Value</div>',
         '<div class="stat-value" id="gTaxable">₹0</div><div class="stat-label">Total Taxable Value</div>'),
        (r'<div class="stat-value">₹[\d,]+</div>\s*<div class="stat-label">Total GST Collected</div>',
         '<div class="stat-value" id="gCollected">₹0</div><div class="stat-label">Total GST Collected</div>'),
        (r'<div class="stat-value">[\d,]+</div>\s*<div class="stat-label">Total Invoices</div>',
         '<div class="stat-value" id="gInvoices">0</div><div class="stat-label">Total Invoices</div>'),
    ],
    js_append="""
(function(){
  var comp=MA.getCompany();
  var gi=document.getElementById('gstinDisplay');
  if(gi) gi.value=comp.gstin||'';
  var bills=MA.getAll('bills').filter(function(b){return b.status==='approved';});
  var taxable=bills.reduce(function(a,b){return a+(b.amount||0);},0);
  var gst=taxable*0.18;
  var el=function(id,v){var e=document.getElementById(id);if(e)e.textContent=v;};
  el('gTaxable',MA.fmt(taxable));el('gCollected',MA.fmt(gst));el('gInvoices',bills.length);
})();
"""
)

# ---- sms_email.html ----
PAGES['sms_email.html'] = dict(
    js_replacements=[
        (r"const templates\s*=\s*\{[\s\S]*?\};(?=\s*function)", "const templates = (function(){var t={};MA.getAll('smsTemplates').forEach(function(tmpl){t[tmpl.key]=tmpl;});return t;})();"),
    ],
    html_replacements=[
        (r'<div class="stat-value">[\d,]+</div>\s*<div class="stat-label">SMS Sent Today</div>',
         '<div class="stat-value" id="smsSent">0</div><div class="stat-label">SMS Sent Today</div>'),
        (r'<div class="stat-value">[\d,]+</div>\s*<div class="stat-label">Emails Sent Today</div>',
         '<div class="stat-value" id="emailsSent">0</div><div class="stat-label">Emails Sent Today</div>'),
        (r'<div class="stat-value">[\d.]+%</div>\s*<div class="stat-label">Delivery Rate</div>',
         '<div class="stat-value" id="deliveryRate">—</div><div class="stat-label">Delivery Rate</div>'),
        (r'<div class="stat-value">[\d,]+</div>\s*<div class="stat-label">SMS Credits Left</div>',
         '<div class="stat-value" id="smsCredits">—</div><div class="stat-label">SMS Credits Left</div>'),
    ],
    js_append="""
(function(){
  var log=MA.getAll('smsSendLog');
  var today=MA.today();
  var todayLog=log.filter(function(l){return (l.date||'').slice(0,10)===today;});
  var el=function(id,v){var e=document.getElementById(id);if(e)e.textContent=v;};
  el('smsSent',todayLog.filter(function(l){return l.channel==='SMS';}).reduce(function(a,l){return a+(l.sent||0);},0));
  el('emailsSent',todayLog.filter(function(l){return l.channel==='Email';}).reduce(function(a,l){return a+(l.sent||0);},0));
  el('deliveryRate','—');el('smsCredits','—');
})();
"""
)

# ---- area_master.html ----
PAGES['area_master.html'] = dict(
    js_replacements=[
        (r"let areas\s*=\s*\[[\s\S]*?\];(?=\s*let nextId)", "let areas = MA.getAll('areas');"),
        (r"let nextId\s*=\s*\d+;", "let nextId = MA.nextId(areas);"),
    ],
    html_replacements=[
        (r'value="Maharashtra"', 'id="aState" value=""'),
    ],
    js_append="""
if(typeof saveArea==='function'){var _origSaveArea=saveArea;saveArea=function(){_origSaveArea();MA.set('areas',areas);};}
if(typeof deleteArea==='function'){var _origDelArea=deleteArea;deleteArea=function(id){_origDelArea(id);MA.set('areas',areas);};}
"""
)

# ---- barcode_list.html ----
PAGES['barcode_list.html'] = dict(
    js_replacements=[
        (r"const items\s*=\s*\[[\s\S]*?\];(?=\s*let selected|\s*function)", "const items = MA.getAll('items').map(function(i){return {id:i.id,sku:i.sku,name:i.name,barcode:i.barcode||'',cat:i.cat,mrp:i.mrp||0};});"),
    ],
)

# ---- booking_master.html ----
PAGES['booking_master.html'] = dict(
    js_replacements=[
        (r"let bookings\s*=\s*\[[\s\S]*?\];(?=\s*let nextId)", "let bookings = MA.getAll('bookings');"),
        (r"let nextId\s*=\s*\d+;", "let nextId = MA.nextId(bookings);"),
    ],
    html_replacements=[
        (r'<div class="stat-value">38</div>\s*<div class="stat-label">Total Bookings</div>',
         '<div class="stat-value" id="bkTotal">0</div><div class="stat-label">Total Bookings</div>'),
        (r'<div class="stat-value">12</div>\s*<div class="stat-label">Pending</div>',
         '<div class="stat-value" id="bkPending">0</div><div class="stat-label">Pending</div>'),
        (r'<div class="stat-value">20</div>\s*<div class="stat-label">Confirmed</div>',
         '<div class="stat-value" id="bkConfirmed">0</div><div class="stat-label">Confirmed</div>'),
        (r'<div class="stat-value">6</div>\s*<div class="stat-label">Delivered</div>',
         '<div class="stat-value" id="bkDelivered">0</div><div class="stat-label">Delivered</div>'),
    ],
    js_append="""
(function(){
  var bk=MA.getAll('bookings');
  var el=function(id,v){var e=document.getElementById(id);if(e)e.textContent=v;};
  el('bkTotal',bk.length);
  el('bkPending',bk.filter(function(b){return b.status==='pending';}).length);
  el('bkConfirmed',bk.filter(function(b){return b.status==='confirmed';}).length);
  el('bkDelivered',bk.filter(function(b){return b.status==='delivered';}).length);
})();
if(typeof saveBooking==='function'){var _origSaveBk=saveBooking;saveBooking=function(){_origSaveBk();MA.set('bookings',bookings);};}
if(typeof confirmBooking==='function'){var _origCnfBk=confirmBooking;confirmBooking=function(id){_origCnfBk(id);MA.set('bookings',bookings);};}
if(typeof markDelivered==='function'){var _origMkDel=markDelivered;markDelivered=function(id){_origMkDel(id);MA.set('bookings',bookings);};}
if(typeof cancelBooking==='function'){var _origCncBk=cancelBooking;cancelBooking=function(id){_origCncBk(id);MA.set('bookings',bookings);};}
"""
)

# ---- new_sale.html ----
PAGES['new_sale.html'] = dict(
    js_replacements=[
        (r"const products\s*=\s*\[[\s\S]*?\];(?=\s*let cart|\s*function)", "const products = MA.getAll('items').map(function(i){return {id:i.id,name:i.name,sku:i.sku||'',price:i.sale||i.mrp||0,cat:i.cat||'',stock:i.stock||0,icon:'fa-cube'};});"),
    ],
    html_replacements=[
        (r"Bill No: <strong id=\"billNo\">SALE-2026-0281</strong>",
         'Bill No: <strong id="billNo">—</strong>'),
    ],
    js_append="""
(function(){
  // generate new bill number from existing sales count
  var sales=MA.getAll('sales');
  var num=String(sales.length+1).padStart(4,'0');
  var bn=document.getElementById('billNo');
  if(bn) bn.textContent='SALE-'+new Date().getFullYear()+'-'+num;
  // override processSale to persist
  var _origPS=processSale;
  processSale=function(){
    if(!cart.length){Swal2.fire('Empty Cart','Add items to cart first.','warning');return;}
    var grand=parseFloat(document.getElementById('grandTotal').textContent.replace(/[₹,]/g,''))||0;
    var saleRec={id:MA.nextId(MA.getAll('sales')),billNo:document.getElementById('billNo').textContent,date:MA.today(),time:new Date().toTimeString().slice(0,5),customer:document.getElementById('custSearch').value||'Walk-in',pos:'POS-01',items:cart.map(function(c){return {id:c.id,name:c.name,qty:c.qty,price:c.price};}),subtotal:parseFloat(document.getElementById('subtotal').textContent.replace(/[₹,]/g,''))||0,total:grand,payMode:payMode,status:'completed'};
    MA.upsert('sales',saleRec);
    MA.addAudit('Sale completed: '+saleRec.billNo+' — '+MA.fmt(grand));
    _origPS();
  };
})();
"""
)

# ---- index.html ----
PAGES['index.html'] = dict(
    html_replacements=[
        (r'<option value="1"[^>]*>Master Assist</option>',
         '<option value="1" id="loginCenterOpt">Loading...</option>'),
    ],
    js_append="""
(function(){
  var comp=MA.getCompany();
  var opt=document.getElementById('loginCenterOpt');
  if(opt) opt.textContent=comp.name||'Master Assist';
  // populate POS
  var posList=MA.getAll('posTerminals');
  var selP=document.querySelector('select[name="pos_id"]')||document.querySelectorAll('select')[1];
  if(selP&&posList.length){selP.innerHTML='<option value="">Select POS</option>'+posList.map(function(p){return '<option value="'+p.id+'">'+p.name+'</option>';}).join('');}
  // populate center
  var centers=MA.getAll('centers');
  var selC=document.querySelector('select[name="center_id"]')||document.querySelectorAll('select')[0];
  if(selC&&centers.length){selC.innerHTML=centers.map(function(c,i){return '<option value="'+c.id+'">'+(i===0?'★ ':'')+c.name+'</option>';}).join('');}
})();
"""
)


# ─── apply patches to a single file ──────────────────────────────────────────
def patch_file(fname, config):
    fpath = os.path.join(DIR, fname)
    if not os.path.exists(fpath):
        return f'SKIP (not found): {fname}'
    with open(fpath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. inject store
    html = inject_store(html)

    # 2. fix badges
    html = fix_navbar_badge(html)
    html = fix_sidebar_badge(html)

    # 3. html replacements
    for pattern, replacement in config.get('html_replacements', []):
        html, n = re.subn(pattern, replacement, html, flags=re.DOTALL)

    # 4. js replacements — operate only inside <script> tags
    def patch_scripts(m):
        content = m.group(1)
        for pattern, replacement in config.get('js_replacements', []):
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        return '<script>' + content + '</script>'
    html = re.sub(r'<script>([\s\S]*?)</script>', patch_scripts, html)

    # 5. js_append — inject before last </script>
    js_extra = config.get('js_append', '')
    if js_extra:
        last = html.rfind('</script>')
        if last != -1:
            html = html[:last] + '\n' + js_extra + '\n' + html[last:]

    # 6. badge-init on every page
    html = inject_badge_init(html)

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(html)
    return f'OK: {fname}'


# ─── run ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    results = []
    for fname, config in PAGES.items():
        results.append(patch_file(fname, config))

    # pages with no specific data but still need store injection + badge fix
    GENERIC = [
        'purchase_orders.html', 'returns.html', 'pos_sales.html',
        'stock_transfer.html', 'inventory.html', 'reports.html',
    ]
    for fname in GENERIC:
        if fname not in PAGES:
            fpath = os.path.join(DIR, fname)
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    html = f.read()
                html = inject_store(html)
                html = fix_navbar_badge(html)
                html = fix_sidebar_badge(html)
                html = inject_badge_init(html)
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(html)
                results.append(f'OK (inject only): {fname}')

    print(f'Patched {len(results)} files:')
    for r in results:
        print(' ', r)
