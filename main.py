import os
import sys
from dotenv import load_dotenv
from gemini_client import GeminiClient
from data_manager import DataManager
from quiz_engine import QuizEngine

def print_welcome_art():
    art = r"""
  _      ______                  _
 | |    |  ____|                (_)
 | |    | |__   __ _ _ __ _ __   _ _ __   __ _
 | |    |  __| / _` | '__| '_ \ | | '_ \ / _` |
 | |____| |___| (_| | |  | | | || | | | | (_| |
 |______|______\__,_|_|  |_| |_||_|_| |_|\__, |
                                          __/ |
                                         |___/
 🇮🇹  Italian Tutor for German Speakers 🇩🇪
    """
    print(art)

def main():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_key_here":
        print("❌ Error: GEMINI_API_KEY is missing or invalid in .env file.")
        print("Please set your API key in the .env file.")
        sys.exit(1)

    try:
        # Initialize components
        client = GeminiClient(api_key=api_key)
        data_manager = DataManager()
        engine = QuizEngine(client, data_manager)

        # Start App
        print_welcome_art()
        
        while True:
            # Mode Selection
            print("\nSelect Mode:")
            print("1. Online (AI Generated)")
            print("2. Offline (Local Questions)")
            print("3. Review Errors (Personalized)")
            print("q. Quit")
            mode_choice = input("Choice: ").strip().lower()
            
            if mode_choice in ['q', 'quit', 'exit']:
                print("Arrivederci! / Auf Wiedersehen! 👋")
                sys.exit(0)
            
            offline_mode = mode_choice == "2" or mode_choice == "3"
            custom_questions = []

            # REVIEW ERRORS MODE
            if mode_choice == "3":
                saved_errors = data_manager.load_errors()
                if not saved_errors:
                    print("🎉 Great news! You have no saved errors to review.")
                    print("Try a normal quiz to practice more!")
                    continue
                
                print(f"📂 Found {len(saved_errors)} errors to review.")
                action = input("Type 'p' to practice immediately, 'v' to view list, or 'b' to back: ").strip().lower()
                
                if action == 'v':
                    # Print the list of errors
                    print(f"\n--- Error List ---")
                    for i, err in enumerate(saved_errors, 1):
                        q_text = err.get('question', '').split('\n')[0]
                        u_ans = err.get('user_answer', '-')
                        c_ans = ', '.join(err.get('correct_answers', [])) if 'correct_answers' in err else 'N/A'
                        exp = err.get('explanation', '')
                        
                        print(f"{i}. {q_text}")
                        print(f"   ❌ Errore: {u_ans}")
                        print(f"   ✅ Corretto: {c_ans}")
                        
                        if exp:
                            print(f"   📖 Spiegazione:")
                            exp_lines = exp.split('\n')
                            for line in exp_lines:
                                print(f"      {line}")
                        print("-" * 30)
                    
                    # Option to Practice after viewing
                    print("\n")
                    practice = input("Ready to practice these errors? (y/n): ").strip().lower()
                    if practice not in ['s', 'si', 'y', 'yes']:
                        continue
                
                elif action == 'p':
                    # Practice immediately
                    pass
                else:
                    # Cancel or Invalid
                    continue
                
                # Filter valid questions for the engine
                valid_questions = []
                for q in saved_errors:
                    if 'question' in q:
                         # Ensure minimal fields for engine execution
                         if 'correct_answers' not in q:
                              # If missing, we can't really grade it, but filtering avoids crash.
                              pass
                         valid_questions.append(q)

                custom_questions = valid_questions
                offline_mode = True
                
                if not custom_questions:
                     print("⚠️  No valid questions to review.")
                     continue

            # Level Selection (Online Mode)
            selected_level = "A1" # Default
            if mode_choice == "1":
                print("\nSelect Difficulty Level:")
                print("1. A1")
                print("2. A2")
                print("3. B1")
                print("4. B2")
                print("5. C1")
                print("6. C2")
                
                lvl_map = {"1": "A1", "2": "A2", "3": "B1", "4": "B2", "5": "C1", "6": "C2"}
                lvl_choice = input("Choice [Default A1]: ").strip()
                if lvl_choice in lvl_map:
                    selected_level = lvl_map[lvl_choice]
                else:
                    print("Defaulting to A1.")


            # OFFLINE LEVEL SELECTION
            elif mode_choice == "2":
                back_to_menu = False
                while True:
                    print("\nSelect Level:")
                    print("1. A1.1")
                    print("2. A1.2")
                    print("3. A2.1")
                    print("4. A2.2")
                    print("b. Back to Main Menu")
                    
                    level_choice = input("Choice: ").strip().lower()
                    
                    level_map = {
                        "1": "a1_1.json",
                        "2": "a1_2.json",
                        "3": "a2_1.json",
                        "4": "a2_2.json"
                    }

                    if level_choice == 'b':
                         back_to_menu = True
                         break

                    if level_choice in level_map:
                        filename = level_map[level_choice]
                        custom_questions = data_manager.load_level_questions(filename)
                        if not custom_questions:
                            print(f"❌ Error: Could not load questions from 'data/{filename}'. File missing or empty.")
                            continue 
                        
                        break 
                    else:
                        print("❌ Invalid choice. Please try again.")

                if back_to_menu:
                    continue

            # Ask for Session Length (Skip for Review Mode, Mode 3)
            silent_start = False
            if mode_choice == "3":
                 session_length = len(custom_questions)
                 silent_start = True
            else:
                print("\nHow many questions do you want to answer? (10 or 20)")
                length_input = input("Number [Default 10]: ").strip()
                
                session_length = 10
                if length_input:
                     if length_input == "20":
                         session_length = 20
                     elif length_input != "10":
                         print("Invalid number. Using default: 10.")

            engine.run(offline_mode=offline_mode, custom_questions=custom_questions, session_length=session_length, silent_start=silent_start, level=selected_level)
            
            # Prompt to return to menu
            print("\n" + "-"*40)
            cont = input("Vuoi tornare al menu principale? (s/n) / Back to menu? (y/n): ").strip().lower()
            if cont not in ['s', 'y', 'si', 'yes']:
                print("Arrivederci! / Auf Wiedersehen! 👋")
                break
            print("\n")
        
    except ValueError as e:
        print(f"Initialization Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
