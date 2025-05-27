import streamlit as st
import pandas as pd
import plotly.express as px # Per grafici più interattivi

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Amazon Resale Analyzer",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNZIONI HELPER ---
@st.cache_data # Cache per migliorare le prestazioni nel ricaricamento dei dati
def load_data(uploaded_file):
    """Carica e pre-processa il file CSV."""
    try:
        df = pd.read_csv(uploaded_file)
        # Validazione colonne base (aggiungere altre se necessario)
        required_cols = [
            'Locale (base)', 'Locale (comp)', 'ASIN', 'Price_Base', 'Acquisto_Netto',
            'Price_Comp', 'Vendita_Netto', 'Margine_Stimato', 'Shipping_Cost',
            'Margine_Netto', 'Margine_Netto_%', 'SalesRank_Comp', 'Trend',
            'Bought_Comp', 'Volume_Score', 'Opportunity_Score', 'Opportunity_Class'
        ]
        # Rinominiamo la colonna con i cm³ per semplicità
        if 'Package: Dimension (cm³)' in df.columns:
             df.rename(columns={'Package: Dimension (cm³)': 'Package_Dimension_cm3_base'}, inplace=True)
             required_cols.append('Package_Dimension_cm3_base') # Aggiungiamo alla lista se esiste

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"Colonne mancanti nel CSV: {', '.join(missing_cols)}. Controlla la struttura del file.")
            return None

        # Conversione tipi per assicurare correttezza (anche se pandas spesso inferisce bene)
        float_cols = ['Price_Base', 'Acquisto_Netto', 'Price_Comp', 'Vendita_Netto',
                      'Margine_Stimato', 'Shipping_Cost', 'Margine_Netto', 'Margine_Netto_%',
                      'Bought_Comp', 'Volume_Score', 'Opportunity_Score']
        int_cols = ['SalesRank_Comp'] # Aggiungere 'Package_Dimension_cm3_base' se necessario
        if 'Package_Dimension_cm3_base' in df.columns:
            int_cols.append('Package_Dimension_cm3_base')


        for col in float_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        for col in int_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce', downcast='integer')

        # Gestione NaNs (opzionale, ma buona pratica)
        # df.dropna(subset=float_cols + int_cols, inplace=True) # Rimuove righe con NaN nelle colonne numeriche cruciali

        return df
    except Exception as e:
        st.error(f"Errore durante il caricamento del file: {e}")
        return None

def format_currency(value):
    return f"€{value:,.2f}"

def format_percentage(value):
    return f"{value:.2f}%"

# --- TITOLO E DESCRIZIONE APP ---
# st.image("assets/logo.png", width=150) # Se hai un logo
st.title("🛒 Amazon Resale Opportunity Analyzer")
st.markdown("""
Benvenuto! Carica il tuo file CSV per analizzare i dati dei prodotti Amazon e scoprire
le migliori opportunità di rivendita. Usa i filtri nel pannello laterale per affinare la tua ricerca.
""")

# --- UPLOAD FILE ---
uploaded_file = st.sidebar.file_uploader("📂 Carica il tuo file CSV", type="csv")

