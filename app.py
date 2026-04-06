import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Tool thống kê vé")

# ================== UPLOAD FILE ==================
uploaded_file = st.file_uploader("Chọn file .xls/.xlsx", type=["xls", "xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # ================== CLEAN DATA ==================
        df.columns = df.columns.str.strip()

        # Check cột bắt buộc
        required_cols = ["Đại lý"]
        for col in required_cols:
            if col not in df.columns:
                st.error(f"❌ Thiếu cột: {col}")
                st.stop()

        # Chuẩn hoá dữ liệu
        df["Đại lý"] = df["Đại lý"].fillna("").astype(str).str.strip().str.lower()

        # ================== CLASSIFY ==================
        def classify(row):
            try:
                agent = row.get("Đại lý", "")

                if pd.isna(agent):
                    agent = ""
                else:
                    agent = str(agent).lower()

                # ====== LOGIC PHÂN LOẠI (bạn sửa theo nhu cầu) ======
                if "phúc hải" in agent:
                    return "PHÚC HẢI"
                elif "limousine" in agent:
                    return "LIMO"
                elif agent == "":
                    return "KHÔNG RÕ"
                else:
                    return "KHÁC"

            except Exception:
                return "LỖI"

        df["Nhóm"] = df.apply(classify, axis=1)

        # ================== HIỂN THỊ ==================
        st.subheader("📋 Dữ liệu sau xử lý")
        st.dataframe(df)

        # ================== THỐNG KÊ ==================
        summary = df["Nhóm"].value_counts().reset_index()
        summary.columns = ["Nhóm", "Số lượng"]

        st.subheader("📊 Thống kê")
        st.dataframe(summary)

        # ================== DOWNLOAD ==================
        csv = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ Tải file kết quả",
            csv,
            "ket_qua.csv",
            "text/csv"
        )

    except Exception as e:
        st.error("❌ Lỗi khi xử lý file")
        st.text(str(e))
