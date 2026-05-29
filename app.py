import streamlit as st

st.title("📊 残高メーター付き家計簿")

st.sidebar.header("設定")
budget = st.sidebar.number_input("今月の予算（円）", min_value=0, value=50000, step=1000)

st.header("💸 支出の入力")
expense = st.number_input("使った金額（円）", min_value=0, value=0, step=100)

remaining = budget - expense
percentage = (expense / budget) if budget > 0 else 0

st.subheader("現在のステータス")

if percentage <= 1.0:
    st.progress(percentage)
    st.success(f"残りの予算: **{remaining:,} 円**（あと {int((1-percentage)*100)}% 使えます）")
else:
    st.progress(1.0)
    st.error(f"⚠️ 予算オーバーです！: **{abs(remaining):,} 円の赤字**")

