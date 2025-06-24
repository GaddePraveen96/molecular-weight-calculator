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
  - `(No)2` → 2 molecules of Nobelium
  - `CuSO4·5H2O` → Hydrate format
""")

sample_formulas = ["H2O", "NaCl", "C6H12O6", "Fe2(SO4)3", "CuSO4·5H2O", "No2", "LrCl3", "NO2"]
sample = st.selectbox("Try a sample formula:", sample_formulas)
user_input = st.text_input(
    "Or enter your own formula",
    value=sample,
    help=(
        "📌 Use correct casing: NO2 ≠ No2\n"
        "🧪 Wrap exotic elements in parentheses if repeated: (No)2, (Lr)3\n"
        "💧 For hydrates, use dot: CuSO4·5H2O or CuSO4.5H2O\n"
        "🧠 Examples: Fe2(SO4)3, NaCl, C6H12O6"
    )
)

# --- Smart formula cleaner with disambiguation ---
def clean_formula(formula):
    formula = formula.strip().replace(" ", "")
    corrected = ""
    i = 0

    # Elements known to cause confusion — exotic, less common in real formulas
    exotic_elements = {"No", "Lr", "Mt", "Rf", "Db", "Bh", "Hs", "Cn", "Fl", "Lv", "Mc", "Ts", "Og"}

    common_split_preference = {
        "NO2": ("N", "O2"), "NO3": ("N", "O3"), "NO4": ("N", "O4"),
        "LR3": ("L", "R3"), "MT2": ("M", "T2"), "MT3": ("M", "T3"),
        "CN2": ("C", "N2"), "CN3": ("C", "N3"), "CN4": ("C", "N4"),
        "OG2": ("O", "G2"), "OG3": ("O", "G3"), "OG4": ("O", "G4"),
        "DB2": ("D", "B2"), "DB3": ("D", "B3"), "TS2": ("T", "S2"),
        "TS3": ("T", "S3"), "FL2": ("F", "L2"), "FL3": ("F", "L3"),
        "MC2": ("M", "C2"), "MC3": ("M", "C3"),
    }

    while i < len(formula):
        if i + 2 < len(formula):
            triplet = formula[i:i+3].upper()
            if triplet in common_split_preference:
                el1, el2 = common_split_preference[triplet]
                st.warning(f"Ambiguous formula `{triplet}` detected. Interpreting as `{el1}` + `{el2}` instead of exotic element.")
                corrected += el1 + el2
                i += 3
                continue

        if i + 1 < len(formula):
            two_letter = formula[i].upper() + formula[i+1].lower()
            if two_letter in atomic_weights:
                corrected += two_letter
                i += 2
                continue

        one_letter = formula[i].upper()
        if one_letter in atomic_weights:
            corrected += one_letter
            i += 1
        elif formula[i].isdigit() or formula[i] in "()·.*":
            corrected += formula[i]
            i += 1
        else:
            i += 1

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
            last_group = stack.pop() if stack else {}
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
