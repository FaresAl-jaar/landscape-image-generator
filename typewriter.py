import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import sys
import time
import random
import threading
from typing import Optional, Callable
import json

# Try to import optional dependencies
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    pyautogui.FAILSAFE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False


class TypingConfig:
    """Configuration class for typing behavior"""
    def __init__(self):
        self.switch_window_delay = 10
        self.mistake_probability = 0.01
        self.break_probability = 0.008
        self.break_durations = [8, 15, 25, 40]
        self.min_typing_delay = 0.08
        self.max_typing_delay = 0.25
        self.long_break_probability = 0.003
        self.long_break_durations = [60, 90, 120]
        
    def to_dict(self):
        return {
            'switch_window_delay': self.switch_window_delay,
            'mistake_probability': self.mistake_probability,
            'break_probability': self.break_probability,
            'break_durations': self.break_durations,
            'min_typing_delay': self.min_typing_delay,
            'max_typing_delay': self.max_typing_delay,
            'long_break_probability': self.long_break_probability,
            'long_break_durations': self.long_break_durations
        }
    
    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class AutoTyper:
    """Handles the auto-typing functionality"""
    
    def __init__(self, config: TypingConfig, logger: Callable[[str, str], None]):
        self.config = config
        self.logger = logger
        self.is_active = False
        self.is_paused = False
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set() # Initially unpaused
        self.typing_thread: Optional[threading.Thread] = None
        
        # Keyboard layout mistakes for realistic typing
        # This dictionary maps a character to a list of characters that are often
        # mistakenly typed instead due to their proximity on a QWERTY keyboard.
        self.keyboard_mistakes = {
            'a': ['s', 'q', 'w'], 's': ['a', 'd', 'w', 'e'],
            'd': ['s', 'f', 'e', 'r'], 'f': ['d', 'g', 'r', 't'],
            'g': ['f', 'h', 't', 'y'], 'h': ['g', 'j', 'y', 'u'],
            'j': ['h', 'k', 'u', 'i'], 'k': ['j', 'l', 'i', 'o'],
            'l': ['k', 'o', 'p'], 'q': ['a', 'w'], 'w': ['q', 'e', 'a', 's'],
            'e': ['w', 'r', 's', 'd'], 'r': ['e', 't', 'd', 'f'],
            't': ['r', 'y', 'f', 'g'], 'y': ['t', 'u', 'g', 'h'],
            'u': ['y', 'i', 'h', 'j'], 'i': ['u', 'o', 'j', 'k'],
            'o': ['i', 'p', 'k', 'l'], 'p': ['o', 'l'],
            'z': ['x'], 'x': ['z', 'c'], 'c': ['x', 'v'],
            'v': ['c', 'b'], 'b': ['v', 'n'], 'n': ['b', 'm'],
            'm': ['n']
        }
    
    def start_typing(self, text: str, delay_seconds: int = 10):
        """
        Starts the auto-typing process with an initial countdown delay.
        Checks for pyautogui availability and ensures no typing is already active.
        """
        if not PYAUTOGUI_AVAILABLE:
            self.logger("PyAutoGUI not available. Please install: pip install pyautogui", "error")
            return False
            
        if self.is_active:
            self.logger("Auto-typing is already active.", "status")
            return False
            
        if not text.strip():
            self.logger("No content to type.", "error")
            return False
            
        self.is_active = True
        self.stop_event.clear()
        self.pause_event.set() # Ensure not paused at start
        self.is_paused = False
        
        # Create and start a new thread for typing to keep the GUI responsive
        self.typing_thread = threading.Thread(
            target=self._countdown_and_type, 
            args=(text, delay_seconds)
        )
        self.typing_thread.daemon = True # Allow the thread to exit with the main program
        self.typing_thread.start()
        return True
    
    def stop_typing(self):
        """
        Signals the typing thread to stop gracefully.
        Unblocks the pause event if it was set, ensuring the thread can check stop_event.
        """
        if self.is_active:
            self.stop_event.set()
            self.pause_event.set()  # Unblock if paused to allow the thread to terminate
            self.is_active = False
            self.logger("Auto-typing stopped.", "status")
    
    def toggle_pause(self):
        """
        Toggles the pause state of the auto-typing.
        If typing is active, it pauses or resumes the process.
        """
        if not self.is_active:
            return False
            
        if self.is_paused:
            self.is_paused = False
            self.pause_event.set() # Set the event to unblock the thread
            self.logger("Typing resumed.", "status")
        else:
            self.is_paused = True
            self.pause_event.clear() # Clear the event to block the thread
            self.logger("Typing paused.", "status")
        return True
    
    def _countdown_and_type(self, text: str, delay_seconds: int):
        """
        Manages the initial countdown before calling the typing simulation.
        Handles exceptions like pyautogui's FailSafe.
        """
        try:
            # Countdown loop
            for i in range(delay_seconds, 0, -1):
                self.logger(f"⏰ {i} seconds remaining...", "countdown")
                time.sleep(1)
                if self.stop_event.is_set():
                    self.logger("Auto-typing cancelled during countdown.", "error")
                    return
            
            self.logger("🚀 Starting auto-typing!", "highlight")
            self._simulate_typing(text)
            self.logger("✅ Auto-typing completed!", "success")
            
        except Exception as e:
            # Catch pyautogui's failsafe exception or other errors
            if "FailSafe" in str(e):
                self.logger("🛑 Emergency stop activated (mouse in corner).", "error")
            else:
                self.logger(f"❌ Error during typing: {e}", "error")
        finally:
            # Ensure is_active is reset regardless of how the thread finishes
            self.is_active = False
    
    def _simulate_typing(self, text: str):
        """
        Simulates human-like typing by iterating through characters,
        introducing delays, mistakes, and breaks based on configured probabilities.
        This version correctly handles newlines and tabs as key presses.
        """
        line_count = 0
        char_count = 0
        
        for char_index, char in enumerate(text):
            # Check for stop signal at the beginning of each character iteration
            if self.stop_event.is_set():
                break
            
            # Handle pause state
            if self.is_paused:
                self.logger("⏸️ Typing paused.", "status")
                self.pause_event.wait() # Block until pause_event is set (resumed)
                if self.stop_event.is_set():
                    break # Check stop signal again after resuming
                self.logger("▶️ Typing resumed.", "status")
            
            # Count lines for progress reporting
            if char == '\n':
                line_count += 1
            
            # Simulate typing mistakes or type character
            if random.random() < self.config.mistake_probability and char.isalnum(): # Only make mistakes on alphanumeric characters
                self._make_mistake(char)
            else:
                # IMPORTANT: Handle newlines and tabs as key presses
                if char == '\n':
                    pyautogui.press('enter')
                elif char == '\t':
                    pyautogui.press('tab')
                else:
                    pyautogui.write(char) # Type the character using pyautogui
            
            char_count += 1
            
            # Introduce a random delay between characters to mimic human typing speed
            time.sleep(random.uniform(
                self.config.min_typing_delay, 
                self.config.max_typing_delay
            ))
            
            # Provide progress updates periodically
            if char_count % 100 == 0:
                progress = (char_index / len(text)) * 100
                self.logger(f"📊 Progress: {progress:.1f}% ({line_count} lines)", "status")
            
            # Introduce short random breaks
            if (random.random() < self.config.break_probability and 
                char_index < len(text) - 1):
                self._take_break()
                if self.stop_event.is_set():
                    break
            
            # Introduce long random breaks (less frequent)
            elif (random.random() < self.config.long_break_probability and 
                  char_index < len(text) - 1):
                self._take_long_break()
                if self.stop_event.is_set():
                    break
    
    def _make_mistake(self, correct_char: str):
        """
        Simulates typing a wrong character, backspacing, and then typing the correct one.
        Uses `keyboard_mistakes` for realistic errors.
        """
        if correct_char.lower() in self.keyboard_mistakes:
            wrong_char = random.choice(self.keyboard_mistakes[correct_char.lower()])
            if correct_char.isupper(): # Preserve case for the wrong character
                wrong_char = wrong_char.upper()
            pyautogui.write(wrong_char) # Type the wrong character
            time.sleep(random.uniform(0.1, 0.3)) # Small delay before correcting
            pyautogui.press('backspace') # Backspace the wrong character
            time.sleep(random.uniform(0.05, 0.15)) # Small delay after backspace
            self.logger(f"Fixed typo: {wrong_char} → {correct_char}", "mistake")
        
        pyautogui.write(correct_char) # Type the correct character
    
    def _take_break(self):
        """Simulates a short typing break."""
        duration = random.choice(self.config.break_durations)
        self.logger(f"☕ Taking a {duration}s break", "break")
        self._sleep_with_checks(duration) # Use special sleep to allow stopping/pausing
        if not self.stop_event.is_set():
            self.logger("💻 Back to typing...", "break")
    
    def _take_long_break(self):
        """Simulates a longer typing break."""
        duration = random.choice(self.config.long_break_durations)
        self.logger(f"🚶 Long break ({duration//60}m {duration%60}s)", "break")
        self._sleep_with_checks(duration) # Use special sleep to allow stopping/pausing
        if not self.stop_event.is_set():
            self.logger("🎯 Refreshed and back to work!", "break")
    
    def _sleep_with_checks(self, duration: int):
        """
        Custom sleep function that checks for stop and pause events every second.
        This allows for responsive stopping/pausing during long breaks.
        """
        for _ in range(duration):
            if self.stop_event.is_set():
                break
            if self.is_paused:
                self.pause_event.wait() # Block until resumed
                if self.stop_event.is_set():
                    break
            time.sleep(1)


