{
    "name": "HR Mission Management",
    "summary": "Employee Mission and Travel Management",
    "description": """
        HR Mission Management
        =====================
        Complete mission management system for tracking employee business travels:
        - Mission planning and approval workflow
        - Mission scales and allowances
        - Travel expense calculations
        - Mission reports and tracking
    """,
    "author": "SARL Transformatek",
    "website": "https://deploily.cloud",
    "category": "Human Resources",
    "version": "18.0.1.0.0",
    "depends": ["hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_dz_mission_scale_views.xml",
        "views/hr_dz_mission_views.xml",
        "views/hr_dz_mission_menus.xml",
        "report/ordre_mission.xml",
    ],
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
        'license': 'LGPL-3',

}
