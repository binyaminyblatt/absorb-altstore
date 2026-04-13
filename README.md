# 📱 AltStore Repo Generator

Automatically generate an **AltStore / SideStore source** from GitHub releases.

This project fetches IPA files from a GitHub repository, extracts metadata, and builds a fully compatible `apps.json` feed for AltStore-compatible distribution — fully automated via GitHub Actions.

---

## ✨ Features

* 🔄 Automatically processes GitHub releases
* 📦 Extracts IPA metadata (version, build, bundle ID, entitlements)
* 🧪 Supports **pre-releases (beta builds)**
* 📰 Generates AltStore **news entries**
* ⚡ Fully automated via **GitHub Actions**
* 🌐 Includes a web UI for installation
* 🔗 Fully dynamic URLs (works on forks + custom domains)
* 🧠 Centralized configuration via `repovars.py`

---

## 🚀 Setup

### 1. Fork this repository

Click **Fork** and clone your copy.

---

### 2. Configure the repo

All configurable values are stored in:

```id="q7j8xv"
repovars.py
```

This file controls everything the generator needs, including:

```python id="k0xq8s"
source = {
    # AltStore source metadata
}

app = {
    # App configuration (name, bundle ID, icons, etc.)
}
```

---

### 3. Edit configuration

Open `repovars.py` and update:

#### 📦 Source settings

* repo name
* description
* icon
* tint color
* homepage

#### 📱 App settings

* app name
* bundle identifier
* screenshots
* developer name
* default metadata

👉 This replaces all previous `.env` / GitHub variable configuration.

---

### 4. GitHub Actions

The workflow will:

* Run every hour ⏱
* Fetch latest releases
* Process IPA files
* Use `repovars.py` for configuration
* Generate `apps.json`
* Deploy to GitHub Pages

No secrets or environment variables required.

---

### 5. Enable GitHub Pages

Go to:

```id="v0v9gn"
Settings → Pages
```

Set:

* Source: `Deploy from branch`
* Branch: `pages`

---

### 6. Done 🎉

Your AltStore source will be available at:

```id="5x9m9j"
https://YOUR_USERNAME.github.io/YOUR_REPO/apps.json
```

---

## 📲 Install in AltStore / SideStore

```id="g6v8qo"
altstore://source?url=https://YOUR_USERNAME.github.io/YOUR_REPO/apps.json
```

```id="9r6h8v"
sidestore://source?url=https://YOUR_USERNAME.github.io/YOUR_REPO/apps.json
```

---

## 🧠 How it works

1. GitHub Actions fetches releases
2. IPA is downloaded and inspected
3. `Info.plist` + binary metadata extracted
4. Configuration is loaded from `repovars.py`
5. `apps.json` is generated
6. Published via GitHub Pages

---

## 📁 Project Structure

```id="m2d9qk"
.
├── generate.py        # Main generator
├── repovars.py        # 🔧 ALL CONFIGURATION
├── index.html         # Web UI
├── out/               # Generated apps.json
├── cache/             # Release tracking
└── .github/workflows/ # Automation
```

---

## ⚠️ Notes

* All customization is done in `repovars.py`
* Pre-releases are supported
* Draft releases are ignored
* Latest version is shown first in AltStore
* No environment variables required

---

## 🔥 Future Improvements

* Multi-app support
* Screenshot gallery UI
* Beta/stable split feeds
* Version history browser
* Faster IPA parsing (no extraction)

---

## 📄 License

MIT (or your choice)

---

## 🙌 Credits

* AltStore / SideStore ecosystem
* GitHub API
