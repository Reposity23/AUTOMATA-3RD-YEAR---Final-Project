import tkinter as tk
from tkinter import ttk 
from tkinter import simpledialog 
import math 
from collections import deque 
import json # Added for saving//loading the /json
from tkinter import filedialog 
from tkinter import font 

class DragDropApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NFA/DFA State Machine Editor")
        self.root.geometry("1000x800")
        

        self.colors = {
            "bg_main": "#F0F0F0",
            "bg_canvas": "#FAFAFA",
            "source_box": "#334155",
            "source_mouth": "#ADD8E6",
            "source_mouth_hover": "#FFFFFF",
            "table_header_bg": "#E1E1E1",
            "table_odd_row": "#E7F5FF"
        }
        self.root.configure(bg=self.colors['bg_main'])

      
        self.style = ttk.Style()
        self.style.theme_use('clam') # Use a modern theme

        self.style.configure('TButton', font=('Arial', 10), padding=5, relief='flat', background='#E1E1E1')
        self.style.map('TButton', background=[('active', '#C0C0C0')])
        

        self.style.configure('TFrame', background=self.colors['bg_main'])
        self.style.configure('TPanedWindow', background=self.colors['bg_main'])
        self.style.configure('TPanedWindow.Sash', sashthickness=6, relief='raised', background='#C0C0C0')
        
   
        self.style.configure('Treeview.Heading', 
                             font=('Arial', 10, 'bold'), 
                             background=self.colors['table_header_bg'], 
                             relief='flat')
        self.style.map('Treeview.Heading', relief=[('active', 'groove'), ('pressed', 'sunken')])
        
   
        self.style.configure('Treeview', 
                             rowheight=25, 
                             font=('Arial', 10), 
                             fieldbackground=self.colors['bg_canvas'])

        self.main_canvas = tk.Canvas(root, bg=self.colors['bg_main'], highlightthickness=0) # Use new color
        self.main_scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        self.main_scrollbar.pack(side="right", fill="y")
        self.main_canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame = ttk.Frame(self.main_canvas, style='TFrame')
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        self.main_canvas.bind(
            "<Configure>",
            lambda e: self.scrollable_frame.config(width=e.width)
        )

        self.v_pane = ttk.PanedWindow(self.scrollable_frame, orient=tk.VERTICAL)
        self.v_pane.pack(fill="both", expand=True, padx=10, pady=10)

        self.top_frame = ttk.Frame(self.v_pane, height=600)
        self.top_frame.pack(fill="both", expand=True)
        self.v_pane.add(self.top_frame, weight=3)

        self.button_frame = ttk.Frame(self.top_frame)
        self.button_frame.pack(pady=5)

        self.convert_button = ttk.Button(
            self.button_frame, 
            text="Convert to DFA", 
            command=self.run_nfa_to_dfa_conversion,
            style='TButton'
        )
        self.convert_button.pack(side=tk.LEFT, padx=5) 

        self.refresh_button = ttk.Button(
            self.button_frame, 
            text="Refresh Graph",
            command=self.refresh_all,
            style='TButton'
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5) 

 
        self.upload_button = ttk.Button(
            self.button_frame,
            text="Upload Script",
            command=self.upload_from_json,
            style='TButton'
        )
        self.upload_button.pack(side=tk.LEFT, padx=5)


        self.export_button = ttk.Button(
            self.button_frame,
            text="Export to .JSON",
            command=self.export_to_json,
            style='TButton'
        )
        self.export_button.pack(side=tk.LEFT, padx=5)


        self.graph_canvas = tk.Canvas(self.top_frame, bg=self.colors['bg_canvas'], width=1000, height=600, highlightthickness=0)
        self.graph_canvas.pack(fill="both", expand=True)


        self.bottom_frame = ttk.Frame(self.v_pane, height=300)
        self.bottom_frame.pack(fill="both", expand=True)
        self.v_pane.add(self.bottom_frame, weight=1)

        self.h_pane = ttk.PanedWindow(self.bottom_frame, orient=tk.HORIZONTAL)
        self.h_pane.pack(fill="both", expand=True, pady=10)

 
        self.nfa_frame = ttk.Frame(self.h_pane, width=500, height=300)
        self.nfa_frame.pack(fill="both", expand=True)
        self.h_pane.add(self.nfa_frame, weight=1)
        
        ttk.Label(self.nfa_frame, text="Non-deterministic Finite Automaton (NFA)", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.nfa_table_frame = ttk.Frame(self.nfa_frame)
        self.nfa_table_frame.pack(fill="both", expand=True)

        # --- DFA Table (Right) ---
        self.dfa_frame = ttk.Frame(self.h_pane, width=500, height=300)
        self.dfa_frame.pack(fill="both", expand=True)
        self.h_pane.add(self.dfa_frame, weight=1)

        ttk.Label(self.dfa_frame, text="Deterministic Finite Automaton (DFA)", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.dfa_table_frame = ttk.Frame(self.dfa_frame)
        self.dfa_table_frame.pack(fill="both", expand=True)
        
        # --- Item IDs and Tags ---
        self.drop_target = None
        self.circle_source = None
        
        self.drop_target_tag = "drop_target"
        self.source_container_tag = "source_container"
        self.source_circle_tag = "source_circle"
        self.source_text_tag = "source_text" # Tag for new text
        
        self.draggable_circle_tag = "draggable_circle"
        self.inside_box_tag = "inside_box"
        self.cover_up_tag = "cover_up" 
        self.arrow_visuals_tag = "arrow_visuals" # Covers arrows, names, final circles

        # --- State Machine Data ---
        self.start_state_item = None
        self.final_states = set() 
        self.transitions = [] 
        self.state_names = {} 
        self.next_state_id = 1 
        self.epsilon_symbols = {'e', 'epsilon', 'ε'} 
        self.default_radius = 25 
        self.export_counter = 1 
        
        # --- Context Menu ---
        self.right_click_menu = tk.Menu(root, tearoff=0)
        
  
        self.transition_source_item = None 

        # --- Event binding ---
        self.graph_canvas.bind('<ButtonPress-1>', self.on_canvas_press)
        self.graph_canvas.bind('<B1-Motion>', self.on_drag_or_pan)
        self.graph_canvas.bind('<ButtonRelease-1>', self.on_release_or_pan_stop)
        self.graph_canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        self.graph_canvas.bind('<Button-4>', self.on_mouse_wheel)
        self.graph_canvas.bind('<Button-5>', self.on_mouse_wheel)
        self.graph_canvas.bind('<Button-3>', self.on_right_click)
        self.graph_canvas.bind('<Configure>', self.on_resize) 
        
        # 10. Interactive Hover Effect
        self.graph_canvas.tag_bind(self.source_circle_tag, '<Enter>', self.on_source_enter)
        self.graph_canvas.tag_bind(self.source_circle_tag, '<Leave>', self.on_source_leave)

        self._drag_data = {"x": 0, "y": 0, "item": None}
        self._pan_data = {"x": 0, "y": 0}
        self.is_panning = False


        self.nfa_table = None
        self.dfa_table = None
        self.create_table(self.nfa_table_frame, "nfa")
        self.create_table(self.dfa_table_frame, "dfa")

    # --- New Hover Methods ---
    def on_source_enter(self, event):
        """Change source circle color on hover."""
        self.graph_canvas.itemconfig(self.source_circle_tag, fill=self.colors['source_mouth_hover'])

    def on_source_leave(self, event):
        """Revert source circle color on hover end."""
        self.graph_canvas.itemconfig(self.source_circle_tag, fill=self.colors['source_mouth'])

    def create_table(self, parent_frame, table_type, columns=None):
        """Helper to create or recreate a table."""

        if columns is None:
            columns = ("State", "Symbol", "Next State")
        
        if table_type == "nfa" and self.nfa_table:
            self.nfa_table.master.destroy()
        elif table_type == "dfa" and self.dfa_table:
            self.dfa_table.master.destroy()

        table_frame = ttk.Frame(parent_frame)
        table_frame.pack(fill="both", expand=True)
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")

        table = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings", 
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )
        
        scroll_y.config(command=table.yview)
        scroll_x.config(command=table.xview)

        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=80, anchor="center")
        
        table.column("State", width=100, anchor="w")

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        table.pack(side="left", fill="both", expand=True)

        if table_type == "nfa":
            self.nfa_table = table
            # 9. Table Row Styling (configure tag)
            self.nfa_table.tag_configure('oddrow', background=self.colors['table_odd_row'])
        elif table_type == "dfa":
            self.dfa_table = table
            # 9. Table Row Styling (configure tag)
            self.dfa_table.tag_configure('oddrow', background=self.colors['table_odd_row'])

    def on_resize(self, event):
        """Redraw the static UI elements when the graph_canvas is resized."""
        # Delete old static items
        self.graph_canvas.delete(self.drop_target_tag)
        self.graph_canvas.delete(self.source_container_tag)
        self.graph_canvas.delete(self.source_circle_tag)
        self.graph_canvas.delete(self.source_text_tag) # Delete old text
        self.graph_canvas.delete(self.cover_up_tag) # Delete old mask
        
        w, h = event.width, event.height
        if w < 100 or h < 100: return # Avoid drawing if too small


        self.drop_target = self.graph_canvas.create_rectangle(
            w * 0.05, h * 0.05, w * 0.6, h * 0.85,
            outline='black', 
            width=2,
            tags=(self.drop_target_tag,)
        )
        

        try:
            t_coords = self.graph_canvas.coords(self.drop_target)
            if t_coords:
                self.graph_canvas.create_rectangle(0, 0, w, t_coords[1], fill=self.colors['bg_canvas'], outline='', tags=(self.cover_up_tag,))
                self.graph_canvas.create_rectangle(0, t_coords[3], w, h, fill=self.colors['bg_canvas'], outline='', tags=(self.cover_up_tag,))
                self.graph_canvas.create_rectangle(0, t_coords[1], t_coords[0], t_coords[3], fill=self.colors['bg_canvas'], outline='', tags=(self.cover_up_tag,))
                self.graph_canvas.create_rectangle(t_coords[2], t_coords[1], w, t_coords[3], fill=self.colors['bg_canvas'], outline='', tags=(self.cover_up_tag,))
        except tk.TclError:
            pass 

    
        src_x1, src_y1 = w * 0.7, h * 0.2
        src_x2, src_y2 = w * 0.9, h * 0.6
        ear_size = (src_x2 - src_x1) * 0.2
        
    
        self.create_rounded_rectangle(
            src_x1 + ear_size*0.5, src_y1 - ear_size*0.8, src_x1 + ear_size*1.5, src_y1,
            radius=10, fill=self.colors['source_box'], outline='black', width=2,
            tags=(self.source_container_tag,)
        )
        self.create_rounded_rectangle(
            src_x2 - ear_size*1.5, src_y1 - ear_size*0.8, src_x2 - ear_size*0.5, src_y1,
            radius=10, fill=self.colors['source_box'], outline='black', width=2,
            tags=(self.source_container_tag,)
        )


        self.create_rounded_rectangle(
            src_x1, src_y1, src_x2, src_y2,
            radius=40, 
            outline='black', 
            width=2,
            fill=self.colors['source_box'],
            tags=(self.source_container_tag,)
        )


        eye_rx, eye_ry = (src_x2 - src_x1) * 0.08, (src_y2 - src_y1) * 0.08
        eye_y = src_y1 + (src_y2 - src_y1) * 0.3
        eye_x_offset = (src_x2 - src_x1) * 0.2
        eye_x_mid = (src_x1 + src_x2) / 2
        self.graph_canvas.create_oval(
            eye_x_mid - eye_x_offset - eye_rx, eye_y - eye_ry,
            eye_x_mid - eye_x_offset + eye_rx, eye_y + eye_ry,
            fill='white', outline='', tags=(self.source_container_tag,)
        )
        self.graph_canvas.create_oval(
            eye_x_mid + eye_x_offset - eye_rx, eye_y - eye_ry,
            eye_x_mid + eye_x_offset + eye_rx, eye_y + eye_ry,
            fill='white', outline='', tags=(self.source_container_tag,)
        )

        # 3. Source "Mouth"
        mouth_x1, mouth_y1 = w * 0.75, h * 0.3 + (h*0.2)
        mouth_x2, mouth_y2 = w * 0.85, h * 0.5 + (h*0.2)
        self.circle_source = self.graph_canvas.create_oval(
            mouth_x1, mouth_y1, mouth_x2, mouth_y2,
            outline='black', 
            width=2, 
            fill=self.colors['source_mouth'],
            tags=(self.source_circle_tag,)
        )
        

        self.graph_canvas.create_text(
            (mouth_x1 + mouth_x2) / 2,
            mouth_y2 + 15,
            text="Drag my mouth to start the graph",
            fill="#222222",
            font=("Arial", 9, "italic"),
            tags=(self.source_text_tag,) # New tag
        )

        
        self.graph_canvas.lift(self.cover_up_tag)
        self.graph_canvas.lift(self.drop_target_tag)
        self.graph_canvas.lift(self.source_container_tag)
        self.graph_canvas.lift(self.source_circle_tag)
        self.graph_canvas.lift(self.source_text_tag)
        
        self.redraw_all_visuals()

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):

        points = [
            x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
            x2, y1 + radius, x2, y2 - radius, x2, y2 - radius, x2, y2, x2 - radius, y2, x2 - radius, y2,
            x1 + radius, y2, x1 + radius, y2, x1, y2, x1, y2 - radius, x1, y2 - radius, x1, y1 + radius,
            x1, y1 + radius, x1, y1,
        ]
        return self.graph_canvas.create_polygon(points, **kwargs, smooth=True)

    def on_right_click(self, event):
 
        if self.transition_source_item:
            self.transition_source_item = None
            self.graph_canvas.config(cursor="")

        item = self.graph_canvas.find_closest(event.x, event.y)
        tags = []
        if item:
            item = item[0]
            tags = self.graph_canvas.gettags(item)
        
        if self.draggable_circle_tag in tags and self.inside_box_tag in tags:
            self.right_click_menu.delete(0, "end")
            self.right_click_menu.add_command(
                label="Set as Starting State", 
                command=lambda i=item: self.set_start_state(i)
            )
            self.right_click_menu.add_command(
                label="Toggle Final State", 
                command=lambda i=item: self.toggle_final_state(i)
            )
            self.right_click_menu.add_command(
                label="Add Transition", 
                command=lambda i=item: self.start_add_transition(i)
            )
            self.right_click_menu.post(event.x_root, event.y_root)

    def set_start_state(self, item):

        self.start_state_item = item
        self.redraw_all_visuals()

    def toggle_final_state(self, item):

        if item in self.final_states:
            self.final_states.remove(item)
        else:
            self.final_states.add(item)
        self.redraw_all_visuals()

    def start_add_transition(self, item):

        self.transition_source_item = item
        self.graph_canvas.config(cursor="crosshair")

    def on_canvas_press(self, event):

        if self.transition_source_item:
            item = self.graph_canvas.find_closest(event.x, event.y)
            tags = []
            if item:
                item = item[0]
                tags = self.graph_canvas.gettags(item)
            
            if self.draggable_circle_tag in tags and self.inside_box_tag in tags:
                dest_item = item
                symbol = simpledialog.askstring("Transition", "Enter symbol(s), comma-separated:", parent=self.root)
                if symbol:
                    # Allow multiple symbols
                    for s in symbol.split(','):
                        s = s.strip()
                        if s:
                            self.transitions.append((self.transition_source_item, dest_item, s))
                    self.redraw_all_visuals()
            
            self.transition_source_item = None
            self.graph_canvas.config(cursor="")
            return 

        item = self.graph_canvas.find_closest(event.x, event.y)
        tags = []
        if item:
            item = item[0]
            tags = self.graph_canvas.gettags(item)
        
        if self.source_circle_tag in tags:
            self.on_press_source(event)
        elif self.draggable_circle_tag in tags:
            self.on_press_existing(event, item)
        else:
            target_coords = self.graph_canvas.coords(self.drop_target)
            if (target_coords and 
                target_coords[0] < event.x < target_coords[2] and 
                target_coords[1] < event.y < target_coords[3]):
                
                if not (self.arrow_visuals_tag in tags):
                    self.on_pan_start(event)
            else:
                self.is_panning = False
                self._drag_data["item"] = None

    def on_press_source(self, event):

        """Called when the SOURCE circle is clicked to create a NEW circle."""
        source_coords = self.graph_canvas.coords(self.circle_source)
        if not source_coords: return 
        
        c_x = (source_coords[0] + source_coords[2]) / 2
        c_y = (source_coords[1] + source_coords[3]) / 2
        r = self.default_radius
        new_coords = (c_x - r, c_y - r, c_x + r, c_y + r)

        new_circle = self.graph_canvas.create_oval(
            new_coords, 
            outline='black', 
            width=2, 
            fill='blue',
            tags=(self.draggable_circle_tag,)
        )

        self._drag_data["item"] = new_circle
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self.graph_canvas.lift(new_circle)

    def on_press_existing(self, event, item):

        self._drag_data["item"] = item
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self.graph_canvas.itemconfig(item, fill='blue')
        self.graph_canvas.lift(item)

    def on_pan_start(self, event):

        self.is_panning = True
        self._pan_data["x"] = event.x
        self._pan_data["y"] = event.y
        self.graph_canvas.config(cursor="fleur")

    def on_drag_or_pan(self, event):

        if self._drag_data["item"]:
            dx = event.x - self._drag_data["x"]
            dy = event.y - self._drag_data["y"]
            self.graph_canvas.move(self._drag_data["item"], dx, dy)
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y
            self.redraw_all_visuals()
        
        elif self.is_panning:
            dx = event.x - self._pan_data["x"]
            dy = event.y - self._pan_data["y"]
            for item in self.graph_canvas.find_withtag(self.inside_box_tag):
                self.graph_canvas.move(item, dx, dy)
            self._pan_data["x"] = event.x
            self._pan_data["y"] = event.y

    def on_release_or_pan_stop(self, event):

        item = self._drag_data["item"]
        
        if item:
            current_tags = self.graph_canvas.gettags(item)
            is_inside_now = self.is_inside_target(self.drop_target, item)
            was_inside = self.inside_box_tag in current_tags

            if is_inside_now:
                self.graph_canvas.itemconfig(item, fill='green')
                if not was_inside:
                    self.graph_canvas.addtag_withtag(self.inside_box_tag, item)
                    if item not in self.state_names:
                        state_name = str(self.next_state_id)
                        self.state_names[item] = state_name
                        self.next_state_id += 1
                
                self.graph_canvas.lower(item, self.cover_up_tag)
                self.redraw_all_visuals() 
            
            elif was_inside:
                self.graph_canvas.itemconfig(item, fill='green')
                self.graph_canvas.lower(item, self.cover_up_tag)
            
            else:
                self.graph_canvas.itemconfig(item, fill='lightgray')
                self.graph_canvas.lift(item, self.cover_up_tag)
        
        elif self.is_panning:
            self.is_panning = False
            self.graph_canvas.config(cursor="")

        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def is_inside_target(self, target, item):

        try:
            target_coords = self.graph_canvas.coords(target)
            item_coords = self.graph_canvas.coords(item)
            if not item_coords or not target_coords: return False
        except tk.TclError:
            return False 
        
        return (
            item_coords[0] >= target_coords[0] and
            item_coords[1] >= target_coords[1] and
            item_coords[2] <= target_coords[2] and
            item_coords[3] <= target_coords[3]
        )

    def on_mouse_wheel(self, event):

        """Handle zooming of items inside the drop target."""
        try:
            target_coords = self.graph_canvas.coords(self.drop_target)
            if not (target_coords and 
                    target_coords[0] < event.x < target_coords[2] and 
                    target_coords[1] < event.y < target_coords[3]):
                return # Not inside the box
        except tk.TclError:
            return # Box not drawn yet

        factor = 0.0
        if event.num == 4 or event.delta > 0: factor = 1.1
        elif event.num == 5 or event.delta < 0: factor = 0.9
        if factor == 0.0: return

        zoom_x, zoom_y = event.x, event.y
        
        for item in self.graph_canvas.find_withtag(self.inside_box_tag):
            self.graph_canvas.scale(item, zoom_x, zoom_y, factor, factor)
        
        r = self.default_radius
        for item in self.graph_canvas.find_withtag(self.draggable_circle_tag):
            if self.inside_box_tag not in self.graph_canvas.gettags(item):
                continue
            try:
                coords = self.graph_canvas.coords(item)
                if not coords: continue
                c_x = (coords[0] + coords[2]) / 2
                c_y = (coords[1] + coords[3]) / 2
                self.graph_canvas.coords(item, c_x - r, c_y - r, c_x + r, c_y + r)
            except tk.TclError:
                continue 

        self.redraw_all_visuals()


    def redraw_all_visuals(self):

        """Delete and redraw all arrows, names, and final state circles."""
        self.graph_canvas.delete(self.arrow_visuals_tag) # Clear all old visuals

        if self.start_state_item:
            try:
                coords = self.graph_canvas.coords(self.start_state_item)
                if coords:
                    c_x = (coords[0] + coords[2]) / 2
                    c_y = (coords[1] + coords[3]) / 2
                    radius = (coords[2] - coords[0]) / 2
                    
                    arrow_start_x = c_x - radius - 30
                    arrow_start_y = c_y - radius - 30
                    arrow_end_x = c_x - (radius * 0.707)
                    arrow_end_y = c_y - (radius * 0.707)

                    self.graph_canvas.create_line(
                        arrow_start_x, arrow_start_y, arrow_end_x, arrow_end_y,
                        arrow=tk.LAST, width=2, 
                        tags=(self.inside_box_tag, self.arrow_visuals_tag)
                    )
            except tk.TclError:
                self.start_state_item = None 

        items_to_delete = []
        grouped_transitions = {} # (src, dest) -> [symbol1, symbol2]
        for (src_item, dest_item, symbol) in self.transitions:
            key = (src_item, dest_item)
            if key not in grouped_transitions:
                grouped_transitions[key] = []
            grouped_transitions[key].append(symbol)

        for (src_item, dest_item), symbols in grouped_transitions.items():
            try:
                src_coords = self.graph_canvas.coords(src_item)
                dest_coords = self.graph_canvas.coords(dest_item)
                if not src_coords or not dest_coords:
                    continue
                
                label = ",".join(sorted(list(set(symbols))))
                self.draw_transition(src_coords, dest_coords, label, src_item == dest_item)
            except tk.TclError:
                items_to_delete.append((src_item, dest_item))
        
        if items_to_delete:
            self.transitions = [t for t in self.transitions if (t[0], t[1]) not in items_to_delete]

        for item, name in self.state_names.items():
            try:
                coords = self.graph_canvas.coords(item)
                if not coords: continue
                c_x = (coords[0] + coords[2]) / 2
                c_y = (coords[1] + coords[3]) / 2

                if item in self.final_states:
                    r = (coords[2] - coords[0]) / 2
                    self.graph_canvas.create_oval(
                        c_x - r*0.8, c_y - r*0.8, c_x + r*0.8, c_y + r*0.8, 
                        outline='black', width=2, 
                        tags=(self.inside_box_tag, self.arrow_visuals_tag)
                    )
                
                self.graph_canvas.create_text(
                    c_x, c_y, text=name, 
                    tags=(self.inside_box_tag, self.arrow_visuals_tag),
                    font=("Arial", 10, "bold")
                )
            except tk.TclError:
                pass 

        self.graph_canvas.lower(self.arrow_visuals_tag, self.cover_up_tag)

    def draw_transition(self, src_coords, dest_coords, symbol, is_self_loop):
 
        tags = (self.inside_box_tag, self.arrow_visuals_tag)
        
        if is_self_loop:
            c_x = (src_coords[0] + src_coords[2]) / 2
            c_y = src_coords[1]
            radius = (src_coords[2] - src_coords[0]) / 1.5
            p1 = (c_x, c_y)
            p_control1 = (c_x + radius, c_y - radius)
            p_control2 = (c_x - radius, c_y - radius)
            self.graph_canvas.create_line(p1, p_control1, p_control2, p1, smooth=True, arrow=tk.LAST, width=2, tags=tags)
            text_pos = (c_x, c_y - radius)
            self.graph_canvas.create_text(text_pos, text=symbol, tags=tags, fill="black")
            
        else:
            src_c = ( (src_coords[0] + src_coords[2]) / 2, (src_coords[1] + src_coords[3]) / 2 )
            dest_c = ( (dest_coords[0] + dest_coords[2]) / 2, (dest_coords[1] + dest_coords[3]) / 2 )
            
            v = (dest_c[0] - src_c[0], dest_c[1] - src_c[1])
            v_len = math.sqrt(v[0]**2 + v[1]**2)
            if v_len == 0: return
            p_v = (-v[1], v[0]) 
            p_v_len = math.sqrt(p_v[0]**2 + p_v[1]**2)
            if p_v_len == 0: p_v = (1,0); p_v_len = 1 
            
            norm_p_v = (p_v[0] / p_v_len, p_v[1] / p_v_len) 
            
            curve_height = min(v_len * 0.2, 40)
            mid_p = ( (src_c[0] + dest_c[0]) / 2, (src_c[1] + dest_c[1]) / 2 )
            ctrl_p = ( mid_p[0] + norm_p_v[0] * curve_height, mid_p[1] + norm_p_v[1] * curve_height)

            src_radius = (src_coords[2] - src_coords[0]) / 2
            dest_radius = (dest_coords[2] - dest_coords[0]) / 2
            
            v_to_ctrl = (ctrl_p[0] - src_c[0], ctrl_p[1] - src_c[1])
            v_to_ctrl_len = math.sqrt(v_to_ctrl[0]**2 + v_to_ctrl[1]**2)
            if v_to_ctrl_len == 0: return
            start_p = ( src_c[0] + v_to_ctrl[0] * src_radius / v_to_ctrl_len,
                        src_c[1] + v_to_ctrl[1] * src_radius / v_to_ctrl_len )
            
            v_from_ctrl = (dest_c[0] - ctrl_p[0], dest_c[1] - ctrl_p[1])
            v_from_ctrl_len = math.sqrt(v_from_ctrl[0]**2 + v_from_ctrl[1]**2)
            if v_from_ctrl_len == 0: return
            end_p = ( dest_c[0] - v_from_ctrl[0] * dest_radius / v_from_ctrl_len,
                      dest_c[1] - v_from_ctrl[1] * dest_radius / v_from_ctrl_len )
            
            self.graph_canvas.create_line(start_p, ctrl_p, end_p, smooth=True, arrow=tk.LAST, width=2, tags=tags)
            self.graph_canvas.create_text(ctrl_p[0], ctrl_p[1], text=symbol, tags=tags, fill="black") 

    # --- NFA TO DFA CONVERSION LOGIC ---

    def run_nfa_to_dfa_conversion(self):

        """The main function to build and convert the NFA."""
        
        if not self.start_state_item:
            simpledialog.messagebox.showerror("Error", "Please set a starting state.")
            return

        states = set(self.state_names.values())
        if not states: 
             self.refresh_all() 
             return
             
        alphabet = set(t[2] for t in self.transitions if t[2] not in self.epsilon_symbols)
        alphabet = sorted(list(alphabet))
        
        start_state = self.state_names.get(self.start_state_item)
        final_states_names = {self.state_names.get(item) for item in self.final_states}

        nfa_table = {s: {} for s in states}
        for (src_item, dest_item, symbol) in self.transitions:
            src_name = self.state_names.get(src_item)
            dest_name = self.state_names.get(dest_item)
            if src_name and dest_name:
                if symbol not in nfa_table[src_name]:
                    nfa_table[src_name][symbol] = set()
                nfa_table[src_name][symbol].add(dest_name)
        
        self.populate_nfa_table_gui(nfa_table, states, alphabet, start_state, final_states_names)

        dfa_states = {} 
        dfa_transitions = {} 
        dfa_final_states = set()
        
        def get_epsilon_closure(state_set):
            closure = set(state_set)
            q = deque(state_set)
            while q:
                current = q.popleft()
                if current not in nfa_table:
                    continue
                for e_sym in self.epsilon_symbols:
                    if e_sym in nfa_table.get(current, {}):
                        for next_state in nfa_table[current][e_sym]:
                            if next_state not in closure:
                                closure.add(next_state)
                                q.append(next_state)
            return frozenset(closure)

        q0_nfa_set = get_epsilon_closure({start_state})
        if not q0_nfa_set:
            q0_nfa_set = frozenset({'Ø'}) 
            
        dfa_states[q0_nfa_set] = self.format_dfa_state_name(q0_nfa_set)
        dfa_start_state = dfa_states[q0_nfa_set]
        
        work_list = deque([q0_nfa_set])
        processed_states = {q0_nfa_set} 
        
        while work_list:
            current_nfa_set = work_list.popleft()
            current_dfa_name = dfa_states[current_nfa_set]
            
            if not current_nfa_set.isdisjoint(final_states_names):
                dfa_final_states.add(current_dfa_name)

            for symbol in alphabet:
                move_set = set()
                for nfa_state in current_nfa_set:
                    if nfa_state in nfa_table:
                        move_set.update(nfa_table.get(nfa_state, {}).get(symbol, set()))
                
                next_nfa_set = get_epsilon_closure(move_set)
                
                if not next_nfa_set:
                    next_nfa_set = frozenset({'Ø'}) 

                if next_nfa_set not in dfa_states:
                    new_dfa_name = self.format_dfa_state_name(next_nfa_set)
                    dfa_states[next_nfa_set] = new_dfa_name
                
                if next_nfa_set not in processed_states:
                    work_list.append(next_nfa_set)
                    processed_states.add(next_nfa_set)
                
                next_dfa_name = dfa_states[next_nfa_set]
                dfa_transitions[(current_dfa_name, symbol)] = next_dfa_name
        
        self.populate_dfa_table_gui(dfa_states, dfa_transitions, alphabet, dfa_start_state, dfa_final_states)


    def refresh_all(self):

        """Clears the graph, resets state, and clears the tables."""
        
        all_circles = self.graph_canvas.find_withtag(self.draggable_circle_tag)
        for item in all_circles:
            self.graph_canvas.delete(item)
            
        self.graph_canvas.delete(self.arrow_visuals_tag)
        
        self.start_state_item = None
        self.final_states = set()
        self.transitions = []
        self.state_names = {}
        self.next_state_id = 1
        
        self.create_table(self.nfa_table_frame, "nfa")
        self.create_table(self.dfa_table_frame, "dfa")
        
        self.redraw_all_visuals()

    def format_dfa_state_name(self, state_set):
 
        """Helper to format DFA state names for the table."""
        if state_set == frozenset({'Ø'}):
            return "Ø"
        sorted_states = sorted(list(state_set), key=lambda x: (int(x) if x.isdigit() else float('inf'), x))
        return "{" + ",".join(sorted_states) + "}"

    def populate_nfa_table_gui(self, nfa_table, states, alphabet, start_state, final_states):
        """Re-create and populate the NFA table."""
        cols = ("State",) + tuple(alphabet)
        has_epsilon = False
        for state_transitions in nfa_table.values():
            if any(s in self.epsilon_symbols for s in state_transitions):
                has_epsilon = True
                break
        
        if has_epsilon:
             cols += ("ε",)
        
        self.create_table(self.nfa_table_frame, "nfa", cols)

        # 9. Table Row Styling (apply tag)
        for i, state in enumerate(sorted(list(states), key=lambda x: (int(x) if x.isdigit() else float('inf'), x))):
            row = [state]
            
            s_display = state
            if state == start_state: s_display = "→" + s_display
            if state in final_states: s_display = "*" + s_display
            row[0] = s_display

            for symbol in alphabet:
                next_states = nfa_table.get(state, {}).get(symbol, set())
                row.append(self.format_dfa_state_name(next_states) if next_states else "Ø")
            
            if "ε" in cols:
                e_next = set()
                for e_sym in self.epsilon_symbols:
                    e_next.update(nfa_table.get(state, {}).get(e_sym, set()))
                row.append(self.format_dfa_state_name(e_next) if e_next else "Ø")
            
            tags = ('oddrow',) if i % 2 != 0 else ()
            self.nfa_table.insert("", "end", values=row, tags=tags)

    def populate_dfa_table_gui(self, dfa_states, dfa_transitions, alphabet, start_state, final_states):
        """Re-create and populate the DFA table."""
        cols = ("State",) + tuple(alphabet)
        self.create_table(self.dfa_table_frame, "dfa", cols)

        def dfa_sort_key(state_name):
            if state_name == "Ø":
                return (0, "")
            if state_name == start_state:
                return (1, "")
            return (2, len(state_name), state_name)

        sorted_dfa_names = sorted(dfa_states.values(), key=dfa_sort_key)
        
        # 9. Table Row Styling (apply tag)
        for i, state_name in enumerate(sorted_dfa_names):
            
            s_display = state_name
            if state_name == start_state: s_display = "→" + s_display
            if state_name in final_states: s_display = "*" + s_display
            
            row = [s_display]

            for symbol in alphabet:
                next_state_name = dfa_transitions.get((state_name, symbol), "Ø")
                row.append(next_state_name)
            
            tags = ('oddrow',) if i % 2 != 0 else ()
            self.dfa_table.insert("", "end", values=row, tags=tags)

    # ==================================================================
    # === MODIFIED FUNCTION ===
    # ==================================================================
    def export_to_json(self):
        """Saves the current graph state to an auto-incrementing JSON file
           with clean, sorted, and validated formatting."""
        try:
            states_data = []
            transitions_data = []
            alphabet_set = set()
            unique_transitions_set = set()

            # --- 1. Determine Start State ---
            # Use the same sorting key as the tables
            def state_sort_key(name):
                # Sort numerically if possible, otherwise alphabetically
                return (int(name) if name.isdigit() else float('inf'), name)

            start_state_name = None
            if self.start_state_item and self.start_state_item in self.state_names:
                start_state_name = self.state_names[self.start_state_item]
            elif self.state_names:
                # If no start state is set, default to the first state added
                all_names = list(self.state_names.values())
                all_names.sort(key=state_sort_key)
                if all_names:
                    start_state_name = all_names[0]

            # --- 2. Process States ---
            # Sort states by name using the same key
            sorted_items = sorted(self.state_names.items(), key=lambda item: state_sort_key(item[1]))
            
            for item_id, name in sorted_items:
                try:
                    coords = self.graph_canvas.coords(item_id)
                    if not coords: continue 
                    
                    # Round coordinates to 2 decimal places
                    rounded_coords = [round(c, 2) for c in coords]
                    
                    # Build state dictionary with consistent key order
                    state_dict = {
                        "name": name,
                        "coords": rounded_coords,
                        "is_start": name == start_state_name,
                        "is_final": item_id in self.final_states
                    }
                    states_data.append(state_dict)
                except tk.TclError:
                    continue 

            # --- 3. Process Transitions ---
            for (src_item, dest_item, symbol) in self.transitions:
                src_name = self.state_names.get(src_item)
                dest_name = self.state_names.get(dest_item)
                
                if src_name and dest_name:
                    # Add to alphabet (ignore epsilon)
                    if symbol not in self.epsilon_symbols:
                        alphabet_set.add(symbol)
                    
                    # Ensure transition is unique
                    transition_tuple = (src_name, dest_name, symbol)
                    if transition_tuple not in unique_transitions_set:
                        unique_transitions_set.add(transition_tuple)
                        # Build transition dictionary with consistent key order
                        transitions_data.append({
                            "source": src_name,
                            "target": dest_name,
                            "symbol": symbol
                        })
            
            # Sort transitions for readability
            transitions_data.sort(key=lambda t: (state_sort_key(t['source']), state_sort_key(t['target']), t['symbol']))

            # --- 4. Build Final JSON Output ---
            # Build final dictionary with consistent key order
            output_data = {
                "alphabet": sorted(list(alphabet_set)),
                "states": states_data,
                "transitions": transitions_data
            }

            filename = f"OUTPUT{self.export_counter}.json"
            with open(filename, 'w') as f:
                json.dump(output_data, f, indent=4)
            
            simpledialog.messagebox.showinfo("Export Successful", f"Graph exported to {filename}")
            self.export_counter += 1

        except Exception as e:
            simpledialog.messagebox.showerror("Export Error", f"Failed to export JSON: {e}")
    # ==================================================================
    # === END MODIFIED FUNCTION ===
    # ==================================================================

    def upload_from_json(self):
 
        """Loads a graph state from a selected JSON file."""
        filepath = filedialog.askopenfilename(
            title="Select JSON Script",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filepath:
            return 

        try:
            self.refresh_all()

            with open(filepath, 'r') as f:
                data = json.load(f)

            name_to_item_id_map = {}
            max_state_id = 0

            for state_data in data.get("states", []):
                name = state_data.get("name")
                coords = state_data.get("coords")
                if not name or not coords:
                    continue

                item_id = self.graph_canvas.create_oval(
                    coords, 
                    outline='black', 
                    width=2, 
                    fill='green', 
                    tags=(self.draggable_circle_tag, self.inside_box_tag)
                )
                
                self.state_names[item_id] = name
                name_to_item_id_map[name] = item_id

                if state_data.get("is_start"):
                    self.start_state_item = item_id
                
                if state_data.get("is_final"):
                    self.final_states.add(item_id)
                
                try:
                    state_num = int(name)
                    if state_num > max_state_id:
                        max_state_id = state_num
                except ValueError:
                    pass 
            
            self.next_state_id = max_state_id + 1

            for trans_data in data.get("transitions", []):
                src_name = trans_data.get("source")
                dest_name = trans_data.get("target")
                symbol = trans_data.get("symbol")

                src_item = name_to_item_id_map.get(src_name)
                dest_item = name_to_item_id_map.get(dest_name)

                if src_item and dest_item and symbol:
                    self.transitions.append((src_item, dest_item, symbol))
            
            self.redraw_all_visuals()
            simpledialog.messagebox.showinfo("Upload Successful", "Graph loaded from file.")

        except Exception as e:
            simpledialog.messagebox.showerror("Upload Error", f"Failed to load JSON: {e}")
            self.refresh_all() 


if __name__ == "__main__":
    root = tk.Tk()
    app = DragDropApp(root)
    root.state('zoomed') 
    root.mainloop()
