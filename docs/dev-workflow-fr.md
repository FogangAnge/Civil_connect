## Travailler avec VS Code (frontend) + PyCharm (backend) + pgAdmin (PostgreSQL)

### Principe

- **VS Code** : ouvre le dossier `frontend/` (Vite + React).
- **PyCharm** : ouvre le dossier `backend_django/` (Django + DRF).
- **pgAdmin** : se connecte à ton instance PostgreSQL locale (ou Docker) et gère la base `Projet DUT` (ou équivalent).

Tu peux aussi ouvrir le fichier `CivilConnect.code-workspace` dans VS Code pour avoir **les deux dossiers** dans un même workspace (pratique), tout en gardant PyCharm sur `backend_django/`.

### PostgreSQL + pgAdmin

1. Démarre PostgreSQL (service Windows ou Docker).
2. Dans **pgAdmin**, crée un serveur (si besoin) pointant vers `127.0.0.1:5432`.
3. Crée une base nommée **`Projet DUT`** (avec guillemets si tu veux exactement un espace dans le nom) ou adapte `DATABASE_URL`.
4. Vérifie l’utilisateur/mot de passe (ex. `postgres` / ton mot de passe).

### Variables d’environnement (important)

Le backend et le seed doivent utiliser **la même base** que celle que tu vois dans pgAdmin.

Exemple (PowerShell) :

```powershell
$env:DJANGO_USE_SQLITE = "0"
$env:DATABASE_URL = "postgresql://postgres:TON_MDP@127.0.0.1:5432/Projet%20DUT"
$env:DEMO_SKIP_MFA = "1"
```

### Migrations + comptes démo

Dans PyCharm (terminal intégré), depuis `backend_django/` :

```powershell
python manage.py migrate
python create_default_login.py
```

### Lancer le backend (PyCharm)

Run configuration Django :

- **Script** : `manage.py`
- **Parameters** : `runserver 127.0.0.1:8000`
- **Working directory** : `.../backend_django`

### Lancer le frontend (VS Code)

Dans `frontend/` :

```powershell
npm install
npm run dev -- --host 127.0.0.1 --port 5174
```

### URLs utiles

- **UI** : `http://127.0.0.1:5174/`
- **Swagger** : `http://127.0.0.1:8000/api/docs/`

### Hôpital (nouveau flux)

- Compte démo : `hopital@civilconnect.cm` / `Civil123!`
- Page : `http://127.0.0.1:5174/dashboard/hopital`
- API : `POST /api/hospital-declarations/` (JWT cookie) avec `mairie_code` (ex. `CMR001`)
