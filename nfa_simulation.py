import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
import json
import time
from PIL import Image, ImageTk
from xai_sdk import Client
from xai_sdk.chat import system, user, assistant, image
import os
import base64
import re

API_KEY = "xai-190haggHSufNOBu1YOmy9WHhJIKG4XsU9S9VHQlPXvki6QrUm98qXmGBNEiifwxEgLwShjVP8qvviiYM"
MODEL_NAME = "grok-2-vision-1212"  # Model that supports vision/image analysis
AUTOMATA_PROFILE_IMAGE = "automata.png" # Must be in the same directory as this script

# ----------------------------------------------------
# 2. XAI API Interaction (Running in a separate thread)
# ----------------------------------------------------
def analyze_image_and_generate_code(app_instance, image_path):
    """
    Handles the communication with the xAI API in a non-blocking thread.
    This function includes the fix for the MergeFrom() error by using the correct multimodal structure.
    Removed response_format to avoid protocol error, relying on prompt for JSON output.
    """
    
    try:
        app_instance.update_status("uploading file...")
        
        # Initialize the xAI Client
        client = Client(api_key=API_KEY)
        
        # Determine MIME type based on file extension
        image_ext = os.path.splitext(image_path)[1].lower()
        if image_ext in ['.jpg', '.jpeg']:
            mime_type = 'image/jpeg'
        elif image_ext == '.png':
            mime_type = 'image/png'
        else:
            raise ValueError("Unsupported image format. Only JPG and PNG are supported.")
        
        # Read and base64 encode the local image
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        image_url = f"data:{mime_type};base64,{encoded_image}"
        
        # Create the message payload using xai_sdk.chat functions with image()
        messages = [
            system("You are an expert Formal Languages and Automata Theory coder. Your task is to analyze the user-provided Non-deterministic Finite Automaton (NFA) drawing and convert its structure into a Python dictionary that strictly follows the requested JSON schema. Use state names from the labels in the image if present (e.g., 'q0', 'q1'), otherwise assign sequential names like 'q0', 'q1', etc. Estimate coordinates for each state based on their relative positions in the image, assuming a canvas size of 1000x600 pixels. Position states to avoid overlap, with bounding boxes of 50x50 pixels (e.g., [x1, y1, x1+50, y1+50]). Identify the start state (usually indicated by an incoming arrow) and set 'is_start': true for it. Identify final states (usually double circles) and set 'is_final': true. For transitions, create separate entries for each source-target-symbol combination; if a transition has multiple symbols (e.g., 'a,b'), create multiple entries; if nondeterministic (same symbol to multiple targets), create multiple entries. Use 'ε' for epsilon transitions. You MUST only output the JSON object, do not include any explanatory text, no markdown, no code blocks."),
            
            user(
                "Analyze the attached NFA drawing. Identify all states, their positions, the start state, final states, and the transitions. Based on the analysis, generate a complete, valid Python dictionary object (in JSON format) representing the NFA. The format must be: {'states': [{'name': 'q0', 'coords': [x1, y1, x2, y2], 'is_start': true, 'is_final': false}, ...], 'transitions': [{'source': 'q0', 'target': 'q1', 'symbol': 'a'}, ...]}. Ensure coordinates are numbers and states are positioned reasonably without overlap.",
                image(image_url)
            )
        ]
        
        app_instance.update_status("file sent...")
        app_instance.update_status("analyzing...")

        # Request without response_format, rely on prompt for JSON
        response = client.chat.create(
            model=MODEL_NAME, 
            messages=messages
        ).sample()

        app_instance.update_status("coding...")
        
        # Extract and parse the JSON content
        nfa_json_text = response.content.strip()
        
        # Remove potential markdown code blocks
        if nfa_json_text.startswith('```json'):
            nfa_json_text = nfa_json_text[7:]
        if nfa_json_text.startswith('```'):
            nfa_json_text = nfa_json_text[3:]
        if nfa_json_text.endswith('```'):
            nfa_json_text = nfa_json_text[:-3]
        nfa_json_text = nfa_json_text.strip()
        
        # Extract the JSON object using regex if necessary
        match = re.search(r'\{[\s\S]*\}', nfa_json_text)
        if match:
            nfa_json_text = match.group(0)
        else:
            raise ValueError("No valid JSON object found in response")
        
        # Parse the JSON
        nfa_data = json.loads(nfa_json_text)
        
        # Save the generated JSON to a file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(nfa_data, f, indent=4)

        # Update the final status as requested
        app_instance.update_status(f"code generate({filename})")
        
        # Display the message in the text box instead of code
        app_instance.output_text.delete(1.0, tk.END)
        app_instance.output_text.insert(tk.END, f"Code generated, please check the file")
        
    except Exception as e:
        app_instance.update_status("ERROR: Failed to process NFA.")
        print(f"An error occurred during API call: {e}")
        messagebox.showerror("API Error", f"Failed to get a response from Grok. Error: {e}")
        
    finally:
        # Re-enable the button regardless of success/failure
        app_instance.process_button.config(state=tk.NORMAL, bg="#28a745")

