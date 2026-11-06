import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime

# 1. State Management Initialization
def initialize_state():
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'welcome' # 'welcome', 'playing', 'game_over'
    if 'player_name' not in st.session_state:
        st.session_state.player_name = ''
    if 'digit_mode' not in st.session_state:
        st.session_state.digit_mode = 2
    if 'question_number' not in st.session_state:
        st.session_state.question_number = 1
    if 'past_questions' not in st.session_state:
        st.session_state.past_questions = set()
    if 'total_beads' not in st.session_state:
        st.session_state.total_beads = 0
    
    # Bead states
    if 'hundreds_beads' not in st.session_state:
        st.session_state.hundreds_beads = 0
    if 'tens_beads' not in st.session_state:
        st.session_state.tens_beads = 0
    if 'units_beads' not in st.session_state:
        st.session_state.units_beads = 0
        
    # Initialize an empty DataFrame in session state to hold the logs
    if 'game_log' not in st.session_state:
        st.session_state.game_log = pd.DataFrame(columns=[
            "Timestamp", "Player Name", "Mode", "Question Number", "Total Beads", 
            "Target", "Parity", "Correct Hundreds", "Correct Tens", "Correct Units", 
            "User Hundreds", "User Tens", "User Units", "Attempts", "Hints Used", 
            "Time Taken (s)", "Solved"
        ])

def generate_new_question():
    while True:
        # Scale the random bead count based on difficulty
        if st.session_state.digit_mode == 2:
            total_beads = random.randint(2, 9)
        else:
            total_beads = random.randint(3, 15)
            
        target = random.choice(["largest", "smallest"])
        parity = random.choice(["odd", "even"])
        
        q_tuple = (total_beads, target, parity)
        if q_tuple not in st.session_state.past_questions:
            st.session_state.past_questions.add(q_tuple)
            
            st.session_state.total_beads = total_beads
            st.session_state.target = target
            st.session_state.parity = parity
            break
            
    st.session_state.hint_level = 0
    st.session_state.attempts = 0
    st.session_state.hundreds_beads = 0
    st.session_state.tens_beads = 0
    st.session_state.units_beads = 0
    
    st.session_state.start_time = time.time()

def get_correct_answer(total, target, parity, mode):
    possible_answers = []
    
    if mode == 2:
        for tens in range(1, min(total + 1, 10)):
            units = total - tens
            if 0 <= units <= 9:
                is_odd = units % 2 != 0
                if (parity == 'odd' and is_odd) or (parity == 'even' and not is_odd):
                    possible_answers.append((0, tens, units))
    else: # mode == 3
        for hundreds in range(1, min(total + 1, 10)):
            for tens in range(0, 10):
                units = total - hundreds - tens
                if 0 <= units <= 9:
                    is_odd = units % 2 != 0
                    if (parity == 'odd' and is_odd) or (parity == 'even' and not is_odd):
                        possible_answers.append((hundreds, tens, units))
                        
    if not possible_answers: return None, None, None
    
    if target == 'largest':
        best = max(possible_answers, key=lambda x: x[0] * 100 + x[1] * 10 + x[2])
    else:
        best = min(possible_answers, key=lambda x: x[0] * 100 + x[1] * 10 + x[2])
        
    return best[0], best[1], best[2]

# 2. Local Logging Function
def log_attempt_to_memory(is_solved, correct_hun, correct_tens, correct_units, time_taken):
    new_row = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Player Name": st.session_state.player_name,
        "Mode": f"{st.session_state.digit_mode}-Digit",
        "Question Number": st.session_state.question_number,
        "Total Beads": st.session_state.total_beads,
        "Target": st.session_state.target,
        "Parity": st.session_state.parity,
        "Correct Hundreds": correct_hun,
        "Correct Tens": correct_tens,
        "Correct Units": correct_units,
        "User Hundreds": st.session_state.hundreds_beads,
        "User Tens": st.session_state.tens_beads,
        "User Units": st.session_state.units_beads,
        "Attempts": st.session_state.attempts,
        "Hints Used": st.session_state.hint_level,
        "Time Taken (s)": round(time_taken, 1),
        "Solved": is_solved
    }])
    st.session_state.game_log = pd.concat([st.session_state.game_log, new_row], ignore_index=True)

# Interactive Callbacks
def drop_hundreds(): st.session_state.hundreds_beads += 1
def pull_hundreds(): 
    if st.session_state.hundreds_beads > 0: st.session_state.hundreds_beads -= 1
