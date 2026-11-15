import streamlit as st
import hashlib
import hmac

# Lấy mã MD5 từ Streamlit Secrets
PASSWORD_HASH = st.secrets["PASSWORD_HASH"]

# Kiểm tra đăng nhập
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.title("🔐 ĐĂNG NHẬP")

    password = st.text_input(
        "Nhập mật khẩu",
        type="password"
    )

    if st.button("ĐĂNG NHẬP", use_container_width=True):

        input_hash = hashlib.md5(
            password.encode("utf-8")
        ).hexdigest()

        if hmac.compare_digest(input_hash, PASSWORD_HASH):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Mật khẩu không chính xác!")

    st.stop()
