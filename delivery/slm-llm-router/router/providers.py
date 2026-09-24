"""Provider adapters. This is what makes the large tier NOT tied to Groq.

Every backend returns the same Answer shape: text + input/output token counts.
Real backends are imported lazily, so an offline `mock` run needs none of them.

Supported backends:
  mock              - deterministic simulation, zero network (default, offline)
  ollama            - local models via the Ollama HTTP API ($0)
  openai_compatible - Groq / OpenAI / Together / OpenRouter / vLLM / LM Studio
  anthropic         - Claude via the Anthropic SDK
  bedrock           - Claude (or others) via Amazon Bedrock + boto3
"""
from __future__ import annotations

import hashlib
import os
import random
from dataclasses import dataclass

from . import cache
from .config import ModelSpec


@dataclass
class Answer:
    text: str
    input_tokens: int
    output_tokens: int


def _est_tokens(s: str) -> int:
    # ~4 chars/token is close enough for costing when a backend omits usage.
    return max(1, round(len(s) / 4))


# ---------------------------------------------------------------------------
# Mock backend: the offline brain of the project.
#
# It answers the shipped eval questions using each question's ground truth and a
# difficulty score, so the whole harness (verifier, matrix, deferral curve,
# stats, charts) runs with zero network and still tells an honest story:
#   - the small tier gets easy questions right and hard ones wrong,
#   - the large tier gets almost everything right,
#   - self-consistency across samples wobbles more on hard questions,
# so the cascade bows above random but below the oracle ceiling.
# ---------------------------------------------------------------------------
def _rng(*parts) -> random.Random:
    h = hashlib.sha256("\x1f".join(str(p) for p in parts).encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def _mock_complete(spec: ModelSpec, prompt: str, role: str, sample: int, meta: dict) -> Answer:
    qid = meta.get("id", prompt)
    difficulty = float(meta.get("difficulty", 0.5))  # 0 easy .. 1 hard
    truth = str(meta.get("answer", ""))
    distractor = str(meta.get("distractor", "")) or _wrong(truth, qid)

    if role == "large":
        # Strong model: right ~97% regardless of difficulty.
        r = _rng("large", qid, sample)
        correct = r.random() > 0.03
        text = truth if correct else distractor
        return Answer(text, _est_tokens(prompt), _est_tokens(text) + 40)

    # Small model. Probability correct falls with difficulty.
    p_correct = max(0.05, 0.98 - 0.9 * difficulty)
    r = _rng("small", qid, sample)
    correct = r.random() < p_correct
    text = truth if correct else distractor
    # Hard questions also make the SLM hedge more (verifier signal).
    if role == "small" and _rng("hedge", qid, sample).random() < 0.5 * difficulty:
        text = text + " (I'm not entirely sure)"
    return Answer(text, _est_tokens(prompt), _est_tokens(text) + 12)


def _wrong(truth: str, seed) -> str:
    r = _rng("wrong", truth, seed)
    if truth.lstrip("-").isdigit():
        return str(int(truth) + r.choice([-3, -2, -1, 1, 2, 3, 10]))
    pool = ["negative", "positive", "neutral", "unknown", "N/A", "none", "0000"]
    cand = [p for p in pool if p.lower() != truth.lower()]
    return r.choice(cand) if cand else "unknown"


# ---------------------------------------------------------------------------
# Real backends (lazy imports).
# ---------------------------------------------------------------------------
def _ollama_complete(spec: ModelSpec, prompt: str, temperature: float) -> Answer:
    import json
    import urllib.request

    body = json.dumps(
        {
            "model": spec.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
    ).encode()
    req = urllib.request.Request(
        spec.base_url.rstrip("/") + "/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    text = data.get("response", "").strip()
    pt = data.get("prompt_eval_count") or _est_tokens(prompt)
    ct = data.get("eval_count") or _est_tokens(text)
    return Answer(text, int(pt), int(ct))


def _openai_compatible_complete(spec: ModelSpec, prompt: str, temperature: float) -> Answer:
    from openai import OpenAI  # pip install openai

    api_key = os.environ.get(spec.api_key_env, "") or "not-needed"
    client = OpenAI(base_url=spec.base_url or None, api_key=api_key)
    resp = client.chat.completions.create(
        model=spec.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    text = (resp.choices[0].message.content or "").strip()
    usage = resp.usage
    pt = getattr(usage, "prompt_tokens", None) or _est_tokens(prompt)
    ct = getattr(usage, "completion_tokens", None) or _est_tokens(text)
    return Answer(text, int(pt), int(ct))


def _anthropic_complete(spec: ModelSpec, prompt: str, temperature: float) -> Answer:
    import anthropic  # pip install anthropic

    kwargs = {}
    if spec.base_url:
        kwargs["base_url"] = spec.base_url
    client = anthropic.Anthropic(**kwargs)
    msg = client.messages.create(
        model=spec.model,
        max_tokens=512,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()
    pt = msg.usage.input_tokens
    ct = msg.usage.output_tokens
    return Answer(text, int(pt), int(ct))


def _bedrock_complete(spec: ModelSpec, prompt: str, temperature: float) -> Answer:
    import json

    import boto3  # pip install boto3

    client = boto3.client("bedrock-runtime", region_name=spec.extra.get("region", "us-east-1"))
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
    )
    resp = client.invoke_model(modelId=spec.model, body=body)
    payload = json.loads(resp["body"].read())
    text = "".join(b.get("text", "") for b in payload.get("content", [])).strip()
    usage = payload.get("usage", {})
    pt = usage.get("input_tokens") or _est_tokens(prompt)
    ct = usage.get("output_tokens") or _est_tokens(text)
    return Answer(text, int(pt), int(ct))


_BACKENDS = {
    "ollama": _ollama_complete,
    "openai_compatible": _openai_compatible_complete,
    "anthropic": _anthropic_complete,
    "bedrock": _bedrock_complete,
}


def complete(
    spec: ModelSpec,
    prompt: str,
    *,
    role: str = "small",
    sample: int = 0,
    temperature: float = 0.0,
    meta: dict | None = None,
    use_cache: bool = True,
) -> Answer:
    """Answer `prompt` with tier `spec`. role is "small" or "large"."""
    meta = meta or {}
    if spec.backend == "mock":
        return _mock_complete(spec, prompt, role, sample, meta)

    ck = cache.key(spec.name, spec.model, role, sample, temperature, prompt)
    if use_cache:
        hit = cache.get(ck)
        if hit is not None:
            return Answer(hit["text"], hit["input_tokens"], hit["output_tokens"])

    fn = _BACKENDS.get(spec.backend)
    if fn is None:
        raise ValueError(f"unknown backend: {spec.backend}")
    ans = fn(spec, prompt, temperature)

    if use_cache:
        cache.put(ck, {"text": ans.text, "input_tokens": ans.input_tokens, "output_tokens": ans.output_tokens})
    return ans
