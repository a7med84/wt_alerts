# -*- coding: utf-8 -*-
{
    'name': 'Documents Alert',
    'version': '14.0.1',
    'summary': 'Documents Alert',
    'description': 'Documents Alert',
    'category': 'base',
    'author': 'Hossam Galal',
    'depends': ['base', 'hr', 'mail'],
    'data': [
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'views/document_type.xml',
        'views/alerts.xml',
        'views/config.xml',
        'data/data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
