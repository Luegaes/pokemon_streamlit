import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kanto Pokédex", page_icon="🔴", layout="centered")

TYPE_COLORS_EN = {
    "Normal":"#A8A878","Fire":"#F08030","Water":"#6890F0","Electric":"#F8D030",
    "Grass":"#78C850","Ice":"#98D8D8","Fighting":"#C03028","Poison":"#A040A0",
    "Ground":"#E0C068","Flying":"#A890F0","Psychic":"#F85888","Bug":"#A8B820",
    "Rock":"#B8A038","Ghost":"#705898","Dragon":"#7038F8","Dark":"#705848","Steel":"#B8B8D0",
}
TYPE_COLORS_DE = {
    "Normal":"#A8A878","Feuer":"#F08030","Wasser":"#6890F0","Elektro":"#F8D030",
    "Pflanze":"#78C850","Eis":"#98D8D8","Kampf":"#C03028","Gift":"#A040A0",
    "Boden":"#E0C068","Flug":"#A890F0","Psycho":"#F85888","Käfer":"#A8B820",
    "Gestein":"#B8A038","Geist":"#705898","Drache":"#7038F8","Unlicht":"#705848","Stahl":"#B8B8D0",
}

MULTIPLIER_STYLE = {
    0:    ("#fff","#757575"),
    0.25: ("#fff","#0288D1"),
    0.5:  ("#fff","#388E3C"),
    1:    ("#555","#E0E0E0"),
    2:    ("#fff","#D32F2F"),
    4:    ("#fff","#7B0000"),
}

LABELS = {
    "de": {
        "title":"🔴 Kanto Pokédex — Typ-Schwächen",
        "subtitle":"FireRed / Gen III · 151 Pokémon",
        "select":"Wähle ein Pokémon:",
        "type":"Typ",
        "interactions":"Typ-Interaktionen",
        "all_table":"📊 Alle Multiplikatoren (Tabelle)",
        "source":"Datenquelle: pokemondb.net · Typ-Chart: Gen III (FireRed)",
        "mult_labels":{0:"Immun (×0)",0.25:"Sehr resistent (×¼)",0.5:"Resistent (×½)",
                       1:"Normal (×1)",2:"Schwach (×2)",4:"Sehr schwach (×4)"},
    },
    "en": {
        "title":"🔴 Kanto Pokédex — Type Weaknesses",
        "subtitle":"FireRed / Gen III · 151 Pokémon",
        "select":"Choose a Pokémon:",
        "type":"Type",
        "interactions":"Type Interactions",
        "all_table":"📊 All Multipliers (Table)",
        "source":"Data source: pokemondb.net · Type chart: Gen III (FireRed)",
        "mult_labels":{0:"Immune (×0)",0.25:"Very resistant (×¼)",0.5:"Resistant (×½)",
                       1:"Normal (×1)",2:"Weak (×2)",4:"Very weak (×4)"},
    },
}

@st.cache_data
def load_data(path):
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
    df.columns = [c.replace(" (x?)", "") for c in df.columns]
    return df

# ── Sprachumschalter ─────────────────────────────────────────────────────────
col_title, col_lang = st.columns([5, 1])
with col_lang:
    lang = st.radio("", ["🇩🇪 DE", "🇬🇧 EN"], horizontal=True, label_visibility="collapsed")

lang_key    = "de" if "DE" in lang else "en"
lbl         = LABELS[lang_key]
TYPE_COLORS = TYPE_COLORS_DE if lang_key == "de" else TYPE_COLORS_EN

csv_file = "pokemon_streamlit\kanto_feuerrot_schwaechen_de.csv" if lang_key == "de" else "pokemon_streamlit\kanto_feuerrot_schwaechen.csv"
df = load_data(csv_file)
ATTACK_TYPES = [c for c in df.columns if c not in ("Nr","Name","Typ 1","Typ 2")]

with col_title:
    st.markdown(f"## {lbl['title']}")
    st.markdown(f"**{lbl['subtitle']}**")

# ── Selectbox ────────────────────────────────────────────────────────────────
options = [f"#{int(row.Nr):03d}  {row.Name}" for _, row in df.iterrows()]
choice  = st.selectbox(lbl["select"], options)
idx     = options.index(choice)
poke    = df.iloc[idx]

# ── Stats-Auswahl ─────────────────────────────────────────────────────────────
st.markdown("#### Stats-Auswahl")
colStat_1 , colStat_2 = st.columns([1,1])
with colStat_1:
    schwächenSelected = st.checkbox("Typ-Schwächen", value=True)

with colStat_2:
    entwicklungsVerlauf = st.checkbox("Entwicklungsverlauf",value=True)

# ── Pokémon-Info ─────────────────────────────────────────────────────────────
if (schwächenSelected):
    st.divider()
    col1, col2 = st.columns([1, 2])

    with col1:
        num = int(poke["Nr"])
        st.image(f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{num}.png", width=800)
        st.markdown(f"### {poke['Name']}")
        st.markdown(f"**#{num:03d}**")

    with col2:
        t1 = str(poke["Typ 1"])
        t2 = str(poke["Typ 2"]) if pd.notna(poke["Typ 2"]) and str(poke["Typ 2"]) not in ("","nan") else None

        def badge(t):
            c = TYPE_COLORS.get(t, "#999")
            return f'<span style="background:{c};color:#fff;padding:4px 12px;border-radius:12px;font-weight:bold;font-size:0.9em;">{t}</span>'

        st.markdown(f"**{lbl['type']}:** {badge(t1)}{('  ' + badge(t2)) if t2 else ''}", unsafe_allow_html=True)
        st.markdown(f"#### {lbl['interactions']}")

        groups = {0:[],0.25:[],0.5:[],1:[],2:[],4:[]}
        for atk in ATTACK_TYPES:
            m = float(poke[atk])
            if m in groups:
                groups[m].append(atk)

        for m in [4,2,1,0.5,0.25,0]:
            typen = groups[m]
            if not typen:
                continue
            fg, bg = MULTIPLIER_STYLE[m]
            label  = lbl["mult_labels"][m]
            pills  = " ".join(
                f'<span style="background:{TYPE_COLORS.get(t,"#999")};color:#fff;'
                f'padding:2px 9px;border-radius:10px;font-size:0.85em;">{t}</span>'
                for t in typen
            )
            st.markdown(
                f'<div style="background:{bg};color:{fg};border-radius:8px;padding:7px 13px;margin:4px 0;">'
                f'<b>{label}</b>: {pills}</div>',
                unsafe_allow_html=True,
            )

# ── Entwicklungsverlauf ───────────────────────────────────────────────────
if entwicklungsVerlauf:
    st.divider()
    from evolution_verlauf import show_evolution
    show_evolution(int(poke["Nr"]), lang_key)

# ------ Source ------------------------
st.caption(lbl["source"])