## CS 300-CS31S1 - Automata Theory and Formal Languages - FINAL PROJECT

## Programs
- **Program 1:** Done
- **Program 2:** In Progress

## Notes
- To run **Program 1**, make sure you have `tkinter` installed:
```bash
pip install tk
```
# Automata 3rd Year - Final Project: Program #1

A **visual NFA (Nondeterministic Finite Automaton) editor** with **DFA (Deterministic Finite Automaton) conversion**, built using Python and Tkinter. Design NFAs graphically and automatically generate their equivalent DFA transition tables.  

![App Screenshot](https://github.com/user-attachments/assets/519e6ca1-eeee-47db-8d1f-afbf7d1f3f2b)

---

## Features

- **Visual Graph Editor:** Drag-and-drop interface to create and manipulate states.  
- **NFA → DFA Conversion:** Implements subset construction algorithm automatically.  
- **Dynamic Transition Tables:** View NFA and DFA tables in real-time.  
- **Save & Load:** Export/import graphs as `.JSON` files.  
- **Interactive UI:** Zoom, pan, and responsive interface for smooth editing.  

---

## How to Use

### 1. Drawing Your NFA

- **Create a State:** Drag the light blue "mouth" from the character on the right onto the canvas. States are auto-numbered.  
- **Move States:** Click and drag any state to reposition it.  

### 2. Graph Controls

- **Pan:** Left-click and drag on empty canvas space.  
- **Zoom:** Hover over the canvas and scroll your mouse wheel.  
- **Scroll Window:** Use mouse wheel outside the canvas (tables/buttons).  

### 3. State Operations (Right-Click)

Right-click a state to access:

- **Set as Starting State:** Marks the start state. Arrow appears.  
- **Toggle Final State:** Marks/unmarks as an accepting state. Inner circle added.  
- **Add Transition:**  
  1. Click destination state (self-loop allowed).  
  2. Enter symbol(s) in dialog (`a`, `a,b`, or `e/epsilon`).  
  3. Labeled arrow appears connecting states.  

![Right-Click Menu](https://github.com/user-attachments/assets/eae4564b-2784-4ddb-8cb1-a95f7f419226)

### 4. Core Buttons

- **Convert to DFA:** Runs subset construction, populates NFA and DFA tables.  
- **Refresh Graph:** Clears graph and tables.  
- **Upload Script:** Load a `.JSON` file to restore a saved graph.  
- **Export to .JSON:** Save current graph (auto-named `OUTPUT1.json`, `OUTPUT2.json`, etc.).  

### 5. Transition Tables

- **NFA Table:** Shows transitions for your drawn NFA.  
  - `→` = start state  
  - `*` = final state  
  - `ε` column = epsilon transitions  
  - Cells can show sets like `{1,3,5}`  

- **DFA Table:** Shows converted DFA.  
  - States as sets `{1,2,6}`  
  - `Ø` = dead/trap state  

---

## Installation & Running

```bash
git clone https://github.com/Reposity23/AUTOMATA-3RD-YEAR---Final-Project.git
cd automata-3rd-year-final-project
python main.py

```
###Credits
---
Program 1 Inspiration & Knowledge: HTML/JavaScript NFA → DFA visualizer by JoeyLemon
----
link: https://github.com/joeylemon/nfa-to-dfa
---
Used the structure and logic of the graphing and transition table as inspiration and reference to implement the Python/Tkinter version.
