# Licensing scope

This project is licensed as three separate things: code, documentation, and the name. They are independent — do not conflate them.

| Subject | Licence | File |
|---|---|---|
| Code (`tools/`, all future implementation) | **GPL-3.0-only** | `LICENSE` |
| Documentation (`design/`, `docs/`, `AGENTS.md`, `README.*`) | **CC BY-4.0** | `LICENSE-DOCS` |
| Name and marks ("TonyOS") | All rights reserved — see the trademark policy | `TRADEMARK.md` |
| Outside contributions | Contributor License Agreement required | `CLA.md` |

SPDX identifiers: `GPL-3.0-only` for code, `CC-BY-4.0` for documentation.

## Why it is split this way

**Code uses GPL, not a permissive licence.**
Commercial use is entirely free — anyone may sell it, preinstall it, build it into a product — which is the only way a standard can form.
But modifications must be published, so nobody can take it into a closed fork and split the ecosystem.

**Why `-only` rather than `-or-later`.**
`-or-later` hands the decision about what a future licence version says to someone else. This project keeps that decision.
(The same reasoning Linus applied to GPLv2; we choose v3 because we want the patent grant and the anti-lockdown clause.)

**Why a CLA as well.**
GPL does not prevent dual licensing later, but only if you **own or control all of the code**. Without a grant, fifty contributed lines can block an entire commercial licence. The CLA solves exactly that and changes nothing about the project's promise to the community.

**Why documentation uses CC BY.**
Documentation's value is in being circulated and quoted, not locked up. CC BY-4.0 requires only credit — which is exactly what we want: **use these ideas, but say whose they are.**

## What is not here

There is no non-commercial clause. Anyone may make money with this and owes us nothing.
We give up licence fees in exchange for **being adopted, being preinstalled, becoming the reference**.
The moat is not in the licence. It is in the name, the official builds, and the fact that this design got here first.
