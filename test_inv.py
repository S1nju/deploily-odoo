import xmlrpc.client
url = "http://localhost:8069"
db = "odoo"
username = "admin"
password = "a" # Odoo master password is not needed for xmlrpc, but we need the admin user's password. The user might have a different password.

# let's assume the password is "admin"
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, "admin", {})

if uid:
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    invoices = models.execute_kw(db, uid, "admin", 'account.move', 'search_read', [[['move_type', '=', 'out_invoice']]], {'fields': ['name', 'state', 'payment_state', 'amount_total', 'amount_residual', 'partner_id']})
    print(invoices)
else:
    print("Authentication failed")
