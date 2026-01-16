{
    "name": "HR Algeria - Employee",
    "summary": "Algerian Employee Extensions",
    "description": "Employee and Leave management extensions for Algeria",
    "author": "SARL Transformatek",
    "website": "https://transformatek.dz",
    "category": "Human Resources/Localization",
    "version": "18.0.1.0.0",
    "depends": ["hr","hr_contract","hr_holidays"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_employee_views.xml",
        "reports/contrat_de_travail.xml",
    ],
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
}
