
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import hashlib
import hmac
import html

# =====================================
# CẤU HÌNH
# =====================================

st.set_page_config(
    page_title="Tool thống kê vé",
    page_icon="📊",
    layout="wide"
)

# =====================================
# LẤY MẬT KHẨU TỪ STREAMLIT SECRETS
# =====================================

try:
    PASSWORD_HASH = str(st.secrets["PASSWORD_HASH"]).strip()

except (KeyError, FileNotFoundError):
    st.error(
        "❌ Chưa cấu hình PASSWORD_HASH trong Streamlit Secrets!"
    )
    st.info(
        'Vào Manage app → Settings → Secrets và thêm '
        'PASSWORD_HASH = "mã MD5 của mật khẩu".'
    )
    st.stop()

# Kiểm tra định dạng mã MD5
if len(PASSWORD_HASH) != 32 or any(
    c not in "0123456789abcdefABCDEF"
    for c in PASSWORD_HASH
):
    st.error("❌ Mã PASSWORD_HASH không đúng định dạng MD5!")
    st.stop()


# =====================================
# ĐĂNG NHẬP
# =====================================

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

    if st.button(
        "ĐĂNG NHẬP",
        use_container_width=True
    ):

        input_hash = hashlib.md5(
            password.encode("utf-8")
        ).hexdigest()

        if hmac.compare_digest(
            input_hash,
            PASSWORD_HASH.lower()
        ):
            st.session_state.authenticated = True
            st.rerun()

        else:
            st.error("❌ Mật khẩu không chính xác!")

    st.stop()


# =====================================
# GIAO DIỆN CHÍNH
# =====================================

st.title("📊 TOOL THỐNG KÊ VÉ")

if st.button("🚪 ĐĂNG XUẤT"):

    st.session_state.authenticated = False
    st.rerun()

st.markdown("---")

file = st.file_uploader(
    "📂 Chọn file .xls",
    type=["xls"]
)


# =====================================
# XỬ LÝ TIỀN
# =====================================

def parse_money(value):

    try:

        if pd.isna(value):
            return 0

        if isinstance(value, (int, float)):
            return int(value)

        value = str(value).strip()

        value = (
            value.replace("đ", "")
            .replace("Đ", "")
            .replace(" ", "")
            .replace(".", "")
            .replace(",", "")
        )

        return int(value)

    except (ValueError, TypeError):
        return 0


def format_money(value):

    return (
        f"{value:,.0f}".replace(",", ".") + " đ"
    )


# =====================================
# IN K80
# =====================================

def generate_print_html(summary, doan):

    def fm(value):
        return format_money(value)

    html_content = """
    <!DOCTYPE html>
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

    html_content += """
    <div class="title">BÁO CÁO VÉ</div>
    """

    html_content += f"""
    <div class="money">{fm(total_all)}</div>
    <div class="line"></div>
    """

    for _, row in summary.iterrows():

        group_name = html.escape(
            str(row["Nhóm"])
        )

        html_content += f"""
        <div class="row">
            <div>{group_name} ({row['Số_vé']})</div>
            <div>{fm(row['Tổng_tiền'])}</div>
        </div>
        """

    html_content += '<div class="line"></div>'

    if not doan.empty:

        html_content += """
        <div class="title" style="font-size:15px">
            DOAN
        </div>
        """

        for _, row in doan.iterrows():

            seat = html.escape(
                str(row["Số ghế"])
            )

            note = html.escape(
                str(row["Ghi chú"])
            )

            html_content += f"""
            <div><b>{seat}</b></div>

            <div style="font-size:12px">
                {note}
            </div>

            <div>{fm(row['Tổng tiền'])}</div>

            <div class="line"></div>
            """

        total_doan = doan["Tổng tiền"].sum()

        html_content += f"""
        <div>
            <b>
                Tổng: {len(doan)} vé — {fm(total_doan)}
            </b>
        </div>
        """

    html_content += """
    <script>
    window.onload = function() {
        window.print();
    };
    </script>

    </body>
    </html>
    """

    return html_content


# =====================================
# ĐỌC FILE EXCEL
# =====================================

if file:

    try:

        df = pd.read_html(file)[0]

    except Exception:

        st.error(
            "❌ Không đọc được file. Kiểm tra lại file .xls"
        )

        st.stop()

    # =================================
    # KIỂM TRA CỘT
    # =================================

    required_columns = [
        "Số ghế",
        "Đại lý",
        "Ghi chú",
        "Tổng tiền"
    ]

    for col in required_columns:

        if col not in df.columns:

            st.error(f"❌ Thiếu cột: {col}")
            st.stop()

    # =================================
    # LOẠI BỎ DÒNG TỔNG
    # =================================

    df = df[
        df["Số ghế"]
        .fillna("")
        .astype(str)
        .str.strip() != "Tổng"
    ].copy()

    # =================================
    # LÀM SẠCH DỮ LIỆU
    # =================================

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

    df["Tổng tiền"] = (
        df["Tổng tiền"].apply(parse_money)
    )

    # =================================
    # PHÂN LOẠI VÉ
    # =================================

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

    df["Nhóm"] = df.apply(
        classify,
        axis=1
    )

    # =================================
    # TỔNG HỢP
    # =================================

    summary = df.groupby("Nhóm").agg(
        Số_vé=("Số ghế", "count"),
        Tổng_tiền=("Tổng tiền", "sum")
    ).reset_index()

    summary_display = summary.copy()

    summary_display["Tổng_tiền"] = (
        summary_display["Tổng_tiền"]
        .apply(format_money)
    )

    st.subheader(
        "📊 KẾT QUẢ SAU KHI CẬP NHẬT"
    )

    st.dataframe(
        summary_display,
        use_container_width=True,
        hide_index=True
    )

    # =================================
    # CHI TIẾT DOAN
    # =================================

    doan = df[
        df["Nhóm"] == "Doan"
    ][
        ["Số ghế", "Ghi chú", "Tổng tiền"]
    ].copy()

    st.subheader("🔎 CHI TIẾT DOAN")

    if doan.empty:

        st.info("Không phát sinh vé Doan")

    else:

        doan_display = doan.copy()

        doan_display["Tổng tiền"] = (
            doan_display["Tổng tiền"]
            .apply(format_money)
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

    # =================================
    # TỔNG DOANH THU
    # =================================

    st.markdown("---")

    st.metric(
        "💰 TỔNG DOANH THU",
        format_money(
            summary["Tổng_tiền"].sum()
        )
    )

    # =================================
    # IN K80
    # =================================

    st.markdown("---")

    st.subheader("🖨️ IN BÁO CÁO K80")

    if st.button(
        "🖨️ IN K80",
        use_container_width=True
    ):

        print_html = generate_print_html(
            summary,
            doan
        )

        components.html(
            print_html,
            height=600,
            scrolling=True
        )

else:

    st.info(
        "📂 Vui lòng tải file .xls để bắt đầu thống kê."
    )
