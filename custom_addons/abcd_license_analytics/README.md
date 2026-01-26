# ABCD License Analytics

Module d'analyses avancées et de surveillance pour le système de licences ABCD.

## Fonctionnalités

### Tableau de Bord
- **Statistiques Globales** : Vue d'ensemble des licences (total, actives, expirées, expirent bientôt)
- **Graphiques Interactifs** : Visualisation des données par édition, tendances temporelles
- **Top Clients** : Liste des clients avec le plus de licences
- **Modules Populaires** : Modules les plus utilisés dans les licences
- **Alertes d'Expiration** : Liste des licences expirant dans les 30 prochains jours

### Analyses Disponibles
- Répartition des licences par édition (Standard, Pro, Enterprise)
- Tendances de génération de licences sur 12 mois
- Analyse par client
- Utilisation des modules
- Statistiques sur les clés cryptographiques

## Installation

1. Copier le module dans `custom_addons/`
2. Mettre à jour la liste des modules dans Odoo
3. Installer le module `abcd_license_analytics`
4. Le module dépend de `abcd_license_server`

## Utilisation

1. Accéder au menu **Licences ABCD > Analyses**
2. Le tableau de bord s'affiche avec toutes les statistiques
3. Les données sont mises à jour en temps réel

## Structure

```
abcd_license_analytics/
├── models/
│   └── license_analytics.py    # Modèle d'analyses
├── views/
│   ├── dashboard_views.xml    # Vue du tableau de bord
│   └── analytics_menu_views.xml # Menu
├── static/
│   └── src/
│       ├── js/
│       │   └── dashboard_widget.js # Widget JavaScript
│       └── css/
│           └── dashboard.css      # Styles
└── security/
    └── ir.model.access.csv        # Droits d'accès
```

## Développement

Les méthodes d'analyse sont dans `license_analytics.py` :
- `get_license_statistics()` : Statistiques globales
- `get_license_by_edition()` : Répartition par édition
- `get_license_by_client()` : Top clients
- `get_expiring_licenses()` : Licences expirant bientôt
- `get_license_trends()` : Tendances temporelles
- `get_module_usage()` : Utilisation des modules
- `get_key_statistics()` : Statistiques sur les clés

## Personnalisation

Pour ajouter de nouvelles analyses :
1. Ajouter une méthode dans `license_analytics.py`
2. Appeler la méthode depuis le widget JavaScript
3. Mettre à jour la vue du dashboard si nécessaire
