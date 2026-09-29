---
name: Gemini model availability
description: Provider model compatibility and transient capacity behavior for the personal finance assistant.
---

The direct Google Gemini API may reject an older model for new accounts even when the request format and API key are valid. Current model availability can also vary by demand, so transient 429/5xx responses should receive short bounded retries.

**Why:** A valid key initially rejected the older default model, and the first replacement model returned a temporary high-demand response before a current flash preview model succeeded.

**How to apply:** Prefer a currently available flash model for routine finance chat, keep the model configurable through `GEMINI_MODEL`, and retry only transient capacity/server responses rather than authentication or request errors.