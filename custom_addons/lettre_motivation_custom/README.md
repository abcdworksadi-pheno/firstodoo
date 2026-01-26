# Module Lettre de Motivation Personnalisée

## Description

Module Odoo pour la génération de lettres de motivation personnalisées avec injection de variables dynamiques. Le module supporte trois niveaux de complexité croissante.

## Fonctionnalités

### Niveau 1 : Variables Texte Simples
- Remplacement de variables simples dans le contenu
- Format : `{{nom_variable}}`
- Exemple : `Bonjour {{nom_candidat}}, votre candidature pour le poste de {{poste}}...`

### Niveau 2 : Tableaux Dynamiques
- Génération de tableaux HTML avec colonnes configurables
- Gestion des lignes et colonnes dynamiques
- Support de différents types de données (texte, nombre, date)

### Niveau 3 : Intégration Excel
- Import de données depuis des fichiers Excel (.xlsx)
- Mapping automatique des colonnes Excel vers les colonnes du tableau
- Génération automatique des lignes de tableau à partir d'Excel

## Installation

1. Copier le module dans le répertoire `custom_addons`
2. Mettre à jour la liste des modules dans Odoo
3. Installer le module "Lettre de Motivation Personnalisée"

### Dépendances Python (optionnelles pour niveau 3)

Pour utiliser la fonctionnalité d'import Excel, installer :
```bash
pip install openpyxl
```

## Utilisation

### 1. Créer un Modèle de Lettre

1. Aller dans **Lettres de Motivation > Modèles**
2. Cliquer sur **Créer**
3. Remplir :
   - **Nom** : Nom du modèle
   - **Niveau** : Choisir le niveau de complexité
   - **Contenu** : Saisir le contenu avec variables `{{variable}}`
   - **Format de Sortie** : PDF, HTML ou DOCX

### 2. Définir les Variables

Les variables sont détectées automatiquement dans le contenu. Vous pouvez aussi les définir manuellement :

1. Dans l'onglet **Variables** du modèle
2. Pour chaque variable :
   - **Nom Technique** : Nom utilisé dans le template (ex: `nom_candidat`)
   - **Libellé** : Libellé affiché à l'utilisateur
   - **Type** : Texte, Nombre, Date, Tableau, Excel
   - **Valeur par Défaut** : Valeur par défaut (optionnel)
   - **Obligatoire** : Cocher si la variable est requise

### 3. Configurer les Tableaux (Niveau 2 et 3)

1. Dans l'onglet **Tableaux** du modèle
2. Créer un nouveau tableau :
   - **Nom** : Nom du tableau
   - **Variable** : Nom de la variable utilisée dans le template
3. Définir les colonnes :
   - **Nom Technique** : Nom de la colonne
   - **Libellé** : Libellé affiché
   - **Type** : Type de données
   - **Largeur** : Largeur de la colonne (optionnel)
4. Ajouter les lignes de données (format JSON)

### 4. Configurer les Sources Excel (Niveau 3)

1. Aller dans **Lettres de Motivation > Sources Excel**
2. Créer une nouvelle source :
   - **Nom** : Nom de la source
   - **Fichier Excel** : Charger le fichier .xlsx
   - **Feuille** : Nom de la feuille Excel
   - **Tableau Associé** : Lier au tableau correspondant
   - **Mapping** : Définir le mapping JSON (ex: `{"A": "competence", "B": "niveau"}`)
3. Cliquer sur **Importer Excel** pour remplir automatiquement le tableau

### 5. Générer une Lettre

1. Ouvrir un modèle
2. Cliquer sur **Générer une Lettre**
3. Remplir les valeurs des variables
4. Cliquer sur **Générer**
5. La lettre est créée et peut être prévisualisée ou téléchargée

## Structure des Modèles

- **lettre.motivation.template** : Modèles de lettres
- **lettre.motivation.variable** : Variables disponibles
- **lettre.motivation.instance** : Instances de lettres générées
- **lettre.motivation.tableau** : Tableaux dynamiques
- **lettre.motivation.tableau.colonne** : Colonnes des tableaux
- **lettre.motivation.tableau.ligne** : Lignes des tableaux
- **lettre.motivation.excel.source** : Sources Excel

## Exemples

### Exemple Niveau 1

**Contenu du modèle :**
```
Bonjour {{nom_candidat}},

Je vous écris pour postuler au poste de {{poste}} au sein de votre entreprise.

Cordialement,
{{signature}}
```

**Variables :**
- `nom_candidat` : Jean Dupont
- `poste` : Développeur Python
- `signature` : Jean Dupont

### Exemple Niveau 2

**Contenu avec tableau :**
```
Mes compétences principales :

{{tableau_competences}}
```

**Tableau "tableau_competences" :**
- Colonnes : Compétence, Niveau, Années d'expérience
- Lignes : Données JSON

### Exemple Niveau 3

1. Créer un fichier Excel avec les compétences
2. Configurer une source Excel
3. Importer les données dans le tableau
4. Générer la lettre avec les données Excel

## Notes Techniques

- Les variables sont remplacées par simple substitution de chaînes
- Les tableaux sont générés en HTML
- L'import Excel nécessite la bibliothèque `openpyxl`
- Les lettres générées sont stockées dans `lettre.motivation.instance`

## Support

Pour toute question ou problème, consulter le fichier `ANALYSE_ET_SOLUTION.md` pour plus de détails sur l'architecture.

