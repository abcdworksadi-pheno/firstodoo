{
    'name': 'Gestion de la Planification des Tâches',
    'version': '1.0',
    'category': 'Project',
    'summary': 'Module pour la gestion et la planification des tâches',
    'description': """
        Ce module fournit un système complet pour gérer et planifier les tâches.
        Fonctionnalités:
        - Créer et gérer les tâches
        - Assigner les tâches aux employés
        - Planifier les tâches avec des dates limites
        - Suivre l'état d'avancement des tâches
        - Générer des rapports sur les tâches
    """,
    'author': 'secure code ',
    'website': 'https://ngamo.vercel.app',
    'depends': ['base', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/task_planning_form_views.xml',
        'views/task_planning_menu.xml',
        'data/task_priority_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
