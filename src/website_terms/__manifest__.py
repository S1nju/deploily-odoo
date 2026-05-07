{
    "name": "website_terms",
    "ressource": """
        Website Terms and Conditions and Privacy Policy Management
    """,
    "author": "SARL Transformatek",
    "website": "https://deploily.cloud",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    "category": "Uncategorized",
    'version': '18.0.1.0',
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "auth_signup",
        "contacts",
        "website",
    ],
    # always loaded
    "data": [
        "views/website_views.xml",
        "views/signup_login_templates.xml",
        "views/menus.xml",
        # "views/newsletter_template.xml",
        "data/contactus_templates.xml",
    ],
    "license": "Other proprietary",
    "assets": {
        "web.assets_frontend": [],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
        'license': 'LGPL-3',

}
