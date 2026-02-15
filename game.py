import sys
import time
import os
import tty
import termios
from rich.live import Live
from rich.console import Console
from pynput import keyboard

# Local imports
from pet_system.pet_data import Pet
from display import console, create_game_layout
from git_tracker import is_git_repo, hours_since_last_commit
from save_system import save_pet, load_pet
from menu_system import Menu, MenuState


class Game:
    def __init__(self):
        self.running = True
        self.message = "Welcome back!"
        self.message_timer = time.time() + 3
        self.pending_key = None
        
        # ✨ Save terminal settings
        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)
        
        # Load Pet
        if os.path.exists("pet_save.json"):
            self.pet = load_pet()
        else:
            self.pet = load_pet(owner_name="Friend")
            
        self._check_decay()
        
        # Start keyboard listener
        self.listener = keyboard.Listener(on_press=self._on_key_press)
        self.listener.start()

    def _check_decay(self):
        if is_git_repo():
             hours = hours_since_last_commit()
             if hours > 24:
                 self.set_message(f"⚠️ {hours:.0f}h since last commit!", 5)
                 self.pet.decay_memory(hours)

    def set_message(self, text, duration=2):
        self.message = text
        self.message_timer = time.time() + duration
    
    def _on_key_press(self, key):
        """Callback from keyboard listener"""
        try:
            if key == keyboard.Key.up:
                self.pending_key = 'UP'
            elif key == keyboard.Key.down:
                self.pending_key = 'DOWN'
            elif key == keyboard.Key.right:
                self.pending_key = 'RIGHT'
            elif key == keyboard.Key.left:
                self.pending_key = 'LEFT'
            elif key == keyboard.Key.enter:
                self.pending_key = 'ENTER'
            elif hasattr(key, 'char'):
                if key.char == 'q':
                    self.pending_key = 'q'
        except:
            pass

    def handle_command(self, command):
        if command == "quit":
            save_pet(self.pet)
            self.running = False
            self.listener.stop()
        elif command == "feed":
            self.pet.stats['happiness'] = min(100, self.pet.stats['happiness'] + 15)
            self.set_message("🍖 Yummy!", 1.5)
        elif command == "play":
            self.pet.pet_memory['bond_level'] = min(100, self.pet.pet_memory['bond_level'] + 5)
            self.set_message("🎾 So fun!", 1.5)
        elif command == "dance":
            self.set_message("💃 Dancing!", 1.5)
        elif command == "sit":
            self.set_message("🪑 Sitting!", 1.5)
        elif command == "sing":
            self.set_message("🎵 Singing!", 1.5)
    
    def cleanup(self):
        """Restore terminal to normal state"""
        self.listener.stop()
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

    def run(self):
        tty.setcbreak(self.fd)
        console.clear()
        
        menu = Menu()
        frame_index = 0
        loop_count = 0
        current_action = None  # ✨ Track what action is happening
        action_timer = 0       # ✨ When action ends
        
        try:
            with Live(
                create_game_layout(self.pet, menu, self.message, 0, None),  
                auto_refresh=False,
                console=console,
                screen=False,
                refresh_per_second=20
            ) as live:
                while self.running:
                    loop_count += 1
                    
                    # Check if action animation finished
                    if current_action and time.time() > action_timer:
                        current_action = None  # ✨ Stop showing action, return to normal
                    
                    # Animate when message showing OR action playing
                    if (time.time() < self.message_timer or current_action) and loop_count % 3 == 0:
                        frame_index = (frame_index + 1) % 100
                    
                    # Handle key press
                    if self.pending_key:
                        key = self.pending_key
                        self.pending_key = None
                        
                        if key == 'UP':
                            menu.navigate_up()
                        elif key == 'DOWN':
                            menu.navigate_down()
                        elif key == 'RIGHT':
                            menu.navigate_right()
                        elif key == 'LEFT':
                            menu.navigate_left()
                        elif key == 'ENTER':
                            action = menu.select()
                            if action:
                                self.handle_command(action)
                                
                                # ✨ Set action animation
                                if action in ['dance', 'sit', 'sing']:
                                    current_action = action
                                    action_timer = time.time() + 2.0  # 2 seconds
                                    frame_index = 0  # Reset to start of animation
                        elif key == 'q':
                            self.handle_command('quit')
                    
                    # Update display
                    msg = self.message if time.time() < self.message_timer else ""
                    live.update(
                        create_game_layout(self.pet, menu, msg, frame_index, current_action),  # ✨ Pass action
                        refresh=True
                    )
                    
                    time.sleep(0.05)
        
        finally:
            self.cleanup()



if __name__ == "__main__":
    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        game.cleanup()
        print("\nGoodbye!")
