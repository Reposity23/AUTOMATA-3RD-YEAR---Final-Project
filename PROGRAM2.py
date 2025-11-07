

import json
import sys
from collections import deque



def _format_state_name(partition):
    """
    Creates a consistent, sorted string name for a partition (a new state).
    Example: frozenset({'3', '1', '2'}) -> '{1,2,3}'
    """
    if not partition:
        return "{}"

    try:
        sorted_states = sorted(list(partition), key=lambda x: int(x))
    except ValueError:
        sorted_states = sorted(list(partition))
    return "{" + ",".join(sorted_states) + "}"

# Main DFA Minimization Class 

class DFAMinimizer:
    """
    Encapsulates the logic for loading, validating, minimizing,
    and reconstructing a DFA.
    """
    
    def __init__(self, dfa_data):
        self._validate_input(dfa_data)
        self._parse_dfa(dfa_data)
        self.dead_state_name = None

    def _validate_input(self, data):
        """Basic validation of the input JSON structure."""
        required_keys = ["alphabet", "states", "transitions"]
        if not all(key in data for key in required_keys):
            raise ValueError("Invalid JSON format. Missing one of: " + ", ".join(required_keys))
        
        if not data["states"]:
            raise ValueError("DFA must have at least one state.")
            
        if not any(s["is_start"] for s in data["states"]):
            raise ValueError("DFA must have at least one start state.")

    def _parse_dfa(self, data):
        """
        Converts the JSON list-based format into a more efficient
        internal dictionary-based representation.
        """
        self.alphabet = set(data["alphabet"])
        self.states = set()
        self.start_state = None
        self.final_states = set()
        
        for state_info in data["states"]:
            name = state_info["name"]
            self.states.add(name)
            if state_info["is_start"]:
                if self.start_state is not None:
                    print(f"Warning: Multiple start states found. Using '{name}'.", file=sys.stderr)
                self.start_state = name
            if state_info["is_final"]:
                self.final_states.add(name)
        
        # Internal transitions format: {state -> {symbol -> next_state}}
        self.transitions = {s: {} for s in self.states}
        for trans in data["transitions"]:
            src, sym, tgt = trans["source"], trans["symbol"], trans["target"]
            if src not in self.states or tgt not in self.states:
                raise ValueError(f"Transition '{src}' -> '{tgt}' references a non-existent state.")
            if sym not in self.alphabet:
                raise ValueError(f"Transition symbol '{sym}' is not in the declared alphabet.")
            if sym in self.transitions[src]:
                print(f"Warning: Non-deterministic transition found for ({src}, {sym}). Using last one.", file=sys.stderr)
            self.transitions[src][sym] = tgt

    def _complete_dfa(self):
        """
        Ensures the DFA is "complete" by adding a dead state.
        A complete DFA has one transition for every symbol from every state.
        This is a prerequisite for Hopcroft's algorithm.
        """
        self.dead_state_name = "__DEAD__"
        # Find a unique name for the dead state
        while self.dead_state_name in self.states:
            self.dead_state_name += "_"
            
        needs_dead_state = False
        for state in self.states:
            for symbol in self.alphabet:
                if symbol not in self.transitions[state]:
                    self.transitions[state][symbol] = self.dead_state_name
                    needs_dead_state = True
        
        if needs_dead_state:
            self.states.add(self.dead_state_name)
            self.transitions[self.dead_state_name] = {}
            for symbol in self.alphabet:
                self.transitions[self.dead_state_name][symbol] = self.dead_state_name

    def _remove_unreachable_states(self):
        """
        Performs a BFS/DFS from the start state to find all reachable states.
        Removes any states (and their transitions) that are not reachable.
        """
        if self.start_state is None:
            return  # No start state, nothing is reachable

        reachable_states = set()
        q = deque([self.start_state])
        
        while q:
            state = q.popleft()
            if state not in reachable_states:
                reachable_states.add(state)
                for symbol in self.alphabet:
                    if symbol in self.transitions[state]:
                        next_state = self.transitions[state][symbol]
                        if next_state not in reachable_states:
                            q.append(next_state)

        unreachable = self.states - reachable_states
        if unreachable:
            print(f"Removing unreachable states: {unreachable}", file=sys.stderr)
        
        self.states = reachable_states
        self.final_states = self.final_states.intersection(reachable_states)
        
        # Filter transitions dictionary
        self.transitions = {s: self.transitions[s] for s in self.states}
        # No need to filter inner dicts, as they only point to
        # states that will be caught in the next iteration if unreachable.

    def _hopcroft_algorithm(self):
        """
        Implements Hopcroft's DFA minimization algorithm.
        Partitions states into blocks of indistinguishable states.
        """
        non_final_states = self.states - self.final_states
        
        # 1. Initial Partitions: P = {F, Q-F}
        # Use frozenset for hashable set-of-sets
        P = {frozenset(self.final_states), frozenset(non_final_states)}
        if not self.final_states:
             P = {frozenset(non_final_states)}
        if not non_final_states:
             P = {frozenset(self.final_states)}

        # 2. Worklist: W = {F, Q-F} (or just {F} as an optimization)
        W = {frozenset(self.final_states)}
        if len(non_final_states) < len(self.final_states):
            W = {frozenset(non_final_states)}

        # 3. Build reverse transitions: reverse_trans[symbol][target] = {source1, ...}
        reverse_trans = {sym: {s: set() for s in self.states} for sym in self.alphabet}
        for source, trans_map in self.transitions.items():
            for symbol, target in trans_map.items():
                reverse_trans[symbol][target].add(source)

        # 4. Process the worklist
        while W:
            A = W.pop() # Get a partition from the worklist
            
            for symbol in self.alphabet:
                # X is the set of states that transition *into* A on *symbol*
                X = set()
                for target_state in A:
                    X.update(reverse_trans[symbol][target_state])
                
                # Refine P by splitting partitions based on X
                P_new = set()
                for Y in P: # For each partition Y in P
                    Y_intersect_X = Y.intersection(X)
                    Y_diff_X = Y.difference(X)
                    
                    if Y_intersect_X and Y_diff_X:
                        # Split Y into two new partitions
                        P_new.add(frozenset(Y_intersect_X))
                        P_new.add(frozenset(Y_diff_X))
                        
                        # Update worklist W
                        if Y in W:
                            W.remove(Y)
                            W.add(frozenset(Y_intersect_X))
                            W.add(frozenset(Y_diff_X))
                        else:
                            if len(Y_intersect_X) <= len(Y_diff_X):
                                W.add(frozenset(Y_intersect_X))
                            else:
                                W.add(frozenset(Y_diff_X))
                    else:
                        # No split, keep Y as is
                        P_new.add(Y)
                P = P_new # Update P with the refined partitions
        
        return P

    def _reconstruct_dfa(self, partitions):
        """
        Builds the new minimized DFA from the final partitions.
        Returns the DFA in the same internal dict format.
        """
        new_states = set()
        new_start_state = None
        new_final_states = set()
        new_transitions = {}
        
        # Map old state partitions (frozensets) to new state names (strings)
        partition_to_name = {p: _format_state_name(p) for p in partitions}
        
        # Map old state *names* to their new partition *name*
        old_state_to_new_name = {}
        for p, new_name in partition_to_name.items():
            for old_state in p:
                old_state_to_new_name[old_state] = new_name
        
        for p, new_name in partition_to_name.items():
            new_states.add(new_name)
            
            # Check for start state
            if self.start_state in p:
                new_start_state = new_name
            
            # Check for final state (if any old state in p was final, p is final)
            if not p.isdisjoint(self.final_states):
                new_final_states.add(new_name)

            # Build new transitions
            # All old states in a partition are indistinguishable,
            # so we can just pick one to find the new transition.
            representative_old_state = next(iter(p))
            new_transitions[new_name] = {}
            
            for symbol in self.alphabet:
                # Find where the representative state went in the *old* DFA
                old_target_state = self.transitions[representative_old_state][symbol]
                
                # Find the *new* state name for that old target state
                new_target_state = old_state_to_new_name[old_target_state]
                
                new_transitions[new_name][symbol] = new_target_state

        return {
            "states": new_states,
            "alphabet": self.alphabet,
            "transitions": new_transitions,
            "start_state": new_start_state,
            "final_states": new_final_states
        }

    def minimize(self):
        """
        Public method to run the full minimization pipeline.
        Returns the minimized DFA in the internal dict format.
        """
        print("1. Completing DFA by adding dead state (if needed)...", file=sys.stderr)
        self._complete_dfa()
        
        print("2. Removing unreachable states...", file=sys.stderr)
        self._remove_unreachable_states()
        
        # Store a copy of the reachable DFA for "before" comparison
        self.reachable_dfa = {
            "states": self.states.copy(),
            "alphabet": self.alphabet.copy(),
            "transitions": self.transitions.copy(),
            "start_state": self.start_state,
            "final_states": self.final_states.copy()
        }
        
        print("3. Running Hopcroft's minimization algorithm...", file=sys.stderr)
        final_partitions = self._hopcroft_algorithm()
        
        print(f"4. Reconstructing minimized DFA from {len(final_partitions)} partitions...", file=sys.stderr)
        minimized_dfa = self._reconstruct_dfa(final_partitions)
        
        print("\nMinimization complete.", file=sys.stderr)
        return minimized_dfa

