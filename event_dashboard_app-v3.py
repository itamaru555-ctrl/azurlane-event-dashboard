import streamlit as st
import datetime
import math
import pandas as pd

# ページ基本設定
st.set_page_config(
    page_title="アズレン イベントショップ交換計画ダッシュボード (Pt交換ラインナップ対応版)",
    page_icon="⚓",
    layout="wide"
)

st.title("⚓ アズールレーン イベントショップ交換計画ダッシュボード (v3)")
st.caption("『Pt交換ラインナップ.png』の全アイテムデータを反映した自分専用の計画ダッシュボードなのだ！")

# --- サイドバー：入力フォーム ---
st.sidebar.header("⚙️ イベント設定 & 現在の状況")

event_name = st.sidebar.text_input("イベント名", "期間限定イベント（ヤーンバーアデン入手等）")
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

# --- 初期データセット (Pt交換ラインナップ.png より抽出) ---
initial_items = [
    {"順位": 1, "カテゴリ": "最優先", "アイテム名": "SSR艦船 ヤーンバーアデン", "単価Pt": 8000, "最大数": 5, "交換済み数": 1, "交換済み": False},
    {"順位": 2, "カテゴリ": "必須枠", "アイテム名": "SSR設備 旧式重火砲", "単価Pt": 2000, "最大数": 2, "交換済み数": 0, "交換済み": False},
    {"順位": 3, "カテゴリ": "必須枠", "アイテム名": "SSR装備 淵の下の力持ち", "単価Pt": 2000, "最大数": 2, "交換済み数": 0, "交換済み": False},
    {"順位": 4, "カテゴリ": "必須枠", "アイテム名": "SR装備 ダブル球型砲丸", "単価Pt": 1000, "最大数": 2, "交換済み数": 0, "交換済み": False},
    {"順位": 5, "カテゴリ": "必須枠", "アイテム名": "DR強化ユニット", "単価Pt": 500, "最大数": 30, "交換済み数": 0, "交換済み": False},
    {"順位": 6, "カテゴリ": "必須枠", "アイテム名": "PR強化ユニット", "単価Pt": 1000, "最大数": 10, "交換済み数": 0, "交換済み": False},
    {"順位": 7, "カテゴリ": "推奨枠", "アイテム名": "メンタルユニットII×10", "単価Pt": 1000, "最大数": 5, "交換済み数": 0, "交換済み": False},
    {"順位": 8, "カテゴリ": "推奨枠", "アイテム名": "メンタルユニット×100", "単価Pt": 300, "最大数": 10, "交換済み数": 0, "交換済み": False},
    {"順位": 9, "カテゴリ": "推奨枠", "アイテム名": "特殊装備変化石T1", "単価Pt": 2500, "最大数": 2, "交換済み数": 0, "交換済み": False},
    {"順位": 10, "カテゴリ": "推奨枠", "アイテム名": "特殊装備変化石T2", "単価Pt": 600, "最大数": 10, "交換済み数": 0, "交換済み": False},
    {"順位": 11, "カテゴリ": "推奨枠", "アイテム名": "特殊装備コア", "単価Pt": 300, "最大数": 5, "交換済み数": 0, "交換済み": False},
    {"順位": 12, "カテゴリ": "推奨枠", "アイテム名": "特殊装備強化石T2", "単価Pt": 90, "最大数": 50, "交換済み数": 0, "交換済み": False},
    {"順位": 13, "カテゴリ": "好み枠", "アイテム名": "装備外装箱", "単価Pt": 2000, "最大数": 10, "交換済み数": 0, "交換済み": False},
    {"順位": 14, "カテゴリ": "オフニャ", "アイテム名": "SSRオフニャ", "単価Pt": 3000, "最大数": 1, "交換済み数": 0, "交換済み": False},
    {"順位": 15, "カテゴリ": "オフニャ", "アイテム名": "ネコハコSSR", "単価Pt": 3000, "最大数": 2, "交換済み数": 0, "交換済み": False},
    {"順位": 16, "カテゴリ": "調整枠", "アイテム名": "資金×2000", "単価Pt": 500, "最大数": 5, "交換済み数": 0, "交換済み": False},
    {"順位": 17, "カテゴリ": "調整枠", "アイテム名": "燃料×1000", "単価Pt": 450, "最大数": 5, "交換済み数": 0, "交換済み": False},
]

if "shop_df_v3" not in st.session_state:
    st.session_state.shop_df_v3 = pd.DataFrame(initial_items)

