import streamlit as st
import pandas as pd
import io
import time
from datetime import datetime
from supabase_utils import get_user_supabase, build_supabase_path

def interventions_tab(username, timepoint_id="T_01", timepoint_modifier="T01"):
    user_supabase = get_user_supabase()
    
    # Create timepoint-scoped session state keys
    df_key = f"intervention_plan_df_{timepoint_modifier}"
    timestamp_key = f"intervention_plan_timestamp_{timepoint_modifier}"
    step_key = f"intervention_step_{timepoint_modifier}"
    selected_areas_key = f"intervention_selected_areas_{timepoint_modifier}"
    
    if df_key not in st.session_state:
        try:
            plan_filename = build_supabase_path(username, timepoint_id, "intervention_plan.csv")
            bucket = user_supabase.storage.from_("data")
            # FIXED: Check files in the timepoint-specific directory, not user root
            files = bucket.list(path=f"{username}/{timepoint_modifier}/")
            in_list = any(f["name"] == "intervention_plan.csv" for f in files)
            
            if in_list:
                # Get timestamp from file metadata
                matching = next((f for f in files if f["name"] == "intervention_plan.csv"), None)
                if matching and "updated_at" in matching:
                    from dateutil import parser
                    st.session_state[timestamp_key] = parser.parse(matching["updated_at"]).strftime("%B %d, %Y")
                
                bytes_data = bucket.download(plan_filename)
                if isinstance(bytes_data, bytes):
                    df = pd.read_csv(io.BytesIO(bytes_data))
                    st.session_state[df_key] = df
        except Exception:
            pass
    
    if df_key in st.session_state:
        timestamp = st.session_state.get(timestamp_key)
        st.markdown(f"<h1>{timepoint_modifier} Interventions</h1>", unsafe_allow_html=True)
        st.markdown(f"Saved on {timestamp}. Double-click any cell to reveal its full contents.")
        st.dataframe(st.session_state[df_key])
    else:
        st.markdown(f"<h1>{timepoint_modifier} Interventions</h1>", unsafe_allow_html=True)
        st.markdown("""
        Use this space to design your personalized 8-week intervention plan. 
        Choose which domains you'd like to focus on, then describe the specific actions you'll commit to. 
        Your plan will be saved and viewable any time you return.
        """, unsafe_allow_html=True)
        focus_areas = [
            "Emotional Wellbeing",
            "Mental Fitness",
            "Physical Fitness",
            "Metabolic Fitness",
            "Sleep",
            "Addiction Dependency"
        ]
        examples = {
            "Emotional Wellbeing": "Example: Morning walks in nature 3x/week to discover silent spots. Weekend trips to scenic places.",
            "Mental Fitness": "Example: Daily Nuroe working memory game. Weekly cognitive training exercises.",
            "Physical Fitness": "Example: Add 1–2 60-90 minute GA1 endurance sessions per week.",
            "Metabolic Fitness": "Example: Supplement Fe, Zn, Mg, NMN+. Reduce sugar. Aim for HbA1c < 6.5.",
            "Sleep": "Example: Set 10:30 PM bedtime, limit screen use after 9 PM, take magnesium glycinate.",
            "Addiction Dependency": "Example: Reduce phone or social media use. Replace late-night scrolling with journaling. Limit alcohol to 1x/week. Track urges daily."
        }
        
        if step_key not in st.session_state:
            st.session_state[step_key] = "select_areas"
            
        if st.session_state[step_key] == "select_areas":
            st.markdown("### Choose your focus areas")
            with st.form("intervention_focus_area_form"):
                selected = st.multiselect("Select areas to focus on:", focus_areas, default=st.session_state.get(selected_areas_key, []))
                proceed = st.form_submit_button("Next")
                if proceed:
                    st.session_state[selected_areas_key] = selected
                    st.session_state[step_key] = "enter_plans"
                    st.rerun()
        elif st.session_state[step_key] == "enter_plans":
            st.markdown("### Describe Your Plans")
            with st.spinner("Loading plan fields..."):
                with st.form("intervention_plan_entry_form"):
                    plans = {}
                    for area in st.session_state[selected_areas_key]:
                        plans[area] = st.text_area(
                            f"Plan for {area}",
                            key=f"plan_{area}_{timepoint_modifier}",
                            placeholder=examples.get(area, f"What do you want to do to improve your {area.lower()} over the next 8 weeks?")
                        )
                    submitted = st.form_submit_button("Save My Plan")
                if submitted:
                    plan_df = pd.DataFrame([(k, v) for k, v in plans.items()], columns=["Category", "Plan"])
                    st.session_state[df_key] = plan_df
                    csv_bytes = plan_df.to_csv(index=False).encode()
                    plan_filename = build_supabase_path(username, timepoint_id, "intervention_plan.csv")
                    bucket = user_supabase.storage.from_("data")
                    try:
                        bucket.remove([plan_filename])
                    except:
                        pass
                    bucket.upload(
                        path=plan_filename,
                        file=csv_bytes,
                        file_options={"content-type": "text/csv"}
                    )
                    st.session_state[timestamp_key] = datetime.utcnow().strftime("%B %d, %Y")
                    st.rerun() 