# ----------------------------------------------------
# 3. Tkinter GUI Application Class
# ----------------------------------------------------
class GrokNfaParserApp:
    def __init__(self, master):
        self.master = master
        master.title("NFA/DFA State Machine Editor (Grok NFA Parser)")
        master.geometry("600x650")
        master.configure(bg="#1e1e1e") # Dark background
        
        # Variables
        self.nfa_image_path = None
        
        # Create Widgets
        self.create_header_frame()
        self.create_main_frame()
        self.create_output_frame()

    def create_header_frame(self):
        """Creates the header area with the profile image and status."""
        header_frame = tk.Frame(self.master, bg="#2d2d2d", padx=10, pady=10)
        header_frame.pack(fill='x', side='top')
        
        # 1. Profile Image (Automata.png)
        try:
            # Resize and load the image
            img = Image.open(AUTOMATA_PROFILE_IMAGE)
            img = img.resize((50, 50), Image.Resampling.LANCZOS)
            self.profile_photo = ImageTk.PhotoImage(img)
            
            # Create a label for the image
            profile_label = tk.Label(header_frame, image=self.profile_photo, bg="#2d2d2d")
            profile_label.pack(side='left', padx=(0, 15))
        except FileNotFoundError:
            profile_label = tk.Label(header_frame, text="[IMG]", fg="white", bg="#2d2d2d", font=("Arial", 24))
            profile_label.pack(side='left', padx=(0, 15))
            messagebox.showwarning("Image Warning", f"Profile image '{AUTOMATA_PROFILE_IMAGE}' not found. Using placeholder.")


        # 2. Status Label
        status_text = tk.Label(header_frame, text="Status:", fg="white", bg="#2d2d2d", font=("Arial", 12, "bold"))
        status_text.pack(side='left', padx=(0, 5))
        
        self.status_var = tk.StringVar(value="Waiting for file upload...")
        self.status_label = tk.Label(header_frame, textvariable=self.status_var, fg="#aaffaa", bg="#2d2d2d", font=("Arial", 12))
        self.status_label.pack(side='left', fill='x', expand=True)

    def create_main_frame(self):
        """Creates the middle section with the image upload and process button."""
        main_frame = tk.Frame(self.master, bg="#1e1e1e", padx=10, pady=10)
        main_frame.pack(fill='x', side='top')

        # 1. Upload Button (Label is "Upload Image" in the image)
        upload_button = tk.Button(main_frame, text="Upload Image", command=self.upload_image, 
                                  bg="#555555", fg="white", relief=tk.FLAT, font=("Arial", 12, "bold"), width=15)
        upload_button.pack(side='left', padx=(0, 10))
        
        # 2. File Path Label
        self.file_path_var = tk.StringVar(value="No file selected.")
        file_path_label = tk.Label(main_frame, textvariable=self.file_path_var, fg="#cccccc", bg="#1e1e1e", font=("Arial", 10))
        file_path_label.pack(side='left', fill='x', expand=True)

        # 3. Process Button (Used for "Process NFA")
        self.process_button = tk.Button(main_frame, text="Process NFA", command=self.start_process, 
                                        bg="#007bff", fg="white", relief=tk.FLAT, font=("Arial", 12, "bold"), width=15, state=tk.DISABLED)
        self.process_button.pack(side='right')

    def create_output_frame(self):
        """Creates the scrolled text area for displaying the JSON output."""
        output_frame = tk.Frame(self.master, bg="#1e1e1e", padx=10, pady=10)
        output_frame.pack(fill='both', expand=True)
        
        tk.Label(output_frame, text="Generated NFA JSON Code:", fg="white", bg="#1e1e1e", font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))

        # ScrolledText for JSON output
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=20, bg="#000000", fg="#00ff00", 
                                                     insertbackground="#00ff00", font=("Consolas", 10), relief=tk.FLAT)
        self.output_text.pack(fill='both', expand=True)

    # --- Methods ---
    def update_status(self, message):
        """Updates the status label and prints to console."""
        print(f"STATUS: {message}")
        self.status_var.set(message)
        self.master.update_idletasks() # Force GUI update
        
    def upload_image(self):
        """Opens a file dialog for the user to select an image."""
        file_path = filedialog.askopenfilename(
            title="Select NFA Drawing Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.nfa_image_path = file_path
            self.file_path_var.set(f"Selected: {os.path.basename(file_path)}")
            self.process_button.config(state=tk.NORMAL, bg="#28a745") # Enable and change color
            self.update_status(f"File '{os.path.basename(file_path)}' selected. Ready to process.")
        else:
            # Only change status if a file was previously selected
            if self.nfa_image_path:
                 self.update_status("File selection cancelled. Using previous file.")
            else:
                 self.update_status("Waiting for file upload...")

    def start_process(self):
        """Starts the analysis in a separate thread to keep the GUI responsive."""
        if not self.nfa_image_path:
            messagebox.showwarning("Warning", "Please upload an image file first.")
            return

        # Disable buttons during processing
        self.process_button.config(state=tk.DISABLED, bg="#ffc107")
        self.update_status("Starting analysis...")
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Processing... please wait for Grok's response.")
        
        # Start the API call in a new thread
        thread = threading.Thread(target=analyze_image_and_generate_code, args=(self, self.nfa_image_path))
        thread.start()

# ----------------------------------------------------
# 4. Main Execution Block
# ----------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = GrokNfaParserApp(root)
    root.mainloop()