# Amazon Resale Analyzer

Questa applicazione Streamlit permette di caricare un file CSV contenente dati di prodotti Amazon per analizzare opportunità di rivendita.

## Struttura del CSV Attesa

Il file CSV deve avere le seguenti colonne (rispettare maiuscole/minuscole e separatori):

- `Unnamed: 0` (int): Indice originario.
- `Locale (base)` (string): Codice paese Amazon di origine (es. it).
- `Locale (comp)` (string): Codice paese Amazon di confronto (es. es, fr).
- `Title (base)` (string): Titolo del prodotto.
- `ASIN` (string): Codice ASIN univoco.
- `Price_Base` (float, separatore: punto): Prezzo nel marketplace base.
- `Acquisto_Netto` (float, separatore: punto): Prezzo netto d’acquisto.
- `Price_Comp` (float, separatore: punto): Prezzo nel marketplace di confronto.
- `Vendita_Netto` (float, separatore: punto): Prezzo netto stimato di vendita.
- `Margine_Stimato` (float, separatore: punto): Guadagno lordo stimato.
- `Shipping_Cost` (float, separatore: punto): Costo di spedizione.
- `Margine_Netto` (float, separatore: punto): Guadagno netto effettivo stimato.
- `Margine_Netto_%` (float, separatore: punto): Percentuale del margine netto.
- `Weight_kg` (int): Peso del prodotto in kg.
- `SalesRank_Comp` (int): Posizione nel ranking vendite Amazon (paese confronto).
- `Trend` (string): Andamento del prodotto (es. ➖ Stabile, 📈 In Crescita).
- `Bought_Comp` (float, separatore: punto): Quantità acquistata stimata (paese confronto).
- `NewOffer_Comp` (int): Numero nuove offerte (paese confronto).
- `Volume_Score` (float, separatore: punto): Punteggio volume di vendita.
- `Opportunity_Score` (float, separatore: punto): Punteggio opportunità commerciale.
- `Opportunity_Class` (string): Classificazione opportunità (Buona, Discreta, Bassa).
- `IVA_Origine` (string): Aliquota IVA paese origine.
- `IVA_Confronto` (string): Aliquota IVA paese confronto.
- `Package: Dimension (cm³)` (base) (int): Volume pacco in cm³.

## Setup e Avvio

1.  **Clona il repository (o estrai lo ZIP).**
2.  **Installa le dipendenze:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Avvia l'applicazione Streamlit:**
    ```bash
    streamlit run app.py
    ```
4.  Apri il browser all'indirizzo indicato (solitamente `http://localhost:8501`).

## Deploy su Streamlit Community Cloud

1.  Assicurati che il tuo progetto sia su un repository GitHub pubblico.
2.  Vai su [share.streamlit.io](https://share.streamlit.io/) e collega il tuo account GitHub.
3.  Clicca su "New app", seleziona il repository, il branch e il file principale (`app.py`).
4.  Clicca su "Deploy!".