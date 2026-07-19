import os
os.environ["PANDAS_USE_PYARROW"] = "0"
import streamlit as st
from few_shot import FewShotPosts
from post_generator import generate_post
import json as _json

length_options = ["Short", "Medium", "Long"]
language_options = ["English", "Hinglish"]

def main():
    st.title("LinkedIn Post Generator")

    col1, col2, col3 = st.columns(3)

    fs = FewShotPosts()
    tags = fs.get_tags()

    with col1:
        selected_tag = st.selectbox("Title", options=tags)

    with col2:
        selected_length = st.selectbox("Length", options=length_options)

    with col3:
        selected_language = st.selectbox("Language", options=language_options)

    if st.button("Generate"):
        # Save parameters and generate
        st.session_state['last_params'] = {
            'length': selected_length,
            'language': selected_language,
            'tag': selected_tag,
        }
        with st.spinner("Generating post..."):
            post = generate_post(selected_length, selected_language, selected_tag)
        st.session_state['last_post'] = post

    # If we have a last post, display it and show Copy + Retry buttons
    if 'last_post' in st.session_state:
        post = st.session_state['last_post']
        st.write(post)

        # Buttons: Copy and Retry side by side
        copy_col, retry_col = st.columns([2, 1])
        with copy_col:
            safe_post = _json.dumps(post)
            html = f"""
            <style>
              #copy-btn{{
                background-color: #0f62fe;
                color: white;
                border: none;
                padding: 10px 18px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                box-shadow: 0 1px 0 rgba(0,0,0,0.04);
              }}
              #copy-btn:active{{ transform: translateY(1px); }}
            </style>
            <button id="copy-btn">Copy to clipboard</button>
            <script>
            const text = {safe_post};
            const btn = document.getElementById("copy-btn");
            btn.addEventListener("click", async () => {{
                try {{
                    await navigator.clipboard.writeText(text);
                    const old = btn.innerText;
                    btn.innerText = "Copied!";
                    setTimeout(()=>btn.innerText=old,2000);
                }} catch(e) {{
                    const ta = document.createElement('textarea');
                    ta.value = text;
                    document.body.appendChild(ta);
                    ta.select();
                    document.execCommand('copy');
                    ta.remove();
                    const old = btn.innerText;
                    btn.innerText = "Copied!";
                    setTimeout(()=>btn.innerText=old,2000);
                }}
            }});
            </script>
            """
            st.components.v1.html(html, height=70)

        with retry_col:
            if st.button("Retry"):
                params = st.session_state.get('last_params', None)
                if params:
                    with st.spinner("Regenerating post..."):
                        post = generate_post(params['length'], params['language'], params['tag'])
                    st.session_state['last_post'] = post

if __name__ == "__main__":
    main()