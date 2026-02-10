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

# 5. Der KI-Experten-Check (Optional)
st.subheader("💬 Frag den Experten dazu")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash') # Oder 'gemini-1.5-flash' falls 2.5 noch zickt
    
    # Wir bauen dem Agenten den Kontext aus den Reglern
    kontext = f"""
    Aktuelle Berechnung:
    Kaufpreis: {kaufpreis}€, Eigenkapital: {eigenkapital}%, 
    Darlehen: {darlehen}€, Zins: {zins}%, Rate: {monatsrate}€.
    """
    
    if prompt := st.chat_input("Z.B.: Ist diese Rate bei 3000€ Netto tragbar?"):
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            # Wir senden die Zahlen UND die Frage an die KI
            full_prompt = f"{kontext}\nFrage des Nutzers: {prompt}. Antworte kurz und prägnant."
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
else:
    st.warning("Bitte gib links oben deinen API-Key ein, um die KI-Analyse zu nutzen.")