if uploaded_file is not None:
    df_original = load_data(uploaded_file)

    if df_original is not None and not df_original.empty:
        df = df_original.copy() # Lavoriamo su una copia per i filtri

        st.sidebar.header("⚙️ Filtri Avanzati")

        # --- FILTRI ---
        # 1. Filtro sul Margine
        st.sidebar.subheader("💰 Margine")
        min_margine_netto, max_margine_netto = float(df['Margine_Netto'].min()), float(df['Margine_Netto'].max())
        selected_margine_netto = st.sidebar.slider(
            "Margine Netto (€)",
            min_value=min_margine_netto,
            max_value=max_margine_netto,
            value=(min_margine_netto, max_margine_netto),
            step=0.5
        )
        df = df[(df['Margine_Netto'] >= selected_margine_netto[0]) & (df['Margine_Netto'] <= selected_margine_netto[1])]

        min_margine_perc, max_margine_perc = float(df['Margine_Netto_%'].min()), float(df['Margine_Netto_%'].max())
        if not df.empty: # Evita errori se il df precedente è vuoto
            selected_margine_perc = st.sidebar.slider(
                "Margine Netto (%)",
                min_value=min_margine_perc,
                max_value=max_margine_perc,
                value=(min_margine_perc, max_margine_perc),
                step=0.1
            )
            df = df[(df['Margine_Netto_%'] >= selected_margine_perc[0]) & (df['Margine_Netto_%'] <= selected_margine_perc[1])]

        # 2. Filtro sul Prezzo
        st.sidebar.subheader("💲 Prezzo")
        if not df.empty and 'Price_Comp' in df.columns:
            min_price_comp, max_price_comp = float(df['Price_Comp'].min()), float(df['Price_Comp'].max())
            selected_price_comp = st.sidebar.slider(
                "Prezzo di Vendita Marketplace Confronto (€)",
                min_value=min_price_comp,
                max_value=max_price_comp,
                value=(min_price_comp, max_price_comp),
                step=1.0
            )
            df = df[(df['Price_Comp'] >= selected_price_comp[0]) & (df['Price_Comp'] <= selected_price_comp[1])]

        if not df.empty and 'Acquisto_Netto' in df.columns:
            min_acquisto_netto, max_acquisto_netto = float(df['Acquisto_Netto'].min()), float(df['Acquisto_Netto'].max())
            selected_acquisto_netto = st.sidebar.slider(
                "Costo d'Acquisto Netto (€)",
                min_value=min_acquisto_netto,
                max_value=max_acquisto_netto,
                value=(min_acquisto_netto, max_acquisto_netto),
                step=1.0
            )
            df = df[(df['Acquisto_Netto'] >= selected_acquisto_netto[0]) & (df['Acquisto_Netto'] <= selected_acquisto_netto[1])]

        # 3. Filtri per prodotti di successo
        st.sidebar.subheader("🌟 Filtri per Successo Rivendita")

        # Opportunity Score
        if not df.empty and 'Opportunity_Score' in df.columns:
            min_opp_score, max_opp_score = float(df['Opportunity_Score'].min()), float(df['Opportunity_Score'].max())
            selected_opp_score = st.sidebar.slider(
                "Punteggio Opportunità (min)",
                min_value=min_opp_score,
                max_value=max_opp_score,
                value=min_opp_score,
                step=0.1
            )
            df = df[df['Opportunity_Score'] >= selected_opp_score]

        # Opportunity Class
        if not df.empty and 'Opportunity_Class' in df.columns:
            unique_opp_classes = df['Opportunity_Class'].dropna().unique().tolist()
            if unique_opp_classes:
                selected_opp_classes = st.sidebar.multiselect(
                    "Classe Opportunità",
                    options=unique_opp_classes,
                    default=unique_opp_classes # Seleziona tutto di default
                )
                if selected_opp_classes: # Applica filtro solo se qualcosa è selezionato
                    df = df[df['Opportunity_Class'].isin(selected_opp_classes)]

        # SalesRank_Comp (più basso è meglio)
        if not df.empty and 'SalesRank_Comp' in df.columns:
            # Usiamo log per gestire meglio la scala, ma il filtro è sul valore originale
            # Il max rank può essere molto alto, quindi limitiamo il cursore o usiamo number_input
            max_rank_val = 100000 # Valore ragionevole per il cursore, l'utente può digitare di più
            if not df.empty:
                max_rank_val = int(df['SalesRank_Comp'].max()) if not df['SalesRank_Comp'].empty else 100000

            selected_sales_rank_max = st.sidebar.number_input(
                "SalesRank Marketplace Confronto (max)",
                min_value=1,
                max_value=max_rank_val, # Può essere molto alto
                value=max_rank_val, # Default al massimo dei dati filtrati
                step=100
            )
            df = df[df['SalesRank_Comp'] <= selected_sales_rank_max]


        # Trend
        if not df.empty and 'Trend' in df.columns:
            unique_trends = df['Trend'].dropna().unique().tolist()
            if unique_trends:
                selected_trends = st.sidebar.multiselect(
                    "Trend di Mercato",
                    options=unique_trends,
                    default=unique_trends
                )
                if selected_trends:
                    df = df[df['Trend'].isin(selected_trends)]

        # Volume Score
        if not df.empty and 'Volume_Score' in df.columns:
            min_vol_score, max_vol_score = float(df['Volume_Score'].min()), float(df['Volume_Score'].max())
            selected_vol_score = st.sidebar.slider(
                "Punteggio Volume Vendite (min)",
                min_value=min_vol_score,
                max_value=max_vol_score,
                value=min_vol_score,
                step=0.1
            )
            df = df[df['Volume_Score'] >= selected_vol_score]

        # Locale (comp)
        if not df.empty and 'Locale (comp)' in df.columns:
            unique_locales_comp = df['Locale (comp)'].dropna().unique().tolist()
            if unique_locales_comp:
                selected_locales_comp = st.sidebar.multiselect(
                    "Marketplace di Confronto",
                    options=unique_locales_comp,
                    default=unique_locales_comp
                )
                if selected_locales_comp:
                    df = df[df['Locale (comp)'].isin(selected_locales_comp)]

        # --- DASHBOARD PRINCIPALE ---
        st.header("📊 Dashboard Riepilogativa")

        if not df.empty:
            # Informazioni Aggregate
            total_products_found = len(df)
            avg_margine_netto = df['Margine_Netto'].mean()
            avg_margine_perc = df['Margine_Netto_%'].mean()
            total_potential_profit_one_unit = df['Margine_Netto'].sum() # Profitto se si vende 1 unità di ogni prodotto filtrato
            avg_opportunity_score = df['Opportunity_Score'].mean()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Prodotti Trovati", total_products_found)
            col2.metric("Margine Netto Medio", format_currency(avg_margine_netto), f"{format_percentage(avg_margine_perc)} %")
            col3.metric("Profitto Potenziale (1x)", format_currency(total_potential_profit_one_unit))
            col4.metric("Opportunity Score Medio", f"{avg_opportunity_score:.2f}")

            st.markdown("---")

            # Visualizzazioni
            st.subheader("📈 Visualizzazioni Dati")
            
            c1, c2 = st.columns((6,4)) # Colonne per i grafici

            with c1:
                st.write("Distribuzione Margine Netto (€)")
                fig_margine_dist = px.histogram(df, x="Margine_Netto", nbins=30, title="Distribuzione Margine Netto")
                fig_margine_dist.update_layout(yaxis_title="Numero Prodotti")
                st.plotly_chart(fig_margine_dist, use_container_width=True)

            with c2:
                st.write("Prodotti per Classe di Opportunità")
                if 'Opportunity_Class' in df.columns:
                    opportunity_counts = df['Opportunity_Class'].value_counts().reset_index()
                    opportunity_counts.columns = ['Opportunity_Class', 'Count']
                    fig_opp_class = px.pie(opportunity_counts, names='Opportunity_Class', values='Count',
                                           title="Distribuzione Classe Opportunità", hole=0.3)
                    st.plotly_chart(fig_opp_class, use_container_width=True)
                else:
                    st.info("Colonna 'Opportunity_Class' non disponibile per questo grafico.")


            st.write("Relazione tra Punteggio Opportunità e Margine Netto")
            fig_scatter_opp_margin = px.scatter(df, x="Opportunity_Score", y="Margine_Netto",
                                                color="Opportunity_Class" if 'Opportunity_Class' in df.columns else None,
                                                size="Volume_Score" if 'Volume_Score' in df.columns else None,
                                                hover_data=['ASIN', 'Title (base)'],
                                                title="Opportunity Score vs. Margine Netto")
            st.plotly_chart(fig_scatter_opp_margin, use_container_width=True)


            # Tabella Dati Filtrati
            st.subheader("📋 Dettaglio Prodotti Filtrati")
            st.write(f"Visualizzati {len(df)} prodotti su {len(df_original)} totali.")

            # Seleziona colonne da mostrare per non affollare troppo
            cols_to_show = [
                'ASIN', 'Title (base)', 'Locale (comp)', 'Price_Comp', 'Acquisto_Netto',
                'Margine_Netto', 'Margine_Netto_%', 'SalesRank_Comp', 'Trend',
                'Opportunity_Score', 'Opportunity_Class', 'Volume_Score'
            ]
            # Mantieni solo le colonne effettivamente presenti nel DataFrame
            display_cols = [col for col in cols_to_show if col in df.columns]
            
            st.dataframe(df[display_cols].style.format({
                'Price_Comp': '{:.2f}€',
                'Acquisto_Netto': '{:.2f}€',
                'Margine_Netto': '{:.2f}€',
                'Margine_Netto_%': '{:.2f}%',
                'Opportunity_Score': '{:.2f}',
                'Volume_Score': '{:.2f}'
            }))

            # Pulsante Download
            @st.cache_data
            def convert_df_to_csv(dataframe):
                return dataframe.to_csv(index=False).encode('utf-8')

            csv_data = convert_df_to_csv(df)
            st.download_button(
                label="📥 Download CSV Filtrato",
                data=csv_data,
                file_name='prodotti_filtrati.csv',
                mime='text/csv',
            )

        else:
            st.warning("⚠️ Nessun prodotto trovato con i filtri selezionati. Prova ad allargare i criteri di ricerca.")

    elif df_original is not None and df_original.empty:
        st.warning("Il file CSV caricato è vuoto.")
    # else: Errore gestito da load_data

else:
    st.info("👋 Attendo il caricamento di un file CSV per iniziare l'analisi.")
    st.sidebar.info("Carica un file per vedere i filtri e la dashboard.")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.info("""
    **Amazon Resale Analyzer**
    Sviluppato da [Il Tuo Nome/Azienda]
    Versione 1.0.0
""")