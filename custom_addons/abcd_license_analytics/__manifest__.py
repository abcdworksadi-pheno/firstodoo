# -*- coding: utf-8 -*-
{
    'name': "ABCD License Analytics",
    'summary': "Analyses avancées et graphiques pour la surveillance des licences",
    'description': """
ABCD License Analytics
======================

Module d'analyses avancées et de surveillance pour le système de licences ABCD.

Fonctionnalités :
-----------------
* Dashboards personnalisés pour la surveillance
* Graphiques de tendances et statistiques
* Analyses de performance des licences
* Rapports d'expiration et alertes
* Analyses par client, édition, module
* Graphiques interactifs personnalisés
* Surveillance en temps réel
    """,
    'author': "ABCD",
    'website': "https://www.abcd.com",
    'category': 'Tools',
    'version': '1.0.0',
    'depends': ['abcd_license_server', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/analytics_menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'abcd_license_analytics/static/src/js/dashboard_widget.js',
            'abcd_license_analytics/static/src/css/dashboard.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
