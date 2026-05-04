# Trésorerie Pro — Module Odoo 18

## Quoi de nouveau vs l'ancien module (`cash_flow_forecast_odoo18`) ?

| Problème ancien module | Solution Trésorerie Pro |
|---|---|
| Les soldes d'ouverture (Banque / Caisse) étaient mélangés avec les flux dans la même liste | **Séparation complète** : soldes → `solde.compte`, flux → `flux.tresorerie` |
| Les soldes ne prenaient pas le vrai solde bancaire/caisse | Bouton **📥 Importer solde réel** qui lit le solde depuis les écritures comptables |
| Pas de tableau de bord visuel | **Kanban cards** par compte avec : montant prévu / solde réel / écart |
| Un seul modèle pour tout | 3 modèles distincts : `compte.tresorerie`, `solde.compte`, `flux.tresorerie` |

---

## Architecture

```
tresorerie_pro/
├── models/
│   ├── compte_tresorerie.py   → Comptes (Banque CPA, Caisse…) liés aux journaux Odoo
│   ├── solde_compte.py        → Soldes d'ouverture/fermeture (SÉPARÉS des flux)
│   └── flux_tresorerie.py     → Mouvements prévisionnels (entrées / sorties)
├── wizards/
│   └── wizard_recurrence.py   → Création de flux récurrents (jour/semaine/mois)
├── views/
│   ├── compte_tresorerie_views.xml
│   ├── flux_tresorerie_views.xml
│   ├── dashboard_views.xml    → Kanban des soldes + vue liste des soldes
│   └── menu_item.xml
├── security/
├── data/
└── static/src/css/
    └── tresorerie_dashboard.css
```

---

## Installation

1. **Désinstaller** l'ancien module `cash_flow_forecast_odoo18` si installé
2. Copier `tresorerie_pro/` dans votre dossier addons
3. Redémarrer le serveur Odoo
4. Mettre à jour la liste des modules
5. Installer **Trésorerie Pro**

> ⚠️ Ne pas faire "upgrade" — installer from scratch car le nom du module est différent.

---

## Configuration initiale

### 1. Créer les comptes de trésorerie
Menu : **Trésorerie Pro → ⚙️ Configuration → Comptes de trésorerie**

- Créer un compte "Banque CPA", lier au journal `BNQ` (type : banque)
- Créer un compte "Caisse", lier au journal `CSH` (type : caisse)

### 2. Créer les soldes d'ouverture
Menu : **Trésorerie Pro → 🏦 Soldes d'ouverture / fermeture**

- Cliquer "Nouveau"
- Choisir le compte, type = "Solde d'ouverture", date = début de période
- Cliquer **📥 Importer solde réel** pour récupérer automatiquement le solde comptable
- Ou saisir manuellement le montant prévu
- Confirmer → Verrouiller

### 3. Saisir les flux prévisionnels
Menu : **Trésorerie Pro → 💸 Flux de trésorerie**

- Les flux sont des mouvements (entrées/sorties) normaux
- Le **solde cumulé** tient compte du solde d'ouverture confirmé/verrouillé du compte

---

## Fonctionnalités

- **Tableau de bord Kanban** : vue visuelle des soldes par compte avec écart prévu/réel
- **Solde réel automatique** : récupéré depuis les écritures `account.move.line` postées
- **Solde cumulé par compte** : calculé via fenêtre SQL (O(n), pas de N+1)
- **Workflow** : Brouillon → Confirmé → Verrouillé (soldes) / Prévu → En cours → Fait (flux)
- **Récurrence** : wizard pour créer des flux jour / semaine / mois
- **Archivage automatique** : cron qui archive les flux dont la date effective + 30j = aujourd'hui
