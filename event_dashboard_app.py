import streamlit as st
import datetime
import math
import pandas as pd

# ページ基本設定
st.set_page_config(
    page_title="アズレン イベントショップ交換計画ダッシュボード",
    page_icon="⚓",
    layout="wide"
)

st.title("⚓ アズールレーン 周回＆イベントショップ交換計画ダッシュボード")
st.caption("GitHub + Streamlit Cloud で運用できる自分専用のインタラクティブ計画アプリなのだ！")

# --- サイドバー：入力フォーム ---
st.sidebar.header("⚙️ イベント設定 & 現在の状況")

event_name = st.sidebar.text_input("イベント名", "アズールレーン 期間限定イベント")
event_end_date = st.sidebar.date_input("イベント終了日", datetime.date(2026, 11, 5))

st.sidebar.markdown("---")
st.sidebar.subheader("💰 現在のプレイ状況")
current_pt = st.sidebar.number_input("現在の所持Pt", min_value=0, value=12500, step=500)
daily_income = st.sidebar.number_input("1日の日課Pt (デイリー/SP等)", min_value=0, value=2240, step=100)

st.sidebar.markdown("---")
st.sidebar.subheader("⚔️ 周回海域の効率")
pt_per_run = st.sidebar.number_input("1周あたりの獲得Pt", min_value=1, value=180)
oil_per_run = st.sidebar.number_input("1周あたりの消費オイル", min_value=0, value=260)

# --- 残り日数の計算 ---
today = datetime.date.today()
remaining_days = max(1, (event_end_date - today).days)
est_daily_total = daily_income * remaining_days
est_final_pt_no_farm = current_pt + est_daily_total

# --- サマリー表示 (Metrics) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("🗓️ 残り日数", f"{remaining_days} 日", f"終了: {event_end_date.strftime('%m/%d')}")
col2.metric("💰 現在の所持Pt", f"{current_pt:,} Pt")
col3.metric("🎁 日課獲得見込み", f"+{est_daily_total:,} Pt", f"{daily_income:,} Pt/日")
col4.metric("📈 自然増加最終予想", f"{est_final_pt_no_farm:,} Pt")

st.markdown("---")

# --- 交換目標の編集エリア ---
st.subheader("🛒 交換目標リストと進行度")

default_items = [
    {"優先度": 1, "カテゴリ": "最優先", "アイテム名": "限定UR/SSR艦船", "必要Pt": 10000},
    {"優先度": 2, "カテゴリ": "必須枠", "アイテム名": "指向型型兵装設計図×10", "必要Pt": 6000},
    {"優先度": 3, "カテゴリ": "推奨枠", "アイテム名": "指向型強化ユニット×10", "必要Pt": 5000},
    {"優先度": 4, "カテゴリ": "推奨枠", "アイテム名": "メンタルユニット×1000", "必要Pt": 3000},
    {"優先度": 5, "カテゴリ": "推奨枠", "アイテム名": "上級試作型兵装パーツ×15", "必要Pt": 4500},
    {"優先度": 6, "カテゴリ": "調整枠", "アイテム名": "資金・メンタルキューブ・各種素材", "必要Pt": 12000},
]

# データフレーム計算
results = []
cum_pt = 0

for item in default_items:
    cum_pt += item["必要Pt"]
    needed_pt = max(0, cum_pt - est_final_pt_no_farm)
    runs = math.ceil(needed_pt / pt_per_run) if pt_per_run > 0 else 0
    daily_runs = round(runs / remaining_days, 1) if remaining_days > 0 else 0
    total_oil = runs * oil_per_run
    
    status = "✅ 達成可能" if runs == 0 else "⚠️ 周回必要"
    
    results.append({
        "順位": f"【{item['優先度']}】",
        "カテゴリ": item["カテゴリ"],
        "アイテム名": item["アイテム名"],
        "必要Pt": f"{item['必要Pt']:,}",
        "累計必要Pt": f"{cum_pt:,}",
        "判定": status,
        "必要周回数": f"{runs} 回",
        "1日目標周回": f"{daily_runs} 回/日",
        "推定消費オイル": f"{total_oil:,} 燃料"
    })

df_results = pd.DataFrame(results)
st.dataframe(df_results, use_container_width=True)

# 進行度プログレスバー
st.markdown("### 📊 全目標クリアまでの進捗率")
total_target_pt = cum_pt
progress = min(1.0, current_pt / total_target_pt) if total_target_pt > 0 else 0
st.progress(progress)
st.caption(f"全目標 {total_target_pt:,} Pt に対する現在の達成率: **{progress*100:.1f}%** (残り必要: {max(0, total_target_pt - current_pt):,} Pt)")

st.info("💡 **アドバイス**: スライダーや数字を変更するとリアルタイムで周回数や消費オイルが更新されるのだ！")
