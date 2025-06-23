import streamlit as st
import re
from elements import atomic_weights

st.set_page_config(page_title="Molecular Weight Calculator", layout="centered")
st.title("🧪 Molecular Weight Calculator")
st.markdown("Enter a chemical formula like `C6H12O6`, `NaCl`, `Fe2(SO4)3`, or `CuSO4·5H2O`")

# Sidebar Guide
st.sidebar.title("📘 User Guide")
st.sidebar.markdown("""
- Supports `C6H12O6`, `NaCl`, `Fe2(SO4)3`, `CuSO4·5H2O`
- Autocorrects casing: `nacl` → `NaCl`, `h2so4` → `H2SO4`
- Handles ambiguous elements like `No`, `Lr`, `Bh`
- **Use correct casing**: 
  - `NO2` → Nitrogen Dioxide
  - `No2` → Nobelium × 2
""")

sample_formulas = ["H2O", "NaCl", "C6H12O6", "Fe2(SO4)3", "CuSO4·5H2O", "No2", "LrCl3", "NO2"]
sample = st.selectbox("Try a sample formula:", sample_formulas)
user_input = st.text_input("Or enter your own formula", value=sample)


# --- Smart formula cleaner with disambiguation ---
def clean_formula(formula):
    formula = formula.strip().replace(" ", "")
    corrected = ""
    i = 0

    # Ambiguous exotic elements
    exotic = {"No", "Lr", "Bh", "Mt", "Rf", "Db", "Sg", "Hs", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og"}

    while i < len(formula):
        if i + 1 < len(formula):
            two = formula[i].upper() + formula[i+1].lower()
            one = formula[i].upper()

            if two in exotic:
                # Check if user typed it in proper casing
                original = formula[i:i+2]
                if original != two:
                    st.warning(
                        f"Ambiguous input: `{original}` was interpreted as `{two}` (atomic weight = {atomic_weights[two]}). "
                        f"If you meant `{one}` + `{formula[i+1]}`, write it that way (e.g., `N` + `O2`)"
                    )
                corrected += two
                i += 2
                continue

        # Regular element (1 or 2 letter) match
        if i + 1 < len(formula) and (two := formula[i].upper() + formula[i+1].lower()) in atomic_weights:
            corrected += two
            i += 2
        elif (one := formula[i].upper()) in atomic_weights:
            corrected += one
            i += 1
        elif formula[i].isdigit() or formula[i] in "()·.*":
            corrected += formula[i]
            i += 1
        else:
            i += 1  # skip invalid characters
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
                st.write(f"{el} × {count} → {weight} × {count} = {weight * count:.3f} g/mol")
                subtotal += weight * count
            st.markdown(f"Subtotal: `{subtotal:.3f} g/mol`")
            total_weight += subtotal
            st.markdown("---")

    st.success(f"✅ **Molecular Weight: {total_weight:.3f} g/mol**")
