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
        
        "views/hr_mission_scale_views.xml",
        "views/hr_education_views.xml",
        "views/hr_discipline_views.xml",
        "views/hr_evaluation_views.xml",
        "views/hr_medical_views.xml",
        "views/hr_mession_views.xml",
        "views/hr_promotion_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_contract_views.xml",
        "views/hr_leave_views.xml",
        "views/hr_menus.xml",
       

      
    ],
    "license": "Other proprietary",
    "assets": {
        "web.assets_frontend": [],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
}
