from pet_system.pet_data import Pet
from display import display_pet, display_message, console, COLORS
from git_tracker import is_git_repo, get_commit_info, hours_since_last_commit
from save_system import save_pet, load_pet, calculate_decay_since_last_save
import time
import os


class Game:
    """Main game controller"""
    
    def __init__(self):
        # Show git repo info
        if is_git_repo():
            repo_name = os.path.basename(os.getcwd())
            console.print(f"[dim]Tracking commits in: {repo_name}[/]")
            
            commit_info = get_commit_info()
            if commit_info:
                console.print(f"[dim]Last commit: {commit_info['message']} ({commit_info['time_ago']})[/]\n")
        else:
            console.print(f"[{COLORS['warning']}]⚠️  Not a git repo! Pet won't decay.[/]\n")
        
        # Get owner name
        owner_name = self.get_owner_name()
        
        # ✨ NEW: Load existing pet or create new
        self.pet = load_pet(owner_name=owner_name)
        
        # ✨ NEW: Calculate decay since last session
        hours_away = calculate_decay_since_last_save()
        
        if hours_away > 0.1:  # More than 6 minutes
            console.print(f"\n[{COLORS['warning']}]⏰ You've been away for {hours_away:.1f} hours...[/]")
            
            # Check git commits during that time
            hours_no_commit = hours_since_last_commit()
            
            if hours_no_commit > hours_away:
                # No commits since before you left
                display_message(
                    f"💔 No commits for {hours_no_commit:.1f} hours! Pet's memory is fading...",
                    COLORS['danger']
                )
                # Apply decay for time away
                self.pet.decay_memory(hours_passed=hours_away)
            else:
                # You committed while away!
                display_message(
                    f"✅ You made commits! Pet remembers you better!",
                    COLORS['success']
                )
                # Reward for committing
                self.pet.pet_memory['name_clarity'] = min(100, self.pet.pet_memory['name_clarity'] + 10)
                self.pet.pet_memory['bond_level'] = min(100, self.pet.pet_memory['bond_level'] + 5)
            
            time.sleep(2)
        
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
        
        # ✨ NEW: Auto-save after every command
        self.pet.last_interaction = time.time()
        save_pet(self.pet)
    
    def run(self):
        """Main game loop"""
        while self.running:
            display_pet(self.pet)
            
            console.print(f"\n[bold {COLORS['primary']}]━━━ Actions ━━━[/]")
            console.print(f"[{COLORS['secondary']}]feed[/] | [{COLORS['secondary']}]play[/] | [{COLORS['secondary']}]dance[/] | [{COLORS['secondary']}]sit[/] | [{COLORS['secondary']}]sing[/] | [{COLORS['info']}]status[/] | save | [{COLORS['danger']}]quit[/]")
            
            command = console.input(f"\n[bold {COLORS['secondary']}]>[/] ").strip().lower()
            self.handle_command(command)


if __name__ == "__main__":
    game = Game()
    game.run()
