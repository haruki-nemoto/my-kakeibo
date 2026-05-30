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
# ---- 合計残高の計算と表示 ----
# ---- 期間の絞り込み（今月分） ----
if not df.empty:
    # 日付カラムを文字型から「日付データ」に変換します
    df["日付"] = pd.to_datetime(df["日付"])
    
    # 今日の「年-月」を取得（例: 2026-05）
    current_month = pd.Timestamp.now().strftime("%Y-%m")
    
    # データの中から、今月のデータだけを神がかり的に抽出！
    df_current_month = df[df["日付"].dt.strftime("%Y-%m") == current_month]
    
    # 画面表示用に、日付の見た目を元の「2026-05-30」のような形式に戻しておきます
    df["日付"] = df["日付"].dt.strftime("%Y-%m-%d")
    df_current_month["日付"] = df_current_month["日付"].dt.strftime("%Y-%m-%d")
else:
    df_current_month = df

# ---- 今月の合計収支の計算と表示 ----
total_balance = df_current_month["金額"].sum() if not df_current_month.empty else 0
st.metric(label="📊 今月の合計収支（残高）", value=f"{total_balance:,} 円")
st.write("---")


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
st.header("💸 日々の収支を入力")

# 👈 新しく「収支タイプ」を選ぶボタンを追加します
type_options = ["支出", "収入"]
action_type = st.radio("タイプを選択", type_options, horizontal=True)

# カテゴリの選択（支出のときだけ出す、などの工夫も後でできますが、いったん共通でOKです）
category_options = ["食費", "交際費", "衣服・美容", "交通費", "サークル・音楽", "バイト収入", "その他"]
category = st.selectbox("カテゴリ", category_options)

amount = st.number_input("金額（円）", min_value=0, step=100)

if st.button("➕ 記録する"):
    # 👈 支出ならマイナス、収入ならプラスの数値に変換します
    final_amount = -amount if action_type == "支出" else amount
    
    new_data = pd.DataFrame([[date, category, final_amount]], columns=["日付", "カテゴリ", "金額"])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success(f"{action_type}を記録しました！")
    st.rerun()



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
    chart_data = df_current_month.groupby("カテゴリ")["金額"].sum()
    st.bar_chart(chart_data)
    
    st.header("📋 これまでの履歴一覧")
    st.dataframe(df_current_month.sort_values("日付", ascending=False), use_container_width=True)
    
    # データをリセットするボタン
    if st.sidebar.button("⚠️ データをすべて削除"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.rerun()

