# Outil d'inspection d'URL multi-LLM

Application Streamlit expérimentale permettant de tester si un grand modèle de langage (LLM)
peut **accéder au contenu d'une page web** et en produire un résumé fidèle.

Adaptation française et multi-fournisseurs de l'outil original conçu par
[Simone De Palma](https://seodepths.com) (SEODepths), qui ne couvrait qu'OpenAI.

---

## Fournisseurs supportés

| Fournisseur | API gratuite | Mécanisme testé |
|---|---|---|
| **OpenAI** | Non | Index en cache (`external_web_access`) ou récupération live |
| **Mistral** | Oui | Recherche web live (connecteur `web_search`) ou connaissance d'entraînement |
| **Google Gemini** | Oui (modèles Flash) | Grounding Google Search ou connaissance d'entraînement |

> Mistral est une entreprise française et propose une clé API gratuite sans carte bancaire.
> Gemini offre un quota gratuit sur les modèles Flash ; le grounding consomme un quota gratuit
> puis devient payant au-delà.

---

## Nuance importante selon le fournisseur

Le concept d'origine repose sur le paramètre `external_web_access: False`, **spécifique à l'API
Responses d'OpenAI** : il force le modèle à n'utiliser que son index mis en cache, sans aller
chercher la page en direct.

Mistral et Gemini n'ont **pas** d'équivalent « cache uniquement ». L'outil distingue donc
deux états pour ces fournisseurs :

- **Recherche désactivée** — on teste si le modèle connaît la page via sa connaissance
  d'entraînement (aucun accès live).
- **Recherche activée** — le modèle peut récupérer la page en direct sur le web.

Le résultat doit donc être interprété en fonction du fournisseur et du mode choisi.

---

## Installation

```bash
pip install -r requirements.txt
```

`requirements.txt` :

```
streamlit
openai
mistralai
google-genai
```

## Lancement

```bash
streamlit run app.py
```

Vous pouvez fournir votre clé API directement dans la barre latérale, ou via une variable
d'environnement :

- `OPENAI_API_KEY`
- `MISTRAL_API_KEY`
- `GEMINI_API_KEY` (ou `GOOGLE_API_KEY`)

---

## Utilisation

1. **Choisissez un fournisseur** dans la barre latérale (Mistral et Gemini sont gratuits).
2. **Saisissez votre clé API** correspondante.
3. **Sélectionnez un modèle** et réglez les options (cache/live, localisation, recherche web).
4. **Collez l'URL** à tester puis cliquez sur **« Tester l'accès du LLM »**.
5. Analysez la **réponse brute** et l'**interprétation**.

L'outil demande au modèle de préfixer sa réponse par un marqueur structuré
(`[ACCÈS_OUI]` / `[ACCÈS_NON]`), ce qui rend l'interprétation fiable quelle que soit
la langue de la réponse.

---

## Interprétation des résultats

- **✅ Accès confirmé** — le modèle a pu restituer le contenu de la page.
  Chez OpenAI en mode cache, cela indique que la page est présente dans l'index ;
  ailleurs, cela indique un accès live réussi ou une bonne couverture par l'entraînement.
- **⚠️ Accès échoué** — page bloquée (JavaScript / rendu CSR / pop-ups de géolocalisation),
  absente de l'index, ou contenu indisponible. Pistes : revoir le JavaScript bloquant le rendu,
  renforcer les mentions et citations via des efforts de Digital PR ciblés.
- **ℹ️ Incertain** — pas de marqueur exploitable ; lisez la réponse brute pour juger manuellement.

---

## Différences avec la version d'origine

- Interface entièrement en **français**.
- Support **multi-LLM** (OpenAI, Mistral, Google Gemini) avec sélecteur de fournisseur.
- Correction d'un bug : `user_location` était défini mais jamais transmis à l'appel API —
  il est désormais correctement câblé côté OpenAI.
- Remplacement du repérage par chaîne anglaise (fragile) par un **marqueur structuré**
  indépendant de la langue.

---

## Crédits

Outil original par [Simone De Palma](https://seodepths.com) pour SEODepths.
Adaptation française et multi-LLM.

Projet open-source — les contributions sont les bienvenues, en particulier autour des règles
conditionnelles qui alimentent la sortie d'interprétation.
