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
        if 'Package: Dimension (cm³)' in df.columns: # Nome esatto della colonna originale
             df.rename(columns={'Package: Dimension (cm³)': 'Package_Dimension_cm3_base'}, inplace=True)
             # required_cols.append('Package_Dimension_cm3_base') # Aggiungiamo alla lista se esiste, non strettamente necessario per i filtri ma per completezza

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"Colonne mancanti nel CSV: {', '.join(missing_cols)}. Controlla la struttura del file.")
            return None

        # Conversione tipi per assicurare correttezza
        float_cols = ['Price_Base', 'Acquisto_Netto', 'Price_Comp', 'Vendita_Netto',
                      'Margine_Stimato', 'Shipping_Cost', 'Margine_Netto', 'Margine_Netto_%',
                      'Bought_Comp', 'Volume_Score', 'Opportunity_Score']
        int_cols = ['SalesRank_Comp']
        if 'Package_Dimension_cm3_base' in df.columns:
            int_cols.append('Package_Dimension_cm3_base')


        for col in float_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        for col in int_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce', downcast='integer')

        return df
    except Exception as e:
        st.error(f"Errore durante il caricamento del file: {e}")
        return None

def format_currency(value):
    return f"€{value:,.2f}"

def format_percentage(value):
    return f"{value:.2f}%"

