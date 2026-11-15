
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# ===== CẤU HÌNH =====
st.set_page_config(
    page_title="Tool thống kê vé",
    layout="wide"
)

# ===== ĐĂNG NHẬP =====
PASSWORD = "locdeptrai"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.title("🔐 ĐĂNG NHẬP")
    st.write("Vui lòng nhập mật khẩu để sử dụng công cụ.")

    password = st.text_input(
        "Mật khẩu",
        type="password",
        placeholder="Nhập mật khẩu..."
    )

    if st.button("ĐĂNG NHẬP", use_container_width=True):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Mật khẩu không chính xác!")

    st.stop()


# ===== GIAO DIỆN CHÍNH =====
st.title("📊 Tool thống kê vé")

# NÚT ĐĂNG XUẤT
if st.button("🚪 Đăng xuất"):
    st.session_state.authenticated = False
    st.rerun()

st.markdown("---")

file = st.file_uploader(
    "Chọn file .xls",
    type=["xls"]
)


# ===== SAFE MONEY =====
def parse_money(s):
    try:
        return int(
            str(s)
            .replace(" đ", "")
            .replace(".", "")
            .replace(",", "")
            .strip()
        )
    except:
        return 0


def format_money(x):
    return f"{x:,.0f}".replace(",", ".") + " đ"


# ===== IN K80 =====
def generate_print_html(summary, doan):

    def fm(x):
        return f"{x:,.0f}".replace(",", ".") + " đ"

    html = """
    <html>
    <head>
    <meta charset="UTF-8">
    <style>

    @page {
        size: 80mm auto;
        margin: 5mm;
    }

    body {
        width: 72mm;
        font-family: Arial, sans-serif;
        text-align: center;
        color: black;
    }

    .title {
        font-size: 18px;
        font-weight: bold;
    }

    .money {
        font-size: 22px;
        font-weight: bold;
        margin: 10px 0;
    }

    .line {
        border-top: 1px dashed black;
        margin: 8px 0;
    }

    .row {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        gap: 5px;
    }

    </style>
    </head>

    <body>
    """

    total_all = summary["Tổng_tiền"].sum()

    html += '<div class="title">BÁO CÁO VÉ</div>'

    html += f'<div class="money">{fm(total_all)}</div>'

    html += '<div class="line"></div>'

    for _, row in summary.iterrows():

        html += f"""
        <div class="row">
            <div>{row['Nhóm']} ({row['Số_vé']})</div>
            <div>{fm(row['Tổng_tiền'])}</div>
        </div>
        """

    html += '<div class="line"></div>'

    if not doan.empty:

        html += """
        <div class="title" style="font-size:15px">
            DOAN
        </div>
        """

        for _, row in doan.iterrows():

            html += f"<div><b>{row['Số ghế']}</b></div>"

            html += f"""
            <div style="font-size:12px">
                {row['Ghi chú']}
            </div>
            """

            html += f"<div>{fm(row['Tổng tiền'])}</div>"

            html += '<div class="line"></div>'

        total = doan["Tổng tiền"].sum()

        html += f"""
        <div>
            <b>Tổng: {len(doan)} vé — {fm(total)}</b>
        </div>
        """

    html += """
    <script>
        window.onload = function() {
            window.print();
        };
    </script>

    </body>
    </html>
    """

    return html


# ===== MAIN =====
if file:

    try:
        df = pd.read_html(file)[0]

    except Exception:
        st.error("❌ Không đọc được file. Kiểm tra lại file .xls")
        st.stop()

    # ===== LOẠI BỎ DÒNG TỔNG =====
    if "Số ghế" not in df.columns:
        st.error("❌ Không tìm thấy cột Số ghế")
        st.stop()

    df = df[
        df["Số ghế"].fillna("").astype(str).str.strip() != "Tổng"
    ].copy()

    # ===== KIỂM TRA CỘT =====
    for col in ["Đại lý", "Ghi chú", "Tổng tiền"]:

        if col not in df.columns:
            st.error(f"❌ Thiếu cột: {col}")
            st.stop()

    # ===== LÀM SẠCH DỮ LIỆU =====
    df["Đại lý"] = (
        df["Đại lý"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["Ghi chú"] = (
        df["Ghi chú"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["Tổng tiền"] = df["Tổng tiền"].apply(parse_money)

    # ===== PHÂN LOẠI =====
    def classify(row):

        agent = row["Đại lý"]
        note = row["Ghi chú"]

        if agent.endswith(".vxr") or "@" in agent:
            return "vxr"

        elif agent.endswith(".phuchai"):
            return agent

        elif agent == "" and (
            "doan" in note or "đoan" in note
        ):
            return "Doan"

        elif agent == "":
            return "Phụ xe"

        else:
            return agent

    df["Nhóm"] = df.apply(classify, axis=1)

    # ===== SUMMARY =====
    summary = df.groupby("Nhóm").agg(
        Số_vé=("Số ghế", "count"),
        Tổng_tiền=("Tổng tiền", "sum")
    ).reset_index()

    summary_display = summary.copy()

    summary_display["Tổng_tiền"] = (
        summary_display["Tổng_tiền"].apply(format_money)
    )

    st.subheader("📊 KẾT QUẢ SAU KHI CẬP NHẬT")

    st.dataframe(
        summary_display,
        use_container_width=True,
        hide_index=True
    )

    # ===== DOAN =====
    doan = df[
        df["Nhóm"] == "Doan"
    ][["Số ghế", "Ghi chú", "Tổng tiền"]].copy()

    st.subheader("🔎 Chi tiết Doan")

    if doan.empty:

        st.info("Không phát sinh vé Doan")

    else:

        doan_display = doan.copy()

        doan_display["Tổng tiền"] = (
            doan_display["Tổng tiền"].apply(format_money)
        )

        st.dataframe(
            doan_display,
            use_container_width=True,
            hide_index=True
        )

        st.success(
            f"👉 Tổng: {len(doan)} vé — "
            f"{format_money(doan['Tổng tiền'].sum())}"
        )

    # ===== TỔNG TIỀN =====
    st.markdown("---")

    st.metric(
        "💰 TỔNG DOANH THU",
        format_money(summary["Tổng_tiền"].sum())
    )

    # ===== IN K80 =====
    st.markdown("---")

    st.subheader("🖨️ IN BÁO CÁO")

    if st.button("🖨️ IN K80", use_container_width=True):

        html = generate_print_html(summary, doan)

        components.html(
            html,
            height=600,
            scrolling=True
        )

else:

    st.info("📂 Vui lòng tải file Excel .xls để bắt đầu thống kê.")
