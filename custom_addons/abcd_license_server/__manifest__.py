# -*- coding: utf-8 -*-
{
    'name': "ABCD License Server",
    'summary': "Serveur de gestion et génération de licences ABCD",
    'description': """
ABCD License Server
===================

Module serveur pour la gestion complète des licences ABCD.

Fonctionnalités :
-----------------
* Gestion des clients
* Génération de clés Ed25519
* Création de licences avec interface graphique
* Génération d'alias lisibles
* Export de licences
* Historique des licences générées
* Gestion des modules autorisés
* Contrôle des quotas utilisateurs

Ce module est destiné à être installé sur une instance Odoo dédiée
pour la gestion des licences en production.
    """,
    'author': "ABCD",
    'website': "https://www.abcd.com",
    'category': 'Tools',
    'version': '1.0.0',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_sequence.xml',
        'views/license_client_views.xml',
        'views/license_client_kanban_views.xml',
        'views/license_key_views.xml',
        'views/license_key_kanban_views.xml',
        'views/license_views.xml',
        'views/license_kanban_views.xml',
        'views/license_graph_views.xml',
        'views/license_pivot_views.xml',
        'wizards/generate_license_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