# --- TITOLO E DESCRIZIONE APP ---
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
        min_margine_netto_val = float(df_original['Margine_Netto'].min())
        max_margine_netto_val = float(df_original['Margine_Netto'].max())
        selected_margine_netto = st.sidebar.slider(
            "Margine Netto (€)",
            min_value=min_margine_netto_val,
            max_value=max_margine_netto_val,
            value=(min_margine_netto_val, max_margine_netto_val),
            step=0.5
        )
        df = df[(df['Margine_Netto'] >= selected_margine_netto[0]) & (df['Margine_Netto'] <= selected_margine_netto[1])]

        min_margine_perc_val = float(df_original['Margine_Netto_%'].min())
        max_margine_perc_val = float(df_original['Margine_Netto_%'].max())
        if not df.empty: # Evita errori se il df precedente è vuoto, ma usiamo df_original per i range globali
            selected_margine_perc = st.sidebar.slider(
                "Margine Netto (%)",
                min_value=min_margine_perc_val,
                max_value=max_margine_perc_val,
                value=(min_margine_perc_val, max_margine_perc_val),
                step=0.1
            )
            df = df[(df['Margine_Netto_%'] >= selected_margine_perc[0]) & (df['Margine_Netto_%'] <= selected_margine_perc[1])]

        # 2. Filtro sul Prezzo
        st.sidebar.subheader("💲 Prezzo")
        if 'Price_Comp' in df_original.columns:
            min_price_comp_val = float(df_original['Price_Comp'].min())
            max_price_comp_val = float(df_original['Price_Comp'].max())
            if not df.empty:
                selected_price_comp = st.sidebar.slider(
                    "Prezzo di Vendita Marketplace Confronto (€)",
                    min_value=min_price_comp_val,
                    max_value=max_price_comp_val,
                    value=(min_price_comp_val, max_price_comp_val),
                    step=1.0
                )
                df = df[(df['Price_Comp'] >= selected_price_comp[0]) & (df['Price_Comp'] <= selected_price_comp[1])]

        if 'Acquisto_Netto' in df_original.columns:
            min_acquisto_netto_val = float(df_original['Acquisto_Netto'].min())
            max_acquisto_netto_val = float(df_original['Acquisto_Netto'].max())
            if not df.empty:
                selected_acquisto_netto = st.sidebar.slider(
                    "Costo d'Acquisto Netto (€)",
                    min_value=min_acquisto_netto_val,
                    max_value=max_acquisto_netto_val,
                    value=(min_acquisto_netto_val, max_acquisto_netto_val),
                    step=1.0
                )
                df = df[(df['Acquisto_Netto'] >= selected_acquisto_netto[0]) & (df['Acquisto_Netto'] <= selected_acquisto_netto[1])]

        # 3. Filtri per prodotti di successo
        st.sidebar.subheader("🌟 Filtri per Successo Rivendita")

        # Opportunity Score
        if 'Opportunity_Score' in df_original.columns:
            min_opp_score_val = float(df_original['Opportunity_Score'].min())
            max_opp_score_val = float(df_original['Opportunity_Score'].max())
            if not df.empty:
                selected_opp_score = st.sidebar.slider(
                    "Punteggio Opportunità (min)",
                    min_value=min_opp_score_val,
                    max_value=max_opp_score_val,
                    value=min_opp_score_val, # Default al minimo dei dati filtrati
                    step=0.1
                )
                df = df[df['Opportunity_Score'] >= selected_opp_score]

        # Opportunity Class
        if 'Opportunity_Class' in df_original.columns:
            unique_opp_classes = sorted(df_original['Opportunity_Class'].dropna().unique().tolist())
            if unique_opp_classes and not df.empty:
                selected_opp_classes = st.sidebar.multiselect(
                    "Classe Opportunità",
                    options=unique_opp_classes,
                    default=unique_opp_classes
                )
                if selected_opp_classes:
                    df = df[df['Opportunity_Class'].isin(selected_opp_classes)]

        # SalesRank_Comp (più basso è meglio)
        if 'SalesRank_Comp' in df_original.columns:
            min_rank_val_orig = int(df_original['SalesRank_Comp'].min())
            max_rank_val_orig = int(df_original['SalesRank_Comp'].max()) if not df_original['SalesRank_Comp'].empty else 1000000
            if not df.empty:
                selected_sales_rank_max = st.sidebar.number_input(
                    "SalesRank Marketplace Confronto (max)",
                    min_value=min_rank_val_orig, # Minimo assoluto
                    max_value=max_rank_val_orig, # Massimo assoluto
                    value=max_rank_val_orig, # Default al massimo
                    step=100
                )
                df = df[df['SalesRank_Comp'] <= selected_sales_rank_max]


        # Trend
        if 'Trend' in df_original.columns:
            unique_trends = sorted(df_original['Trend'].dropna().unique().tolist())
            if unique_trends and not df.empty:
                selected_trends = st.sidebar.multiselect(
                    "Trend di Mercato",
                    options=unique_trends,
                    default=unique_trends
                )
                if selected_trends:
                    df = df[df['Trend'].isin(selected_trends)]

        # Volume Score
        if 'Volume_Score' in df_original.columns:
            min_vol_score_val = float(df_original['Volume_Score'].min())
            max_vol_score_val = float(df_original['Volume_Score'].max())
            if not df.empty:
                selected_vol_score = st.sidebar.slider(
                    "Punteggio Volume Vendite (min)",
                    min_value=min_vol_score_val,
                    max_value=max_vol_score_val,
                    value=min_vol_score_val,
                    step=0.1
                )
                df = df[df['Volume_Score'] >= selected_vol_score]

        # NUOVO: Filtro Bought_Comp (Vendite stimate mese scorso)
        if 'Bought_Comp' in df_original.columns:
            min_bought_comp_val = float(df_original['Bought_Comp'].min())
            max_bought_comp_val = float(df_original['Bought_Comp'].max())
            if not df.empty:
                selected_bought_comp_min = st.sidebar.number_input(
                    "Vendite Stimate Minime Mese Scorso (Comp)",
                    min_value=min_bought_comp_val,
                    max_value=max_bought_comp_val, # L'utente può inserire qualsiasi valore fino al max
                    value=min_bought_comp_val,    # Default al minimo
                    step=1.0                      # Incrementi di 1 unità
                )
                df = df[df['Bought_Comp'] >= selected_bought_comp_min]


        # Locale (comp)
        if 'Locale (comp)' in df_original.columns:
            unique_locales_comp = sorted(df_original['Locale (comp)'].dropna().unique().tolist())
            if unique_locales_comp and not df.empty:
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
            total_potential_profit_one_unit = df['Margine_Netto'].sum()
            avg_opportunity_score = df['Opportunity_Score'].mean() if 'Opportunity_Score' in df.columns else 0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Prodotti Trovati", total_products_found)
            col2.metric("Margine Netto Medio", format_currency(avg_margine_netto), f"{format_percentage(avg_margine_perc)} %")
            col3.metric("Profitto Potenziale (1x)", format_currency(total_potential_profit_one_unit))
            col4.metric("Opportunity Score Medio", f"{avg_opportunity_score:.2f}")

            st.markdown("---")

            # Visualizzazioni
            st.subheader("📈 Visualizzazioni Dati")

            c1, c2 = st.columns((6,4))

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


            if 'Opportunity_Score' in df.columns and 'Margine_Netto' in df.columns:
                st.write("Relazione tra Punteggio Opportunità e Margine Netto")
                hover_data_scatter = ['ASIN']
                if 'Title (base)' in df.columns: hover_data_scatter.append('Title (base)')

                fig_scatter_opp_margin = px.scatter(df, x="Opportunity_Score", y="Margine_Netto",
                                                    color="Opportunity_Class" if 'Opportunity_Class' in df.columns else None,
                                                    size="Volume_Score" if 'Volume_Score' in df.columns else None,
                                                    hover_data=hover_data_scatter,
                                                    title="Opportunity Score vs. Margine Netto")
                st.plotly_chart(fig_scatter_opp_margin, use_container_width=True)
            else:
                st.info("Colonne 'Opportunity_Score' o 'Margine_Netto' non disponibili per il grafico scatter.")


            # Tabella Dati Filtrati
            st.subheader("📋 Dettaglio Prodotti Filtrati")
            st.write(f"Visualizzati {len(df)} prodotti su {len(df_original)} totali.")

            # NUOVO: Opzioni di Ordinamento
            sort_col1, sort_col2 = st.columns(2)
            with sort_col1:
                # Definisci le colonne ordinabili e i loro nomi user-friendly
                sortable_columns_map = {
                    'Margine_Netto_%': 'Margine Netto %',
                    'Margine_Netto': 'Margine Netto (€)',
                    'Opportunity_Score': 'Opportunity Score',
                    'SalesRank_Comp': 'SalesRank (Comp)',
                    'Price_Comp': 'Prezzo (Comp)',
                    'Bought_Comp': 'Venduti Mese Scorso (Comp)',
                    'Volume_Score': 'Volume Score',
                    'ASIN': 'ASIN' # Aggiungiamo ASIN per ordinamento testuale se serve
                }
                # Filtra le colonne effettivamente presenti nel dataframe
                available_sort_columns = {k: v for k, v in sortable_columns_map.items() if k in df.columns}

                if available_sort_columns:
                    selected_sort_column_key = st.selectbox(
                        "Ordina per:",
                        options=list(available_sort_columns.keys()),
                        format_func=lambda x: available_sort_columns[x], # Mostra nome user-friendly
                        index=0 # Default alla prima opzione (es. Margine Netto %)
                    )
                else:
                    selected_sort_column_key = None # Nessuna colonna disponibile per l'ordinamento

            with sort_col2:
                sort_ascending = st.radio(
                    "Direzione:",
                    options=[False, True], # False per Discendente, True per Ascendente
                    format_func=lambda x: "Discendente" if not x else "Ascendente",
                    index=0 # Default Discendente (solitamente più utile per margini, score)
                )

            # Applica l'ordinamento se una colonna è stata selezionata
            df_display = df.copy() # Lavoriamo su una copia per l'ordinamento da visualizzare
            if selected_sort_column_key and selected_sort_column_key in df_display.columns:
                df_display.sort_values(by=selected_sort_column_key, ascending=sort_ascending, inplace=True)


            # Seleziona colonne da mostrare per non affollare troppo
            cols_to_show = [
                'ASIN', 'Title (base)', 'Locale (comp)', 'Price_Comp', 'Acquisto_Netto',
                'Margine_Netto', 'Margine_Netto_%', 'SalesRank_Comp', 'Trend', 'Bought_Comp',
                'Opportunity_Score', 'Opportunity_Class', 'Volume_Score'
            ]
            display_cols = [col for col in cols_to_show if col in df_display.columns]

            st.dataframe(df_display[display_cols].style.format({
                'Price_Comp': '{:.2f}€',
                'Acquisto_Netto': '{:.2f}€',
                'Margine_Netto': '{:.2f}€',
                'Margine_Netto_%': '{:.2f}%',
                'Bought_Comp': '{:.0f}', # Numero intero per le vendite
                'Opportunity_Score': '{:.2f}',
                'Volume_Score': '{:.2f}'
            }))

            # Pulsante Download (scarica i dati come sono stati filtrati e ordinati al momento del click)
            @st.cache_data
            def convert_df_to_csv(dataframe):
                return dataframe.to_csv(index=False).encode('utf-8')

            csv_data = convert_df_to_csv(df_display) # Usa df_display per includere l'ordinamento
            st.download_button(
                label="📥 Download CSV Filtrato e Ordinato",
                data=csv_data,
                file_name='prodotti_filtrati_ordinati.csv',
                mime='text/csv',
            )

        else:
            st.warning("⚠️ Nessun prodotto trovato con i filtri selezionati. Prova ad allargare i criteri di ricerca.")

    elif df_original is not None and df_original.empty:
        st.warning("Il file CSV caricato è vuoto.")

else:
    st.info("👋 Attendo il caricamento di un file CSV per iniziare l'analisi.")
    st.sidebar.info("Carica un file per vedere i filtri e la dashboard.")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.info("""
    **Amazon Resale Analyzer**
    Sviluppato con Streamlit
    Versione 1.1.0
""")