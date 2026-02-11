import streamlit as st
import google.generativeai as genai

# 1. Konfiguration der Seite
st.set_page_config(page_title="Immo-Cockpit 2026", layout="wide")

st.title("🏠 Immobilien-Finanzierungs-Cockpit")
st.markdown("---")

# 2. Die Sidebar (Steuerzentrale)
with st.sidebar:
    st.header("⚙️ Einstellungen")
    api_key = st.text_input("Google API Key", type="password")
    
    st.header("🔢 Die harten Fakten")
    # Kaufpreis als Zahleneingabe
    kaufpreis = st.number_input("Kaufpreis (€)", value=450000, step=5000)
    
    # Schieberegler für die Prozentwerte
    eigenkapital = st.slider("Eigenkapital (%)", 0, 100, 20)
    zins = st.slider("Zinssatz (%)", 0.5, 10.0, 3.9, step=0.1)
    tilgung = st.slider("Tilgung (%)", 1.0, 10.0, 2.0, step=0.1)
    inflation = st.slider("Erwartete Inflation (%)", 0.0, 10.0, 2.5, step=0.1)

# 3. Automatische Berechnung (Python pur - super schnell)
ek_betrag = kaufpreis * (eigenkapital / 100)
darlehen = kaufpreis - ek_betrag
jahresrate = darlehen * (zins + tilgung) / 100
monatsrate = jahresrate / 12
reale_last = monatsrate / (1 + inflation / 100)

# 4. Anzeige der Ergebnisse (Das Dashboard)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="🏦 Darlehenshöhe", value=f"{darlehen:,.2f} €")
    st.caption(f"Eigenkapital: {ek_betrag:,.2f} €")

with col2:
    st.metric(label="📅 Monatliche Rate", value=f"{monatsrate:,.2f} €")
    st.caption(f"Zins & Tilgung: {zins + tilgung}%")

with col3:
    st.metric(label="baguette_bread Kaufkraft-Rate", value=f"{reale_last:,.2f} €")
    st.caption(f"Bereinigt um {inflation}% Inflation")

st.markdown("---")

# 5. Der KI-Experten-Check (ROBUSTER MODUS)
st.subheader("💬 Frag den Experten dazu")

if api_key:
    # Wir probieren, die KI zu starten und fangen Fehler ab
    try:
        genai.configure(api_key=api_key)
        
        # 1. Wir fragen Google: "Welche Modelle darf dieser Key benutzen?"
        # Das verhindert den "NotFound" Fehler, weil wir nur nehmen, was da ist.
        all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not all_models:
            st.error("❌ Dein API-Key ist gültig, aber er hat keinen Zugriff auf Text-Modelle. (Liste leer)")
            st.stop()

        # 2. Wir suchen uns das beste verfügbare Modell aus
        # Wir bevorzugen 'flash', wenn nicht da, nehmen wir 'pro', sonst das erste was wir finden.
        # Wir erzwingen Version 1.5, weil sie 1500 statt nur 20 Anfragen erlaubt
if any("models/gemini-1.5-flash" in m for m in all_models):
    active_model_name = "models/gemini-1.5-flash"
else:
    active_model_name = all_models[0]
        if not active_model_name:
             active_model_name = next((m for m in all_models if 'pro' in m), all_models[0])
        
        # Starten mit dem gefundenen Modell
        model = genai.GenerativeModel(active_model_name)

        # 3. Der Kontext für die KI
        kontext = f"""
        Aktuelle Berechnung:
        Kaufpreis: {kaufpreis}€, Eigenkapital: {eigenkapital}%, 
        Darlehen: {darlehen}€, Zins: {zins}%, Rate: {monatsrate:.2f}€.
        """
        
        # 4. Das Chat-Eingabefeld
        if prompt := st.chat_input("Z.B.: Ist diese Rate bei 3000€ Netto tragbar?"):
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                full_prompt = f"{kontext}\nFrage des Nutzers: {prompt}. Antworte kurz und prägnant auf Deutsch."
                try:
                    response = model.generate_content(full_prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Fehler bei der Antwort: {e}")

    except Exception as e:
        st.error(f"❌ Der API-Key scheint nicht zu stimmen oder hat keine Rechte:\n{e}")

else:
    st.warning("Bitte gib links oben deinen API-Key ein, um die KI-Analyse zu nutzen.")

