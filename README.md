## CivilConnect

Projet full-stack **React (Vite + TS)** + **Django (DRF)** avec Docker.

### Développement (VS Code + PyCharm + pgAdmin)

Voir `docs/dev-workflow-fr.md`.

Tu peux aussi ouvrir `CivilConnect.code-workspace` dans VS Code pour charger `frontend/` + `backend_django/` ensemble.

### Démarrage (Docker)

- **Pré-requis**: Docker Desktop
- **Configuration**:
  - Copier `.env.example` en `.env` et ajuster si besoin

Puis lancer:

```bash
docker compose up --build
```

Accès:

- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000/api/`
- **Swagger**: `http://localhost:8000/api/docs/`

### Démarrage (local)

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Backend (Python installé):

```bash
cd backend_django
py -m pip install -r requirements.txt
py manage.py migrate
py create_default_login.py
py manage.py runserver 127.0.0.1:8000
```

### Déclarations hôpital → mairie (POC)

- Compte démo : `hopital@civilconnect.cm` / `Civil123!`
- UI : `/dashboard/hopital`
- API : `GET/POST /api/hospital-declarations/`
- Mairies : `GET /api/mairies/`

