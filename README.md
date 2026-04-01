# pyrecodes

**pyrecodes** is an open-source Python library for regional disaster recovery simulation and resilience assessment of the built environment, based on the [iRe-CoDeS framework](https://www.research-collection.ethz.ch/handle/20.500.11850/605682) developed at ETH Zurich.

[![Documentation](https://img.shields.io/badge/docs-online-blue)](https://nikolablagojevic.github.io/pyrecodes/html/index.html)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-≥3.9-blue)](https://www.python.org/)

---

## What it does

pyrecodes simulates how communities and infrastructure systems recover after disasters by modeling:

- **Component damage and functionality** — how damage affects the ability of components to supply resources
- **Resource distribution** — how operation and recovery resources flow among interdependent components
- **Recovery activities** — how repair and restoration restore functionality over time
- **Resilience metrics** — quantification of unmet resource demand during the recovery period

It integrates with [NHERI SimCenter R2DTool](https://nheri-simcenter.github.io/R2D-Documentation/), [REWET](https://doi.org/10.1061/JITSE4.ISENG-2427) (water network simulator), and residual demand traffic simulators via JSON-based APIs.

Starting from v0.3, pyrecodes also supports **LLM-driven household agents** that make post-disaster relocation decisions based on damage state, infrastructure access, and socio-economic characteristics.

---

## Installation

**Don't have Python?** Download and install Python 3.9+ from [python.org](https://www.python.org/downloads/). On macOS, you can also use `brew install python`. On Windows, make sure to check "Add Python to PATH" during installation.

**Quick setup (virtual environment + install) — run in terminal:**

macOS / Linux:
```bash
python -m venv env && source env/bin/activate && pip install pyrecodes                              # Core only (Examples 1–4)
python -m venv env && source env/bin/activate && pip install "pyrecodes[household]"                  # + LLM household agents (Example 6)
python -m venv env && source env/bin/activate && pip install "pyrecodes[third_party_models]"         # + REWET & traffic simulators (Example 5)
python -m venv env && source env/bin/activate && pip install "pyrecodes[household,third_party_models]" # Full install (Example 7)
```

Windows (run each line separately in Command Prompt):
```bash
python -m venv env
env\Scripts\activate
pip install pyrecodes                                # Core only (Examples 1–4)
pip install "pyrecodes[household]"                   # + LLM household agents (Example 6)
pip install "pyrecodes[third_party_models]"          # + REWET & traffic simulators (Example 5)
pip install "pyrecodes[household,third_party_models]" # Full install (Example 7)
```

**Core:**
```bash
pip install pyrecodes
```

**With household / LLM agents (Examples 6–7):**
```bash
pip install "pyrecodes[household]"
```

**With third-party infrastructure simulators (Example 5):**
```bash
pip install "pyrecodes[third_party_models]"
```

**Full (Example 7 — household agents + REWET + traffic):**
```bash
pip install "pyrecodes[household,third_party_models]"
```

> **Examples 5 and 7** require x86_64 Python — `wntrfr` and `pandana` do not provide arm64 wheels. On macOS with Apple Silicon, use the x86_64 Python installer from [python.org](https://www.python.org/downloads/) (runs via Rosetta 2), or a conda x86_64 environment. `third_party_models` also pins `numpy<2` due to a `pandana` binary compatibility constraint.
>
> See the [installation page](https://nikolablagojevic.github.io/pyrecodes/html/usage/installation.html) for full setup instructions.

---

## Quick start

```python
from pyrecodes import main

# run from the repository root folder
system = main.run('Example 1', 'ThreeLocalitiesCommunity_Main.json')
```

All examples are Jupyter notebooks in the `Example 1/` – `Example 7/` folders. **Run notebooks from the repository root** — input files are resolved using relative paths.

---

## Examples

| Example | Description |
|---------|-------------|
| [Example 1](https://nikolablagojevic.github.io/pyrecodes/html/usage/examples/example_1.html) | Three-locality community — simplest starting point |
| [Example 2](https://nikolablagojevic.github.io/pyrecodes/html/usage/examples/example_2.html) | Virtual community with complex infrastructure interdependencies |
| [Example 3](https://nikolablagojevic.github.io/pyrecodes/html/usage/examples/example_3.html) | R2DTool integration — regional risk assessment pipeline |
| [Example 4](https://nikolablagojevic.github.io/pyrecodes/html/usage/examples/example_4.html) | Interdependent infrastructure interfaces |
| [Example 5](https://nikolablagojevic.github.io/pyrecodes/html/usage/examples/example_5.html) | REWET and traffic simulator APIs — requires `[third_party_models]`, x86_64 |
| [Example 6](https://nikolablagojevic.github.io/pyrecodes/html/usage/examples/example_6.html) | LLM household agent validation against US Census Household Pulse Survey — requires `[household]`, notebook-only |
| [Example 7](https://nikolablagojevic.github.io/pyrecodes/html/usage/examples/example_7.html) | Socio-technical recovery with LLM-driven household displacement — requires `[household,third_party_models]`, x86_64 |

---

## Documentation

Full documentation, including API reference and user guide, is available at:
**https://nikolablagojevic.github.io/pyrecodes/html/index.html**

---

## Citation

If you use pyrecodes in your research, please cite it using the information on the [How to Cite](https://nikolablagojevic.github.io/pyrecodes/html/usage/how_to_cite.html) page.

---

## License

pyrecodes is released under the [BSD 3-Clause License](LICENSE).

Developed at the [Chair of Structural Dynamics and Earthquake Engineering](https://stojadinovic.ibk.ethz.ch/), ETH Zurich, Switzerland, and the [Stanford Urban Resilience Initiative](https://urbanresilience.stanford.edu/), Stanford University, USA.
