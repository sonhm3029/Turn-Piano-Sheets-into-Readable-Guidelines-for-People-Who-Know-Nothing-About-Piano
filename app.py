import base64
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from src.processor import analyze

st.set_page_config(
    page_title="Piano Guide",
    page_icon="🎹",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── i18n ──────────────────────────────────────────────────────────────────

I18N = {
    "vi": dict(
        page_title = "Sheet Nhạc → Hướng Dẫn Piano",
        subtitle   = "Chơi bài piano bạn thích từ sheet nhạc · không cần biết piano hay nhạc lý",
        lang_label = "Ngôn ngữ",
        upload_hint= "PDF, PNG, JPG hoặc JPEG",
        file_ready = "File đã sẵn sàng",
        btn        = "Phân tích",
        s1         = "Đọc và chuyển đổi file...",
        s2         = "Nhận dạng nốt nhạc...",
        s3         = "Tạo hướng dẫn...",
        done       = "Hoàn tất!",
        dl         = "Tải về HTML",
        fullscreen = "Mở toàn màn hình",
        preview    = "Xem trước hướng dẫn",
    ),
    "en": dict(
        page_title = "Sheet Music → Piano Guide",
        subtitle   = "Play the piano songs you love from sheet music · no piano skills or music theory needed",
        lang_label = "Language",
        upload_hint= "PDF, PNG, JPG, or JPEG",
        file_ready = "File ready",
        btn        = "Analyze",
        s1         = "Reading and converting file...",
        s2         = "Recognizing notes...",
        s3         = "Building guide...",
        done       = "Done!",
        dl         = "Download HTML",
        fullscreen = "Open fullscreen",
        preview    = "Guide preview",
    ),
}

LANG_OPTIONS = {"Tiếng Việt": "vi", "English": "en"}

# ─── CSS ───────────────────────────────────────────────────────────────────

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:ital@1&display=swap');

#MainMenu, footer,
[data-testid="stDecoration"],
[data-testid="stToolbar"] { display:none !important; }

/* ── Background ──────────────────────────────────── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
  background:
    linear-gradient(180deg, #fbfcff 0%, #f2f6f8 48%, #eef3f0 100%) !important;
}
[data-testid="stHeader"]  {
  background:transparent !important;
  pointer-events:none !important;
}
[data-testid="stBottom"]  { background:#eef3f0 !important; }

html, body, [class*="css"] { font-family:'Inter',sans-serif !important; }

.block-container {
  max-width: 920px !important;
  margin: 0 auto !important;
  padding: .9rem 2rem 5rem !important;
}

/* ── Top bar ─────────────────────────────────────── */
.topbar-brand {
  display: flex;
  align-items: center;
  gap: .72rem;
  min-height: 44px;
}
.brand-mark {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: #111827;
  color: #ffffff;
  box-shadow: 0 12px 24px rgba(17,24,39,.14);
  font-size: 1.05rem;
}
.brand-copy {
  display: flex;
  flex-direction: column;
  gap: .05rem;
}
.brand-name {
  color: #111827;
  font-size: .92rem;
  font-weight: 800;
  line-height: 1.1;
}
.brand-sub {
  color: #7a8793;
  font-size: .72rem;
  font-weight: 700;
}

/* ── Language dropdown ───────────────────────────── */
[data-testid="stSelectbox"] {
  width: 174px !important;
  min-width: 174px !important;
  margin-left: auto !important;
  padding-top: 2px !important;
  position: relative !important;
}
[data-testid="stSelectbox"]::before {
  content: "";
  position: absolute;
  z-index: 2;
  left: 16px;
  top: 23px;
  width: 16px;
  height: 16px;
  background: #111827;
  opacity: .72;
  pointer-events: none;
  transform: translateY(-50%);
  -webkit-mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 0 20"/><path d="M12 2a15.3 15.3 0 0 0 0 20"/></svg>') center / contain no-repeat;
  mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 0 20"/><path d="M12 2a15.3 15.3 0 0 0 0 20"/></svg>') center / contain no-repeat;
}
[data-testid="stSelectbox"] label {
  display: none !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] * {
  cursor: pointer !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  min-height: 42px !important;
  background: rgba(255,255,255,.86) !important;
  border: 1px solid rgba(17,24,39,.12) !important;
  border-radius: 999px !important;
  color: #111827 !important;
  font-size: .86rem !important;
  font-weight: 800 !important;
  padding: 0 .36rem 0 2.28rem !important;
  box-shadow: 0 8px 20px rgba(31,41,55,.04) !important;
  align-items: center !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover,
[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
  background: #ffffff !important;
  border-color: #14b8a6 !important;
  box-shadow: 0 0 0 4px rgba(20,184,166,.10) !important;
}
[data-testid="stSelectbox"] input {
  caret-color: transparent !important;
  cursor: pointer !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] svg {
  color: #111827 !important;
  fill: #111827 !important;
  opacity: .72 !important;
  width: 16px !important;
  height: 16px !important;
}

/* ── Hero ────────────────────────────────────────── */
.hero {
  text-align: center;
  padding: 2.1rem 0 1.65rem;
}
.hero-mark {
  width: 58px;
  height: 58px;
  margin: 0 auto .95rem;
  border-radius: 15px;
  display: grid;
  place-items: center;
  background: #ffffff;
  border: 1px solid rgba(17,24,39,.08);
  color: #111827;
  box-shadow: 0 20px 46px rgba(31,41,55,.10);
  font-size: 1.72rem;
}
.hero h1 {
  color: #111827;
  font-family:'Playfair Display',Georgia,serif;
  font-size: clamp(2.05rem, 4.7vw, 3.05rem);
  font-style: italic;
  font-weight: 400;
  line-height: 1.08;
  margin: 0 0 .9rem;
}
.hero h1 span {
  color: #0f766e;
}
.hero p {
  color:#68717d;
  font-size: .98rem;
  max-width: 560px;
  margin:0 auto;
  line-height:1.8;
}

/* ── Upload zone ─────────────────────────────────── */
[data-testid="stFileUploader"] section {
  background: rgba(255,255,255,.92) !important;
  border: 1.5px dashed #c3d0d2 !important;
  border-radius: 16px !important;
  padding: 2.25rem 2rem !important;
  box-shadow: 0 22px 60px rgba(31,41,55,.08) !important;
  transition: border-color .2s, box-shadow .2s, transform .2s !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  gap: .7rem !important;
}
[data-testid="stFileUploader"] section:hover {
  border-color: #14b8a6 !important;
  box-shadow: 0 22px 55px rgba(20,184,166,.12) !important;
  transform: translateY(-1px) !important;
}
[data-testid="stFileUploader"] section > button {
  background: #ffffff !important;
  border: 1.5px solid #cfd8dc !important;
  color: #111827 !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
  font-size: .85rem !important;
  padding: .48rem 1.4rem !important;
  transition: all .15s !important;
}
[data-testid="stFileUploader"] section > button:hover {
  border-color: #14b8a6 !important;
  color: #0f766e !important;
}
[data-testid="stFileUploader"] section small,
[data-testid="stFileUploader"] section span {
  color: #7b8792 !important;
  font-size: .8rem !important;
}

/* ── Primary button ──────────────────────────────── */
[data-testid="baseButton-primary"] {
  background: linear-gradient(135deg,#0f766e,#ef6f61) !important;
  border: none !important;
  color: #ffffff !important;
  font-weight: 800 !important;
  border-radius: 10px !important;
  font-size: .9rem !important;
  min-height: 42px !important;
  box-shadow: 0 14px 28px rgba(15,118,110,.18) !important;
  transition: opacity .15s, transform .15s !important;
}
[data-testid="baseButton-primary"]:hover {
  opacity:.92 !important;
  transform: translateY(-1px) !important;
}

/* ── Download button ─────────────────────────────── */
[data-testid="stDownloadButton"] button {
  background: #ffffff !important;
  border: 1.5px solid #d8e0e3 !important;
  color: #111827 !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
  font-size: .88rem !important;
  min-height: 40px !important;
  box-shadow: 0 10px 28px rgba(31,41,55,.07) !important;
  transition: all .15s !important;
}
[data-testid="stDownloadButton"] button:hover {
  border-color: #14b8a6 !important;
  color: #0f766e !important;
  transform: translateY(-1px) !important;
}

/* ── Status widget ───────────────────────────────── */
[data-testid="stStatusWidget"] {
  background: #ffffff !important;
  border: 1px solid #dfe7ea !important;
  border-radius: 12px !important;
  box-shadow: 0 12px 32px rgba(31,41,55,.07) !important;
}

/* ── Alert ───────────────────────────────────────── */
[data-testid="stAlertContainer"] {
  background: rgba(20,184,166,.07) !important;
  border: 1px solid rgba(20,184,166,.22) !important;
  border-radius: 10px !important;
}

/* ── Divider ─────────────────────────────────────── */
hr { border-color: #dfe7ea !important; margin: 1.25rem 0 !important; }

.file-meta {
  margin: 0;
  padding: .48rem 0;
  color: #697586;
  font-size: .84rem;
}
.file-meta strong {
  color: #111827;
  font-weight: 800;
}
@media (max-width: 640px) {
  .block-container {
    padding: .85rem 1rem 4rem !important;
  }
  .brand-sub {
    display: none;
  }
  [data-testid="stSelectbox"] {
    width: 158px !important;
    min-width: 158px !important;
  }
  .hero {
    padding-top: 1.45rem;
  }
  .hero-mark {
    width: 54px;
    height: 54px;
    border-radius: 14px;
    font-size: 1.7rem;
  }
}
</style>""", unsafe_allow_html=True)

# ─── Language toggle ────────────────────────────────────────────────────────

query_lang = st.query_params.get("lang", st.session_state.get("language_code", "vi"))
if query_lang not in I18N:
    query_lang = "vi"

st.session_state["language_code"] = query_lang
lang_options = list(LANG_OPTIONS.keys())
current_pick = next(
    label for label, code in LANG_OPTIONS.items() if code == query_lang
)

brand_col, lang_col = st.columns([6, 2], vertical_alignment="center")
with brand_col:
    st.markdown(
        """
        <div class="topbar-brand">
          <div class="brand-mark">🎹</div>
          <div class="brand-copy">
            <div class="brand-name">Piano Guide</div>
            <div class="brand-sub">Play songs without theory</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with lang_col:
    picked = st.selectbox(
        I18N[query_lang]["lang_label"],
        options=lang_options,
        index=lang_options.index(current_pick),
        key="language_dropdown",
        label_visibility="collapsed",
    )

lang = LANG_OPTIONS.get(picked or current_pick, "vi")
if lang != query_lang:
    st.session_state["language_code"] = lang
    st.query_params["lang"] = lang
    st.rerun()

t = I18N[lang]

# ─── Hero ──────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="hero">
  <div class="hero-mark">🎹</div>
  <h1>{t['page_title'].replace('→', '<span>→</span>')}</h1>
  <p>{t['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

# ─── Upload zone ───────────────────────────────────────────────────────────

uploaded = st.file_uploader(
    "upload",
    type=["pdf", "png", "jpg", "jpeg"],
    label_visibility="collapsed",
    help=t["upload_hint"],
)

if uploaded:
    st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
    name_col, btn_col = st.columns([4, 1])
    with name_col:
        st.markdown(
            f"<p class='file-meta'>{t['file_ready']}: "
            f"<strong>{uploaded.name}</strong>"
            f"&nbsp;·&nbsp;{uploaded.size / 1024:.1f} KB</p>",
            unsafe_allow_html=True,
        )
    with btn_col:
        do_analyze = st.button(t["btn"], type="primary", use_container_width=True)

    if do_analyze:
        with st.status(t["s1"], expanded=True) as status:
            st.write(t["s1"])
            result_html = analyze(uploaded.read(), uploaded.name)
            st.write(t["s2"])
            time.sleep(0.35)
            st.write(t["s3"])
            time.sleep(0.2)
        status.update(label=t["done"], state="complete", expanded=False)
        st.session_state["result_html"] = result_html
        st.session_state["source_name"] = uploaded.name

# ─── Result ────────────────────────────────────────────────────────────────

if "result_html" in st.session_state:
    html = st.session_state["result_html"]
    stem = Path(st.session_state["source_name"]).stem
    html_b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")

    st.divider()
    st.markdown(
        f"<p class='file-meta'><strong>{t['preview']}</strong></p>",
        unsafe_allow_html=True,
    )
    dl_col, full_col, _ = st.columns([2, 2, 3])
    with dl_col:
        st.download_button(
            t["dl"],
            data=html,
            file_name=f"{stem}_guide.html",
            mime="text/html",
            use_container_width=True,
        )
    with full_col:
        components.html(
            f"""
            <!doctype html>
            <html>
            <head>
              <meta charset="utf-8">
              <style>
                html, body {{
                  margin: 0;
                  padding: 0;
                  background: transparent;
                  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                }}
                button {{
                  width: 100%;
                  min-height: 40px;
                  border: 1.5px solid #d8e0e3;
                  border-radius: 10px;
                  background: #fff;
                  color: #111827;
                  cursor: pointer;
                  font-size: 14px;
                  font-weight: 800;
                  box-shadow: 0 10px 28px rgba(31,41,55,.07);
                  transition: border-color .15s, color .15s, transform .15s;
                }}
                button:hover {{
                  border-color: #14b8a6;
                  color: #0f766e;
                  transform: translateY(-1px);
                }}
              </style>
            </head>
            <body>
              <button type="button" id="open-guide">{t["fullscreen"]}</button>
              <script>
                const encoded = "{html_b64}";
                document.getElementById("open-guide").addEventListener("click", () => {{
                  const bytes = Uint8Array.from(atob(encoded), char => char.charCodeAt(0));
                  const guideHtml = new TextDecoder("utf-8").decode(bytes);
                  const blob = new Blob([guideHtml], {{ type: "text/html;charset=utf-8" }});
                  const url = URL.createObjectURL(blob);
                  window.open(url, "_blank", "noopener,noreferrer");
                  setTimeout(() => URL.revokeObjectURL(url), 60000);
                }});
              </script>
            </body>
            </html>
            """,
            height=44,
            scrolling=False,
        )
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    components.html(html, height=920, scrolling=True)
