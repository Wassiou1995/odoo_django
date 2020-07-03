{
    'name': "Daily Reports",

    'summary': """Items of Projects""",

    'description': """this module is for estimate and manage projects in doha """,

    'author': "Wassim Guesmi",
    'website': "http://five-consulting.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Construction management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'project',
                'mail',
                'board',
                'survey'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/daily_production.xml',
        'views/daily_delivery.xml',
        'views/daily_site.xml',
        'data/sequence.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}