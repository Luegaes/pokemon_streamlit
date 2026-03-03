import streamlit as st
import pandas as pd


def show_evolution(poke_nr: int, lang_key: str):
   
    # ── CSV laden ──────────────────────────────────────────────────────────
    csv_evo = (
        "pokemon_evolutions_de.csv"
        if lang_key == "de"
        else "pokemon_evolutions_en.csv"
    )

    @st.cache_data
    def load_evo(path):
        df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
        # IDs als Zahlen, fehlende Werte bleiben NaN
        df["ID1"] = pd.to_numeric(df["ID1"], errors="coerce")
        df["ID2"] = pd.to_numeric(df["ID2"], errors="coerce")
        df["ID3"] = pd.to_numeric(df["ID3"], errors="coerce")
        return df

    df_evo = load_evo(csv_evo)

    # ── Zeile finden, in der poke_nr vorkommt ─────────────────────────────
    mask = (
        (df_evo["ID1"] == poke_nr) |
        (df_evo["ID2"] == poke_nr) |
        (df_evo["ID3"] == poke_nr)
    )
    treffer = df_evo[mask]

    if treffer.empty:
        st.info("Keine Entwicklungsdaten gefunden." if lang_key == "de" else "No evolution data found.")
        return

    row = treffer.iloc[0]

    # ── Spaltennamen je Sprache ────────────────────────────────────────────
    if lang_key == "de":
        name_cols = ["Entwicklungsstufe 1", "Entwicklungsstufe 2", "Entwicklungsstufe 3"]
        stufen_label = ["Stufe 1", "Stufe 2", "Stufe 3"]
    else:
        name_cols = ["Evolution Stage 1", "Evolution Stage 2", "Evolution Stage 3"]
        stufen_label = ["Stage 1", "Stage 2", "Stage 3"]

    id_cols = ["ID1", "ID2", "ID3"]

    # ── Welche Stufe ist das aktuelle Pokémon? ────────────────────────────
    aktuelle_stufe = None
    for i, id_col in enumerate(id_cols):
        if pd.notna(row[id_col]) and int(row[id_col]) == poke_nr:
            aktuelle_stufe = i + 1
            break

    # ── Einträge zusammenstellen (nur Stufen mit gültiger ID) ─────────────
    stufen = []
    for i in range(3):
        if pd.notna(row[id_cols[i]]):
            stufen.append({
                "id":    int(row[id_cols[i]]),
                "name":  row[name_cols[i]],
                "label": stufen_label[i],
                "aktiv": (i + 1 == aktuelle_stufe),
            })

    # ── Darstellung ────────────────────────────────────────────────────────
    cols = st.columns(len(stufen))

    for col, s in zip(cols, stufen):
        with col:
            # Hervorhebung des aktuellen Pokémon
            border = "3px solid #E53935" if s["aktiv"] else "3px solid transparent"
            bg     = "#FFF3E0"           if s["aktiv"] else "#F5F5F5"

            st.markdown(
                f"""
                <div style="
                    border: {border};
                    border-radius: 14px;
                    background: {bg};
                    padding: 10px 6px 6px 6px;
                    text-align: center;
                ">
                    <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{s['id']}.png"
                         width="120" style="image-rendering: pixelated;">
                    <p style="margin:4px 0 0 0; font-weight:{'bold' if s['aktiv'] else 'normal'}; font-size:1em;">
                        {s['name']}
                    </p>
                    <p style="margin:0; font-size:0.8em; color:#888;">#{s['id']:03d} · {s['label']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