def drop_tens(): st.session_state.tens_beads += 1
def pull_tens():
    if st.session_state.tens_beads > 0: st.session_state.tens_beads -= 1
def drop_units(): st.session_state.units_beads += 1
def pull_units():
    if st.session_state.units_beads > 0: st.session_state.units_beads -= 1

# Base CSS
st.markdown("""
<style>
.abacus-rod { width: 8px; height: 250px; background-color: #d2b48c; position: relative; display: flex; flex-direction: column-reverse; align-items: center; border-radius: 4px; border: 1px solid #8b4513; margin: 0 auto; }
.bead { width: 60px; height: 18px; background-color: #e74c3c; border-radius: 10px; margin-bottom: 1px; border: 1px solid #c0392b; box-shadow: inset 0 -3px 3px rgba(0,0,0,0.2); }
.base { width: 100px; height: 30px; background-color: #8b4513; border-radius: 5px; text-align: center; color: white; font-weight: bold; line-height: 30px; margin: 5px auto 0 auto; font-size: 14px;}
</style>
""", unsafe_allow_html=True)

st.title("🧮 Abacus Logic Puzzle")
initialize_state()

# --- SCREEN 1: WELCOME ---
if st.session_state.game_state == 'welcome':
    st.subheader("Welcome to the Abacus Challenge!")
    name_input = st.text_input("Please enter your name to start:")
    
    # Difficulty Selector
    mode_selection = st.radio(
        "Select Difficulty Level:",
        options=["2-Digit Game (Tens & Units)", "3-Digit Game (Hundreds, Tens & Units)"],
        index=0
    )
    
    if st.button("Start Game", type="primary"):
        if name_input.strip() == "":
            st.error("Don't forget to type your name!")
        else:
            st.session_state.player_name = name_input.strip()
            st.session_state.digit_mode = 2 if "2-Digit" in mode_selection else 3
            st.session_state.question_number = 1
            st.session_state.past_questions = set()
            st.session_state.game_log = st.session_state.game_log.iloc[0:0]
            st.session_state.game_state = 'playing'
            generate_new_question()
            st.rerun()

