# -*- coding: utf-8 -*-

def migrate(cr, version):
    """Ajoute les colonnes manquantes pour lettre_motivation_instance_variable"""
    # Vérifier et ajouter les colonnes si elles n'existent pas
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='lettre_motivation_instance_variable'
    """)
    existing_columns = [row[0] for row in cr.fetchall()]
    
    # Colonnes à ajouter
    columns_to_add = {
        'name': 'VARCHAR',
        'label': 'VARCHAR',
        'type': 'VARCHAR',
        'valeur_par_defaut': 'TEXT',
        'required': 'BOOLEAN',
    }
    
    for column_name, column_type in columns_to_add.items():
        if column_name not in existing_columns:
            try:
                cr.execute(f"""
                    ALTER TABLE lettre_motivation_instance_variable 
                    ADD COLUMN {column_name} {column_type}
                """)
            except Exception as e:
                # Ignorer si la colonne existe déjà
                pass


