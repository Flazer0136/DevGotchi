from pet_system.pet_data import Pet
from display import display_message, console, COLORS, create_main_layout, display_pet_live
from git_tracker import is_git_repo, get_commit_info, hours_since_last_commit
from save_system import save_pet, load_pet, calculate_decay_since_last_save
from rich.live import Live
import time
import os


class Game:
    """Main game controller"""
    
    def __init__(self):
        console.clear()
    
        # Show git repo info
        if is_git_repo():
            repo_name = os.path.basename(os.getcwd())
            console.print(f"[dim]📁 Tracking commits in: {repo_name}[/]")
            
            commit_info = get_commit_info()
            if commit_info:
                console.print(f"[dim]⏰ Last commit: {commit_info['message']} ({commit_info['time_ago']})[/]\n")
        else:
            console.print(f"[{COLORS['warning']}]⚠️  Not a git repo! Pet won't decay.[/]\n")
        
        
        save_exists = os.path.exists("pet_save.json")
        
        if save_exists:
            console.print(f"[{COLORS['info']}]💾 Loading your pet...[/]\n")
            self.pet = load_pet()  
            time.sleep(0.5)
        else:
            owner_name = self.get_owner_name()
            self.pet = load_pet(owner_name=owner_name)  
            
        # Show "away" message and check commits
        hours_away = calculate_decay_since_last_save()

        if save_exists:  
            if hours_away > 0.1:
                console.print(f"\n[{COLORS['warning']}]⏰ You've been away for {hours_away:.1f} hours...[/]")
            
            hours_no_commit = hours_since_last_commit()
            
            if hours_no_commit > hours_away:
                if hours_away > 0.1: 
                    display_message(
                        f"💔 No commits for {hours_no_commit:.1f} hours! Pet's memory is fading...",
                        COLORS['danger']
                    )
                    self.pet.decay_memory(hours_passed=hours_away)
            else:
                display_message(
                    f"✅ You made commits! Pet remembers you better!",
                    COLORS['success']
                )
                self.pet.pet_memory['name_clarity'] = min(100, self.pet.pet_memory['name_clarity'] + 10)
                self.pet.pet_memory['bond_level'] = min(100, self.pet.pet_memory['bond_level'] + 5)
                self.pet.player_memory['file_corruption'] = max(0, self.pet.player_memory['file_corruption'] - 10)
            
            if hours_away > 0.1:  
                console.input(f"\n[dim]Press Enter to continue...[/]")
            
        self.running = True

    
    def get_owner_name(self):
        """Get player's name at start"""
        console.clear()
        console.print(f"[bold {COLORS['primary']}]╔═══ WELCOME TO MEMORY PET ═══╗[/]")
        console.print("\n[cyan]Your pet's memory depends on your git commits![/]")
        console.print("[dim]Commit code to keep your pet's memory alive.[/]\n")
        name = console.input(f"[{COLORS['secondary']}]What's your name?[/] ").strip()
        return name if name else "Friend"
    
    def handle_command(self, command):
        """Process user commands and update pet state"""
        
        if command == "quit" or command == "exit":
            self.running = False
            
            # ✨ NEW: Save before quitting
            display_message("💾 Saving pet...", COLORS['info'])
            if save_pet(self.pet):
                display_message("✅ Pet saved successfully!", COLORS['success'])
            
            # ✨ NEW: Reminder about commits
            hours_no_commit = hours_since_last_commit()
            if hours_no_commit > 12:
                display_message(
                    f"⚠️  Warning: {hours_no_commit:.0f}h since last commit! Make a commit soon!",
                    COLORS['warning']
                )
            
            display_message("👋 Goodbye! Come back soon (and commit code)!", COLORS['primary'])
            return
        
        elif command == "feed":
            self.pet.stats['happiness'] = min(100, self.pet.stats['happiness'] + 15)
            self.pet.stats['health'] = min(100, self.pet.stats['health'] + 10)
            self.pet.stats['hunger'] = max(0, self.pet.stats['hunger'] - 20)
            self.pet.pet_memory['interaction_count'] += 1
            
            self.pet.pet_memory['name_clarity'] = min(100, self.pet.pet_memory['name_clarity'] + 2)
            self.pet.pet_memory['bond_level'] = min(100, self.pet.pet_memory['bond_level'] + 3)
            
            display_message(f"🍖 {self.pet.pet_name} is eating... nom nom! Health restored!", COLORS['success'])
            time.sleep(1.5)
        
        elif command == "play":
            self.pet.stats['happiness'] = min(100, self.pet.stats['happiness'] + 20)
            self.pet.pet_memory['bond_level'] = min(100, self.pet.pet_memory['bond_level'] + 5)
            self.pet.pet_memory['interaction_count'] += 1
            self.pet.pet_memory['name_clarity'] = min(100, self.pet.pet_memory['name_clarity'] + 3)
            
            display_message(f"🎾 {self.pet.pet_name} is playing! So much fun!", COLORS['success'])
            time.sleep(1.5)
        
        elif command == "dance":
            if 'dance' not in self.pet.pet_memory['learned_tricks']:
                self.pet.pet_memory['learned_tricks'].append('dance')
                display_message(f"✨ {self.pet.pet_name} learned to dance!", COLORS['info'])
            else:
                display_message(f"💃 {self.pet.pet_name} dances gracefully!", COLORS['success'])
            
            self.pet.stats['happiness'] = min(100, self.pet.stats['happiness'] + 10)
            self.pet.pet_memory['bond_level'] = min(100, self.pet.pet_memory['bond_level'] + 4)
            self.pet.pet_memory['interaction_count'] += 1
            time.sleep(1.5)
        
        elif command == "sit":
            if 'sit' not in self.pet.pet_memory['learned_tricks']:
                self.pet.pet_memory['learned_tricks'].append('sit')
                display_message(f"✨ {self.pet.pet_name} learned to sit!", COLORS['info'])
            else:
                display_message(f"🪑 {self.pet.pet_name} sits down obediently!", COLORS['success'])
            
            self.pet.pet_memory['interaction_count'] += 1
            time.sleep(1.5)
        
        elif command == "sing":
            if 'sing' not in self.pet.pet_memory['learned_tricks']:
                self.pet.pet_memory['learned_tricks'].append('sing')
                display_message(f"✨ {self.pet.pet_name} learned to sing!", COLORS['info'])
            else:
                display_message(f"🎵 {self.pet.pet_name} sings a beautiful song! ♪♫", COLORS['success'])
            
            self.pet.stats['happiness'] = min(100, self.pet.stats['happiness'] + 15)
            self.pet.pet_memory['interaction_count'] += 1
            time.sleep(1.5)
        
        elif command == "status":
            # ✨ NEW: Show commit info in status
            tricks = ", ".join(self.pet.pet_memory['learned_tricks']) if self.pet.pet_memory['learned_tricks'] else "None yet"
            hours_no_commit = hours_since_last_commit()
            
            display_message(
                f"📊 Interactions: {self.pet.pet_memory['interaction_count']} | Tricks: {tricks}\n"
                f"⏰ Hours since commit: {hours_no_commit:.1f}",
                COLORS['info']
            )
            time.sleep(2)
        
        elif command == "save":
            # ✨ NEW: Manual save command
            display_message("💾 Saving...", COLORS['info'])
            if save_pet(self.pet):
                display_message("✅ Saved!", COLORS['success'])
            time.sleep(1)
        
        elif command == "decay":
            display_message("⏱️  Simulating 10 hours of decay...", COLORS['warning'])
            self.pet.decay_memory(hours_passed=10)
            time.sleep(1)
        
        else:
            display_message("❓ Unknown command! Try: feed, play, dance, sit, sing, status, save, quit", COLORS['danger'])
            time.sleep(1)
        
        self.pet.last_interaction = time.time()
        save_pet(self.pet)
    
    def run(self):
        """Main game loop with Live display"""
        frame_index = 0
        
        while self.running:
            # Create layout
            layout = create_main_layout(self.pet, frame_index)
            
            # Show with Live (redraws in place)
            with Live(layout, console=console, refresh_per_second=1, screen=False) as live:
                # Show animated pet for 2 seconds
                for i in range(8):  # 8 frames = 2 seconds at 4 FPS
                    frame_index += 1
                    layout = create_main_layout(self.pet, frame_index)
                    live.update(layout)
                    time.sleep(0.25)
                
                # Stop animation, get input
                live.stop()
            
            # Show command prompt (outside Live context)
            command = console.input(f"\n[bold {COLORS['secondary']}]>[/] ").strip().lower()
            
            # Handle the command
            self.handle_command(command)
            
            # Brief animation after action
            if command in ['feed', 'play', 'dance', 'sit', 'sing']:
                display_pet_live(self.pet, duration=1.5)  # 1.5 sec celebration animation



if __name__ == "__main__":
    game = Game()
    game.run()
