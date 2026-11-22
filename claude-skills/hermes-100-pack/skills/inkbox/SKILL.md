---
name: inkbox
description: Use an Inkbox agent identity (mailbox, SMS/MMS, iMessage, outbound phone calls, contacts) from Claude by calling the Inkbox Python SDK the same way the Hermes inkbox plugin does. Use when the user has INKBOX_API_KEY and INKBOX_IDENTITY and asks to "send an email from my agent's Inkbox address", "text this number", "send an iMessage", "look up / create / update an Inkbox contact", "list my Inkbox conversations", "place a call through Inkbox", or mentions Inkbox. Inbound messages, webhooks and voice stacks are NOT covered (see Limits).
---
# Inkbox (email, SMS, iMessage, calls, contacts)

**Hermes original:** https://github.com/inkbox-ai/hermes-agent-plugin @ 0948a16 · tier: community · category: platform · license: no LICENSE file found
**Port class:** C · the 33 outbound/read tools are thin wrappers over the public `inkbox` Python SDK and are reproducible; the gateway adapter (inbound routing, tunnel, voice bridges, A2A hooks) depends on the Hermes gateway.

## What the Hermes plugin does
A `kind: platform` plugin. It runs an adapter inside `hermes gateway` that opens an Inkbox tunnel, subscribes to mail/text/iMessage/call webhooks and routes inbound events into per-contact Hermes sessions; it adds `hermes inkbox setup|doctor|bootstrap` CLI commands and `pre_llm_call`, `pre_tool_call`, `post_tool_call` hooks (contact memories, A2A task progress). It registers tools: `inkbox_whoami`, contacts (`inkbox_lookup_contact`, `inkbox_list_contacts`, `inkbox_get_contact`, `inkbox_create_contact`, `inkbox_update_contact`, `inkbox_delete_contact`), `inkbox_send_email`, `inkbox_send_sms`, text conversations (`inkbox_list_text_conversations`, `inkbox_get_text_conversation`, `inkbox_list_texts`, `inkbox_get_text`, `inkbox_mark_text_read`, `inkbox_mark_text_conversation_read`), iMessage (`inkbox_imessage_triage_number`, `inkbox_send_imessage`, `inkbox_list_imessage_assignments`, `inkbox_list_imessage_conversations`, `inkbox_get_imessage_conversation`, `inkbox_send_imessage_reaction`, `inkbox_mark_imessage_conversation_read`), `inkbox_place_call`, and A2A tools (`inkbox_a2a_call|check|reply|complete|ask_caller|fail`, `inkbox_list_a2a_tasks|messages|sent_tasks`, `inkbox_get_a2a_sent_task`). It ships 13 bundled skills (email triage, SMS and iMessage responders, outreach sequence, contact lookup and rules, outbound calling, call review, identity/access, credential use, notes/memory, webhook providers, troubleshooting).

## Equivalent in Claude
Env vars (same names): `INKBOX_API_KEY` (required), `INKBOX_IDENTITY` (required handle), `INKBOX_BASE_URL` (optional; the plugin passes it to the SDK only when set, default is the SDK's own and is not in the plugin source).

Install the SDK the plugin depends on (verified: `pip index versions inkbox` lists `inkbox (0.7.40)`; the plugin pins `inkbox>=0.5.9,<1.0.0`):
```bash
pip install 'inkbox>=0.5.9,<1.0.0'
```
Client construction copied from the plugin source (`tools.py`):
```python
from inkbox import Inkbox
client = Inkbox(api_key=os.environ["INKBOX_API_KEY"])          # add base_url=... only if INKBOX_BASE_URL is set
identity = client.get_identity(os.environ["INKBOX_IDENTITY"])
```
| Hermes tool | SDK call per the plugin source |
|---|---|
| `inkbox_lookup_contact` / `list` / `get` / `create` / `update` / `delete` | `client.contacts.lookup(...)`, `.list(...)`, `.get(id)`, `.create(**fields)`, `.update(id, **fields)`, `.delete(id)` |
| `inkbox_send_email` | `identity.send_email(to=[...], subject=..., body_text=..., body_html=...)` |
| `inkbox_send_imessage` | `identity.send_imessage(conversation_id=..., text=...)` |
| `inkbox_place_call` | `identity.place_call(...)` (purpose, opening message, context, origination) |
| `inkbox_send_sms`, text/iMessage conversation tools, A2A tools | Methods on the identity object; names are not quoted in this port, inspect the SDK (`help(identity)`) before calling |
| `inkbox_whoami` | Read identity attributes (handle, mailbox, phone) from `identity` |

Before any send or call, restate recipient and content and get the user's confirmation. Use `conversationId` style replies for existing threads, as the tool schemas recommend.

## Setup
1. Get an Inkbox API key and identity handle (Inkbox Console or `hermes inkbox setup` on a Hermes install).
2. `export INKBOX_API_KEY=... INKBOX_IDENTITY=<handle>`; optionally `INKBOX_BASE_URL`.
3. `pip install 'inkbox>=0.5.9,<1.0.0'` in the Python Claude runs.

## Limits
- Inbound email/SMS/iMessage/call handling, webhook signature verification (`INKBOX_SIGNING_KEY`), the Inkbox tunnel (`INKBOX_PUBLIC_URL`, `INKBOX_TUNNEL_NAME`), voice stacks (`INKBOX_VOICE_STACK`, OpenAI Realtime, Inkbox TTS/STT), contact-memory injection and A2A progress hooks all live in the Hermes gateway adapter and are not reproduced.
- The 13 bundled skills are not copied: the repository has no LICENSE file. Their topics are listed above; the gist is: triage inbound mail by sender rules, keep SMS replies short, reply in the existing conversation, confirm before outreach, never paste credentials.
- Sending email/SMS/iMessage and placing calls costs money on the Inkbox account and transmits content to Inkbox (and to OpenAI if a Realtime voice stack is configured server-side).
- SDK method names other than those quoted above are not verified.

## Source
- Catalog entry (reviewed commit): https://github.com/inkbox-ai/hermes-agent-plugin/tree/0948a16679f09fcfc78ed3d9171604b2c853402c
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/inkbox.yaml
