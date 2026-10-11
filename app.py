from __future__ import annotations

import re
from typing import Optional

import requests
from flask import Flask, render_template, url_for

app = Flask(__name__)

LINKEDIN_URL = "https://www.linkedin.com/in/shafiul-akhtar-9606b3116"


def normalize_image_url(raw_url: str) -> str:
    if raw_url.startswith("//"):
        return "https:" + raw_url
    return raw_url


def fetch_linkedin_profile_image(profile_url: str) -> Optional[str]:
    """Try to extract a public profile image from the LinkedIn page.

    This is best-effort, because LinkedIn often blocks non-browser bots. When the
    request fails or the URL is not exposed, the app falls back to a local asset.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(profile_url, headers=headers, timeout=15)
        response.raise_for_status()
        text = response.text

        patterns = [
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
            r'<img[^>]+src=["\']([^"\']+)["\']',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                image_url = normalize_image_url(match.group(1))
                if image_url.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".svg")):
                    return image_url

        image_candidates = re.findall(r'https?:\/\/[^\"\'\s>]+\.(?:jpg|jpeg|png|webp|svg)', text, re.IGNORECASE)
        for candidate in image_candidates:
            if "linkedin" in candidate.lower() or "media" in candidate.lower() or "profile" in candidate.lower():
                return candidate
    except requests.RequestException:
        return None

    return None


def build_context(page_title: str):
    profile_image_url = url_for("static", filename="images/profile_placeholder.png", _external=True)
    logo_url = url_for("static", filename="images/logo.png", _external=True)
    return {
        "page_title": page_title,
        "linkedin_url": LINKEDIN_URL,
        "profile_image_url": profile_image_url,
        "logo_url": logo_url,
        "favicon_url": logo_url,
    }


@app.route("/")
def home():
    return render_template("index.html", **build_context("Home"))


@app.route("/about")
def about():
    return render_template("about.html", **build_context("About"))


@app.route("/projects")
def projects():
    return render_template("projects.html", **build_context("Projects"))


@app.route("/contact")
def contact():
    return render_template("contact.html", **build_context("Contact"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
