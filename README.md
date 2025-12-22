
# **🛡️ DCP Eval – Plateforme d’évaluation et de détection des Données à Caractère Personnel (DCP)**

## **🎯 Objectif du projet**

Ce repository propose une **plateforme modulaire et extensible** permettant de :

* **détecter automatiquement des ****Données à Caractère Personnel (DCP)**
* comparer et évaluer **plusieurs solutions open source** de détection (regex, NER, IA)
* appliquer des **règles métier RGPD** (priorités, fusion, nettoyage)
* anonymiser / pseudonymiser les données détectées
* exposer l’ensemble via une **API FastAPI**

Le projet est conçu comme :

* **un ****outil d’évaluation / benchmark**
* un **socle technique réutilisable** pour des cas industriels (audit RGPD, data catalog, DLP, GenAI safety…)

---

## **🧠 Principes clés de conception**

### **1️⃣ Multi-détecteurs (approche “ensemble”)**

Aucun moteur n’est parfait :

* les **regex** sont très précises mais limitées
* les **NER IA** ont un bon rappel mais génèrent des faux positifs
* certains outils sont spécialisés par langue ou type de données

**👉 Le projet exécute ** **plusieurs détecteurs en parallèle** **, puis :**

* fusionne les résultats
* **applique des ****priorités métier**
* nettoie les faux positifs connus

---

### **2️⃣ Pilotage dynamique par API**

Depuis le **body de l’API**, on peut :

* choisir quels détecteurs exécuter
* régler les seuils
* activer/désactiver la fusion
* récupérer les résultats **par moteur** ou **fusionnés**

➡️ Idéal pour comparer des solutions open source.

---

### **3️⃣ Séparation claire des responsabilités**

Le code est structuré en **couches lisibles** :

* détecteurs (techniques)
* services (logique métier)
* pipelines (types de données)
* API (exposition)

---

## **🗂️ Structure globale du repository**

```
DCP_Eval/
├── app/
│   ├── api/                # Routes FastAPI
│   ├── detectors/          # Implémentations des détecteurs DCP
│   ├── models/             # Schémas Pydantic (DcpSpan, requests, responses)
│   ├── services/           # Logique métier (orchestration, scoring, pipelines)
│   ├── main.py             # Entrypoint FastAPI
│
├── data/
│   └── tmp/                # Stockage local des résultats (POC)
│
├── tests/                  # (optionnel) tests unitaires / intégration
│
├── pyproject.toml          # Dépendances Python
├── Dockerfile              # Image Docker (optionnelle)
├── README.md               # Documentation
```

---

## **🔍 Détail des dossiers et fichiers clés**

---

## **📦** ****

## **app/detectors/**

## ** – Détecteurs DCP**

Chaque détecteur implémente une **stratégie technique spécifique**.

| **Fichier**    | **Rôle**                                          |
| -------------------- | -------------------------------------------------------- |
| base.py              | Interface abstraite commune                              |
| regex_detector.py    | Détection haute précision (email, IBAN, téléphone…) |
| presidio_detector.py | Microsoft Presidio (patterns + NER)                      |
| spacy_detector.py    | spaCy NER (modèle français)                            |
| hf_ner_detector.py   | HuggingFace Transformers (CamemBERT NER)                 |
| ensemble.py          | Fusion basique des spans                                 |

👉 Chaque détecteur retourne une liste de **DcpSpan**.

---

## **🧩** ****

## **app/models/**

## ** – Modèles de données**

### **schemas.py**

Contient tous les modèles **Pydantic** :

* **DcpSpan** : une entité DCP détectée
* DetectTextRequest** / **DetectTextResponse
* types normalisés : **PERSON**, **EMAIL**, **IBAN**, **HEALTH**, etc.

➡️ Ces modèles servent :

* aux détecteurs
* aux services
* à l’API FastAPI

---

## **⚙️** ****

## **app/services/**

## ** – Cœur métier du projet**

**C’est ** **la couche la plus importante** **.**

---

### **🔁** ****

### **orchestrator.py**

**Chef d’orchestre** de la détection.

Responsabilités :

* instancier les détecteurs (lazy loading)
* exécuter plusieurs moteurs en parallèle
* gérer les erreurs en mode *best-effort*
* produire :
  * résultats fusionnés
  * résultats par détecteur
  * résumé global
  * benchmark de performance

---

### **🧠** ****

### **scoring.py**

**Applique les ****règles métier RGPD** :

* priorités par type de donnée
  (ex : IBAN > PERSON > OTHER)
* priorités par moteur
  (regex > HF > spaCy > Presidio)
* fusion des spans qui se chevauchent
* fusion des PERSON fragmentées
* suppression de faux positifs connus

➡️ C’est ici que l’on passe de “détection IA” à **détection exploitable métier**.

---

### **🔐** ****

### **anonymizer.py**

Fonctions d’anonymisation :

* mask** → **********
* redact** → **`<EMAIL>`
* hash** → **[EMAIL:ab34f9e12c](EMAIL:ab34f9e12c)

Utilisable après la détection pour :

* DLP
* GenAI safety
* partage de données anonymisées

---

### **🧪 Pipelines par type de données**

| **Fichier**      | **Description**                      |
| ---------------------- | ------------------------------------------ |
| pipeline_text.py       | Texte brut (API principale)                |
| pipeline_docs.py       | Documents (PDF, DOCX, XLSX)                |
| pipeline_images.py     | Images (OCR → texte)                      |
| pipeline_structured.py | Données structurées (JSON, dict, listes) |

Chaque pipeline :

