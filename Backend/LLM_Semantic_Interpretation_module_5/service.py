"""
Module 5 — Main Semantic Interpretation Service

Orchestrates:
  1. Load delivery schema
  2. Build LLM prompt from selected product + organization data
  3. Invoke Gemini LLM
  4. Parse and validate LLM response
  5. Enforce exact 252-column schema
  6. Return Module5Response
"""

import json
import os
import time
import uuid
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Load .env
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    load_dotenv()

from .models import Module5Response, ClassificationResult, CandidateField
from .schema_loader import empty_delivery_record, load_delivery_headers
from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

logger = logging.getLogger("module5")


class SemanticInterpretationService:
    """
    Module 5 Semantic Interpretation Service.
    Interprets selected Module 1 product + organization context via LLM
    and maps the result to the fixed 252-column delivery schema.
    """

    def __init__(self):
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.llm_model: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
        try:
            self.llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
        except ValueError:
            self.llm_temperature = 0.0

    # ──────────────────────────────────────────────────────────────────────────
    # Public entry point
    # ──────────────────────────────────────────────────────────────────────────

    def interpret(
        self,
        product: Dict[str, Any],
        organization: Optional[Dict[str, Any]] = None,
    ) -> Module5Response:
        start_ts = time.time()
        request_id = str(product.get("request_id", f"M5-{uuid.uuid4().hex[:8].upper()}"))
        selected_product_id = str(product.get("request_id", "UNKNOWN"))

        logger.info(
            "Module 5 | request_id=%s | product_id=%s | org_provided=%s",
            request_id, selected_product_id, organization is not None
        )

        try:
            delivery_record = empty_delivery_record()
            schema_headers = load_delivery_headers()

            if not self.gemini_api_key:
                logger.warning("Module 5 | No GEMINI_API_KEY — running schema-only fallback")
                delivery_record, metadata, classification = self._deterministic_fallback(
                    product, organization, delivery_record
                )
            else:
                delivery_record, metadata, classification = self._llm_interpret(
                    product, organization, delivery_record, schema_headers
                )

            # Enforce schema integrity: keep only known headers; force all values to str
            clean_record = {h: str(delivery_record.get(h, "")) for h in schema_headers}

            populated = sum(1 for v in clean_record.values() if v)
            inferred = sum(1 for m in metadata if m.source == "LLM_INFERENCE")
            elapsed = (time.time() - start_ts) * 1000

            logger.info(
                "Module 5 | populated=%d | inferred=%d | time_ms=%.1f",
                populated, inferred, elapsed
            )

            return Module5Response(
                request_id=request_id,
                selected_product_id=selected_product_id,
                status="CANDIDATE_GENERATED",
                processing_time_ms=round(elapsed, 1),
                populated_fields_count=populated,
                inferred_fields_count=inferred,
                delivery_record=clean_record,
                semantic_metadata=metadata,
                classification=classification,
            )

        except Exception as exc:
            logger.error("Module 5 | Interpretation failed: %s", exc, exc_info=True)
            elapsed = (time.time() - start_ts) * 1000
            return Module5Response(
                request_id=request_id,
                selected_product_id=selected_product_id,
                status="FAILED",
                processing_time_ms=round(elapsed, 1),
                delivery_record=empty_delivery_record(),
                error=f"Semantic interpretation failed: {str(exc)}",
            )

    # ──────────────────────────────────────────────────────────────────────────
    # LLM Interpretation
    # ──────────────────────────────────────────────────────────────────────────

    def _llm_interpret(
        self,
        product: Dict[str, Any],
        organization: Optional[Dict[str, Any]],
        delivery_record: Dict[str, str],
        schema_headers: List[str],
    ):
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import SystemMessage, HumanMessage

        product_json = json.dumps(product, indent=2, ensure_ascii=False)
        org_json = json.dumps(organization or {}, indent=2, ensure_ascii=False)
        schema_fields_str = "\n".join(schema_headers)

        user_content = USER_PROMPT_TEMPLATE.format(
            product_json=product_json,
            organization_json=org_json,
            schema_fields=schema_fields_str,
            field_count=len(schema_headers),
        )

        llm = ChatGoogleGenerativeAI(
            model=self.llm_model,
            google_api_key=self.gemini_api_key,
            temperature=self.llm_temperature,
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]

        response = llm.invoke(messages)
        raw = str(response.content).strip()

        parsed = self._safe_parse_llm_json(raw)
        return self._map_llm_output(parsed, delivery_record, schema_headers)

    # ──────────────────────────────────────────────────────────────────────────
    # Deterministic fallback (no LLM key)
    # ──────────────────────────────────────────────────────────────────────────

    def _deterministic_fallback(
        self,
        product: Dict[str, Any],
        organization: Optional[Dict[str, Any]],
        delivery_record: Dict[str, str],
    ):
        """Rule-based extraction when no LLM key is configured."""
        identity = product.get("identity") or {}
        raw = (product.get("source_record") or {}).get("raw") or {}
        org = organization or {}

        metadata: List[CandidateField] = []

        def set_field(field: str, value: str, source: str, itype: str, conf: float):
            if value:
                delivery_record[field] = str(value)
                metadata.append(CandidateField(
                    field=field, value=str(value),
                    source=source, interpretation_type=itype,
                    llm_confidence=conf, requires_validation=True
                ))

        # Identity fields
        set_field("Mfg_Part_Num", identity.get("part_number") or raw.get("Mfg_Part_Num", ""), "SOURCE_EVIDENCE", "IDENTITY", 0.95)
        set_field("MANUFACTURER_PART_NUMBER", identity.get("part_number") or raw.get("Mfg_Part_Num", ""), "SOURCE_EVIDENCE", "IDENTITY", 0.95)
        set_field("PART_NUMBER", identity.get("part_number") or raw.get("Mfg_Part_Num", ""), "SOURCE_EVIDENCE", "IDENTITY", 0.95)
        set_field("MANUFACTURER_NAME", identity.get("manufacturer") or raw.get("Part_Manuf", ""), "SOURCE_EVIDENCE", "IDENTITY", 0.90)
        set_field("Part_Manuf", identity.get("manufacturer") or raw.get("Part_Manuf", ""), "SOURCE_EVIDENCE", "IDENTITY", 0.90)
        set_field("Part_Desc", identity.get("product_name") or raw.get("Part_Desc", ""), "SOURCE_EVIDENCE", "IDENTITY", 0.90)
        set_field("SHORT_DESC", identity.get("product_name") or raw.get("Part_Desc", ""), "SOURCE_EVIDENCE", "DESCRIPTION", 0.85)
        set_field("Product Name", identity.get("product_name") or raw.get("Part_Desc", ""), "SOURCE_EVIDENCE", "DESCRIPTION", 0.85)

        brand = identity.get("brand") or raw.get("E1_Brand", "")
        if brand and brand.strip() and "unbranded" not in brand.lower():
            set_field("BRAND_NAME", brand, "SOURCE_EVIDENCE", "IDENTITY", 0.80)
        set_field("E1_Brand", raw.get("E1_Brand", ""), "SOURCE_EVIDENCE", "IDENTITY", 0.80)
        set_field("Unilog_Brand", raw.get("Unilog_Brand", ""), "SOURCE_EVIDENCE", "IDENTITY", 0.80)
        set_field("DIB_Brand", raw.get("DIB_Brand", ""), "SOURCE_EVIDENCE", "IDENTITY", 0.80)

        # Org context
        if org:
            set_field("Dept", str(org.get("Dept") or org.get("category", "")), "ORG_CONTEXT", "CLASSIFICATION", 0.70)
            set_field("Class", str(org.get("Class") or org.get("product_family", "")), "ORG_CONTEXT", "CLASSIFICATION", 0.70)

        classification = ClassificationResult(
            dept=delivery_record.get("Dept", ""),
            **{"class": delivery_record.get("Class", "")},
            fine=delivery_record.get("Fine", ""),
            classpath=delivery_record.get("Classpath", ""),
            confidence=0.70 if delivery_record.get("Dept") else 0.0,
            status="CANDIDATE"
        )

        return delivery_record, metadata, classification

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _safe_parse_llm_json(self, raw: str) -> Dict[str, Any]:
        """Strip markdown fences and parse JSON safely."""
        text = raw.strip()
        for fence in ("```json", "```"):
            if text.startswith(fence):
                text = text[len(fence):]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.error("Module 5 | Invalid LLM JSON: %s | raw snippet: %s", exc, text[:200])
            raise ValueError(f"LLM returned invalid JSON: {exc}") from exc

    def _map_llm_output(
        self,
        parsed: Dict[str, Any],
        delivery_record: Dict[str, str],
        schema_headers: List[str],
    ):
        """Map validated LLM output onto the delivery record and build metadata."""
        schema_set = set(schema_headers)
        metadata: List[CandidateField] = []

        # Map delivery_record fields — enforce schema, ignore unknown keys
        llm_record = parsed.get("delivery_record") or {}
        for key, val in llm_record.items():
            if key in schema_set:
                delivery_record[key] = str(val) if val is not None else ""

        # Map semantic_metadata
        for item in (parsed.get("semantic_metadata") or []):
            if isinstance(item, dict) and item.get("field") in schema_set:
                try:
                    metadata.append(CandidateField(
                        field=item["field"],
                        value=str(item.get("value", "")),
                        source=str(item.get("source", "LLM_INFERENCE")),
                        interpretation_type=str(item.get("interpretation_type", "SEMANTIC")),
                        llm_confidence=float(item.get("llm_confidence", 0.0)),
                        requires_validation=bool(item.get("requires_validation", True)),
                    ))
                except Exception:
                    pass

        # Map classification
        cls_raw = parsed.get("classification") or {}
        classification = ClassificationResult(
            dept=str(cls_raw.get("dept", "")),
            **{"class": str(cls_raw.get("class", ""))},
            fine=str(cls_raw.get("fine", "")),
            classpath=str(cls_raw.get("classpath", "")),
            confidence=float(cls_raw.get("confidence", 0.0)),
            status="CANDIDATE",
        )

        # Sync classification → delivery record
        if classification.dept and not delivery_record.get("Dept"):
            delivery_record["Dept"] = classification.dept
        if classification.class_ and not delivery_record.get("Class"):
            delivery_record["Class"] = classification.class_
        if classification.fine and not delivery_record.get("Fine"):
            delivery_record["Fine"] = classification.fine
        if classification.classpath and not delivery_record.get("Classpath"):
            delivery_record["Classpath"] = classification.classpath

        return delivery_record, metadata, classification
