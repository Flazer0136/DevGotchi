import json
import os
from datetime import datetime
import time

SAVE_FILE = "pet_save.json"

def save_pet(pet):
    """Save pet state to JSON file"""
    save_data = {
        # Pet identity
        "pet_name": pet.pet_name,
        "creation_time": pet.creation_time,
        
        # Pet's memory of owner
        "pet_memory": pet.pet_memory,
        
        # Pet stats
        "stats": pet.stats,
        
        # Player's memory (file corruption)
        "player_memory": pet.player_memory,
        
        # Timestamps
        "last_interaction": pet.last_interaction,
        "last_commit": pet.last_commit,
        "last_save_time": time.time()  # When we saved
    }
    
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(save_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False

def load_pet(owner_name="Friend", pet_name="Buddy"):
    """
    Load pet from save file or create new one.
    Returns: Pet object
    """
    from pet_system.pet_data import Pet
    
    # Check if save exists
    if not os.path.exists(SAVE_FILE):
        # New pet
        return Pet(owner_name=owner_name, pet_name=pet_name)
    
    try:
        with open(SAVE_FILE, 'r') as f:
            save_data = json.load(f)
        
        # Create pet and restore state
        pet = Pet(owner_name=owner_name, pet_name=save_data.get("pet_name", pet_name))
        
        # Restore all data
        pet.creation_time = save_data.get("creation_time", time.time())
        pet.pet_memory = save_data.get("pet_memory", pet.pet_memory)
        pet.stats = save_data.get("stats", pet.stats)
        pet.player_memory = save_data.get("player_memory", pet.player_memory)
        pet.last_interaction = save_data.get("last_interaction", time.time())
        pet.last_commit = save_data.get("last_commit", time.time())
        
        return pet
        
    except Exception as e:
        print(f"Load error: {e}, creating new pet")
        return Pet(owner_name=owner_name, pet_name=pet_name)

def calculate_decay_since_last_save():
    """
    Calculate how many hours passed since last save.
    Returns: float (hours)
    """
    if not os.path.exists(SAVE_FILE):
        return 0.0
    
    try:
        with open(SAVE_FILE, 'r') as f:
            save_data = json.load(f)
        
        last_save = save_data.get("last_save_time", time.time())
        now = time.time()
        hours = (now - last_save) / 3600
        
        return max(0, hours)
    except:
        return 0.0

def delete_save():
    """Delete save file (for testing or pet death)"""
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
        return True
    return False
