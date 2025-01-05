from ai_character import AICharacterAgent
import time
from ohbot import ohbot
import random
import threading
import argparse

class OhbotCharacterAgent(AICharacterAgent):
    """
    OhbotCharacterAgent extends AICharacterAgent to add Ohbot-specific behaviors.
    
    Important methods from AICharacterAgent:
    - _on_speaking_state_changed(is_speaking): Override to handle speaking state changes.
    - run(): Override to implement the main interaction loop.
    - stop(): Override to handle cleanup and shutdown.
    
    This class adds methods for animating gestures and head movements specific to the Ohbot robot.
    """
    def __init__(self, config_path, debug=False):
        super().__init__(config_path, debug)
        self.motor_enabled = True
        self._is_speaking = False
        
        # Initialize Ohbot
        print("Initializing Ohbot...")
        ohbot.init()
        self._center_position()
        
        # Start random head movement thread
        self.head_movement_thread = threading.Thread(target=self._random_head_movement, daemon=True)
        self.head_movement_thread.start()
        
        # Add talking animation thread
        self.talking_thread = None

    def _on_speaking_state_changed(self, is_speaking):
        """
        This method is called when the speaking state changes.
        It animates the robot's mouth and head movements based on the current response.
        """

        super()._on_speaking_state_changed(is_speaking)
        self._is_speaking = is_speaking

        if is_speaking:
        
            # Get the current response being spoken from the character
            current_text = self.character.current_response
            if self.debug:
                print(f"\nPreparing gesture for text: {current_text}")
        
            # Prepare and execute gesture based on text
            self._prepare_gesture(current_text)
        
            # Start talking animation in a separate thread
            self.talking_thread = threading.Thread(target=self._animate_talking, daemon=True)
            self.talking_thread.start()
        else:
            self._close_mouth()

    def _animate_talking(self):
        """Animate mouth while talking"""
        while self._is_speaking:
            # Randomize mouth opening amount
            top_open = random.uniform(7, 9)
            bottom_open = random.uniform(7, 9)
            
            ohbot.move(ohbot.TOPLIP, top_open)
            ohbot.move(ohbot.BOTTOMLIP, bottom_open)
            ohbot.wait(random.uniform(0.1, 0.3))
            
            closed_pos = random.uniform(4.5, 5.5)
            ohbot.move(ohbot.TOPLIP, closed_pos)
            ohbot.move(ohbot.BOTTOMLIP, closed_pos)
            ohbot.wait(random.uniform(0.1, 0.25))

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

    def stop(self):
        """Cleanup and shutdown"""
        self.running = False
        if self.motor_enabled:
            self._center_position()
        ohbot.close()
        super().stop()

    def run(self):
        """Run the main interaction loop with robot behaviors"""
        try:
            # Initialize robot position
            self._center_position()
            
            # Use parent class run logic
            super().run()

        except KeyboardInterrupt:
            if self.debug:
                print("\nStopping robot character...")
        finally:
            self.stop()

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    robot = OhbotCharacterAgent(args.config, args.debug)
    try:
        robot.run()
    except KeyboardInterrupt:
        pass
    robot.stop()