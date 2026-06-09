import os
import streamlit as st

# ---------------------------------------------------------------------------
# Configuration de la page
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Outil d'inspection d'URL multi-LLM",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Fournisseurs supportés
#   - OpenAI : test de l'index en cache via `external_web_access`
#   - Mistral (FR, API gratuite) : recherche web live vs connaissance d'entraînement
#   - Google Gemini (API gratuite sur les modèles Flash) : grounding Google Search
# ---------------------------------------------------------------------------
PROVIDERS = {
    "OpenAI": {
        "key_env": ["OPENAI_API_KEY"],
        "key_label": "Clé API OpenAI",
        "models": ["gpt-5", "gpt-4.1", "gpt-4o", "gpt-4o-mini"],
        "free": False,
        "note": "API payante. Seul fournisseur exposant le paramètre `external_web_access` "
                "(test de l'index en cache, comme dans l'outil d'origine).",
    },
    "Mistral (gratuit)": {
        "key_env": ["MISTRAL_API_KEY"],
        "key_label": "Clé API Mistral",
        "models": ["mistral-medium-latest", "mistral-small-latest", "mistral-large-latest"],
        "free": True,
        "note": "Entreprise française. Le plan gratuit inclut la recherche web (connecteur `web_search`).",
    },
    "Google Gemini (gratuit)": {
        "key_env": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "key_label": "Clé API Google Gemini",
        "models": ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-3-flash-preview"],
        "free": True,
        "note": "Plan gratuit disponible sur les modèles Flash. Le grounding Google Search "
                "dispose d'un quota gratuit.",
    },
}

# ---------------------------------------------------------------------------
# Localisations prédéfinies (paramètre `user_location`, propre à OpenAI)
# country = code ISO 3166-1 alpha-2
# ---------------------------------------------------------------------------
LOCATIONS = {
    "Aucune (par défaut)": None,
    "France — Paris": {"country": "FR", "city": "Paris", "region": "Île-de-France"},
    "Royaume-Uni — Londres": {"country": "GB", "city": "London", "region": "London"},
    "États-Unis — New York": {"country": "US", "city": "New York", "region": "New York"},
    "États-Unis — San Francisco": {"country": "US", "city": "San Francisco", "region": "California"},
    "Allemagne — Berlin": {"country": "DE", "city": "Berlin", "region": "Berlin"},
    "Espagne — Madrid": {"country": "ES", "city": "Madrid", "region": "Madrid"},
    "Italie — Rome": {"country": "IT", "city": "Rome", "region": "Lazio"},
    "Belgique — Bruxelles": {"country": "BE", "city": "Brussels", "region": "Brussels"},
    "Canada — Montréal": {"country": "CA", "city": "Montreal", "region": "Quebec"},
    "Personnalisée…": "custom",
}

# ---------------------------------------------------------------------------
# Barre latérale : choix du fournisseur et configuration
# ---------------------------------------------------------------------------
st.sidebar.header("Configuration")

provider_name = st.sidebar.selectbox(
    "Fournisseur de modèle (LLM)",
    list(PROVIDERS.keys()),
    help="Choisissez le LLM à interroger. Les options « (gratuit) » disposent d'une API gratuite.",
)
provider = PROVIDERS[provider_name]

# Récupération d'une éventuelle clé dans les variables d'environnement
default_key = ""
for env_name in provider["key_env"]:
    if os.environ.get(env_name):
        default_key = os.environ[env_name]
        break

api_key = st.sidebar.text_input(
    provider["key_label"],
    type="password",
    help="Saisissez votre clé API pour le fournisseur sélectionné.",
    value=default_key,
)

model = st.sidebar.selectbox("Modèle", provider["models"])

st.sidebar.caption(f"ℹ️ {provider['note']}")
st.sidebar.markdown("---")

# Options spécifiques selon le fournisseur
if provider_name == "OpenAI":
    # external_web_access=False -> n'utilise que l'index en cache d'OpenAI
    cache_only = st.sidebar.toggle(
        "Index en cache uniquement (sans fetch live)",
        value=True,
        help="Active `external_web_access: False`. Le modèle ne peut s'appuyer que sur "
             "son index mis en cache, sans récupérer la page en direct.",
    )
    location_choice = st.sidebar.selectbox(
        "Localisation IP déclarée",
        list(LOCATIONS.keys()),
        index=1,  # « France - Paris » par défaut (comportement d'origine)
        help="Localisation déclarée pour le modèle (paramètre `user_location` d'OpenAI). "
             "Peut rendre les sorties plus concises et moins sujettes aux hallucinations.",
    )
    preset = LOCATIONS[location_choice]
    if preset == "custom":
        # Saisie libre d'une localisation
        c1, c2 = st.sidebar.columns(2)
        custom_country = c1.text_input("Pays (ISO 2)", value="FR", help="Ex. FR, US, GB, DE…").strip().upper()
        custom_city = c2.text_input("Ville", value="Paris").strip()
        custom_region = st.sidebar.text_input("Région", value="Île-de-France").strip()
        user_location = {
            "country": custom_country,
            "city": custom_city,
            "region": custom_region,
        }
    else:
        user_location = preset  # dict ou None
    live_mode_label = "live" if not cache_only else "cache"
