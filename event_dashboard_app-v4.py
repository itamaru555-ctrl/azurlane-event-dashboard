import streamlit as st
import datetime
import math
import pandas as pd

# ページ基本設定
st.set_page_config(
    page_title="アズレン イベントショップ交換計画 (自由優先度版)",
    page_icon="⚓",
    layout="wide"
)

st.title("⚓ アズールレーン イベントショップ周回＆交換計画 (自由優先度調整版)")
st.caption("優先順位を自由に変更・並び替えできるカスタム対応ダッシュボードなのだ！")

# --- サイドバー：入力フォーム ---
st.sidebar.header("⚙️ イベント設定 & 現在の状況")

event_name = st.sidebar.text_input("イベント名", "Pt交換ラインナップ")
event_end_date = st.sidebar.date_input("イベント終了日", datetime.date(2026, 11, 5))

st.sidebar.markdown("---")
st.sidebar.subheader("💰 現在のプレイ状況")
current_pt = st.sidebar.number_input("現在の所持Pt", min_value=0, value=15000, step=500)
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

# --- サマリー表示 ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("🗓️ 残り日数", f"{remaining_days} 日", f"終了: {event_end_date.strftime('%m/%d')}")
col2.metric("💰 現在の所持Pt", f"{current_pt:,} Pt")
col3.metric("🎁 日課獲得見込み", f"+{est_daily_total:,} Pt", f"{daily_income:,} Pt/日")
col4.metric("📈 自然増加最終予想", f"{est_final_pt_no_farm:,} Pt")

st.markdown("---")

st.subheader("🛒 交換目標リスト (優先順位・個数は自由に変更可能！)")
st.info("💡 **使いかた**: 表の「優先度」の数字を自由に打ち替えて変更できます！数字が小さいものから順に計算されます。不要なアイテムを削除したり、欲しいアイテムを追加することも自由自在なのだ！")

# 初期データ
if "items_df" not in st.session_state:
    initial_items = [
        {"優先度": 1, "カテゴリ": "最優先", "アイテム名": "SSR艦船 ヤーンバーアデン (8000Pt×5)", "単価Pt": 8000, "個数": 5, "完了": False},
        {"優先度": 2, "カテゴリ": "必須枠", "アイテム名": "SSR設備 旧式重火砲 (2000Pt×2)", "単価Pt": 2000, "個数": 2, "完了": False},
        {"優先度": 3, "カテゴリ": "必須枠", "アイテム名": "SSR装備 淵の下の力持ち (2000Pt×2)", "単価Pt": 2000, "個数": 2, "完了": False},
        {"優先度": 4, "カテゴリ": "必須枠", "アイテム名": "SR装備 ダブル球型砲丸 (1000Pt×2)", "単価Pt": 1000, "個数": 2, "完了": False},
        {"優先度": 5, "カテゴリ": "必須枠", "アイテム名": "DR強化ユニット (500Pt×30)", "単価Pt": 500, "個数": 30, "完了": False},
        {"優先度": 6, "カテゴリ": "必須枠", "アイテム名": "PR強化ユニット (1000Pt×10)", "単価Pt": 1000, "個数": 10, "完了": False},
        {"優先度": 7, "カテゴリ": "推奨枠", "アイテム名": "メンタルユニットII×10 (1000Pt×5)", "単価Pt": 1000, "個数": 5, "完了": False},
        {"優先度": 8, "カテゴリ": "推奨枠", "アイテム名": "メンタルユニット×100 (300Pt×10)", "単価Pt": 300, "個数": 10, "完了": False},
        {"優先度": 9, "カテゴリ": "推奨枠", "アイテム名": "特殊装備変化石T1 (2500Pt×2)", "単価Pt": 2500, "個数": 2, "完了": False},
        {"優先度": 10, "カテゴリ": "推奨枠", "アイテム名": "特殊装備変化石T2 (600Pt×10)", "単価Pt": 600, "個数": 10, "完了": False},
        {"優先度": 11, "カテゴリ": "推奨枠", "アイテム名": "特殊装備コア (300Pt×5)", "単価Pt": 300, "個数": 5, "完了": False},
        {"優先度": 12, "カテゴリ": "好み枠", "アイテム名": "装備外装箱 (2000Pt×10)", "単価Pt": 2000, "個数": 10, "完了": False},
        {"優先度": 13, "カテゴリ": "オフニャ", "アイテム名": "SSRオフニャ / ネコハコSSR (3000Pt×3)", "単価Pt": 3000, "個数": 3, "完了": False},
        {"優先度": 14, "カテゴリ": "調整枠", "アイテム名": "資金・燃料・パーツ各種", "単価Pt": 1000, "個数": 5, "完了": False},
    ]
    st.session_state.items_df = pd.DataFrame(initial_items)

# 編集用Editor
edited_df = st.data_editor(
    st.session_state.items_df,
    column_config={
        "完了": st.column_config.CheckboxColumn("完了?", default=False),
        "優先度": st.column_config.NumberColumn("優先度", min_value=1, step=1, help="数字が小さいほど優先して計算されます"),
        "単価Pt": st.column_config.NumberColumn("単価Pt", min_value=0, format="%d Pt"),
        "個数": st.column_config.NumberColumn("個数", min_value=1, step=1),
    },
    num_rows="dynamic",
    use_container_width=True,
    key="editor"
)

# 優先度順に並び替え
sorted_df = edited_df.sort_values(by="優先度").reset_index(drop=True)

# リアルタイム再計算
calc_results = []
cum_unclaimed_pt = 0
total_all_pt = 0
total_completed_pt = 0

for idx, row in sorted_df.iterrows():
    item_total_pt = row["単価Pt"] * row["個数"]
    total_all_pt += item_total_pt
    
    if row["完了"]:
        total_completed_pt += item_total_pt
        status = "🎉 交換完了"
        runs = 0
        daily_runs = 0.0
        oil = 0
    else:
        cum_unclaimed_pt += item_total_pt
        needed_pt = max(0, cum_unclaimed_pt - est_final_pt_no_farm)
        runs = math.ceil(needed_pt / pt_per_run) if pt_per_run > 0 else 0
        daily_runs = round(runs / remaining_days, 1) if remaining_days > 0 else 0
        oil = runs * oil_per_run
        status = "✅ 達成可能" if runs == 0 else "⚠️ 周回必要"
    
    calc_results.append({
        "順位": int(row["優先度"]),
        "カテゴリ": row["カテゴリ"],
        "アイテム名": row["アイテム名"],
        "合計必要Pt": f"{item_total_pt:,} Pt",
        "状態": status,
        "必要周回数": f"{runs} 回" if not row["完了"] else "-",
        "1日目標周回": f"{daily_runs} 回/日" if not row["完了"] else "-",
        "消費燃料": f"{oil:,} 燃料" if not row["完了"] else "-"
    })

df_calc = pd.DataFrame(calc_results)

st.markdown("### 📊 優先度順の計算結果一覧")
st.dataframe(df_calc, use_container_width=True)

# 進行度表示
progress_pct = min(1.0, (total_completed_pt + current_pt) / total_all_pt) if total_all_pt > 0 else 0.0
st.markdown("### 📈 コンプリート進捗率")
st.progress(progress_pct)
st.caption(f"全ラインナップ {total_all_pt:,} Pt に対する達成・所持割合: **{progress_pct*100:.1f}%** （残り未交換必要Pt: {max(0, cum_unclaimed_pt - current_pt):,} Pt）")
