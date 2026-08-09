{
    'name': 'Contacts - Restrict by Salesperson',
    'version': '18.0.1.1.0',
    'summary': 'Restrict contact (res.partner) visibility to the assigned salesperson',
    'description': """
Contacts - Restrict by Salesperson
===================================

Restricts visibility of Contacts (res.partner) so that a salesperson only
sees contacts where:

* they are set as the Salesperson on the contact (``user_id``), or
* they created the contact themselves, or
* the contact is a child (e.g. a person) of a company contact they are
  the Salesperson of, or
* they are the Salesperson of a CRM opportunity (crm.lead) that points
  to this contact.

Safeguards included so the restriction doesn't break normal Odoo behaviour:

* A restricted user can always see their own related partner record
  (needed for their avatar, chatter, preferences, etc. to keep working).
* A restricted user can always see the company's own partner record.

Users who are NOT put in the new "Contacts: Restricted to Own" group are
completely unaffected (full admins, "User: All Documents", etc.).

Installation notes
-------------------
1. Install this module.
2. Go to Settings > Users & Companies > Users.
3. Open the salesperson you want to restrict, enable Developer mode if
   needed, and add them to the group "Contacts: Restricted to Own"
   (found under the Sales section of the Groups list, or via the
   "Other" field on the user form in developer mode).
4. Make sure each contact that the salesperson should see has its
   Salesperson field (Sales & Purchase tab) set to that user.

Note: because res.partner is referenced from many other models (sale
orders, invoices, CRM leads, etc.), a user may still hit an access error
if they open a document that points to a contact they are not allowed to
see (e.g. a lead whose contact's Salesperson field isn't set to them).
Keeping the Salesperson field consistent across Contacts/CRM/Sales avoids
this in practice.
    """,
    'category': 'Sales/CRM',
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': ['contacts', 'crm'],
    'data': [
        'security/contact_restrict_security.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