else:
    # Mistral / Gemini : recherche web/grounding ON = live, OFF = connaissance d'entraînement
    web_search_on = st.sidebar.toggle(
        "Activer la recherche web / grounding (accès live)",
        value=False,
        help="Désactivé : on teste si le modèle connaît la page via son entraînement (sans accès live). "
             "Activé : le modèle peut chercher la page en direct sur le web.",
    )

# ---------------------------------------------------------------------------
# Contenu principal
# ---------------------------------------------------------------------------
st.title("Outil d'inspection d'URL multi-LLM")
st.markdown(
    """
Cet outil teste si un LLM peut **accéder au contenu d'une page** et en faire un résumé fidèle.

Selon le fournisseur, le test ne signifie pas exactement la même chose :

- **OpenAI** — avec l'option « index en cache uniquement », on vérifie si la page est présente
  dans l'index mis en cache d'OpenAI (sans récupération live de la page).
- **Mistral / Gemini** — ces API n'ont pas d'équivalent « cache seulement ». On distingue donc
  deux états : *recherche web désactivée* (le modèle s'appuie sur sa connaissance d'entraînement)
  et *recherche web activée* (le modèle récupère la page en direct).

**Pour en savoir plus** – [Documentation OpenAI Web Search](https://platform.openai.com/docs/guides/tools-web-search#live-internet-access)
"""
)
st.markdown("---")

url = st.text_input(
    "Saisissez l'URL à tester :",
    placeholder="https://exemple.com",
    help="Collez l'URL que vous souhaitez vérifier.",
)

# ---------------------------------------------------------------------------
# Construction du prompt (marqueur structuré, indépendant de la langue de réponse)
# ---------------------------------------------------------------------------
def build_prompt(target_url: str) -> str:
    return (
        f"Peux-tu accéder au contenu de cette page : {target_url} ?\n\n"
        "Commence IMPÉRATIVEMENT ta réponse par l'un de ces deux marqueurs :\n"
        "- \"[ACCÈS_OUI]\" si tu as réellement pu accéder au contenu de la page et peux en faire "
        "un résumé fidèle ;\n"
        "- \"[ACCÈS_NON]\" si tu n'as pas pu y accéder (page bloquée, introuvable, "
        "ou contenu indisponible).\n\n"
        "Ensuite, rédige un court résumé de la page (si accès) ou explique pourquoi l'accès a échoué."
    )


# ---------------------------------------------------------------------------
# Fonctions d'appel par fournisseur
# ---------------------------------------------------------------------------
def query_openai(key, model_name, target_url, cache_only_flag, location):
    import openai

    client = openai.Client(api_key=key)

    web_search_tool = {
        "type": "web_search",
        "external_web_access": not cache_only_flag,  # False = index en cache uniquement
    }
    if location:
        # Câblage correct de la localisation (absent du code d'origine)
        web_search_tool["user_location"] = {
            "type": "approximate",
            "country": location.get("country", ""),
            "city": location.get("city", ""),
            "region": location.get("region", ""),
        }

    response = client.responses.create(
        model=model_name,
        tools=[web_search_tool],
        tool_choice="auto",
        input=build_prompt(target_url),
    )
    return response.output_text


def query_mistral(key, model_name, target_url, web_on):
    from mistralai import Mistral

    client = Mistral(api_key=key)
    tools = [{"type": "web_search"}] if web_on else None

    response = client.beta.conversations.start(
        model=model_name,
        inputs=build_prompt(target_url),
        tools=tools,
    )

    # Extraction robuste du texte depuis les `outputs`
    parts = []
    for output in getattr(response, "outputs", []) or []:
        if getattr(output, "type", None) == "message.output":
            content = output.content
            if isinstance(content, str):
                parts.append(content)
            elif isinstance(content, list):
                for chunk in content:
                    text = getattr(chunk, "text", None)
                    if text is None and isinstance(chunk, dict):
                        text = chunk.get("text")
                    if text:
                        parts.append(text)
    return "\n".join(parts).strip()


