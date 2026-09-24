"""SLM + LLM cascade router that proves its own savings.

A small local model answers each query; a local verifier decides whether to
trust it; only distrusted answers escalate to a large hosted model. The harness
then proves whether that routing was worth it, by comparing accuracy at a
matched routing rate against random and oracle controls.
"""

__version__ = "0.1.0"
