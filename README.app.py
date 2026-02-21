import streamlit as st
from datetime import datetime
import os

# --- Einstellungen & Daten speichern ---
TASK_FILE = "tasks.txt"
priority_order = {"Hoch": 1, "Mittel": 2, "Niedrig": 3}

# Aufgaben beim Start laden
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 4:
                    st.session_state.tasks.append({
                        "status": parts[0],
                        "priority": parts[1],
                        "name": parts[2],
                        "date": parts[3]
                    })

def save_tasks():
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        for t in st.session_state.tasks:
            f.write(f"{t['status']}|{t['priority']}|{t['name']}|{t['date']}\n")

# --- Benutzeroberfläche (UI) ---
st.set_page_config(page_title="To-Do Liste Pro", page_icon="🎯")
st.title("🎯 Meine Aufgaben-Manager")

# Statistik-Dashboard
if st.session_state.tasks:
    total = len(st.session_state.tasks)
    done = len([t for t in st.session_state.tasks if t['status'] == "Erledigt"])
    st.write(f"Fortschritt: **{done} von {total}** Aufgaben erledigt")
    st.progress(done / total if total > 0 else 0)
    st.divider()

# Seitenleiste zum Hinzufügen von Aufgaben
with st.sidebar:
    st.header("➕ Neue Aufgabe")
    task_input = st.text_input("Beschreibung")
    priority_input = st.selectbox("Priorität", ["Hoch", "Mittel", "Niedrig"])
    if st.button("Hinzufügen", use_container_width=True, type="primary"):
        if task_input:
            new_task = {
                "status": "Offen",
                "priority": priority_input,
                "name": task_input,
                "date": datetime.now().strftime("%d.%m.%Y %H:%M")
            }
            st.session_state.tasks.append(new_task)
            save_tasks()
            st.rerun()

# --- NEU: Suche und Filter ---
st.subheader("🔍 Suche und Filter")
search_query = st.text_input("Suche nach einer Aufgabe...", placeholder="Schreiben Sie hier...")

# Aufgaben anzeigen
st.subheader("📝 Aufgabenliste")

if not st.session_state.tasks:
    st.info("Deine Liste ist leer.")
else:
    # Aufgaben filtern basierend auf der Suche
    filtered_tasks = [
        t for t in st.session_state.tasks 
        if search_query.lower() in t['name'].lower()
    ]
    
    # Aufgaben nach Priorität sortieren
    sorted_tasks = sorted(filtered_tasks, key=lambda x: priority_order.get(x['priority'], 3))
    
    if not sorted_tasks and search_query:
        st.warning("Keine Aufgabe gefunden, die Ihrer Suche entspricht.")
    else:
        for idx, t in enumerate(sorted_tasks):
            col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
            
            with col1:
                is_done = t['status'] == "Erledigt"
                if st.checkbox("", value=is_done, key=f"check_{idx}_{t['name']}"):
                    t['status'] = "Erledigt"
                    save_tasks()
                    st.rerun()
                else:
                    if is_done: # إذا كانت "تم" وتم إلغاء التحديد
                        t['status'] = "Offen"
                        save_tasks()
                        st.rerun()
            
            with col2:
                if t['status'] == "Erledigt":
                    st.write(f"~~{t['name']}~~")
                else:
                    st.write(f"**{t['name']}**")
                st.caption(f"Prio: {t['priority']} | {t['date']}")
                
            with col3:
                if st.button("🗑️", key=f"del_{idx}_{t['name']}"):
                    st.session_state.tasks.remove(t)
                    save_tasks()
                    st.rerun()
            st.divider()

# Button zum Aufräumen
if st.button("🧹 Alle erledigten Aufgaben löschen"):
    st.session_state.tasks = [t for t in st.session_state.tasks if t['status'] != "Erledigt"]
    save_tasks()
    st.rerun()
