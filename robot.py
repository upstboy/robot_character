from ai_character import AICharacterAgent
import time
from ohbot import ohbot
import random
import threading
import argparse
import sys
import tkinter as tk
from threading import Lock
import queue

class OhbotCharacterAgent(AICharacterAgent):
    """
    OhbotCharacterAgent extends AICharacterAgent to add Ohbot-specific behaviors
    and integrates a fullscreen display for rendering text.
    """
    
    def __init__(self, config_path, debug=False):
        super().__init__(config_path, debug)
        self.motor_enabled = True
        self._is_speaking = False
        self.display_lock = Lock()
        self.display_queue = queue.Queue()  # Queue for GUI updates
        self.root = None
        self.label = None
        
        # Setup display
        self._setup_display()
        self.add_display_callback(self._queue_display)

        # Show intro message
        self._show_intro_message()
        
        # Initialize Ohbot
        print("Initializing Ohbot...")
        ohbot.init()
        self._center_position()
        
        # Start random head movement thread
        self.head_movement_thread = threading.Thread(target=self._random_head_movement, daemon=True)
        self.head_movement_thread.start()
        
        # Add talking animation thread
        self.talking_thread = None

        # Start the GUI update loop
        self._process_queue()

    def _setup_display(self):
        """Setup the fullscreen display for rendering text."""
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.configure(background='black')
        
        # Create label for text
        self.label = tk.Label(
            self.root,
            text="",
            fg='white',
            bg='black',
            wraplength=self.root.winfo_screenwidth() - 40,  # Leave some margin
            justify="center"
        )
        self.label.pack(expand=True)
        
        # Bind escape key to toggle fullscreen
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', True))
        
        # Update the window without blocking
        self.root.update()

    def _show_intro_message(self):
        """Display a welcoming message and list of capabilities."""
        intro_text = (
            "Hi there! I'm your friendly robot buddy.\n"
            "Here are some fun things I can do:\n"
            "- Play trivia\n"
            "- Tell jokes\n"
            "- Read stories\n"
            "- Sing songs\n"
            "- Answer your questions\n"
            "- Describe what I see\n"
            "- Play 'Simon Says'\n"
            "Just say something, and I'll try to respond!"
        )
        self._queue_display(intro_text)


    def _queue_display(self, text):
        """Put display update requests in the queue."""
        self.display_queue.put(text)

    def _process_queue(self):
        """Process the display queue and update the GUI."""
        try:
            if not self.display_queue.empty():
                text = self.display_queue.get()
                self._update_display(text)
        finally:
            # Schedule the next check
            self.root.after(100, self._process_queue)

    def _update_display(self, text):
        """Update the GUI with the given text (must be called on the main thread)."""
        if text:
            # Clear existing text
            self.label.config(text="")
            self.root.update()

            # Start with a large font size and adjust down if needed
            font_size = 100
            self.label.config(font=('Arial', font_size))
            self.label.config(text=text)

            # Adjust font size until text fits
            while (self.label.winfo_reqwidth() > self.root.winfo_width() * 0.9 or
                self.label.winfo_reqheight() > self.root.winfo_height() * 0.9) and font_size > 10:
                font_size -= 5
                self.label.config(font=('Arial', font_size))

            self.root.update()
        else:
            self.label.config(text="")
            self.root.update()

    def _on_speaking_state_changed(self, is_speaking):
        """Override to handle speaking state changes and update display."""
        super()._on_speaking_state_changed(is_speaking)
        self._is_speaking = is_speaking

        if is_speaking:
            # Get the current response being spoken from the character
            current_text = self.character.current_response
            if self.debug:
                print(f"\nPreparing gesture for text: {current_text}")
        
            # Show the text on the display
            self._queue_display(current_text)
        
            # Prepare and execute gesture based on text
            self._prepare_gesture(current_text)
        
            # Start talking animation in a separate thread if not already running
            if self.talking_thread is None or not self.talking_thread.is_alive():
                self.talking_thread = threading.Thread(target=self._animate_talking, daemon=True)
                self.talking_thread.start()
        else:
            self._close_mouth()
            self._is_speaking = False  # Ensure speaking state is properly reset
            self._queue_display("")  # Clear display when not speaking

    def run(self):
        """Override run to handle GUI updates."""
        try:
            super().run()
            self.root.mainloop()  # Start the GUI event loop
        finally:
            if self.root:
                self.root.destroy()

    def stop(self):
        """Override stop to cleanup GUI."""
        super().stop()
        if self.root:
            self.root.quit()

    def _animate_talking(self):
        """Animate mouth while talking."""
        while self._is_speaking:
            try:
                # Randomize mouth opening amount
                top_open = random.uniform(6.5, 8.5)
                bottom_open = random.uniform(6.5, 8.5)
                
                ohbot.move(ohbot.TOPLIP, top_open)
                ohbot.move(ohbot.BOTTOMLIP, bottom_open)
                ohbot.wait(random.uniform(0.15, 0.25))  # Slightly longer wait for smoother animation
                
                closed_pos = random.uniform(4.8, 5.2)
                ohbot.move(ohbot.TOPLIP, closed_pos)
                ohbot.move(ohbot.BOTTOMLIP, closed_pos)
                ohbot.wait(random.uniform(0.1, 0.2))  # Slight pause when closing the mouth
            except Exception as e:
                print(f"Error in talking animation: {e}")
                break

    def _random_head_movement(self):
        """Continuous random head movement thread"""
        while self.running:
            try:
                # Random movement type (0: normal, 1: look around, 2: focused look)
                movement_type = random.choices([0, 1, 2], weights=[0.7, 0.2, 0.1])[0]
                
                if movement_type == 0:  # Normal subtle movements
                    head_turn = random.uniform(4, 6)    # Subtle turn around center position
                    head_nod = random.uniform(4, 6)     # Subtle nod around center position
                    eye_turn = random.uniform(4, 6)     # Subtle eye turn
                    eye_tilt = random.uniform(4, 6)     # Subtle eye tilt
                
                elif movement_type == 1:  # Look around
                    # More extreme movements for "looking around" behavior
                    head_turn = random.uniform(3, 7)
                    eye_turn = head_turn + random.uniform(-1, 1)  # Eyes follow head movement
                    head_nod = random.uniform(3, 7)
                    eye_tilt = head_nod + random.uniform(-1, 1)
                
                else:  # Focused look at something
                    # Eyes move first, then head follows
                    eye_turn = random.uniform(2, 8)
                    eye_tilt = random.uniform(2, 8)
                    ohbot.move(ohbot.EYETURN, eye_turn, 10)
                    ohbot.move(ohbot.EYETILT, eye_tilt, 10)
                    ohbot.wait(0.2)
                    head_turn = eye_turn + random.uniform(-0.5, 0.5)
                    head_nod = eye_tilt + random.uniform(-0.5, 0.5)
                
                # Randomly decide if we should blink
                should_blink = random.random() < 0.3  # 30% chance to blink
                
                # Execute movements
                ohbot.move(ohbot.HEADTURN, head_turn, 2)
                ohbot.move(ohbot.HEADNOD, head_nod, 2)
                ohbot.move(ohbot.EYETURN, eye_turn, 3)  # Slightly faster eye movements
                ohbot.move(ohbot.EYETILT, eye_tilt, 3)
                
                # If blinking, do a quick blink motion
                if should_blink:
                    if self.debug:
                        print("Blinking...")
                    ohbot.move(ohbot.LIDBLINK, 10, 10)  # Close eyes quickly
                    ohbot.wait(0.1)
                    ohbot.move(ohbot.LIDBLINK, 0, 10)   # Open eyes quickly
                
                # Random wait between movements
                if movement_type == 0:
                    time.sleep(random.uniform(1, 3))
                elif movement_type == 1:
                    time.sleep(random.uniform(0.5, 1.5))  # Shorter pauses when looking around
                else:
                    time.sleep(random.uniform(2, 4))  # Longer pauses when focused
                
            except Exception as e:
                print(f"Head movement error: {e}")
                break

    def _prepare_gesture(self, text):
        """Analyze text and prepare appropriate movement sequence"""
        if not text:  # Guard against None or empty text
            return
        
        text = text.lower()
        if self.debug:
            print(f"Analyzing text for gestures: {text}")
        
        # Keywords for different emotions/responses
        agreement_words = ['yes', 'agree', 'correct', 'right', 'absolutely']
        disagreement_words = ['no', 'disagree', 'incorrect', 'wrong']
        thinking_words = ['hmm', 'well', 'let me think', 'perhaps', 'maybe']
        excited_words = ['wow', 'amazing', 'awesome', 'excellent', 'fantastic']
        
        # Check for matches and perform gesture immediately
        if any(word in text for word in agreement_words):
            if self.debug:
                print("Performing agreement gesture")
            self._perform_agreement()
        elif any(word in text for word in disagreement_words):
            if self.debug:
                print("Performing disagreement gesture")
            self._perform_disagreement()
        elif any(word in text for word in thinking_words):
            if self.debug:
                print("Performing thinking gesture")
            self._perform_thinking()
        elif any(word in text for word in excited_words):
            if self.debug:
                print("Performing excited gesture")
            self._perform_excited()

    def _center_position(self):
        """Move all motors to center position"""
        ohbot.move(ohbot.HEADTURN, 5)
        ohbot.move(ohbot.HEADNOD, 5)
        ohbot.move(ohbot.EYETURN, 5)
        ohbot.move(ohbot.EYETILT, 5)
        ohbot.move(ohbot.LIDBLINK, 0)
        ohbot.move(ohbot.TOPLIP, 5)
        ohbot.move(ohbot.BOTTOMLIP, 5)
        ohbot.wait(0.5)

    def _close_mouth(self):
        """Ensure mouth is closed"""
        ohbot.move(ohbot.TOPLIP, 5)
        ohbot.move(ohbot.BOTTOMLIP, 5)
        ohbot.wait(0.1)

    def _perform_agreement(self):
        """Nod head up and down"""
        try:
            ohbot.move(ohbot.HEADNOD, 7)
            ohbot.wait(0.3)
            ohbot.move(ohbot.HEADNOD, 3)
            ohbot.wait(0.3)
            ohbot.move(ohbot.HEADNOD, 5)
        except Exception as e:
            print(f"Error in agreement gesture: {e}")

    def _perform_disagreement(self):
        """Shake head side to side"""
        try:
            ohbot.move(ohbot.HEADTURN, 7)
            ohbot.wait(0.3)
            ohbot.move(ohbot.HEADTURN, 3)
            ohbot.wait(0.3)
            ohbot.move(ohbot.HEADTURN, 5)
        except Exception as e:
            print(f"Error in disagreement gesture: {e}")

    def _perform_thinking(self):
        """Tilt head and look up"""
        try:
            ohbot.move(ohbot.HEADTURN, 6)
            ohbot.move(ohbot.EYETILT, 7)
            ohbot.wait(0.5)
            ohbot.move(ohbot.HEADTURN, 5)
            ohbot.move(ohbot.EYETILT, 5)
        except Exception as e:
            print(f"Error in thinking gesture: {e}")

    def _perform_excited(self):
        """Quick head and eye movements"""
        try:
            ohbot.move(ohbot.HEADNOD, 7)
            ohbot.move(ohbot.EYETILT, 3)
            ohbot.wait(0.2)
            ohbot.move(ohbot.HEADNOD, 4)
            ohbot.move(ohbot.EYETILT, 7)
            ohbot.wait(0.2)
            ohbot.move(ohbot.HEADNOD, 5)
            ohbot.move(ohbot.EYETILT, 5)
        except Exception as e:
            print(f"Error in excited gesture: {e}")

def main():
    parser = argparse.ArgumentParser(description="Runner for AICharacterAgent")
    parser.add_argument("--config", required=True, help="Path to config YAML")
    parser.add_argument("--debug", action="store_true", help="Enable debug")
    args = parser.parse_args()

    agent = OhbotCharacterAgent(args.config, debug=args.debug)
    try:
        agent.run()
    except KeyboardInterrupt:
        agent.stop()
        print("\nStopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
