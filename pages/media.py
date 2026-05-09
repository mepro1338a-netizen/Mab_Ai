import streamlit as st

from ai_service import generate_image, generate_video
from ai_pipeline import run_ai_task
from config import TOKEN_COSTS
from ui_helpers import require_login, can_use, render_download


def render_image_page():
    require_login()

    st.markdown(
        """
        <div class="page-card">
            <span class="badge">PRO FEATURE</span>
            <h1>🎨 AI Image Generator</h1>
            <p>Erstelle Bilder für Branding, Social Media und Kampagnen.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not can_use("pro"):
        st.warning("Dieses Feature benötigt mindestens PRO.")
        st.stop()

    cost = TOKEN_COSTS.get("image", 25)

    prompt = st.text_area(
        "Bild Prompt",
        key="image_prompt",
        height=180,
        placeholder="Futuristisches Luxus Logo, neon blue, cinematic lighting...",
    )

    image_style = st.selectbox(
        "Bild Stil",
        ["Realistisch", "Cinematic", "Anime", "3D Render", "Luxury", "Cyberpunk"],
        key="image_style",
    )

    style_prompts = {
        "Realistisch": "Ultra realistic, highly detailed, real photography.",
        "Cinematic": "Cinematic lighting, movie quality, dramatic atmosphere.",
        "Anime": "Anime art style, vibrant colors, Japanese animation.",
        "3D Render": "High quality 3D render, detailed materials.",
        "Luxury": "Luxury premium aesthetic, elegant branding.",
        "Cyberpunk": "Cyberpunk neon futuristic atmosphere.",
    }

    final_prompt = f"{style_prompts[image_style]}\n\n{prompt}"

    st.info(f"Kosten: {cost} Tokens pro Bild")

    if st.button("Bild generieren", key="generate_image_btn"):
        with st.spinner("Bild wird generiert..."):
            success, result, updated_user = run_ai_task(
                username=st.session_state.user,
                tool="image",
                prompt=final_prompt,
                provider="openai",
                generator_func=generate_image,
            )

        if success:
            st.session_state.last_image_path = result

            if updated_user:
                st.session_state.tokens = updated_user["tokens"]

            st.success("Bild erfolgreich generiert.")
        else:
            st.error(result)

    if st.session_state.get("last_image_path"):
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.subheader("Ergebnis")
        st.image(st.session_state.last_image_path, use_container_width=True)
        render_download(st.session_state.last_image_path, "Bild herunterladen")
        st.markdown("</div>", unsafe_allow_html=True)


def render_video_page():
    require_login()

    st.markdown(
        """
        <div class="page-card">
            <span class="badge">GRAND FEATURE</span>
            <h1>🎬 AI Video Generator</h1>
            <p>Generiere AI Videos für Reels, Ads, Branding und Social Media.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not can_use("grand"):
        st.warning("Dieses Feature benötigt mindestens GRAND.")
        st.stop()

    cost = TOKEN_COSTS.get("video", 150)

    prompt = st.text_area(
        "Video Prompt",
        key="video_prompt",
        height=200,
        placeholder="Cinematic product video, neon energy waves, luxury commercial...",
    )

    video_mode = st.selectbox(
        "Video Modus",
        [
            "Realistisch",
            "Cinematic",
            "Anime",
            "3D Animation",
            "Produktvideo",
            "TikTok/Reel",
            "Luxury Ad",
        ],
        key="video_mode",
    )

    mode_prompts = {
        "Realistisch": "Ultra realistic, natural lighting, realistic humans, real camera footage.",
        "Cinematic": "Cinematic movie scene, dramatic lighting, smooth camera movement.",
        "Anime": "Anime style animation, vibrant colors, smooth anime motion.",
        "3D Animation": "High quality 3D animated video, detailed rendering.",
        "Produktvideo": "Professional product commercial, luxury branding.",
        "TikTok/Reel": "Vertical viral social media reel, fast cuts, trendy style.",
        "Luxury Ad": "Luxury advertisement, elegant lighting, premium visuals.",
    }

    final_prompt = f"{mode_prompts[video_mode]}\n\n{prompt}"

    st.info(f"Kosten: {cost} Tokens pro Video")

    if st.button("Video generieren", key="generate_video_btn"):
        with st.spinner("Video wird generiert. Das kann länger dauern..."):
            success, result, updated_user = run_ai_task(
                username=st.session_state.user,
                tool="video",
                prompt=final_prompt,
                provider="replicate",
                generator_func=generate_video,
            )

        if success:
            st.session_state.last_video_path = result

            if updated_user:
                st.session_state.tokens = updated_user["tokens"]

            st.success("Video erfolgreich generiert.")
        else:
            st.error(result)

    if st.session_state.get("last_video_path"):
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.subheader("Ergebnis")

        if str(st.session_state.last_video_path).startswith("http"):
            st.video(st.session_state.last_video_path)
            st.markdown(f"[Video öffnen]({st.session_state.last_video_path})")
        else:
            st.video(st.session_state.last_video_path)
            render_download(st.session_state.last_video_path, "Video herunterladen")

        st.markdown("</div>", unsafe_allow_html=True)


def render_coding_page():
    require_login()

    if not can_use("pro"):
        st.warning("Dieses Feature benötigt mindestens PRO.")
        st.stop()

    st.markdown(
        """
        <div class="page-card">
            <span class="badge">PRO FEATURE</span>
            <h1>💻 Coding AI</h1>
            <p>Code schreiben, Fehler fixen und Projekte planen.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    prompt = st.text_area(
        "Was soll die Coding AI machen?",
        height=220,
        placeholder="Beispiel: Schreibe mir eine Flask Login Funktion...",
    )

    if st.button("Coding AI starten", key="coding_ai_btn"):
        if not prompt.strip():
            st.error("Bitte Prompt eingeben.")
            return

        from coding_service import generate_code

        with st.spinner("Coding AI arbeitet..."):
            success, answer = generate_code(prompt)

        if success:
            st.markdown("### Ergebnis")
            st.code(answer)
        else:
            st.error(answer)


def render_music_page():
    require_login()

    if not can_use("pro"):
        st.warning("Dieses Feature benötigt mindestens PRO.")
        st.stop()

    st.title("🎵 Music Generator")
    st.info("Music AI verbinden wir als nächstes.")


def render_reels_page():
    require_login()

    if not can_use("pro"):
        st.warning("Dieses Feature benötigt mindestens PRO.")
        st.stop()

    st.title("🎞️ Reels Generator")
    st.info("Reels AI verbinden wir als nächstes.")