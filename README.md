A fast, intuitive app to calculate the molecular weight of chemical compounds — including hydrates, nested groups, and exotic elements.

🌐 Try it here:

📘 How to Use

Enter a chemical formula like:
H2O      → Water  
NaCl     → Sodium Chloride  
Fe2(SO4)3 → Iron(III) Sulfate  
CuSO4·5H2O → Copper(II) sulfate pentahydrate  
The app parses your formula, calculates element-wise contributions, and gives you the accurate molecular weight in g/mol.

⚠️ Formula Entry Guidelines

✅ Valid Examples
| Input        | Meaning                                |
| ------------ | -------------------------------------- |
| `NO2`        | Nitrogen dioxide (N + O₂)              |
| `No2`        | Nobelium (No) + 2 (not 2 atoms of No!) |
| `(No)2`      | Two atoms of Nobelium                  |
| `C6H12O6`    | Glucose                                |
| `Mg3(PO4)2`  | Magnesium phosphate                    |
| `CuSO4·5H2O` | Copper sulfate pentahydrate            |

Important Notes

Capitalization matters:

NO = Nitrogen + Oxygen

No = Nobelium (a distinct exotic element)

Use parentheses for exotic atoms if repeated:

✅ (No)2 → 2 Nobelium atoms

🚫 No2 → Nobelium + 2, not 2 Nobelium

Hydrates (·, *) are supported.

Extra characters or symbols will be auto-cleaned.

💻 Features

Intelligent parsing with nested brackets

Hydrate support (e.g., ·5H2O, *6H2O)

Formula autocorrection for ambiguous inputs

Warning system for exotic element ambiguity

🧪 Built With

Python

Streamlit

Custom parser with support for all 118 IUPAC-recognized elements
