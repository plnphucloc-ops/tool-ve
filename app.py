import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Tool thống kê vé", layout="wide")
st.title("📊 Tool thống kê vé")

file = st.file_uploader("Chọn file .xls", type=["xls"])

def parse_money(s):
    return int(str(s).replace(" đ","").replace(".",""))

def format_money(x):
    return f"{x:,}".replace(",", ".") + " đ"

# ===== HÀM IN K80 =====
def generate_print_html(summary, doan):
    def fm(x):
        return f"{x:,}".replace(",", ".") + " đ"

    html = """
    <html>
    <head>
    <style>
    @media print {
        @page {
            width: 80mm;
            margin: 5mm;
        }
        body {
            font-family: monospace;
            font-size: 12px;
        }
    }
    body {
        width: 80mm;
        margin: auto;
        font-family: monospace;
    }
    h3 { text-align: center; }
    .line { border-top: 1px dashed #000; margin: 5px 0; }
    table { width: 100%; }
    td { font-size: 12px; }
    .right { text-align: right; }
    </style>
    </head>
    <body>

    <h3>BAO CAO VE</h3>
    <div class="line"></div>
    """

    # Tổng hợp
    for _, row in summary.iterrows():
        html += f"""
        <table>
        <tr>
            <td>{row['Nhóm']}</td>
            <td class='right'>{row['Số_vé']}</td>
            <td class='right'>{fm(row['Tổng_tiền'])}</td>
        </tr>
        </table>
        """

    html += "<div class='line'></div>"

    # Doan
    if not doan.empty:
        html += "<b>DOAN</b><br>"
        for _, row in doan.iterrows():
            html += f"""
            <div>{row['Số ghế']} - {row['Ghi chú']}</div>
            <div class='right'>{fm(row['Tổng tiền'])}</div>
            <div class='line'></div>
            """

        total = doan["Tổng tiền"].sum()
        html += f"<b>Tổng: {len(doan)} vé - {fm(total)}</b>"

    html += """
    <script>
    window.onload = function() {
        window.print();
    }
    </script>
    </body>
    </html>
    """

    return html

# ===== XỬ LÝ FILE =====
if file:
    df = pd.read_html(file)[0]
    df = df[df["Số ghế"] != "Tổng"]

    df["Đại lý"] = df["Đại lý"].astype(str).str.strip()
    df["Ghi chú"] = df["Ghi chú"].astype(str)

    df["Tổng tiền"] = df["Tổng tiền"].apply(parse_money)

    def classify(row):
        agent = row["Đại lý"].lower()
        note = row["Ghi chú"].lower()
        if agent.endswith(".vxr") or "@" in agent:
            return "vxr"
        elif agent.endswith(".phuchai"):
            return row["Đại lý"]
        elif (agent == "" or agent == "nan") and ("doan" in note or "đoan" in note):
            return "Doan"
        elif agent == "" or agent == "nan":
            return "Phụ xe"
        else:
            return row["Đại lý"]

    df["Nhóm"] = df.apply(classify, axis=1)

    summary = df.groupby("Nhóm").agg(
        Số_vé=("Số ghế","count"),
        Tổng_tiền=("Tổng tiền","sum")
    ).reset_index()

    # Format tiền để hiển thị
    summary_display = summary.copy()
    summary_display["Tổng_tiền"] = summary_display["Tổng_tiền"].apply(format_money)

    st.subheader("📊 KẾT QUẢ SAU KHI CẬP NHẬT")
    st.dataframe(summary_display, use_container_width=True)

    doan = df[df["Nhóm"]=="Doan"][["Số ghế","Ghi chú","Tổng tiền"]]

    st.subheader("🔎 Chi tiết Doan")
    if doan.empty:
        st.info("Không phát sinh vé Doan")
    else:
        doan_display = doan.copy()
        doan_display["Tổng tiền"] = doan_display["Tổng tiền"].apply(format_money)

        st.dataframe(doan_display, use_container_width=True)
        st.success(f"👉 Tổng: {len(doan)} vé — {format_money(doan['Tổng tiền'].sum())}")

    # ===== NÚT IN =====
    st.markdown("---")
    if st.button("🖨️ IN KẾT QUẢ (K80)"):
        html = generate_print_html(summary, doan)
        components.html(html, height=600)
