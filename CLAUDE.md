# Working rules for Claude in this repository

## Delegate to agents first
"Quantum Agents" is the owner's name for Claude's agents: subagents, workflows and task
sessions, including task cards that start a Claude session on the owner's own computer.
Assign every step an agent can do to an agent. Never ask the owner to do a step an agent can do.
Ask the owner only for what no agent can perform: an approval click, a login, or an action on a
computer no session can reach. Then say once what is blocked and why, and name the single
smallest action that unblocks it.

## Reaching the owner's Mac
Cloud sessions cannot reach the owner's MacBook Air (Remote Control folders reported
`not_available` on 2026-11-21). Agents spawned from a cloud session share its container and
cannot reach the Mac either. For work on the Mac, queue a task card the owner starts on the
Mac, or work from a session started on the Mac.