# --- Standalone Functions for I/O and Display ---

def load_json_file(filepath):
    """Loads and parses a JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filepath}'. Check format.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return None

def print_transition_table(dfa_data):
    """
    Prints a clean, formatted transition table to the console
    from the internal DFA dict format.
    """
    states = dfa_data["states"]
    alphabet = sorted(list(dfa_data["alphabet"]))
    transitions = dfa_data["transitions"]
    start_state = dfa_data["start_state"]
    final_states = dfa_data["final_states"]

    if not states:
        print("DFA is empty.")
        return

    # Sort states for printing: start state first, then others
    def sort_key(state_name):
        if state_name == start_state:
            return (0, state_name)
        return (1, state_name)
    
    sorted_states = sorted(list(states), key=sort_key)
    
    # --- Print Header ---
    header = "State".ljust(15) + " | " + " | ".join(alphabet)
    print(header)
    print("-" * len(header))
    
    # --- Print Rows ---
    for state in sorted_states:
        row = ""
        
        # Add start/final markers
        prefix = ""
        if state in final_states:
            prefix += "*"
        if state == start_state:
            prefix += "→"
        
        row += (prefix + state).ljust(15) + " | "
        
        # Add transitions
        trans_cells = []
        for symbol in alphabet:
            target = transitions.get(state, {}).get(symbol, "Ø")
            trans_cells.append(target)
        
        row += " | ".join(trans_cells)
        print(row)

def save_dfa_to_json(dfa_data, filepath):
    """
    Saves the minimized DFA (in internal dict format) back to
    the JSON format required by the project.
    """
    output = {
        "alphabet": sorted(list(dfa_data["alphabet"])),
        "states": [],
        "transitions": []
    }
    
    for state_name in sorted(list(dfa_data["states"])):
        output["states"].append({
            "name": state_name,
            "is_start": state_name == dfa_data["start_state"],
            "is_final": state_name in dfa_data["final_states"]
        })
        
    for source, trans_map in dfa_data["transitions"].items():
        for symbol, target in trans_map.items():
            output["transitions"].append({
                "source": source,
                "target": target,
                "symbol": symbol
            })
            
    try:
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=4)
        print(f"\nSuccessfully saved minimized DFA to '{filepath}'")
    except Exception as e:
        print(f"\nError saving file: {e}", file=sys.stderr)

# --- Main Execution ---

def main():
    """
    Main CLI function to run the minimization tool.
    """
    print("====================================")
    print("  Program 2: DFA Minimization Tool  ")
    print("====================================")
    
    filepath = input("Enter path to input DFA JSON file: ")
    
    dfa_json_data = load_json_file(filepath)
    if dfa_json_data is None:
        return

    try:
        minimizer = DFAMinimizer(dfa_json_data)
        minimized_dfa = minimizer.minimize()

        print("\n--- Original DFA (Reachable) ---")
        print_transition_table(minimizer.reachable_dfa)
        
        print("\n--- Minimized DFA ---")
        print_transition_table(minimized_dfa)
        
        # --- Optional: Save to JSON ---
        print("\n------------------------------------")
        save = input("Save minimized DFA to a new JSON file? (y/n): ").strip().lower()
        if save == 'y':
            out_path = input("Enter output filename (e.g., minimized_dfa.json): ")
            if not out_path.endswith(".json"):
                out_path += ".json"
            save_dfa_to_json(minimized_dfa, out_path)
            
    except ValueError as e:
        print(f"\nAn error occurred during processing: {e}", file=sys.stderr)
    except Exception as e:
        print(f"\nAn unexpected critical error occurred: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

