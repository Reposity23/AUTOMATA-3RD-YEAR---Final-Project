# CS 300-CS31S1 - Automata Theory and Formal Languages - FINAL PROJECT

This project consists of two main programs that fulfill the course requirements:
* Program 1 (Real-Life Application): A visual, interactive NFA (Nondeterministic Finite Automaton) editor with a built-in converter that generates an equivalent DFA (Deterministic Finite Automaton).
* Program 2 (Implementation): A command-line tool that implements Hopcroft's DFA minimization algorithm to take any DFA in a specified JSON format and produce its minimized equivalent.

Programs:
- Program 1: Done
- Program 2: Done

Installation & Running:
git clone https://github.com/Reposity23/AUTOMATA-3RD-YEAR---Final-Project.git
cd AUTOMATA-3RD-YEAR---Final-Project
pip install tk

Program 1: Visual NFA → DFA Converter (Real-Life Application)
A visual NFA editor with DFA conversion, built using Python and Tkinter. This tool allows you to design NFAs graphically by drawing states and transitions, and then automatically generate their equivalent DFA transition tables.

Run Program 1:
python PROGRAM1.py

Features:
Visual Graph Editor: Drag-and-drop interface to create and manipulate states.
NFA → DFA Conversion: Implements the subset construction algorithm automatically.
Dynamic Transition Tables: View NFA and DFA tables in real-time.
Save & Load: Export/import your automaton graph as a .JSON file.
Interactive UI: Zoom, pan, and responsive interface for smooth editing.

How to Use Program 1:
1. Drawing Your NFA
   Create a State: Drag the light blue "mouth" from the character on the right onto the canvas. States are auto-numbered.
   Move States: Click and drag any state to reposition it.
2. Graph Controls
   Pan: Left-click and drag on empty canvas space.
   Zoom: Hover over the canvas and scroll your mouse wheel.
   Scroll Window: Use mouse wheel outside the canvas (tables/buttons).
3. State Operations (Right-Click)
   Set as Starting State: Marks the start state. An arrow will appear.
   Toggle Final State: Marks/unmarks as an accepting state. An inner circle is added.
   Add Transition: Click the destination state (self-loops are allowed), enter symbol(s) in the dialog (a, a,b, or e/epsilon), a labeled arrow appears connecting the states.
4. Core Buttons
   Convert to DFA: Runs subset construction and populates the NFA and DFA tables.
   Refresh Graph: Clears the graph and tables.
   Upload Script: Load a .JSON file to restore a saved graph.
   Export to .JSON: Save the current graph (auto-named OUTPUT1.json, OUTPUT2.json, etc.). This JSON file can be used as input for Program 2.
5. Transition Tables
   NFA Table: Shows transitions for your drawn NFA.
       → = start state
       * = final state
       ε column = epsilon transitions
       Cells can show sets like {1,3,5}
   DFA Table: Shows the converted DFA.
       States are represented as sets of the original NFA states, e.g., {1,2,6}
       Ø = dead/trap state

Program 2: DFA Minimization Tool (Implementation)
A command-line tool that implements Hopcroft's algorithm to minimize any DFA. It takes a DFA in the JSON format exported by Program 1, removes unreachable states, runs the minimization algorithm, and then displays the resulting minimized DFA as a new transition table.

Run Program 2:
python PROGRAM2.py

Features:
JSON Input: Accepts any DFA defined in the project's standard .JSON format.
Hopcroft's Algorithm: Implements the efficient partition-refinement algorithm for minimization.
Unreachable State Removal: Automatically prunes any states not reachable from the start state before minimizing.
Dead State Handling: Correctly processes complete and incomplete DFAs by creating a "dead" partition.
Clear Table Output: Displays both the original (reachable) DFA and the new minimized DFA in easy-to-read transition tables.
JSON Output: Asks the user if they want to save the new minimized DFA back to a .JSON file.

How to Use Program 2:
Use Program 1 to create a DFA and export it (e.g., OUTPUT1.json). Run Program 2 from your terminal. Follow the command-line prompts: It will ask for the path to your input JSON file, print its progress showing the original reachable DFA table and the new minimized table, and finally ask if you want to save the result.

Sample Output:
====================================
  Program 2: DFA Minimization Tool
====================================
Enter path to input DFA JSON file: OUTPUT1.json
1. Completing DFA by adding dead state (if needed)...
2. Removing unreachable states...
3. Running Hopcroft's minimization algorithm...
4. Reconstructing minimized DFA from 4 partitions...

Minimization complete.

--- Original DFA (Reachable) ---
State           | a | b
-------------------------------
→{1}            | {2,3} | {1}
*{2,3}          | {4} | {1}
*{4}            | {4} | {4}

--- Minimized DFA ---
State           | a | b
-------------------------------
→{{1}}          | {{2,3}} | {{1}}
*{{2,3}}        | {{4}} | {{1}}
*{{4}}          | {{4}} | {{4}}
{{__DEAD__}}    | {{__DEAD__}} | {{__DEAD__}}

Save minimized DFA to a new JSON file? (y/n): y
Enter output filename (e.g., minimized_dfa.json): minimized.json

Successfully saved minimized DFA to 'minimized.json'

Credits:
Program 1 Inspiration & Knowledge: HTML/JavaScript NFA → DFA visualizer by JoeyLemon.
Link: https://github.com/joeylemon/nfa-to-dfa
Used the structure and logic of the graphing and transition table as inspiration to implement the Python/Tkinter version.
