from enum import Enum
import sys
import os

if os.name == 'posix':
    import tty
    import termios
elif os.name == 'nt':
    import msvcrt

class MenuState(Enum):
    MAIN = "main"
    ACTIONS = "actions"
    SETTINGS = "settings"

class MenuItem:
    def __init__(self, label, action=None, submenu=None):
        self.label = label
        self.action = action
        self.submenu = submenu

class Menu:
    def __init__(self):
        self.state = MenuState.MAIN
        self.selected_index = 0
        
        # Main Menu
        self.main_items = [
            MenuItem("Actions", submenu="actions"),
            MenuItem("Settings", submenu="settings"), 
            MenuItem("Exit", action="quit")
        ]
        
        # Actions Tab
        self.action_items = [
            MenuItem("Dance", action="dance"),
            MenuItem("Sit", action="sit"),
            MenuItem("Sing", action="sing"),
            MenuItem("Feed", action="feed"),
            MenuItem("Play", action="play"),
        ]
        self.settings_items = [
            MenuItem("Git Status", action="git_status"),
            MenuItem("Manual Decay", action="decay"),
            MenuItem("Show Stats", action="show_stats"),
        ]
    
    def get_current_items(self):
        if self.state == MenuState.MAIN:
            return self.main_items
        elif self.state == MenuState.ACTIONS:
            return self.action_items
        elif self.state == MenuState.SETTINGS:  # ✨ Add this
            return self.settings_items
        return []

    
    def navigate_up(self):
        items = self.get_current_items()
        self.selected_index = (self.selected_index - 1) % len(items)
    
    def navigate_down(self):
        items = self.get_current_items()
        self.selected_index = (self.selected_index + 1) % len(items)


    def navigate_left(self):
        """Go back to the sidebar"""
        if self.state == MenuState.ACTIONS:
            self.state = MenuState.MAIN
            self.selected_index = 0  
        elif self.state == MenuState.SETTINGS: 
            self.state = MenuState.MAIN
            self.selected_index = 1 


    def navigate_right(self):
        """Enter the tab if selected item has submenu"""
        items = self.get_current_items()
        selected = items[self.selected_index]
        
        if selected.submenu == "actions":
            self.state = MenuState.ACTIONS
            self.selected_index = 0
        elif selected.submenu == "settings":  # ✨ Add this
            self.state = MenuState.SETTINGS
            self.selected_index = 0

    def select(self):
        """Handle Enter key"""
        items = self.get_current_items()
        selected = items[self.selected_index]
        
        # Open submenus
        if selected.submenu == "actions":
            self.state = MenuState.ACTIONS
            self.selected_index = 0
            return None
        elif selected.submenu == "settings":  # ✨ Add this
            self.state = MenuState.SETTINGS
            self.selected_index = 0
            return None
        else:
            return selected.action


    def is_actions_open(self):
        return self.state == MenuState.ACTIONS

def get_key():
    if os.name == 'nt':
        key = msvcrt.getch()
        if key == b'\xe0':
            key = msvcrt.getch()
            if key == b'H': return 'UP'
            elif key == b'P': return 'DOWN'
            elif key == b'M': return 'RIGHT'
            elif key == b'K': return 'LEFT'
        try:
            return key.decode('utf-8')
        except:
            return '?'
        
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return 'UP'
                    elif ch3 == 'B': return 'DOWN'
                    elif ch3 == 'C': return 'RIGHT'
                    elif ch3 == 'D': return 'LEFT'
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)