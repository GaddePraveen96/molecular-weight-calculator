import streamlit as st
import re
from elements import atomic_weights

st.set_page_config(page_title="Molecular Weight Calculator", layout="centered")
st.title("🧪 Molecular Weight Calculator")
st.markdown("Enter a chemical formula like `C6H12O6`, `NaCl`, `Fe2(SO4)3`, or `CuSO4·5H2O`")

# Sidebar Guide
st.sidebar.title("📘 User Guide")
st.sidebar.markdown("""
- Enter chemical formulas (case-insensitive): `h2so4`, `nacl`, `C6H12O6`
- Supports parentheses, hydrates, nested groups
- Handles ambiguous cases like `NO2` vs. `No2` with intelligent fallback
- Warns if input is ambiguous (e.g., `No2` could be `No` or `N+O`)
""")

# Sample Inputs
sample_formulas = ["H2O", "NaCl", "C6H12O6", "Fe2(SO4)3", "CuSO4·5H2O", "No2", "LrCl3", "BhF6", "NO2"]
sample = st.selectbox("Try a sample formula:", sample_formulas)
user_input = st.text_input("Or enter your own formula", value=sample)


# --- Clean formula with smart disambiguation ---
def clean_formula(formula):
    formula = formula.strip().replace(" ", "")
    corrected = ""
    i = 0

    while i < len(formula):
        two_letter = formula[i:i+2].capitalize()  # e.g., "No"
        one_letter = formula[i].upper()

        is_two_valid = two_letter in atomic_weights
        is_one_valid = one_letter in atomic_weights

        if is_two_valid and is_one_valid:
            # Ambiguous: could be two-letter or one-letter + something else
            if (i + 2 < len(formula)) and formula[i+2].isdigit():
                # Looks like one-letter + something else (e.g., N + O2)
                st.warning(f"Ambiguous input at `{two_letter}` — assuming `{one_letter}` + `{formula[i+1]}`. If you meant `{two_letter}`, enter it separately.")
                corrected += one_letter
                i += 1
            else:
                # Default to one-letter still (likely more common)
                st.warning(f"Ambiguous input at `{two_letter}` — assuming `{one_letter}` + `{formula[i+1]}`. If you meant `{two_letter}`, enter it clearly.")
                corrected += one_letter
                i += 1

        elif is_two_valid:
            corrected += two_letter
            i += 2
        elif is_one_valid:
            corrected += one_letter
            i += 1
        elif formula[i].isdigit() or formula[i] in "()·.*":
            corrected += formula[i]
            i += 1
        else:
            i += 1  # skip invalid
    return corrected


# --- Parse formula into element counts ---
def parse_formula(formula):
    def multiply_group(group, multiplier):
        return {el: cnt * multiplier for el, cnt in group.items()}

    def merge_groups(base, addition):
        for el, cnt in addition.items():
            base[el] = base.get(el, 0) + cnt
        return base

    stack = []
    current = {}
    i = 0
    element_regex = re.compile(r"([A-Z][a-z]?)(\d*)")

    while i < len(formula):
        char = formula[i]

        if char == "(":
            stack.append(current)
            current = {}
            i += 1
        elif char == ")":
            i += 1
            mult = ''
            while i < len(formula) and formula[i].isdigit():
                mult += formula[i]
                i += 1
            mult = int(mult) if mult else 1
            last_group = stack.pop()
            current = merge_groups(last_group, multiply_group(current, mult))
        else:
            match = element_regex.match(formula, i)
            if match:
                el, count = match.groups()
                count = int(count) if count else 1
                if el not in atomic_weights:
                    st.error(f"Unknown element: `{el}`")
                    return None
                current[el] = current.get(el, 0) + count
                i += len(match.group(0))
            else:
                st.error(f"Invalid syntax at: `{formula[i:]}`")
                return None
    return current


# --- Handle hydrates and dot notation ---
def split_formula_parts(formula):
    return [f.strip() for f in re.split(r"[·.*]", formula) if f.strip()]


# --- Main Logic ---
if user_input:
    total_weight = 0.0
    all_parts = split_formula_parts(clean_formula(user_input))

    st.subheader("🧬 Element Breakdown")

    for part in all_parts:
        parsed = parse_formula(part)
        if parsed:
            subtotal = 0
            st.markdown(f"**{part}**")
            for el, count in parsed.items():
                weight = atomic_weights[el]
                line = f"{el} × {count} → {weight} × {count} = {weight * count:.3f} g/mol"
                st.write(line)
                subtotal += weight * count
            st.markdown(f"Subtotal: `{subtotal:.3f} g/mol`")
            total_weight += subtotal
            st.markdown("---")

    st.success(f"✅ **Molecular Weight: {total_weight:.3f} g/mol**")
