"""Subject themes: colours + cover art. Every colour becomes a CSS variable."""

THEMES = {
    "microbiology": dict(p="#1d6b6f", pdk="#12464a", p2="#5fa9a0", acc="#e07a5f", accdk="#b4553c",
                         tint="#e6f2f0", soft="#f2f8f7", warm="#fbf3e8", warm_line="#efdcc4", line="#d3e2df",
                         art=None, keys=["microbio", "مجهري", "bacteri"]),
    "histology": dict(p="#6d3a7c", pdk="#45214f", p2="#a77bb5", acc="#d9608c", accdk="#a83f66",
                      tint="#f1e8f4", soft="#f8f3f9", warm="#fcf1f4", warm_line="#f1d6df", line="#e2d4e7",
                      art=None, keys=["histo", "أنسجة", "نسيج"]),
    "physiology": dict(p="#24508a", pdk="#163459", p2="#6f98c9", acc="#d9534f", accdk="#a8322f",
                       tint="#e8eff8", soft="#f3f7fc", warm="#fbf2ec", warm_line="#f0dbcd", line="#d4deeb",
                       art="physiology.svg", keys=["physio", "فسلج", "وظائف الأعضاء"]),
    "parasitology": dict(p="#56692a", pdk="#37441a", p2="#94a865", acc="#d9932f", accdk="#a86d1c",
                         tint="#eef2e3", soft="#f6f8ef", warm="#fbf4e6", warm_line="#efe0c2", line="#dde4cc",
                         art=None, keys=["parasit", "طفيلي"]),
    "hematology": dict(p="#8c2735", pdk="#5c1621", p2="#c46a74", acc="#3f6e8c", accdk="#2b4f66",
                       tint="#f6e9eb", soft="#fbf4f5", warm="#fbf3ec", warm_line="#efdccb", line="#ead5d8",
                       art=None, keys=["hemato", "haemato", "دم"]),
    "default": dict(p="#2f5d73", pdk="#1d3d4d", p2="#6fa3b5", acc="#d98e4f", accdk="#a8662f",
                    tint="#e8f0f3", soft="#f3f7f9", warm="#fbf3e8", warm_line="#efdcc4", line="#d6e1e6",
                    art=None, keys=[]),
}


def pick(meta):
    if meta.get("theme") in THEMES:
        return meta["theme"]
    hay = (meta.get("subject", "") + " " + meta.get("subject_ar", "")).lower()
    for k, t in THEMES.items():
        if any(w in hay for w in t["keys"]):
            return k
    return "default"


def css_vars(key):
    t = THEMES[key]
    names = ["p", "pdk", "p2", "acc", "accdk", "tint", "soft", "warm", "warm_line", "line"]
    return ";".join(f"--{n.replace('_', '-')}:{t[n]}" for n in names)
