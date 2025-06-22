import streamlit as st
import re
from elements import atomic_weights

st.set_page_config(page_title="Molecular Weight Calculator", layout="centered")
st.title("🧪 Molecular Weight Calculator")
st.markdown("Enter a chemical formula like `C6H12O6`, `NaCl`, `Fe2(SO4)3`, or `CuSO4·5H2O`")

# Sidebar guide
st.sidebar.title("📘 User Guide")
st.sidebar.markdown("""
- ✅ Enter any chemical formula using standard notation
- ✅ Works with hydrates (`CuSO4·5H2O`, `BaCl2.2H2O`)
- ✅ Accepts any case: `h2so4`, `NACL`, `fe(so4)3`
- 🚫 Charge states (`NH4+`, `[Fe(CN)6]4−`) currently not supported
""")

# Sample inputs
sample_formulas = ["H2O", "NaCl", "C6H12O6", "Fe2(SO4)3", "CuSO4·5H2O"]
sample = st.selectbox("Try a sample formula:", sample_formulas)
user_input = st.text_input("Or enter your own formula", value=sample)


# 1. Case-correction function
def clean_formula(formula):
    formula = formula.strip().replace(" ", "")
    corrected = ""
    i = 0
    symbols = sorted(atomic_weights.keys(), key=lambda x: -len(x))  # Match longest first

    while i < len(formula):
        matched = False
        for symbol in symbols:
            length = len(symbol)
            if formula[i:i+length].lower() == symbol.lower():
                corrected += symbol
                i += length
                matched = True
                break
        if not matched:
            if formula[i].isdigit() or formula[i] in "()":
                corrected += formula[i]
                i += 1
            elif formula[i] in [".", "·", "*"]:  # treat as hydrate separator
                corrected += "·"
                i += 1
            else:
                # Skip invalid character or add error handling
                i += 1
    return corrected


# 2. Formula parser
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


# 3. Split on hydrate separators (·, ., *)
def split_formula_parts(formula):
    return [f.strip() for f in re.split(r"[·.*]", formula) if f.strip()]


# 4. Main logic
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
