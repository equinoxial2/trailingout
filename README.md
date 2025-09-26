# 3Commas Instruction Translator

Ce projet propose un outil en ligne de commande qui transforme des instructions
rédigées en langage naturel (par exemple générées par ChatGPT) en requêtes HTTP
compatibles avec l'API de 3Commas. Il gère des ordres simples d'achat ou de
vente, qu'ils soient au marché ou à cours limité.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copiez le fichier `.env.example` vers `.env` et renseignez vos identifiants
API 3Commas ainsi que l'identifiant du compte à utiliser.

## Utilisation

```bash
python -m translator.main "Achète 0.25 BTCUSDT à 30000 en limite" --dry-run
```

Avec `--dry-run` l'application affiche uniquement la requête qui serait envoyée
à 3Commas. Supprimez cette option pour envoyer la requête réelle.

## Fonctionnement

1. `translator/parser.py` : interprète l'instruction textuelle et en extrait le
   sens (achat/vente, paire, quantité, type d'ordre, prix limite).
2. `translator/translator.py` : convertit l'instruction structurée en charge
   utile (payload) adaptée à l'API de 3Commas.
3. `translator/client.py` : gère la signature HMAC, l'envoi des requêtes HTTP et
   propose un mode *dry-run* pour les tests.

## Avertissement

L'API de 3Commas évolue régulièrement. Vérifiez les paramètres obligatoires des
endpoints `smart_trades/create_simple_buy` et `smart_trades/create_simple_sell`
avant de passer des ordres réels et effectuez vos propres tests sur un compte
de démonstration.
