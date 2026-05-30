import streamlit as st

# ---- 簡易パスワード機能 ----
PASSWORD = "3373"  # 👈 あなたの好きなパスワードに変えてもOKです！

st.sidebar.title("🔒 ログイン")
auth_password = st.sidebar.text_input("パスワードを入力してください", type="password")

if auth_password != PASSWORD:
    st.info("左側のサイドバーからパスワードを入力してください。")
    st.stop()  # 👈 パスワードが違う場合、ここでプログラムを強制ストップさせる
# ----------------------------

# ここから下に、昨日まで作った「st.title('📊 カテゴリ別・残高メーター付き家計簿')」などのコードが続くようにします

import pandas as pd
import datetime
import os

# データの保存先ファイル（CSV形式）
DATA_FILE = "kakeibo_data.csv"

# アプリのタイトル
st.title("📊 カテゴリ別・残高メーター付き家計簿")

# --- 1. データの読み込み機能（Step 2） ---
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    # ファイルがない場合は空のデータ枠（DataFrame）を作る
    df = pd.DataFrame(columns=["日付", "カテゴリ", "金額"])

# --- 2. サイドバー設定：カテゴリ別の予算設定（Step 1） ---
st.sidebar.header("⚙️ 今月の予算設定")
categories = ["食費", "交際費", "趣味・音楽", "交通費・その他"]
budgets = {}

for cat in categories:
    # カテゴリごとに予算を入力できるようにする（初期値は15,000円）
    budgets[cat] = st.sidebar.number_input(f"【{cat}】の予算（円）", min_value=0, value=15000, step=1000)

total_budget = sum(budgets.values())

# --- 3. メイン画面：支出の入力と保存（Step 2） ---
st.header("💸 日々の支出を入力")

# 入力フォームを横並びにする
col1, col2, col3 = st.columns(3)
with col1:
    input_date = st.date_input("日付", datetime.date.today())
with col2:
    input_cat = st.selectbox("カテゴリ", categories)
with col3:
    input_price = st.number_input("金額（円）", min_value=0, value=0, step=100)

if st.button("➕ 支出を記録する", use_container_width=True):
    if input_price > 0:
        # 新しいデータを追加
        new_data = pd.DataFrame([{"日付": str(input_date), "カテゴリ": input_cat, "金額": input_price}])
        df = pd.concat([df, new_data], ignore_index=True)
        # CSVファイルに保存
        df.to_csv(DATA_FILE, index=False)
        st.success(f"「{input_cat}: {input_price:,}円」を記録しました！")
        st.rerun() # 画面を更新してグラフに反映

# --- 4. 計算とビジュアル化（Step 1 & Step 3） ---
st.markdown("---")
st.header("📈 今月の利用状況")

if not df.empty:
    # カテゴリごとに合計金額を計算
    summary = df.groupby("カテゴリ")["金額"].sum().to_dict()
else:
    summary = {}

# 各カテゴリのメーターを表示
for cat in categories:
    spent = summary.get(cat, 0)
    budget = budgets[cat]
    
    st.subheader(f"🔹 {cat}")
    col_text, col_bar = st.columns([1, 2])
    
    with col_text:
        st.write(f"消費: {spent:,} / 予算: {budget:,} 円")
    
    with col_bar:
        ratio = (spent / budget) if budget > 0 else 0
        if ratio <= 1.0:
            st.progress(ratio)
            st.caption(f"あと {budget - spent:,} 円使えます")
        else:
            st.progress(1.0)
            st.caption(f"⚠️ 予算オーバー！ ({spent - budget:,} 円の赤字)")

# --- 5. グラフと履歴の表示（Step 3） ---
if not df.empty:
    st.markdown("---")
    st.header("📊 支出の割合（グラフ）")
    
    # Streamlit標準の棒グラフを表示
    chart_data = df.groupby("カテゴリ")["金額"].sum()
    st.bar_chart(chart_data)
    
    st.header("📋 これまでの履歴一覧")
    st.dataframe(df.sort_values("日付", ascending=False), use_container_width=True)
    
    # データをリセットするボタン
    if st.sidebar.button("⚠️ データをすべて削除"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.rerun()

