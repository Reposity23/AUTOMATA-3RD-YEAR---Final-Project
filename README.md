AUTOMATA-3RD-YEAR---Final-Project

A visual NFA (Nondeterministic Finite Automaton) editor and DFA (Deterministic Finite Automaton) converter, built with Python and Tkinter. This tool allows users to graphically design an NFA, which can then be automatically converted into its equivalent DFA transition table.

<img width="990" height="590" alt="image" src="https://github.com/user-attachments/assets/519e6ca1-eeee-47db-8d1f-afbf7d1f3f2b" />

Features

Visual Graph Editor: A drag-and-drop interface for creating and manipulating states.

NFA to DFA Conversion: Implements the subset construction algorithm to automatically generate a DFA from your NFA graph.

Dynamic Transition Tables: Instantly view the NFA and DFA transition tables based on your graph.

Save/Load: Export your graph to a .JSON file and upload it later to continue your work.

Interactive UI: A stylized interface with zoom, pan, and responsive elements.

How to Use

1. Drawing Your NFA

The application is split into a graph canvas (top) and two transition tables (bottom).

Create a State: On the right, find the character with the "ears" and "eyes." Click and drag the "mouth" (the light blue circle) onto the main graph canvas to create a new state. Each state is automatically numbered (1, 2, 3...).

Drag States: You can reposition any state by clicking and dragging it.

2. Graph and Canvas Controls

Pan: To move your view of the graph, left-click and drag on the empty background of the graph canvas.

Zoom: To zoom in and out, hover your mouse over the graph canvas and use your mouse wheel. The circles themselves will remain a consistent size, but their positions will scale.

Scroll: Use your mouse wheel anywhere outside the graph canvas (e.g., over the tables or buttons) to scroll the entire application window up or down.

3. State Operations (Right-Click Menu)

Right-click on any state (circle) inside the graph box to open a context menu with three options:

Set as Starting State: Marks the state as the NFA's start state. An arrow will appear, pointing to it.

Toggle Final State: Marks or un-marks the state as an accepting (final) state. A final state is drawn with an inner circle.

Add Transition:

After clicking, your cursor will turn into a crosshair.

Click a destination state (this can be the same state to create a self-loop).

A dialog box will pop up asking for a symbol. You can enter single symbols (a), multiple symbols separated by commas (a,b), or an epsilon symbol (e or epsilon).

A labeled arrow will be drawn from the source to the destination.

4. Core Functionality (Top Buttons)

Convert to DFA: This is the main function. It analyzes your NFA graph (states, start state, final states, and transitions) and runs the complete subset construction algorithm.

It populates the NFA Table on the left.

It calculates and populates the DFA Table on the right, showing the new DFA states (e.g., {1,2}) and their transitions.

Refresh Graph: Clears everything. The graph, NFA table, and DFA table are all reset to their empty, default state.

Upload Script: Opens a file dialog allowing you to select a .json file that you previously saved. This will clear the canvas and perfectly reconstruct your saved graph, including all state positions, names, and transitions.

Export to .JSON: Saves the current state of your graph (all state positions, names, start/final status, and transitions) to a file. The files are automatically named OUTPUT1.json, OUTPUT2.json, and so on.

5. Transition Tables

The tables at the bottom provide a formal summary of your automaton.

Non-deterministic Finite Automaton (NFA) Table: This table is populated when you press "Convert." It shows the transitions for the NFA you drew.

→ indicates a start state.

* indicates a final state.

ε column shows all epsilon transitions.

Cells can contain sets of states, like {1,3,5}.

Deterministic Finite Automaton (DFA) Table: This table shows the final, converted DFA.

States are represented as sets (e.g., {1,2,6}).

Ø represents the "dead state" or "trap state" if a transition is not defined.
