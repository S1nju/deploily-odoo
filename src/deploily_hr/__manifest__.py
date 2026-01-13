{
    "name": "deploily_hr",
    "ressource": """
     hr with Deploily
    """,
    "author": "SARL Transformatek",
    "website": "https://transformatek.dz",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "contacts","website","hr","hr_contract","hr_holidays"],
    # always loaded
    "data": [
         
         "security/ir.model.access.csv",
        
        "views/menus.xml",
        "views/hr_models_views.xml",
       

      
    ],
    "license": "Other proprietary",
    "assets": {
        "web.assets_frontend": [],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
}
