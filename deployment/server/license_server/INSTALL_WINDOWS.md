# Installation sur Windows

## Prérequis

### 1. Installer Python

**Option A : Depuis python.org (Recommandé)**
1. Téléchargez Python depuis https://www.python.org/downloads/
2. Lors de l'installation, cochez **"Add Python to PATH"**
3. Vérifiez l'installation : ouvrez PowerShell et tapez `python --version`

**Option B : Depuis Microsoft Store**
1. Ouvrez Microsoft Store
2. Recherchez "Python"
3. Installez Python 3.11 ou supérieur

**Option C : Utiliser le launcher Python**
- Windows installe souvent un launcher `py.exe`
- Testez avec : `py --version`

### 2. Installer les dépendances

Ouvrez PowerShell ou CMD dans le répertoire `deployment/server/license_server/` :

```powershell
# Avec python
python -m pip install -r requirements.txt

# Ou avec py launcher
py -m pip install -r requirements.txt

# Ou avec python3
python3 -m pip install -r requirements.txt
```

## Utilisation

### Méthode 1 : Scripts batch (Recommandé sur Windows)

```batch
# Générer les clés
generate_keys.bat

# Générer une licence
generate_license.bat example_config.json license.txt
```

### Méthode 2 : Commandes Python directes

```powershell
# Avec python
python generate_keys.py --output-dir ./keys
python generate_license.py --config example_config.json --output license.txt

# Ou avec py launcher
py generate_keys.py --output-dir ./keys
py generate_license.py --config example_config.json --output license.txt

# Ou avec python3
python3 generate_keys.py --output-dir ./keys
python3 generate_license.py --config example_config.json --output license.txt
```

## Dépannage

### Erreur "Python was not found"

1. **Vérifier l'installation** :
   ```powershell
   py --version
   python --version
   python3 --version
   ```

2. **Ajouter Python au PATH** :
   - Ouvrez "Variables d'environnement" dans Windows
   - Ajoutez le chemin Python (ex: `C:\Python311\` ou `C:\Users\VotreNom\AppData\Local\Programs\Python\Python311\`)
   - Redémarrez le terminal

3. **Utiliser le launcher Python** :
   - Utilisez `py` au lieu de `python`
   - Les scripts batch utilisent déjà `py`

### Erreur "Module 'cryptography' not found"

```powershell
# Installer cryptography
py -m pip install cryptography

# Ou mettre à jour pip d'abord
py -m pip install --upgrade pip
py -m pip install cryptography
```

### Erreur "Permission denied"

- Exécutez PowerShell ou CMD en tant qu'administrateur
- Ou installez dans un environnement virtuel :
  ```powershell
  py -m venv venv
  venv\Scripts\activate
  pip install -r requirements.txt
  ```

## Vérification

Après installation, testez :

```powershell
py test_license.py
```

Cela devrait générer des clés, créer une licence de test et valider le système.
