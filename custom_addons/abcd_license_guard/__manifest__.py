# -*- coding: utf-8 -*-
{
    'name': "ABCD License Guard",
    'summary': "Protection d'installation pour modules ABCD (toujours chargé)",
    'description': """
ABCD License Guard
==================

Module minimal qui intercepte l'installation de modules ABCD
AVANT qu'Odoo n'installe automatiquement abcd_license_core.

Ce module doit être installé en PREMIER et ne dépend de rien.
    """,
    'author': "ABCD",
    'website': "https://www.abcd.com",
    'category': 'Tools',
    'version': '1.0.0',
    'depends': ['base'],  # Dépend uniquement de base
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    # Auto-install si un module ABCD est détecté (mais ce n'est pas fiable)
    # Mieux vaut documenter qu'il doit être installé manuellement en premier
    'auto_install': False,
    'license': 'LGPL-3',
}
