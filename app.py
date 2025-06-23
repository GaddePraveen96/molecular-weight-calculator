import streamlit as st
import re
from elements import atomic_weights

st.set_page_config(page_title="Molecular Weight Calculator", layout="centered")
st.title("🧪 Molecular Weight Calculator")
st.markdown("Enter a chemical formula like `C6H12O6`, `NaCl`, `Fe2(SO4)3`, or `CuSO4·5H2O`")

# Sidebar Guide
st.sidebar.title("📘 User Guide")
st.sidebar.markdown("""
- Enter chemical formulas (case-insensitive): `H2SO4`, `NaCl`, `C6H12O6`
- Use proper element casing: `NO2` for Nitrogen Dioxide (not `No2`, which is Nobelium)
- Supports parentheses, hydrates (`·`), nested groups
""")

sample_formulas = ["H2O", "NaCl", "C6H12O6", "Fe2(SO4)3", "CuSO4·5H2O", "NO2", "Mg3(PO4)2"]
sample = st.selectbox("Try a sample formula:", sample_formulas)
user_input = st.text_input("Or enter your own formula", value=sample)

# --- Clean formula with improved autocorrection ---
def clean_formula(formula):
    formula = formula.strip().replace(" ", "")
    corrected = ""
    i = 0

    while i < len(formula):
        # Two-letter element symbol
        if i + 1 < len(formula):
            two_letter = formula[i].upper() + formula[i+1].lower()
            if two_letter in atomic_weights:
                corrected += two_letter
                i += 2
                continue

        # One-letter element
        one_letter = formula[i].upper()
        if one_letter in atomic_weights:
            corrected += one_letter
            i += 1
        elif formula[i].isdigit() or formula[i] in "()·.*":
            corrected += formula[i]
            i += 1
        else:
            i += 1  # skip unknown character

    return corrected

# --- Formula Part Splitter ---
def split_formula_parts(formula):
    return [f.strip() for f in re.split(r"[·.*]", formula) if f.strip()]

# --- Parser ---
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
            last = stack.pop()
            current = merge_groups(last, multiply_group(current, mult))
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

# --- Suggestion logic for common confusion ---
def suggest_common_mistakes(raw_formula, cleaned_formula):
    if raw_formula.lower() == "no2" and cleaned_formula == "No2":
        st.warning("`No2` was interpreted as **Nobelium (No) × 2**.\n\nDid you mean **Nitrogen Dioxide** (`NO2`)? Try using capital letters: `NO2`.")
    if raw_formula.lower() == "co" and cleaned_formula == "Co":
        st.warning("`Co` was interpreted as **Cobalt**. If you meant **Carbon Monoxide**, try typing `CO`.")

# --- Main Logic ---
if user_input:
    cleaned = clean_formula(user_input)
    suggest_common_mistakes(user_input, cleaned)

    all_parts = split_formula_parts(cleaned)
    total_weight = 0.0

    st.subheader("🧬 Element Breakdown")

    for part in all_parts:
        parsed = parse_formula(part)
        if parsed:
            subtotal = 0
            st.markdown(f"**{part}**")
            for el, count in parsed.items():
                weight = atomic_weights[el]
                st.write(f"{el} × {count} → {weight} × {count} = {weight * count:.3f} g/mol")
                subtotal += weight * count
            total_weight += subtotal
            st.markdown(f"Subtotal: `{subtotal:.3f} g/mol`")
            st.markdown("---")

    st.success(f"✅ **Molecular Weight: {total_weight:.3f} g/mol**")