class PythonFileEditor:
    """Main application class for the Python Auto-Typer GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Python Auto-Typer - Enhanced Edition")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Application state variables
        self.current_file: Optional[str] = None
        self.file_modified = False
        
        # Configuration for typing behavior
        self.config = TypingConfig()
        self.config_file = "typer_config.json"
        self._load_config() # Load settings from file on startup
        
        # Auto-typer instance, passing the configuration and logger function
        self.auto_typer = AutoTyper(self.config, self._log_message)
        
        # Flag for global hotkeys availability
        self.hotkeys_active = False
        
        # Initialize GUI components
        self._setup_style()
        self._create_gui()
        self._create_menu()
        self._setup_hotkeys()
        
        # Bind the window closing protocol to a custom handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Check for required external dependencies (pyautogui, keyboard)
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Checks if pyautogui and keyboard packages are installed and warns the user."""
        missing = []
        if not PYAUTOGUI_AVAILABLE:
            missing.append("pyautogui")
        if not KEYBOARD_AVAILABLE:
            missing.append("keyboard")
        
        if missing:
            deps = ", ".join(missing)
            self._log_message(f"Missing optional dependencies: {deps}", "error")
            self._log_message(f"Install with: pip install {deps}", "status")
    
    def _load_config(self):
        """Loads typing configuration from a JSON file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                self.config.from_dict(data)
        except Exception as e:
            # Print to console for debugging, as messagebox might not be ideal at init
            print(f"Failed to load config: {e}")
    
    def _save_config(self):
        """Saves current typing configuration to a JSON file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def _setup_style(self):
        """Configures the visual style of the Tkinter application."""
        style = ttk.Style()
        try:
            style.theme_use('clam') # Use 'clam' theme for a more modern look
        except:
            pass  # Fallback to default if 'clam' theme is not available
    
    def _setup_hotkeys(self):
        """Sets up global hotkeys for stopping and pausing the auto-typer."""
        if not KEYBOARD_AVAILABLE:
            self._log_message("Global hotkeys not available (keyboard package missing)", "error")
            return
            
        try:
            # Bind Ctrl+Shift+Q to emergency stop
            keyboard.add_hotkey('ctrl+shift+q', self._emergency_stop)
            # Bind Ctrl+Shift+P to toggle pause
            keyboard.add_hotkey('ctrl+shift+p', self._toggle_pause)
            self.hotkeys_active = True
            self._log_message("Global hotkeys: Ctrl+Shift+Q (stop), Ctrl+Shift+P (pause)", "status")
        except Exception as e:
            self._log_message(f"Failed to setup hotkeys: {e}", "error")
    
    def _emergency_stop(self):
        """Handler for the emergency stop hotkey."""
        self.auto_typer.stop_typing()
        self._update_button_states() # Update UI buttons
    
    def _toggle_pause(self):
        """Handler for the toggle pause hotkey and button."""
        if self.auto_typer.toggle_pause():
            self._update_pause_button() # Update the pause button text/state
    
    def _create_menu(self):
        """Creates the application's menu bar with File, Edit, and Auto-Type options."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open File...", command=self._open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self._save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="New File", command=self._new_file, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=lambda: self.text_editor.edit_undo(), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=lambda: self.text_editor.edit_redo(), accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.text_editor.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=lambda: self.text_editor.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=lambda: self.text_editor.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=lambda: self.text_editor.tag_add("sel", "1.0", "end"), accelerator="Ctrl+A")
        
        # Auto-Type menu
        type_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Auto-Type", menu=type_menu)
        type_menu.add_command(label="Start (10s delay)", command=self._start_typing, accelerator="F5")
        type_menu.add_command(label="Quick Start (3s)", command=self._quick_start, accelerator="F6")
        type_menu.add_command(label="Pause/Resume", command=self._toggle_pause, accelerator="Ctrl+Shift+P")
        type_menu.add_command(label="Stop", command=self._stop_typing, accelerator="Ctrl+Shift+Q")
        type_menu.add_separator()
        type_menu.add_command(label="Settings...", command=self._show_settings)
        
        # Bind shortcuts to root window events
        self.root.bind("<Control-o>", lambda e: self._open_file())
        self.root.bind("<Control-s>", lambda e: self._save_file())
        self.root.bind("<Control-Shift-S>", lambda e: self._save_as_file())
        self.root.bind("<Control-n>", lambda e: self._new_file())
        self.root.bind("<F5>", lambda e: self._start_typing())
        self.root.bind("<F6>", lambda e: self._quick_start())
    
    def _create_gui(self, ):
        """Creates the main frame and all sub-widgets of the application GUI."""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create toolbar at the top
        self._create_toolbar(main_frame)
        
        # Create text editor in the middle
        self._create_text_editor(main_frame)
        
        # Create status area below the editor
        self._create_status_area(main_frame)
        
        # Create status bar at the bottom
        self._create_status_bar(main_frame)
    
    def _create_toolbar(self, parent):
        """Creates the toolbar containing file operations and auto-typing controls."""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File operations section
        file_frame = ttk.LabelFrame(toolbar_frame, text="File Operations", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 5))
        
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill=tk.X)
        
        # File operation buttons
        ttk.Button(button_frame, text="📁 Open", command=self._open_file, width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="💾 Save", command=self._save_file, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Save As", command=self._save_as_file, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📄 New", command=self._new_file, width=12).pack(side=tk.LEFT, padx=5)
        
        # Label to display the current file name
        self.file_label = ttk.Label(file_frame, text="No file selected", font=('Arial', 10, 'italic'))
        self.file_label.pack(anchor=tk.W, pady=(10, 0))
        
        # Auto-typing controls section
        typing_frame = ttk.LabelFrame(toolbar_frame, text="Auto-Typing Controls", padding="10")
        typing_frame.pack(fill=tk.X, pady=(5, 0))
        
        button_frame2 = ttk.Frame(typing_frame)
        button_frame2.pack(fill=tk.X)
        
        # Auto-typing control buttons
        self.start_button = ttk.Button(button_frame2, text="🎯 Start (10s)", command=self._start_typing, width=15)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.quick_button = ttk.Button(button_frame2, text="⚡ Quick (3s)", command=self._quick_start, width=15)
        self.quick_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = ttk.Button(button_frame2, text="⏸️ Pause", command=self._toggle_pause, width=15, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame2, text="🛑 Stop", command=self._stop_typing, width=15, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame2, text="⚙️ Settings", command=self._show_settings, width=15).pack(side=tk.LEFT, padx=5)
    
    def _create_text_editor(self, parent):
        """Creates the scrolled text editor with line numbers."""
        editor_frame = ttk.LabelFrame(parent, text="Python Code Editor", padding="10")
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        text_frame = ttk.Frame(editor_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers widget
        self.line_numbers = tk.Text(text_frame, width=5, padx=3, takefocus=0,
                                     border=0, state='disabled', wrap='none',
                                     font=('Courier New', 11))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Main text editor widget
        self.text_editor = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.NONE, # No word wrapping
            font=('Courier New', 11),
            undo=True, # Enable undo/redo
            maxundo=50, # Limit undo history
            tabs=('1c', '2c', '3c', '4c') # Set tab stops for proper indentation
        )
        self.text_editor.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Bind events to update line numbers and handle scrolling
        self.text_editor.bind('<KeyPress>', self._on_text_change)
        self.text_editor.bind('<KeyRelease>', self._update_line_numbers)
        self.text_editor.bind('<Button-1>', self._update_line_numbers)
        self.text_editor.bind('<MouseWheel>', self._on_mousewheel)
        
        self._update_line_numbers() # Initial update of line numbers
    
    def _create_status_area(self, parent):
        """Creates the scrolled text area for displaying auto-typing status and logs."""
        status_frame = ttk.LabelFrame(parent, text="Auto-Typing Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_text = scrolledtext.ScrolledText(
            status_frame, 
            height=6, # Set initial height
            font=('Courier New', 10),
            state=tk.DISABLED # Make it read-only
        )
        self.status_text.pack(fill=tk.X)
        
        # Configure various tags for colored and styled messages
        tags = {
            'countdown': {'foreground': 'blue', 'font': ('Courier New', 10, 'bold')},
            'highlight': {'foreground': 'darkgreen', 'font': ('Courier New', 10, 'bold')},
            'success': {'foreground': 'green', 'font': ('Courier New', 10, 'bold')},
            'error': {'foreground': 'red', 'font': ('Courier New', 10, 'bold')},
            'status': {'foreground': 'purple', 'font': ('Courier New', 10, 'italic')},
            'mistake': {'foreground': 'orange'},
            'break': {'foreground': 'brown'}
        }
        
        for tag, config in tags.items():
            self.status_text.tag_config(tag, **config)
    
    def _create_status_bar(self, parent):
        """Creates the status bar at the bottom of the window."""
        self.status_frame = ttk.Frame(parent)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.cursor_label = ttk.Label(self.status_frame, text="Line: 1, Col: 1", relief=tk.SUNKEN)
        self.cursor_label.pack(side=tk.RIGHT)
        
        # Bind events to update cursor position
        self.text_editor.bind('<KeyRelease>', self._update_cursor_position)
        self.text_editor.bind('<Button-1>', self._update_cursor_position)
    
    def _on_mousewheel(self, event):
        """Synchronizes scrolling between the text editor and line numbers."""
        self.line_numbers.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _update_line_numbers(self, event=None):
        """Updates the line numbers display based on the content of the text editor."""
        self.line_numbers.config(state='normal') # Enable editing to update
        self.line_numbers.delete('1.0', tk.END) # Clear existing numbers
        
        # Get total number of lines in the editor
        lines = int(self.text_editor.index('end-1c').split('.')[0])
        # Generate line numbers string
        line_numbers_text = '\n'.join(str(i) for i in range(1, lines + 1))
        self.line_numbers.insert('1.0', line_numbers_text) # Insert new numbers
        
        self.line_numbers.config(state='disabled') # Disable editing again
        # Sync line numbers scroll with editor scroll
        self.line_numbers.yview_moveto(self.text_editor.yview()[0])
    
    def _update_cursor_position(self, event=None):
        """Updates the status bar with the current line and column of the cursor."""
        cursor_pos = self.text_editor.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        self.cursor_label.config(text=f"Line: {line}, Col: {int(col) + 1}")
    
    def _on_text_change(self, event=None):
        """Marks the file as modified when text content changes."""
        if not self.file_modified:
            self.file_modified = True
            self._update_title() # Add '*' to title to indicate modification
        self._update_status("Modified")
    
    def _update_title(self):
        """Updates the window title to reflect current file and modification status."""
        title = "Python Auto-Typer - Enhanced Edition"
        if self.current_file:
            filename = os.path.basename(self.current_file)
            title = f"{filename} - {title}"
            if self.file_modified:
                title = f"*{title}" # Add asterisk if modified
        self.root.title(title)
    
    def _update_status(self, message):
        """Updates the main status bar label."""
        self.status_label.config(text=message)
    
    def _log_message(self, message, tag=None):
        """
        Logs a message to the status scrolled text area.
        Messages can be tagged for different colors/styles.
        """
        self.status_text.config(state=tk.NORMAL) # Enable to insert text
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.status_text.see(tk.END) # Scroll to the end
        self.status_text.config(state=tk.DISABLED) # Disable again
    
    # --- File operations ---
    def _open_file(self):
        """Opens a file and loads its content into the text editor."""
        if self.file_modified and not self._ask_save_changes():
            return # User chose not to save or cancelled
            
        file_path = filedialog.askopenfilename(
            title="Open Python File",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                self.text_editor.delete('1.0', tk.END) # Clear editor
                self.text_editor.insert('1.0', content) # Insert new content
                
                self.current_file = file_path
                self.file_modified = False # Reset modified flag
                
                self.file_label.config(text=f"File: {os.path.basename(file_path)}")
                self._update_title()
                self._update_status(f"Opened: {os.path.basename(file_path)}")
                self._update_line_numbers() # Update line numbers for new content
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")
    
    def _save_file(self):
        """Saves the current content to the current file. If no file is open, calls save-as."""
        if not self.current_file:
            self._save_as_file()
            return
            
        try:
            content = self.text_editor.get('1.0', tk.END + '-1c') # Get all text except trailing newline
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(content)
            
            self.file_modified = False # Clear modified flag after saving
            self._update_title()
            self._update_status(f"Saved: {os.path.basename(self.current_file)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
    
    def _save_as_file(self):
        """Prompts user for a new file name and saves the content."""
        file_path = filedialog.asksaveasfilename(
            title="Save Python File As",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            defaultextension=".py" # Default to .py extension
        )
        
        if file_path:
            try:
                content = self.text_editor.get('1.0', tk.END + '-1c')
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                self.current_file = file_path
                self.file_modified = False
                
                self.file_label.config(text=f"File: {os.path.basename(file_path)}")
                self._update_title()
                self._update_status(f"Saved as: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
    
    def _new_file(self):
        """Clears the editor and resets file state to create a new, unsaved file."""
        if self.file_modified and not self._ask_save_changes():
            return # User chose not to save or cancelled
            
        self.text_editor.delete('1.0', tk.END)
        self.current_file = None
        self.file_modified = False
        
        self.file_label.config(text="No file selected")
        self._update_title()
        self._update_status("New file created")
        self._update_line_numbers()
    
    def _ask_save_changes(self) -> bool:
        """
        Asks the user if they want to save changes before closing or opening a new file.
        Returns True if the user proceeds (saves or discards), False if cancelled.
        """
        if self.file_modified:
            result = messagebox.askyesnocancel(
                "Save Changes?",
                "You have unsaved changes. Do you want to save them before proceeding?"
            )
            if result is True:
                self._save_file()
                return not self.file_modified # If save failed, self.file_modified will still be True
            elif result is False:
                return True # Discard changes
            else:
                return False # Cancel operation
        return True # No changes to save
        
    # --- Auto-typing controls ---
    def _start_typing(self):
        """Initiates auto-typing with a 10-second delay."""
        text_content = self.text_editor.get('1.0', tk.END + '-1c')
        if self.auto_typer.start_typing(text_content, self.config.switch_window_delay):
            self._update_button_states()
    
    def _quick_start(self):
        """Initiates auto-typing with a shorter 3-second delay."""
        text_content = self.text_editor.get('1.0', tk.END + '-1c')
        if self.auto_typer.start_typing(text_content, 3): # 3 second delay for quick start
            self._update_button_states()
            
    def _stop_typing(self):
        """Stops the active auto-typing process."""
        self.auto_typer.stop_typing()
        self._update_button_states()
        
    def _update_button_states(self):
        """Updates the enabled/disabled state of control buttons based on auto-typer's activity."""
        is_active = self.auto_typer.is_active
        is_paused = self.auto_typer.is_paused
        
        self.start_button.config(state=tk.DISABLED if is_active else tk.NORMAL)
        self.quick_button.config(state=tk.DISABLED if is_active else tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL if is_active else tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL if is_active else tk.DISABLED)
        
        self._update_pause_button() # Ensure pause button text is correct
        
    def _update_pause_button(self):
        """Updates the text of the pause/resume button."""
        if self.auto_typer.is_paused:
            self.pause_button.config(text="▶️ Resume")
        else:
            self.pause_button.config(text="⏸️ Pause")

    def _show_settings(self):
        """Opens a new window for configuring typing parameters."""
        settings_window = self._SettingsWindow(self.root, self.config, self._save_config)
        self.root.wait_window(settings_window.top) # Wait for settings window to close
        # After settings window closes, ensure config is re-applied to auto_typer
        self.auto_typer.config = self.config

    def _on_closing(self):
        """Handles the application closing event, prompting to save unsaved changes."""
        if self.file_modified:
            if not self._ask_save_changes():
                return # User cancelled closing
        
        # Clean up hotkeys if they were active
        if self.hotkeys_active and KEYBOARD_AVAILABLE:
            try:
                keyboard.unhook_all_hotkeys()
            except Exception as e:
                print(f"Error unhooking hotkeys: {e}")

        # Stop any active typing threads
        self.auto_typer.stop_typing()
        self.root.destroy() # Close the main window


    class _SettingsWindow:
        """A Toplevel window for configuring auto-typing settings."""
        def __init__(self, parent, config: TypingConfig, save_callback: Callable[[ ], None]):
            self.config = config
            self.save_callback = save_callback
            
            self.top = tk.Toplevel(parent)
            self.top.title("Auto-Typer Settings")
            self.top.transient(parent) # Make it appear on top of the parent
            self.top.grab_set() # Make it modal
            self.top.resizable(False, False) # Disable resizing
            
            # Use a frame for padding and structure
            frame = ttk.Frame(self.top, padding="15")
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Variables to hold setting values
            self.switch_window_delay_var = tk.IntVar(value=self.config.switch_window_delay)
            self.mistake_probability_var = tk.DoubleVar(value=self.config.mistake_probability)
            self.break_probability_var = tk.DoubleVar(value=self.config.break_probability)
            self.min_typing_delay_var = tk.DoubleVar(value=self.config.min_typing_delay)
            self.max_typing_delay_var = tk.DoubleVar(value=self.config.max_typing_delay)
            self.long_break_probability_var = tk.DoubleVar(value=self.config.long_break_probability)

            # Create entry fields for each setting
            self._create_setting_row(frame, "Switch Window Delay (s):", self.switch_window_delay_var, 
                                     tk.Entry, {"width": 8})
            self._create_setting_row(frame, "Mistake Probability (0-1):", self.mistake_probability_var, 
                                     tk.Entry, {"width": 8})
            self._create_setting_row(frame, "Break Probability (0-1):", self.break_probability_var, 
                                     tk.Entry, {"width": 8})
            self._create_setting_row(frame, "Min Typing Delay (s):", self.min_typing_delay_var, 
                                     tk.Entry, {"width": 8})
            self._create_setting_row(frame, "Max Typing Delay (s):", self.max_typing_delay_var, 
                                     tk.Entry, {"width": 8})
            self._create_setting_row(frame, "Long Break Probability (0-1):", self.long_break_probability_var, 
                                     tk.Entry, {"width": 8})

            # Break durations (represented as a string for easy editing)
            tk.Label(frame, text="Short Break Durations (s, comma-separated):").grid(row=6, column=0, sticky=tk.W, pady=5)
            self.break_durations_entry = ttk.Entry(frame, width=30)
            self.break_durations_entry.insert(0, ', '.join(map(str, self.config.break_durations)))
            self.break_durations_entry.grid(row=6, column=1, sticky=tk.W, pady=5)

            tk.Label(frame, text="Long Break Durations (s, comma-separated):").grid(row=7, column=0, sticky=tk.W, pady=5)
            self.long_break_durations_entry = ttk.Entry(frame, width=30)
            self.long_break_durations_entry.insert(0, ', '.join(map(str, self.config.long_break_durations)))
            self.long_break_durations_entry.grid(row=7, column=1, sticky=tk.W, pady=5)
            
            # Buttons frame
            button_frame = ttk.Frame(frame)
            button_frame.grid(row=8, columnspan=2, pady=15)
            
            ttk.Button(button_frame, text="Save", command=self._apply_settings).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT, padx=5)
            
            # Center the window on the screen
            self.top.update_idletasks()
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.top.winfo_width() // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.top.winfo_height() // 2)
            self.top.geometry(f"+{x}+{y}")

            self.top.protocol("WM_DELETE_WINDOW", self.top.destroy) # Handle window close button
            
        def _create_setting_row(self, parent_frame, label_text, tk_var, widget_type, widget_options):
            """Helper to create a label and an input widget for a setting."""
            row_num = parent_frame.grid_size()[1] # Get next available row
            ttk.Label(parent_frame, text=label_text).grid(row=row_num, column=0, sticky=tk.W, pady=5)
            widget = widget_type(parent_frame, textvariable=tk_var, **widget_options)
            widget.grid(row=row_num, column=1, sticky=tk.W + tk.E, pady=5)
            return widget

        def _apply_settings(self):
            """Applies the settings from the input fields to the TypingConfig object."""
            try:
                self.config.switch_window_delay = self.switch_window_delay_var.get()
                self.config.mistake_probability = self.mistake_probability_var.get()
                self.config.break_probability = self.break_probability_var.get()
                self.config.min_typing_delay = self.min_typing_delay_var.get()
                self.config.max_typing_delay = self.max_typing_delay_var.get()
                self.config.long_break_probability = self.long_break_probability_var.get()

                # Parse comma-separated durations
                self.config.break_durations = [int(x.strip()) for x in self.break_durations_entry.get().split(',') if x.strip()]
                self.config.long_break_durations = [int(x.strip()) for x in self.long_break_durations_entry.get().split(',') if x.strip()]
                
                # Input validation
                if not (0 <= self.config.mistake_probability <= 1 and
                        0 <= self.config.break_probability <= 1 and
                        0 <= self.config.long_break_probability <= 1):
                    raise ValueError("Probabilities must be between 0 and 1.")
                
                if not (self.config.min_typing_delay >= 0 and self.config.max_typing_delay >= self.config.min_typing_delay):
                    raise ValueError("Typing delays must be non-negative, and max must be >= min.")
                
                if not all(d >= 0 for d in self.config.break_durations + self.config.long_break_durations):
                    raise ValueError("Break durations must be non-negative.")

                self.save_callback() # Save the updated config to file
                messagebox.showinfo("Settings Saved", "Settings applied successfully!")
                self.top.destroy() # Close settings window
            except ValueError as e:
                messagebox.showerror("Invalid Input", f"Please check your input:\n{e}")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred while saving settings:\n{e}")

# Entry point of the application
if __name__ == "__main__":
    root = tk.Tk()
    app = PythonFileEditor(root)
    root.mainloop()