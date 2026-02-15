from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.markup import escape
from rich.live import Live
import random
import time

console = Console()

# Color scheme 
COLORS = {
    "primary": "bright_magenta",
    "secondary": "bright_cyan", 
    "success": "bright_green",
    "warning": "bright_yellow",
    "danger": "bright_red",
    "info": "bright_blue"
}

# Base ASCII art 
PET_ART = {
    "happy": [
        """
   /\\_/\\  
  ( ^.^ ) 
   > ^ <
        """,
        """
   /\\_/\\  
  ( ^ω^ ) 
   > ^ <
        """,
        """
   /\\_/\\  
  ( ^.^ ) 
   >   <
        """,
        """
   /\\_/\\  
  ( ^.^ ) 
   > ^ <
        """
    ],
    "neutral": [
        """
   /\\_/\\  
  ( -.- ) 
   > ~ <
        """,
        """
   /\\_/\\  
  ( o.o ) 
   > ~ <
        """
    ],
    "sad": [
        """
   /\\_/\\  
  ( ;_; ) 
   > . <
        """,
        """
   /\\_/\\  
  ( T_T ) 
   > . <
        """
    ],
    "forgotten": [
        """
   / _ \\  
  (  ?  ) 
   >   <
        """
    ]
}


def corrupt_text(text, corruption_level):
    """Corrupt text based on corruption level (0-100)"""
    if corruption_level < 20:
        return text
    
    corrupted = ""
    for char in text:
        if char == ' ' or char == '\n':
            corrupted += char
        elif random.random() < (corruption_level / 200):
            corrupted += random.choice(['?', '█', '▓', '░', '*', '#'])
        else:
            corrupted += char
    return corrupted

def create_progress_bar(value, max_value=100, color="bright_cyan"):
    """Create a visual progress bar"""
    filled = int((value / max_value) * 10)
    empty = 10 - filled
    bar = "█" * filled + "░" * empty
    return f"[{color}]{bar}[/{color}] {int(value)}%"

def get_pet_art(pet):
    """Get ASCII art based on pet's bond level"""
    bond = pet.pet_memory["bond_level"]
    art_quality = pet.player_memory.get("art_quality", 100)
    
    # Choose art based on bond
    if bond > 70:
        art = PET_ART["happy"]
    elif bond > 40:
        art = PET_ART["neutral"]
    elif bond > 10:
        art = PET_ART["sad"]
    else:
        art = PET_ART["forgotten"]
    
    # Corrupt the art based on YOUR memory loss
    corruption = pet.player_memory["file_corruption"]
    if corruption > 30:
        art = corrupt_text(art, corruption)
    
    return art

def display_pet_live(pet, duration=None):
    """
    Display pet with Live updating (no scrollback)
    duration: If None, shows static. If number, animates for that many seconds.
    """
    layout = create_main_layout(pet, frame_index=0)
    
    if duration is None:
        # Static display - just show once
        console.clear()
        console.print(layout)
    else:
        # Animated display
        with Live(layout, console=console, refresh_per_second=4, screen=False) as live:
            frame_index = 0
            start_time = time.time()
            
            while time.time() - start_time < duration:
                frame_index += 1
                layout = create_main_layout(pet, frame_index)
                live.update(layout)
                time.sleep(0.25)  # 4 FPS

def create_main_layout(pet, frame_index=0):
    """Create the full layout (we'll use this for Live updates)"""
    layout = Layout()
    
    # Split into header, main, footer
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    
    # Split main into pet and stats
    layout["main"].split_row(
        Layout(name="pet", ratio=2),
        Layout(name="stats", ratio=1)
    )
    
    # Header
    corruption = pet.player_memory["file_corruption"]
    if corruption > 60:
        title_text = corrupt_text("═══ MEMORY PET ═══", corruption)
        title_style = COLORS['danger']
    else:
        title_text = "═══ MEMORY PET ═══"
        title_style = COLORS['primary']
    
    layout["header"].update(
        Panel(
            Text(title_text, style=f"bold {title_style}", justify="center"),
            style=title_style
        )
    )
    
    # Pet display with animation frame
    pet_art = get_pet_art(pet, frame_index)
    greeting = f"\n🦆 {pet.pet_name} greets: '{pet.get_display_name()}'"
    
    layout["pet"].update(
        Panel(
            Text(pet_art + greeting, style=COLORS['info']),
            title=f"[{COLORS['primary']}]Your Pet[/]",
            border_style=COLORS['primary']
        )
    )
    
    # Stats panel
    layout["stats"].update(create_stats_panel(pet))
    
    # Footer (actions)
    actions = "feed | play | dance | sit | sing | status | save | quit"
    layout["footer"].update(
        Panel(
            Text(actions, style=COLORS['secondary'], justify="center"),
            title=f"[{COLORS['primary']}]Actions[/]",
            style=COLORS['primary']
        )
    )
    
    return layout


def create_stats_panel(pet):
    """Create the stats panel with progress bars"""
    from rich.table import Table
    
    table = Table.grid(padding=(0, 1))
    table.add_column(style=COLORS['info'], width=18)
    table.add_column()
    
    # Stats with progress bars
    table.add_row(
        "😊 Happiness",
        create_progress_bar(pet.stats['happiness'])
    )
    table.add_row(
        "💝 Bond Level",
        create_progress_bar(pet.pet_memory['bond_level'])
    )
    table.add_row(
        "🧠 Memory Clarity",
        create_progress_bar(pet.pet_memory['name_clarity'])
    )
    table.add_row(
        "📁 File Integrity",
        create_progress_bar(100 - pet.player_memory['file_corruption'])
    )
    
    # Add tricks if any
    if pet.pet_memory['learned_tricks']:
        tricks = ", ".join(pet.pet_memory['learned_tricks'])
        table.add_row("", "")  # Spacer
        table.add_row(
            "✨ Tricks",
            Text(tricks, style="dim")
        )
    
    # Check for corruption
    corruption = pet.player_memory['file_corruption']
    
    return Panel(
        table,
        title=f"[{COLORS['secondary']}]Status[/]",
        border_style=COLORS['secondary']
    )

def get_pet_art(pet, frame_index=0):
    """Get animated ASCII art frame"""
    bond = pet.pet_memory["bond_level"]
    corruption = pet.player_memory["file_corruption"]
    
    # Choose animation set based on state
    if corruption > 80:
        frames = PET_ART["forgotten"]
    elif bond > 70:
        frames = PET_ART["happy"]
    elif bond > 40:
        frames = PET_ART["neutral"]
    else:
        frames = PET_ART["sad"]
    
    # Get current frame (cycle through)
    art = frames[frame_index % len(frames)]
    
    # Apply corruption
    if corruption > 30:
        art = corrupt_text(art, corruption)
    
    return art


def display_message(message, style="white"):
    """Show a message to the player"""
    console.print(f"\n[{style}]{message}[/{style}]")

def get_command():
    """Get user input with nice formatting"""
    console.print(f"\n[bold {COLORS['primary']}]Commands:[/] feed | play | status | quit")
    return console.input(f"[bold {COLORS['secondary']}]>[/] ").strip().lower()
