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
    if 'question_number' not in st.session_state:
        st.session_state.question_number = 1
    if 'past_questions' not in st.session_state:
        st.session_state.past_questions = set()
    if 'total_beads' not in st.session_state:
        st.session_state.total_beads = 0
    if 'tens_beads' not in st.session_state:
        st.session_state.tens_beads = 0
    if 'units_beads' not in st.session_state:
        st.session_state.units_beads = 0
    # Initialize an empty DataFrame in session state to hold the logs
    if 'game_log' not in st.session_state:
        st.session_state.game_log = pd.DataFrame(columns=[
            "Timestamp", "Player Name", "Question Number", "Total Beads", 
            "Target", "Parity", "Correct Tens", "Correct Units", 
            "User Tens", "User Units", "Attempts", "Hints Used", 
            "Time Taken (s)", "Solved"
        ])

def generate_new_question():
    # Loop until we find a combination that hasn't been asked yet
    while True:
        total_beads = random.randint(2, 9)
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
    st.session_state.tens_beads = 0
    st.session_state.units_beads = 0
    
    # Start the timer for this question
    st.session_state.start_time = time.time()

def get_correct_answer(total, target, parity):
    possible_answers = []
    for tens in range(1, min(total + 1, 10)):
        units = total - tens
        if 0 <= units <= 9:
            is_odd = units % 2 != 0
            if (parity == 'odd' and is_odd) or (parity == 'even' and not is_odd):
                possible_answers.append((tens, units))
    
    if not possible_answers: return None, None
    if target == 'largest':
        best = max(possible_answers, key=lambda x: x[0] * 10 + x[1])
    else:
        best = min(possible_answers, key=lambda x: x[0] * 10 + x[1])
    return best[0], best[1]

# 2. Local Logging Function (Updates the in-memory DataFrame)
def log_attempt_to_memory(is_solved, correct_tens, correct_units, time_taken):
    new_row = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Player Name": st.session_state.player_name,
        "Question Number": st.session_state.question_number,
        "Total Beads": st.session_state.total_beads,
        "Target": st.session_state.target,
        "Parity": st.session_state.parity,
        "Correct Tens": correct_tens,
        "Correct Units": correct_units,
        "User Tens": st.session_state.tens_beads,
        "User Units": st.session_state.units_beads,
        "Attempts": st.session_state.attempts,
        "Hints Used": st.session_state.hint_level,
        "Time Taken (s)": round(time_taken, 1),
        "Solved": is_solved
    }])
    
    # Append the new attempt to the session state log
    st.session_state.game_log = pd.concat([st.session_state.game_log, new_row], ignore_index=True)

