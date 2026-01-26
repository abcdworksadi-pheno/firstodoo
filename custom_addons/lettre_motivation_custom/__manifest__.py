# -*- coding: utf-8 -*-
{
    'name': "lettre de mission kof",

    'summary': "Génération de lettres de motivation avec injection de variables dynamiques",

    'description': """
Module de Génération de Lettres de Motivation
==============================================

Ce module permet de créer et générer des lettres de motivation personnalisées avec trois niveaux de complexité :

* **Niveau 1** : Variables texte simples ({{nom_candidat}}, {{poste}}, etc.)
* **Niveau 2** : Tableaux dynamiques avec colonnes configurables
* **Niveau 3** : Intégration de données depuis des fichiers Excel

Fonctionnalités :
-----------------
* Création de modèles de lettres réutilisables
* Injection de variables dynamiques
* Génération de tableaux avec colonnes configurables
* Import de données depuis Excel
* Export en PDF, HTML ou DOCX
* Historique des lettres générées
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Human Resources',
    'version': '1.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'mail', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/lettre_variable_views.xml',
        'views/lettre_template_views.xml',
        'views/lettre_instance_views.xml',
        'views/lettre_tableau_views.xml',
        'views/lettre_excel_views.xml',
        'views/wizard_views.xml',
        'views/menu_views.xml',
        'views/templates.xml',
        'views/sale_order_views.xml',  # Charger en dernier pour s'assurer que sale.order est bien chargé
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}

