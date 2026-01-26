# -*- coding: utf-8 -*-
{
    'name': "ABCD License Core",
    'summary': "Système de gestion de licences pour modules ABCD",
    'description': """
Système de Licence ABCD
=======================

Module central de vérification de licences pour les modules personnalisés ABCD.

Fonctionnalités :
-----------------
* Vérification de licence offline par défaut
* Vérification online optionnelle
* Cache mémoire et base de données
* Période de grâce configurable
* Vérification de signature Ed25519
* Validation UUID base de données
* Contrôle quota utilisateurs
* Messages d'erreur professionnels

Sécurité :
----------
* Aucune clé privée stockée côté client
* Signature asymétrique obligatoire
* Validation stricte JSON
* Protection contre modification payload

Compatibilité :
---------------
* Odoo 18+ (compatible 19+)
* On-premise et Odoo.sh
    """,
    'author': "ABCD",
    'website': "https://www.abcd.com",
    'category': 'ABCD',
    'version': '1.0.0',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        'views/license_config_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