# Interactive Callbacks
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
.base { width: 100px; height: 30px; background-color: #8b4513; border-radius: 5px; text-align: center; color: white; font-weight: bold; line-height: 30px; margin: 5px auto 0 auto; }
</style>
""", unsafe_allow_html=True)

st.title("🧮 Abacus Logic Puzzle")
initialize_state()

# --- SCREEN 1: WELCOME ---
if st.session_state.game_state == 'welcome':
    st.subheader("Welcome to the Abacus Challenge!")
    name_input = st.text_input("Please enter your name to start:")
    
    if st.button("Start Game", type="primary"):
        if name_input.strip() == "":
            st.error("Don't forget to type your name!")
        else:
            st.session_state.player_name = name_input.strip()
            st.session_state.question_number = 1
            st.session_state.past_questions = set() # Clear question history
            st.session_state.game_log = st.session_state.game_log.iloc[0:0] # Clear log history
            st.session_state.game_state = 'playing'
            generate_new_question()
            st.rerun()

# --- SCREEN 2: GAMEPLAY ---
elif st.session_state.game_state == 'playing':
    # Top Action Bar for End Game Early
    col_title, col_end = st.columns([3, 1])
    with col_title:
        st.markdown(f"### Player: {st.session_state.player_name} | Question {st.session_state.question_number} / 10")
    with col_end:
        if st.button("🚪 End Game", help="Finish playing and download your score now"):
            st.session_state.game_state = 'game_over'
            st.rerun()
            
    total_used = st.session_state.tens_beads + st.session_state.units_beads

    st.info(f"**Mission:** Use exactly **{st.session_state.total_beads} beads** to show the **{st.session_state.target} possible 2-digit {st.session_state.parity} number**.")
    st.markdown(f"**Total Beads Dropped:** {total_used}")
    st.divider()

    # Rendering the Abacus
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬇️ Drop Bead", key="d_tens", on_click=drop_tens, use_container_width=True)
        beads_html = "".join(["<div class='bead'></div>" for _ in range(st.session_state.tens_beads)])
        st.markdown(f'<div class="abacus-rod">{beads_html}</div><div class="base">TENS</div>', unsafe_allow_html=True)
        st.button("⬆️ Pull Bead", key="p_tens", on_click=pull_tens, use_container_width=True, disabled=(st.session_state.tens_beads == 0))

    with col2:
        st.button("⬇️ Drop Bead", key="d_units", on_click=drop_units, use_container_width=True)
        beads_html = "".join(["<div class='bead'></div>" for _ in range(st.session_state.units_beads)])
        st.markdown(f'<div class="abacus-rod">{beads_html}</div><div class="base">UNITS</div>', unsafe_allow_html=True)
        st.button("⬆️ Pull Bead", key="p_units", on_click=pull_units, use_container_width=True, disabled=(st.session_state.units_beads == 0))

    st.divider()

    # Checking Answers
    if st.button("Check My Answer", type="primary"):
        st.session_state.attempts += 1
        time_taken = time.time() - st.session_state.start_time
        correct_tens, correct_units = get_correct_answer(st.session_state.total_beads, st.session_state.target, st.session_state.parity)
        
        is_solved = False
        
        # Validation checks
        if total_used != st.session_state.total_beads:
            st.error(f"You need exactly {st.session_state.total_beads} beads. You have {total_used}.")
        elif st.session_state.tens_beads > 9 or st.session_state.units_beads > 9:
            st.error("A single rod can only hold up to 9 beads.")
        elif st.session_state.tens_beads == 0:
            st.error("A 2-digit number must have at least 1 bead in the Tens place!")
        elif (st.session_state.parity == 'odd' and st.session_state.units_beads % 2 == 0) or \
             (st.session_state.parity == 'even' and st.session_state.units_beads % 2 != 0):
            st.error(f"Remember, the number must be {st.session_state.parity}!")
        else:
            if st.session_state.tens_beads == correct_tens and st.session_state.units_beads == correct_units:
                is_solved = True
                st.success(f"🎉 Fantastic! {st.session_state.tens_beads}{st.session_state.units_beads} is correct!")
                
                # Log successful attempt
                log_attempt_to_memory(is_solved, correct_tens, correct_units, time_taken)
                
                time.sleep(2)
                
                # Advance to next question or end game
                if st.session_state.question_number >= 10:
                    st.session_state.game_state = 'game_over'
                else:
                    st.session_state.question_number += 1
                    generate_new_question()
                st.rerun()
            else:
                st.warning(f"Is {st.session_state.tens_beads}{st.session_state.units_beads} the **{st.session_state.target}** one possible? Try adjusting!")

        # Log failed attempts
        if not is_solved:
            log_attempt_to_memory(is_solved, correct_tens, correct_units, time_taken)

    # Hint System
    if st.button("I need a hint!"):
        st.session_state.hint_level += 1
    
    if st.session_state.hint_level > 0:
        st.info("Hint: Put as many beads as possible in the Tens rod if looking for the largest number, or as few as possible for the smallest.")

# --- SCREEN 3: GAME OVER & DOWNLOAD ---
elif st.session_state.game_state == 'game_over':
    st.balloons()
    st.header(f"Amazing job, {st.session_state.player_name}! 🏆")
    
    # Calculate how many questions were actually solved from the log
    solved_count = 0
    if not st.session_state.game_log.empty:
        solved_count = len(st.session_state.game_log[st.session_state.game_log['Solved'] == True])
        
    st.markdown(f"You have successfully completed {solved_count} challenges.")
    
    st.divider()
    st.subheader("📊 Your Game Report")
    
    if not st.session_state.game_log.empty:
        st.dataframe(st.session_state.game_log)
        
        # 3. Create the downloadable CSV
        csv_data = st.session_state.game_log.to_csv(index=False).encode('utf-8')
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download Game Log (CSV)",
                data=csv_data,
                file_name=f"abacus_log_{st.session_state.player_name}_{datetime.now().strftime('%Y%m%d')}.csv",
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
