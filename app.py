import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tool thống kê vé", layout="wide")
st.title("📊 Tool thống kê vé")

file = st.file_uploader("Chọn file .xls", type=["xls"])

def parse_money(s):
    return int(str(s).replace(" đ","").replace(".",""))

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

    st.subheader("📊 KẾT QUẢ SAU KHI CẬP NHẬT")
    st.dataframe(summary, use_container_width=True)

    doan = df[df["Nhóm"]=="Doan"][["Số ghế","Ghi chú","Tổng tiền"]]
    st.subheader("🔎 Chi tiết Doan")
    if doan.empty:
        st.write("Không phát sinh vé Doan")
    else:
        st.dataframe(doan, use_container_width=True)
        st.write(f"👉 Tổng: {len(doan)} vé — {doan['Tổng tiền'].sum():,} đ".replace(",","."))
