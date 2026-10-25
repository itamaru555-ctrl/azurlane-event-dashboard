import streamlit as st
import datetime
import math
import pandas as pd

# ページ基本設定
st.set_page_config(
    page_title="アズレン イベントショップ交換計画ダッシュボード v2",
    page_icon="⚓",
    layout="wide"
)

st.title("⚓ アズールレーン 周回＆イベントショップ交換計画ダッシュボード (v2)")
st.caption("交換済みアイテムのチェック機能を追加！スマホ・PCからリアルタイムで進捗管理できるのだ！")

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

# --- 初期アイテムデータセット ---
if "shop_df" not in st.session_state:
    st.session_state.shop_df = pd.DataFrame([
        {"交換済み": False, "優先度": 1, "カテゴリ": "最優先", "アイテム名": "限定UR/SSR艦船", "必要Pt": 10000},
        {"交換済み": False, "優先度": 2, "カテゴリ": "必須枠", "アイテム名": "指向型型兵装設計図×10", "必要Pt": 6000},
        {"交換済み": False, "優先度": 3, "カテゴリ": "推奨枠", "アイテム名": "指向型強化ユニット×10", "必要Pt": 5000},
        {"交換済み": False, "優先度": 4, "カテゴリ": "推奨枠", "アイテム名": "メンタルユニット×1000", "必要Pt": 3000},
        {"交換済み": False, "優先度": 5, "カテゴリ": "推奨枠", "アイテム名": "上級試作型兵装パーツ×15", "必要Pt": 4500},
        {"交換済み": False, "優先度": 6, "カテゴリ": "調整枠", "アイテム名": "資金・メンタルキューブ・各種素材", "必要Pt": 12000},
    ])

st.subheader("🛒 交換目標リストの編集（交換済みチェック＆編集可能）")
st.caption("👇 表の中の「交換済み」にチェックを入れたり、必要Ptやアイテム名を直接編集・追加できるのだ！")

# 編集可能なデータフレーム (st.data_editor)
edited_df = st.data_editor(
    st.session_state.shop_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "交換済み": st.column_config.CheckboxColumn("交換済み?", default=False),
        "優先度": st.column_config.NumberColumn("優先度", min_value=1, max_value=20, step=1),
        "必要Pt": st.column_config.NumberColumn("必要Pt", min_value=0, step=500, format="%d Pt"),
    },
    key="editor"
)

# 優先度順にソート
edited_df = edited_df.sort_values(by="優先度").reset_index(drop=True)

# --- 計算ロジック ---
results = []
cum_unexchanged_pt = 0
total_all_pt = edited_df["必要Pt"].sum()
already_spent_pt = edited_df[edited_df["交換済み"] == True]["必要Pt"].sum()

for _, row in edited_df.iterrows():
    is_done = row["交換済み"]
    pt_cost = int(row["必要Pt"])
    
    if is_done:
        status = "🎉 交換済み"
        runs = 0
        daily_runs = 0.0
        total_oil = 0
        cum_str = "-"
    else:
        cum_unexchanged_pt += pt_cost
        needed_pt = max(0, cum_unexchanged_pt - est_final_pt_no_farm)
        runs = math.ceil(needed_pt / pt_per_run) if pt_per_run > 0 else 0
        daily_runs = round(runs / remaining_days, 1) if remaining_days > 0 else 0
        total_oil = runs * oil_per_run
        status = "✅ 達成可能" if runs == 0 else "⚠️ 周回必要"
        cum_str = f"{cum_unexchanged_pt:,} Pt"

    results.append({
        "順位": f"【{int(row['優先度'])}】",
        "状態": status,
        "カテゴリ": row["カテゴリ"],
        "アイテム名": row["アイテム名"],
        "必要Pt": f"{pt_cost:,} Pt",
        "未交換累計Pt": cum_str,
        "必要周回": f"{runs} 回" if not is_done else "-",
        "1日目標": f"{daily_runs} 回/日" if not is_done else "-",
        "消費燃料": f"{total_oil:,} 燃料" if not is_done else "-"
    })

df_results = pd.DataFrame(results)

st.markdown("---")
st.subheader("📊 周回・交換計画シミュレーション結果")
st.dataframe(df_results, use_container_width=True)

# 進捗計算
remaining_unexchanged_total = cum_unexchanged_pt
progress_val = min(1.0, (already_spent_pt + current_pt) / total_all_pt) if total_all_pt > 0 else 1.0

st.markdown("### 📈 イベントショップ完全コンプリート進捗")
st.progress(progress_val)
st.caption(f"ショップ全目標 {total_all_pt:,} Pt のうち、**交換済み: {already_spent_pt:,} Pt** + **所持Pt: {current_pt:,} Pt** (達成度: **{progress_val*100:.1f}%**)")
st.info(f"💡 **残り未交換アイテムに必要なPt**: 合計 **{remaining_unexchanged_total:,} Pt** （日課予測 {est_final_pt_no_farm:,} Pt と比較して、あと **{max(0, remaining_unexchanged_total - est_final_pt_no_farm):,} Pt** の周回が必要なのだ！）")