# --- 編集可能なデータテーブル ---
st.subheader("🛒 『Pt交換ラインナップ』交換目標と進捗管理")
st.caption("※「交換済み」にチェックを入れると、そのアイテムの必要Ptが自動的に除外されて残り必要周回数が再計算されるのだ！")

edited_df = st.data_editor(
    st.session_state.shop_df_v3,
    column_config={
        "交換済み": st.column_config.CheckboxColumn("完了", default=False),
        "単価Pt": st.column_config.NumberColumn("単価Pt", min_value=0, format="%d Pt"),
        "最大数": st.column_config.NumberColumn("最大数", min_value=1),
        "交換済み数": st.column_config.NumberColumn("済数", min_value=0),
    },
    num_rows="dynamic",
    use_container_width=True
)

# --- 計算処理 ---
results = []
cum_needed_pt = 0
total_shop_pt = 0
already_spent_pt = 0

for _, row in edited_df.iterrows():
    total_item_pt = row["単価Pt"] * row["最大数"]
    total_shop_pt += total_item_pt
    
    is_done = row["交換済み"]
    if is_done:
        already_spent_pt += total_item_pt
        status = "🎉 交換完了"
        item_needed = 0
        runs_for_this = 0
        daily_runs_for_this = 0
        oil_for_this = 0
    else:
        # 一部交換考慮（もし交換済み数が設定されている場合）
        done_cnt = min(row["最大数"], row["交換済み数"])
        already_spent_pt += row["単価Pt"] * done_cnt
        item_needed = row["単価Pt"] * (row["最大数"] - done_cnt)
        cum_needed_pt += item_needed
        
        # 自然増加だけでの達成判定
        rem_pt_after_natural = max(0, cum_needed_pt - est_final_pt_no_farm)
        runs_for_this = math.ceil(rem_pt_after_natural / pt_per_run) if pt_per_run > 0 else 0
        daily_runs_for_this = round(runs_for_this / remaining_days, 1) if remaining_days > 0 else 0
        oil_for_this = runs_for_this * oil_per_run
        
        status = "✅ 自然増加でOK" if runs_for_this == 0 else "⚠️ 周回必要"

    results.append({
        "順位": row["順位"],
        "カテゴリ": row["カテゴリ"],
        "アイテム名": row["アイテム名"],
        "合計Pt": f"{total_item_pt:,} Pt",
        "状態": status,
        "未交換必要Pt": f"{item_needed:,} Pt",
        "必要周回": f"{runs_for_this} 回" if not is_done else "-",
        "1日目標": f"{daily_runs_for_this} 回/日" if not is_done else "-",
        "消費燃料": f"{oil_for_this:,} 燃料" if not is_done else "-"
    })

res_df = pd.DataFrame(results)

# --- サマリー表示 ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("🗓️ 残り期間", f"{remaining_days} 日", f"終了: {event_end_date.strftime('%m/%d')}")
col2.metric("💰 現在所持 + 獲得予想", f"{est_final_pt_no_farm:,} Pt", f"現在: {current_pt:,} Pt")
col3.metric("🛒 未交換分の必要Pt", f"{cum_needed_pt:,} Pt")

# 総周回数・総消費オイル
total_rem_needed = max(0, cum_needed_pt - est_final_pt_no_farm)
total_runs_needed = math.ceil(total_rem_needed / pt_per_run) if pt_per_run > 0 else 0
total_daily_runs = round(total_runs_needed / remaining_days, 1) if remaining_days > 0 else 0
total_oil_needed = total_runs_needed * oil_per_run

col4.metric("⚔️ 必要周回 (1日あたり)", f"{total_runs_needed} 回 ({total_daily_runs} 回/日)", f"合計 {total_oil_needed:,} オイル")

st.markdown("---")

# 計算結果テーブルの表示
st.subheader("📊 未交換目標の周回シミュレーション結果")
st.dataframe(res_df, use_container_width=True)

# 進行度プログレスバー
st.markdown("### 📈 ショップコンプリート進捗率")
current_total_earned_val = current_pt + already_spent_pt
overall_progress = min(1.0, current_total_earned_val / total_shop_pt) if total_shop_pt > 0 else 0

st.progress(overall_progress)
st.caption(f"ショップ全体ラインナップ ({total_shop_pt:,} Pt) に対する達成度: **{overall_progress*100:.1f}%** （累計獲得推定: {current_total_earned_val:,} Pt / 残り全回収必要: {max(0, total_shop_pt - current_total_earned_val):,} Pt）")