def query_gemini(key, model_name, target_url, grounding_on):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key)

    config = None
    if grounding_on:
        config = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )

    response = client.models.generate_content(
        model=model_name,
        contents=build_prompt(target_url),
        config=config,
    )
    return response.text


# ---------------------------------------------------------------------------
# Interprétation du résultat (basée sur le marqueur structuré)
# ---------------------------------------------------------------------------
def interpret(output_text: str) -> str:
    if not output_text:
        return "incertain"
    head = output_text.strip().upper()[:40]
    # On tolère les variantes avec/sans accent
    if "[ACCÈS_OUI]" in head or "[ACCES_OUI]" in head:
        return "oui"
    if "[ACCÈS_NON]" in head or "[ACCES_NON]" in head:
        return "non"
    return "incertain"


# ---------------------------------------------------------------------------
# Bouton d'exécution
# ---------------------------------------------------------------------------
run = st.button(
    "Tester l'accès du LLM",
    type="primary",
    disabled=not api_key or not url,
)

if run:
    if not api_key:
        st.error("⚠️ Veuillez saisir votre clé API dans la barre latérale.")
    elif not url:
        st.error("⚠️ Veuillez saisir une URL à tester.")
    else:
        try:
            with st.status("Vérification de l'URL...", expanded=True) as status_box:
                status_box.update(label="Appel à l'API en cours...", state="running")

                if provider_name == "OpenAI":
                    output_text = query_openai(api_key, model, url, cache_only, user_location)
                elif provider_name == "Mistral (gratuit)":
                    output_text = query_mistral(api_key, model, url, web_search_on)
                else:  # Google Gemini
                    output_text = query_gemini(api_key, model, url, web_search_on)

                status_box.update(label="Terminé", state="complete")

            # Réponse brute
            st.subheader("Réponse du modèle :")
            st.info(output_text or "(réponse vide)")

            # Interprétation
            st.subheader("Interprétation :")
            verdict = interpret(output_text)

            if verdict == "oui":
                if provider_name == "OpenAI" and cache_only:
                    st.success(
                        "✅ **La page semble présente dans l'index en cache d'OpenAI.**\n\n"
                        "Le modèle a pu en restituer le contenu sans récupération live. "
                        "Peu ou pas d'optimisation nécessaire de ce côté."
                    )
                else:
                    st.success(
                        "✅ **Le modèle a pu accéder au contenu de la page et en faire un résumé.**\n\n"
                        "Selon le mode choisi, cela signifie soit un accès web live réussi, "
                        "soit une bonne couverture par la connaissance d'entraînement du modèle."
                    )
            elif verdict == "non":
                st.warning(
                    "⚠️ **Le modèle n'a pas pu accéder au contenu de la page.**\n\n"
                    "Causes possibles : blocage par du JavaScript (rendu CSR, pop-ups de géolocalisation), "
                    "page absente de l'index, ou contenu indisponible. "
                    "Envisagez de revoir le JavaScript bloquant le rendu et de renforcer les mentions "
                    "et citations via des efforts de Digital PR ciblés."
                )
            else:
                st.info(
                    "ℹ️ **Résultat incertain** — le modèle n'a pas renvoyé de marqueur exploitable. "
                    "Lisez la réponse brute ci-dessus pour juger manuellement."
                )

        except Exception as e:
            st.error(f"❌ Une erreur est survenue : {str(e)}")
            st.info(
                "Vérifiez votre clé API et le modèle sélectionné. Assurez-vous que le SDK du "
                "fournisseur est bien installé (voir requirements.txt) et que vous avez accès "
                "au modèle choisi."
            )

# ---------------------------------------------------------------------------
# Mode d'emploi
# ---------------------------------------------------------------------------
with st.expander("ℹ️ Comment utiliser cet outil"):
    st.markdown(
        """
1. **Choisissez un fournisseur** dans la barre latérale (Mistral et Gemini disposent d'une API gratuite).
2. **Saisissez votre clé API** correspondante.
3. **Sélectionnez un modèle** et réglez les options (cache/live, localisation, recherche web).
4. **Collez l'URL** à tester puis cliquez sur **« Tester l'accès du LLM »**.
5. Analysez la **réponse brute** et l'**interprétation**.

**Rappel important :** le test « index en cache uniquement » n'existe que chez OpenAI
(paramètre `external_web_access`). Pour Mistral et Gemini, l'outil distingue
« connaissance d'entraînement » (recherche désactivée) et « accès live » (recherche activée).
"""
    )

# ---------------------------------------------------------------------------
# Pied de page
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "Outil original par Simone De Palma pour [SEODepths](https://seodepths.com) — "
    "adaptation française et multi-LLM par [JC ESPINOSA](http://jc-espinosa.com/)."
)
