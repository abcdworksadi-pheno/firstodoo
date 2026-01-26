# -*- coding: utf-8 -*-
{
    'name': "ABCD Sales Pro",
    'summary': "Module de vente avancé ABCD (exemple avec licence)",
    'description': """
ABCD Sales Pro
==============

Module exemple démontrant l'intégration du système de licence ABCD.

Fonctionnalités :
-----------------
* Gestion avancée des ventes
* Rapports personnalisés
* Intégration CRM

Ce module nécessite une licence ABCD valide.
    """,
    'author': "ABCD",
    'website': "https://www.abcd.com",
    'category': 'ABCD',
    'version': '1.0.0',
    'depends': ['base', 'sale', 'abcd_license_core'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