1. prépare la donnée
2. appelle l’orchestrateur
3. retourne un résultat homogène

---

### **💾** ****

### **storage.py**

Stockage local simple (POC) :

* sauvegarde JSON des résultats
* récupération par ID

➡️ Remplaçable facilement par :

* S3
* base SQL
* data catalog

---

## **🌐** ****

## **app/api/**

## ** – Exposition FastAPI**

Expose les fonctionnalités via une API REST :

* **/detect/text** → détection DCP texte
* (optionnel) **/bench/text** → benchmark des moteurs
* (optionnel) **/detect/file** → documents
* **(optionnel) **/anonymize/text

Swagger auto-disponible :

```
http://localhost:8000/docs
```

---

## **🚀 Lancement du projet**

### **1️⃣ Installation des dépendances**

```
pip install -e .
```

### **2️⃣ Lancer l’API**

```
uvicorn app.main:app --reload --port 8000
```

### **3️⃣ Exemple d’appel API**

```
curl -X POST "http://localhost:8000/detect/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text":"Jean Dupont - jean.dupont@email.com - IBAN FR76...",
    "language":"fr",
    "detectors":["regex","presidio","spacy","hf"],
    "min_score":0.4
  }'
```

---

## **🧭 Cas d’usage cibles**

* Audit RGPD / cartographie DCP
* Benchmark de solutions open source
* Pré-traitement avant indexation GenAI / RAG
* Data Catalog enrichi
* DLP / sécurité de la donnée
* Anonymisation avant partage ou entraînement IA

---

## **📌 Limites connues (assumées)**

* Les modèles NER peuvent produire des faux positifs
* La qualité dépend fortement du contexte métier
* Les détecteurs doivent être **ajustés / réentraînés** pour un usage industriel

**➡️ Le repo est conçu pour ** **tester, comparer et améliorer** **.**

## **🚀 Run (local)**

```
# (optionnel) venv
python -m venv .venv
source .venv/bin/activate

# installe les deps
pip install -r requirements.txt

# lance l'API (adapte le module si besoin)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**➡️ API: **http://localhost:8000

**➡️ Swagger UI: **http://localhost:8000/docs

**➡️ OpenAPI JSON: **http://localhost:8000/openapi.json

## **🔎 Lister tous les endpoints automatiquement (OpenAPI)**

### **Avec** ****

### **jq**

### ** (recommandé)**

```
curl -s http://localhost:8000/openapi.json \
| jq -r '.paths | to_entries[] as $p | $p.value | keys[] as $m | "\($m|ascii_upcase) \($p.key)"'
```

### **Sans** ****

### **jq**

### ** (Python)**

```
python - <<'PY'
import json, urllib.request
spec = json.load(urllib.request.urlopen("http://localhost:8000/openapi.json"))
for path, methods in spec.get("paths", {}).items():
    for m in methods.keys():
        print(m.upper(), path)
PY
```

## **📡 Endpoints**

### **POST /files/detect/image**

**But**: détecter des entités/PII sur une image (OCR + NER).

**Content-Type**: multipart/form-data

 **Body** **:**

* **file**  *(required)* : image (**.png**, **.jpg**, …)

**cURL**

```
curl -X POST "http://localhost:8000/files/detect/image" \
  -H "accept: application/json" \
  -F "file=@./path/to/image.png"
```

**HTTPie**

```
http -f POST :8000/files/detect/image file@./path/to/image.png
```

### **POST /files/detect/document**

**But**: détecter des entités/PII sur un document (ex: PDF).

**Content-Type**: multipart/form-data

 **Body** **:**

* **file**  *(required)* : document (**.pdf**, …)

**cURL**

```
curl -X POST "http://localhost:8000/files/detect/document" \
  -H "accept: application/json" \
  -F "file=@./path/to/document.pdf"
```

**HTTPie**

```
http -f POST :8000/files/detect/document file@./path/to/document.pdf
```

## **🧾 Format de réponse (détection)**

Exemple de structure (comme ce que tu as montré) :

```
{
  "file": "nom_du_fichier.pdf",
  "spans": [
    {
      "start": 25,
      "end": 29,
      "label": "ORG",
      "score": 0.95,
      "source": "hf",
      "text": null,
      "metadata": { "hf_entity": "ORG" }
    }
  ],
  "by_detector": {
    "regex": [],
    "presidio": [],
    "spacy": [],
    "hf": []
  },
  "summary": { "ORG": 31, "PERSON": 36, "LOCATION": 25, "OTHER": 79 },
  "errors": { "presidio": "'fr'" }
}
```

**Interprétation rapide**

* **spans[]**: segments détectés **dans le texte extrait**, avec offsets **[start, end)** (indices caractères).
* **label**: type normalisé (**PERSON**, **ORG**, **LOCATION**, **OTHER**, …).
* **score**: confiance du modèle (souvent élevé côté HF, souvent **0.55** côté spaCy dans ton output actuel).
* source**: moteur (**hf**, **spacy**, **regex**, **presidio**…).**
* **text: null**: tu ne renvoies pas le substring ; pour le reconstruire il faut le texte complet extrait (si tu veux, tu peux l’ajouter dans la réponse, ex: **raw_text**).
* **by_detector**: même info regroupée par moteur.
* **errors**: erreurs non bloquantes (ex: **presidio: "'fr'"** → langue/registry non dispo ou mauvais code langue).


## **🧠 Philosophie**

> **“La détection de DCP n’est pas un problème purement IA,**

> **mais un problème de gouvernance, de contexte et de règles métier.”**
