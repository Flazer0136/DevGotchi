import time
import random
from rich.console import Console, Group  # <--- Added Group import
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich import box
from menu_system import MenuState
import os

console = Console(force_terminal=True)

THEME = {
    "bg": "#1a1b26",           
    "border": "#7aa2f7",       
    "tab_active": "#f7768e",   
    "tab_inactive": "#414868",
    "primary": "#7aa2f7",      
    "secondary": "#bb9af7", 
    "text_active": "#1a1b26",  
    "text_normal": "#a9b1d6",  
    "highlight": "#bb9af7",    
    "success": "#9ece6a",      
    "warning": "#e0af68",
    "danger": "#f7768e"
}

def load_sprite_frames(filename):
    """
    Load sprite frames from a text file.
    If file has multiple frames, they're separated by blank lines.
    Returns list of frames.
    """
    try:
        with open(f"pet_sprites/{filename}", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by double newlines (frame separator)
        frames = content.split('\n\n\n\n\n\n')  # Your files use 6 newlines
        
        # Clean up frames (remove extra whitespace)
        frames = [frame.strip() for frame in frames if frame.strip()]
        
        # If only one frame, return it as single-item list
        return frames if frames else [content]
    except:
        # Fallback if file doesn't exist
        return ["???"]


PET_SPRITES = {
    "happy": load_sprite_frames("happy.txt"),
    "normal": load_sprite_frames("normal.txt"),
    "sadness": load_sprite_frames("sadness.txt"),
    "fear": load_sprite_frames("fear.txt"),
    "anger": load_sprite_frames("anger.txt"),
    "regular": load_sprite_frames("regular.txt"),
    "dance": load_sprite_frames("Dance.txt"),
    "sit": load_sprite_frames("sit.txt"),

    "sing": load_sprite_frames("happy.txt"), 
    "feed": load_sprite_frames("normal.txt"),  
    "play": load_sprite_frames("happy.txt"),
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

def get_pet_art(pet, frame_index=0, current_action=None):
    """Get sprite based on pet state or current action."""
    
    # If performing an action, show action sprite (NEVER corrupted)
    if current_action:
        frames = PET_SPRITES.get(current_action, PET_SPRITES.get("normal", ["???"]))
        frame = frames[frame_index % len(frames)]
        return frame  # ✨ Return uncorrupted action sprite
    
    # Choose sprite based on emotional state
    bond = pet.pet_memory["bond_level"]
    corruption = pet.player_memory["file_corruption"]
    
    if corruption > 80:
        frames = PET_SPRITES.get("fear", ["???"])
    elif corruption > 50:
        frames = PET_SPRITES.get("sadness", ["???"])
    elif bond > 70:
        frames = PET_SPRITES.get("happy", ["???"])
    elif bond > 40:
        frames = PET_SPRITES.get("normal", ["???"])
    else:
        frames = PET_SPRITES.get("sadness", ["???"])
    
    # Get current frame
    frame = frames[frame_index % len(frames)]
    
    if frame == "???" and corruption > 30:
        frame = corrupt_text(frame, corruption)
    
    return frame


def create_stats_panel(pet):
    """Create Happy Index panel with 4 stats in vertical list"""
    stats_grid = Table.grid(expand=True, padding=(1, 1))
    stats_grid.add_column(justify="left")
    
    def create_bar_text(emoji, label, value, color):
        blocks_filled = int(value / 10)
        blocks_empty = 10 - blocks_filled
        
        bar = Text()
        bar.append(f"{emoji} {label}\n", style="bold white")
        bar.append("  ")  # Indent
        bar.append("█" * blocks_filled, style=color)
        bar.append("░" * blocks_empty, style="dim white")
        bar.append(f" {int(value)}%", style="dim white")
        return bar
    
    stats_grid.add_row(create_bar_text("😊", "Happiness", pet.stats['happiness'], THEME['success']))
    stats_grid.add_row(Text(""))  # Spacer
    stats_grid.add_row(create_bar_text("💝", "Bond", pet.pet_memory['bond_level'], THEME['warning']))
    stats_grid.add_row(Text(""))  # Spacer
    stats_grid.add_row(create_bar_text("🧠", "Memory", pet.pet_memory['name_clarity'], THEME['success']))
    stats_grid.add_row(Text(""))  # Spacer
    stats_grid.add_row(create_bar_text("📁", "File", 100 - pet.player_memory['file_corruption'], THEME['danger']))
    
    return stats_grid


def create_git_panel(git_info):
    """Create Git Index panel showing commit info"""
    git_table = Table.grid(expand=True, padding=(1, 1))
    git_table.add_column(justify="left")
    
    git_table.add_row(Text(f"📊 Last Commit", style=f"bold {THEME['highlight']}"))
    git_table.add_row(Text(f"  {git_info.get('message', 'N/A')}", style="white"))
    git_table.add_row(Text(""))
    
    git_table.add_row(Text(f"👤 Author", style=f"bold {THEME['highlight']}"))
    git_table.add_row(Text(f"  {git_info.get('author', 'N/A')}", style="white"))
    git_table.add_row(Text(""))
    
    git_table.add_row(Text(f"⏰ Time Ago", style=f"bold {THEME['highlight']}"))
    git_table.add_row(Text(f"  {git_info.get('time_ago', 'N/A')}", style=THEME['warning']))
    git_table.add_row(Text(""))
    
    git_table.add_row(Text(f"📝 Total Commits", style=f"bold {THEME['highlight']}"))
    git_table.add_row(Text(f"  {git_info.get('total', 0)}", style=THEME['success']))
    
    return git_table

def create_game_layout(pet, menu, current_message="", frame_index=0, current_action=None, view_mode="stats", git_info=None):
    """Creates the 'Lip Gloss' style interface with duck left, stats/git right"""
    layout = Layout()
    layout.split_column(
        Layout(name="top", ratio=2),
        Layout(name="bottom", size=10)
    )

    # --- TOP AREA: SPLIT LEFT (DUCK) + RIGHT (STATS/GIT) ---
    layout["top"].split_row(
        Layout(name="duck", ratio=1),
        Layout(name="info", ratio=1)
    )
    
    # === LEFT SIDE: DUCK + MESSAGE ===
    art_str = get_pet_art(pet, frame_index, current_action)
    
    duck_content = Group(
        Text(""),  # Top spacer
        Align.center(Text(art_str, style="bold white", justify="center")),
        Text(""),  # Bottom spacer
        Align.center(Text(current_message if current_message else "", 
                         style=f"bold {THEME['highlight']}", 
                         justify="center"))
    )
    
    layout["duck"].update(
        Panel(
            duck_content,
            title=f"[{THEME['primary']}]Your Pet[/]",
            border_style=THEME["border"],
            box=box.ROUNDED,
            padding=(1, 2)
        )
    )
    
    # === RIGHT SIDE: STATS OR GIT INFO ===
    if view_mode == "git" and git_info:
        # Show Git Index
        info_content = create_git_panel(git_info)
        info_title = f"[{THEME['secondary']}]Git Index[/]"
        info_border = THEME['secondary']
    else:
        # Show Happy Index (default)
        info_content = create_stats_panel(pet)
        info_title = f"[{THEME['success']}]Happy Index[/]"
        info_border = THEME['success']
    
    layout["info"].update(
        Panel(
            info_content,
            title=info_title,
            border_style=info_border,
            box=box.ROUNDED,
            padding=(1, 2)
        )
    )

    # --- BOTTOM AREA: VERTICAL TABS ---
    bottom_grid = Table.grid(expand=True)
    bottom_grid.add_column(width=20) 
    bottom_grid.add_column(ratio=1)  
    
    # Sidebar
    sidebar_content = Table.grid(padding=(1, 1), expand=True)
    
    for i, item in enumerate(menu.main_items):
        is_selected = (menu.state == MenuState.MAIN and i == menu.selected_index)
        
        if is_selected:
            label = Text(f" {item.label.upper()} ", style=f"bold {THEME['text_active']} on {THEME['tab_active']}")
            indicator = Text("● ", style=THEME['tab_active'])
        else:
            label = Text(f" {item.label.upper()} ", style=f"{THEME['text_normal']}")
            indicator = Text("  ")
            
        sidebar_content.add_row(indicator + label)

    # Content Panel
    content_panel = None
    
    # Check which submenu to show
    show_actions = menu.state == MenuState.ACTIONS or (
        menu.state == MenuState.MAIN and 
        menu.main_items[menu.selected_index].label == "Actions"
    )
    
    show_settings = menu.state == MenuState.SETTINGS or (
        menu.state == MenuState.MAIN and 
        menu.main_items[menu.selected_index].label == "Settings"
    )

    if show_actions:
        # Show Actions submenu
        action_table = Table.grid(padding=(0, 2))
        for i, item in enumerate(menu.action_items):
            if menu.state == MenuState.ACTIONS and i == menu.selected_index:
                style = f"bold {THEME['highlight']}"
                prefix = ">"
            else:
                style = "dim white"
                prefix = " "
            action_table.add_row(Text(f"{prefix} {item.label}", style=style))
        content_panel = Panel(action_table, border_style=THEME["tab_inactive"], box=box.MINIMAL)
    
    elif show_settings:
        # Show Settings submenu
        settings_table = Table.grid(padding=(0, 2))
        for i, item in enumerate(menu.settings_items):
            if menu.state == MenuState.SETTINGS and i == menu.selected_index:
                style = f"bold {THEME['highlight']}"
                prefix = ">"
            else:
                style = "dim white"
                prefix = " "
            settings_table.add_row(Text(f"{prefix} {item.label}", style=style))
        content_panel = Panel(settings_table, border_style=THEME["tab_inactive"], box=box.MINIMAL)
        
    elif menu.main_items[menu.selected_index].label == "Exit":
        # Show Exit confirmation
        content_panel = Panel(
            Align.center("[dim]Are you sure you want to leave?\nYour pet will miss you.[/]", vertical="middle"),
            border_style=THEME["tab_inactive"],
            box=box.MINIMAL
        )

    bottom_grid.add_row(
        Panel(sidebar_content, border_style=THEME["border"], box=box.ROUNDED),
        content_panel if content_panel else Panel("", box=box.MINIMAL)
    )

    layout["bottom"].update(bottom_grid)
    return layout