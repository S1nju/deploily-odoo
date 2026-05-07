{
    "name": "Website Sale Terms",
    "ressource": """
        Website Sales Terms and Conditions and Privacy Policy Management
    """,
    "author": "SARL Transformatek",
    "website": "https://deploily.cloud",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    "category": "Uncategorized",
    'version': '18.0.1.0',
    # any module necessary for this one to work correctly
    "depends": ["website_terms", "website_sale"],
    # always loaded
    "data": [
        "views/address_template.xml",
        # "views/newsletter_template.xml",
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