# --- SCREEN 2: GAMEPLAY ---
elif st.session_state.game_state == 'playing':
    col_title, col_end = st.columns([3, 1])
    with col_title:
        st.markdown(f"### Player: {st.session_state.player_name} | Question {st.session_state.question_number} / 10")
    with col_end:
        if st.button("🚪 End Game", help="Finish playing and download your score now"):
            st.session_state.game_state = 'game_over'
            st.rerun()
            
    total_used = st.session_state.hundreds_beads + st.session_state.tens_beads + st.session_state.units_beads
    mode_str = f"{st.session_state.digit_mode}-digit"
    highest_place = "Hundreds" if st.session_state.digit_mode == 3 else "Tens"

    st.info(f"**Mission:** Use exactly **{st.session_state.total_beads} beads** to show the **{st.session_state.target} possible {mode_str} {st.session_state.parity} number**.")
    st.markdown(f"**Total Beads Dropped:** {total_used}")
    st.divider()

    # Rendering the Abacus dynamically based on digit_mode
    cols = st.columns(st.session_state.digit_mode)
    
    # Setup rendering for Hundreds if 3-Digit mode
    col_idx = 0
    if st.session_state.digit_mode == 3:
        with cols[col_idx]:
            st.button("⬇️ Drop Bead", key="d_hun", on_click=drop_hundreds, use_container_width=True)
            beads_html = "".join(["<div class='bead'></div>" for _ in range(st.session_state.hundreds_beads)])
            st.markdown(f'<div class="abacus-rod">{beads_html}</div><div class="base">HUNDREDS</div>', unsafe_allow_html=True)
            st.button("⬆️ Pull Bead", key="p_hun", on_click=pull_hundreds, use_container_width=True, disabled=(st.session_state.hundreds_beads == 0))
        col_idx += 1

    # Render Tens
    with cols[col_idx]:
        st.button("⬇️ Drop Bead", key="d_tens", on_click=drop_tens, use_container_width=True)
        beads_html = "".join(["<div class='bead'></div>" for _ in range(st.session_state.tens_beads)])
        st.markdown(f'<div class="abacus-rod">{beads_html}</div><div class="base">TENS</div>', unsafe_allow_html=True)
        st.button("⬆️ Pull Bead", key="p_tens", on_click=pull_tens, use_container_width=True, disabled=(st.session_state.tens_beads == 0))
    col_idx += 1
    
    # Render Units
    with cols[col_idx]:
        st.button("⬇️ Drop Bead", key="d_units", on_click=drop_units, use_container_width=True)
        beads_html = "".join(["<div class='bead'></div>" for _ in range(st.session_state.units_beads)])
        st.markdown(f'<div class="abacus-rod">{beads_html}</div><div class="base">UNITS</div>', unsafe_allow_html=True)
        st.button("⬆️ Pull Bead", key="p_units", on_click=pull_units, use_container_width=True, disabled=(st.session_state.units_beads == 0))

    st.divider()

    # Checking Answers
    if st.button("Check My Answer", type="primary"):
        st.session_state.attempts += 1
        time_taken = time.time() - st.session_state.start_time
        correct_hun, correct_tens, correct_units = get_correct_answer(
            st.session_state.total_beads, 
            st.session_state.target, 
            st.session_state.parity, 
            st.session_state.digit_mode
        )
        
        is_solved = False
        
        # Validation checks
        if total_used != st.session_state.total_beads:
            st.error(f"You need exactly {st.session_state.total_beads} beads. You have {total_used}.")
        elif st.session_state.hundreds_beads > 9 or st.session_state.tens_beads > 9 or st.session_state.units_beads > 9:
            st.error("A single rod can only hold up to 9 beads.")
        elif (st.session_state.digit_mode == 3 and st.session_state.hundreds_beads == 0) or (st.session_state.digit_mode == 2 and st.session_state.tens_beads == 0):
            st.error(f"A {mode_str} number must have at least 1 bead in the {highest_place} place!")
        elif (st.session_state.parity == 'odd' and st.session_state.units_beads % 2 == 0) or \
             (st.session_state.parity == 'even' and st.session_state.units_beads % 2 != 0):
            st.error(f"Remember, the number must be {st.session_state.parity}!")
        else:
            if st.session_state.hundreds_beads == correct_hun and st.session_state.tens_beads == correct_tens and st.session_state.units_beads == correct_units:
                is_solved = True
                success_str = f"{st.session_state.hundreds_beads}{st.session_state.tens_beads}{st.session_state.units_beads}" if st.session_state.digit_mode == 3 else f"{st.session_state.tens_beads}{st.session_state.units_beads}"
                st.success(f"🎉 Fantastic! {success_str} is correct!")
                
                log_attempt_to_memory(is_solved, correct_hun, correct_tens, correct_units, time_taken)
                time.sleep(2)
                
                if st.session_state.question_number >= 10:
                    st.session_state.game_state = 'game_over'
                else:
                    st.session_state.question_number += 1
                    generate_new_question()
                st.rerun()
            else:
                st.warning(f"You met the rules, but is it the **{st.session_state.target}** one possible? Try adjusting!")

        # Log failed attempts
        if not is_solved:
            log_attempt_to_memory(is_solved, correct_hun, correct_tens, correct_units, time_taken)

    # Hint System
    if st.button("I need a hint!"):
        st.session_state.hint_level += 1
    
    if st.session_state.hint_level > 0:
        st.info(f"Hint: Put as many beads as possible in the **{highest_place}** rod if looking for the largest number, or as few as possible for the smallest.")

# --- SCREEN 3: GAME OVER & DOWNLOAD ---
elif st.session_state.game_state == 'game_over':
    st.balloons()
    st.header(f"Amazing job, {st.session_state.player_name}! 🏆")
    
    solved_count = 0
    if not st.session_state.game_log.empty:
        solved_count = len(st.session_state.game_log[st.session_state.game_log['Solved'] == True])
        
    st.markdown(f"You successfully solved {solved_count} challenges on {st.session_state.digit_mode}-Digit mode.")
    
    st.divider()
    st.subheader("📊 Your Game Report")
    
    if not st.session_state.game_log.empty:
        st.dataframe(st.session_state.game_log)
        
        csv_data = st.session_state.game_log.to_csv(index=False).encode('utf-8')
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download Game Log (CSV)",
                data=csv_data,
                file_name=f"abacus_log_{st.session_state.player_name}_{st.session_state.digit_mode}D_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                type="primary"
            )
        with col2:
            if st.button("Play Again"):
                st.session_state.game_state = 'welcome'
                st.session_state.player_name = ''
                st.rerun()
    else:
        st.info("No attempts were made this round.")
        if st.button("Play Again"):
            st.session_state.game_state = 'welcome'
            st.session_state.player_name = ''
            st.rerun()
