# Project Rules & Architecture Guidelines

## ProductDNA Architecture (8-Module Pipeline)

Always adhere to and build according to the following 8-module pipeline architecture order:

1. **Module 1 — Product Input / Standardization**
   - Takes raw product input such as CSV, PDF, URL, or text.
   - Extracts and standardizes basic product identity (candidates only).
   - Produces structured `StandardProductInput` (saved in `Backend/input_data/Standard_input/`).

2. **Module 2 — Evidence Collection**
   - Finds relevant product sources.
   - Collects manufacturer pages, datasheets, manuals, PDFs, and other reliable sources.
   - Provides source material for downstream processing.

3. **Module 3 — Evidence Extraction**
   - Reads the collected evidence.
   - Extracts product identifiers, specifications, attributes, and relevant claims.
   - Converts unstructured evidence into structured information.

4. **Module 4 — Product Resolution Engine**
   - Uses Module 1 identity + Module 5 extracted information.
   - Matches the product against the organization's Product Registry.
   - Uses SKU, part number, manufacturer + model, product name, and aliases.
   - Produces `RESOLVED`, `AMBIGUOUS`, or `UNRESOLVED` results.

5. **Module 5 — LLM / Semantic Interpretation**
   - Interprets extracted product information.
   - Normalizes terminology, values, and units.
   - Reasons across evidence.
   - Generates candidate claims.

6. **Module 6 — Validation Layer**
   - Verifies claims against evidence.
   - Handles conflicting information.
   - Calculates confidence.
   - Confirms which product information can be trusted.

7. **Module 7 — ProductDNA Builder**
   - Takes validated identity and claims.
   - Builds the canonical ProductDNA.
   - Organizes the final structured product knowledge.

8. **Module 8 — Delivery / Output Mapper**
   - Converts ProductDNA into the required delivery format.
   - Maps fields to the required Unilog schema.
   - Produces the final 252-column output.
