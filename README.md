<p align="center">
  <img src="https://raw.githubusercontent.com/MKishoreDev/kagunebin-pypi/main/banner.png" alt="KaguneBin Banner">
</p>

<h1 align="center">KaguneBin</h1>

<h3 align="center">
🩸 Paste Fear. Share Power.
</h3>

<p align="center">
  Official Python SDK for KaguneBin
</p>

<p align="center">
  Create, retrieve, download, and manage pastes directly from Python.
</p>

---

# 🌌 About

KaguneBin is a modern paste sharing platform inspired by the dark aesthetic of Tokyo Ghoul.

Built for developers who want a fast, minimal, and privacy-focused way to share code snippets, logs, notes, and text online.

I wanted a paste service that felt:

* ⚡ Fast
* 🎯 Minimal
* 🔒 Secure
* 🩸 Beautiful
* 🧩 Developer Friendly

So KaguneBin was created.

The platform is live at:

🔗 https://kagunebin.vercel.app

After building the platform, I created this official Python SDK so developers can interact with KaguneBin directly from scripts, applications, automation workflows, and bots.

---

# ✨ Features

* 📝 Create pastes instantly
* 🔒 Password protected pastes
* 🔥 Burn-after-read support
* ⏳ Expiring pastes
* 📥 Download pastes
* 📄 Raw content access
* 📊 View tracking
* 🎨 Syntax highlighting support
* 🐍 Lightweight Python SDK

---

# 📦 Installation

```bash
pip install kagunebin
```

---

# ⚡ Quick Start

```python
from kagunebin import KaguneBin

kb = KaguneBin()

paste = kb.create(
    title="Hello World",
    content="print('Hello KaguneBin!')",
    syntax="python"
)

print(paste["url"])
```

---

# 📝 Create a Paste

```python
from kagunebin import KaguneBin

kb = KaguneBin()

paste = kb.create(
    title="Example",
    content="console.log('Hello World');",
    syntax="javascript"
)

print(paste)
```

---

# 🔒 Password Protected Paste

```python
paste = kb.create(
    title="Secret Notes",
    content="Top Secret",
    syntax="text",
    password="mypassword"
)
```

---

# 🔥 Burn After Read

```python
paste = kb.create(
    title="One Time Paste",
    content="This will self-destruct after viewing.",
    burn_after_read=True
)
```

---

# 📥 Retrieve a Paste

```python
paste = kb.get("kgn_12345678")

print(paste["content"])
```

Protected paste:

```python
paste = kb.get(
    "kgn_12345678",
    password="mypassword"
)
```

---

# 📄 Get Raw Content

```python
content = kb.raw("kgn_12345678")

print(content)
```

---

# 💾 Download a Paste

```python
data = kb.download("kgn_12345678")

with open("paste.txt", "wb") as f:
    f.write(data)
```

---

# 🎨 Available Syntaxes

```python
from kagunebin import KaguneBin

kb = KaguneBin()

print(kb.syntaxes())
```

---

# ✅ Validate Syntax

```python
kb.is_valid_syntax("python")
# True

kb.is_valid_syntax("py")
# False
```

---

# 📄 Example Response

```python
{
    "id": "kgn_a1b2c3d4",
    "title": "Hello World",
    "content": "print('Hello')",
    "syntax": "python",
    "url": "/p/kgn_a1b2c3d4",
    "is_protected": False,
    "is_burn_after_read": False,
    "views": 0,
    "downloads": 0,
    "created_at": "2026-05-30T12:00:00+00:00",
    "expires_at": None
}
```

---

# 🎯 Philosophy

KaguneBin focuses on simplicity.

No accounts.
No clutter.
No unnecessary friction.

Just create a paste and share it.

Fast.

Simple.

Developer-first.

---

# 🌍 Open Source

Contributions are welcome.

You can help by:

* Fixing bugs
* Improving documentation
* Suggesting features
* Improving SDK usability
* Creating integrations

Pull requests and issues are always welcome.

---

# 🔗 Links

| Platform            | Link                                          |
| ------------------- | --------------------------------------------- |
| 🌐 Website          | https://kagunebin.vercel.app                  |
| 📦 PyPI             | https://pypi.org/project/kagunebin/           |
| 💻 Docs             | https://kagunebin.vercel.app/docs             |
| 🩸 KaguneBin Source | https://github.com/MKishoreDev/KaguneBin      |

---

# 📄 License

MIT License © Kishore

---

<p align="center">
  <img src="https://img.shields.io/badge/Built%20with-Passion-ff1744?style=for-the-badge">
</p>

<p align="center">
  🩸 Made with passion by Kishore
</p>
