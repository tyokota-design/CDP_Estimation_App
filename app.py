import streamlit as st
import pandas as pd
import io

# --- ページ設定 ---
st.set_page_config(page_title="CDP提案支援ツール", layout="wide")

# --- デザイン：高級感のあるモダンなUI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans JP', sans-serif; background-color: #f4f7f9 !important; }
    
    /* ヘッダー：深いネイビーのグラデーション */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 40px; border-radius: 24px; color: white; margin-bottom: 40px; text-align: center;
        box-shadow: 0 12px 24px rgba(30, 60, 114, 0.15);
    }
    
    .header-title {
        background: -webkit-linear-gradient(left, #ffffff, #cbd5e1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 2.4rem;
        letter-spacing: -0.02em;
    }
    
    /* 工程カード：境界線を消し、リッチな影で浮遊感を演出 */
    /* st.container(border=True) の標準スタイルを強力に上書き */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: none !important; /* グレーの実線を消去 */
        border-radius: 24px !important;
        padding: 32px !important;
        box-shadow: 0 15px 45px -10px rgba(30, 60, 114, 0.1), 0 5px 15px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
        margin-bottom: 0px !important;
    }
    
    /* ホバー時の高級感あふれる演出 */
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 30px 60px -15px rgba(30, 60, 114, 0.18) !important;
    }

    /* ステップバッジ：グラデーションと光沢 */
    .step-badge {
        display: inline-block;
        width: 30px; height: 30px;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white; border-radius: 8px; text-align: center;
        font-size: 0.95rem; font-weight: 800; line-height: 30px;
        box-shadow: 0 4px 10px rgba(30, 60, 114, 0.2);
    }

    /* コネクトライン：太さとグラデーション */
    .flow-line {
        width: 4px; height: 40px;
        background: linear-gradient(to bottom, #1e3c72, #e2e8f0);
        margin-left: 51px; /* バッジの中央に正確に配置 */
    }

    /* 説明ボックス：淡いブルーの背景と左側のアクセント線 */
    .task-info-content {
        margin-left: 54px;
        padding: 20px 25px;
        background: #f8fafc;
        border-radius: 0 16px 16px 16px;
        border-left: 5px solid #1e3c72;
        color: #334155; line-height: 1.8;
    }

    /* 工数タグ：丸みのあるモダンなデザイン */
    .hour-tag {
        display: inline-block;
        padding: 6px 16px;
        background: linear-gradient(135deg, #e0e7ff 0%, #eff6ff 100%);
        color: #1e3c72; border-radius: 50px;
        font-weight: 800; font-size: 0.8rem; margin-bottom: 12px;
        border: 1px solid rgba(30, 60, 114, 0.05);
    }

    /* 見積サマリー */
    .price-display { color: #b91c1c; font-size: 4.2rem; font-weight: 900; line-height: 1; margin: 15px 0; }
    .sticky-summary { position: sticky; top: 2rem; }
    
    /* モジュールカード（サイドバー） */
    .module-card-header {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        color: white; padding: 8px 15px; font-size: 0.85rem; font-weight: bold;
        display: flex; align-items: center; border-radius: 12px 12px 0 0;
    }
    .module-card-body {
        padding: 12px; color: #475569; font-size: 0.8rem; line-height: 1.6;
        background: linear-gradient(to bottom, #ffffff, #f9fbff);
        border-radius: 0 0 12px 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- データ読み込み ---
def load_data_direct():
    try:
        with open("pricing_table.xlsx", "rb") as f:
            df = pd.read_excel(f, engine='openpyxl')
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].astype(str).str.strip().str.replace('（', '(').str.replace('）', ')')
        return df
    except Exception as e:
        st.error(f"Excelを読み込めませんでした: {e}")
        st.stop()

df_master = load_data_direct()

# --- サイドバー：設定 ＆ 解説 ---
with st.sidebar:
    st.header("🏢 案件設定")
    client_name = st.text_input("顧客名", value="○○株式会社")
    st.divider()
    category = st.selectbox("1. 支援対象", ["初回答支援", "既回答支援"])
    plan_type = st.radio("2. 支援スタイル", ["フルパッケージ", "回数制限プラン"])
    st.divider()
    # 選択肢の拡張
    target_theme = st.radio("3. 対象回答項目", ["気候変動", "水セキュリティ", "気候変動＋水セキュリティ"], index=0)
    
    # 水セキュリティ単体の時は「支援範囲」を表示しない
    limit_scope = False
    if target_theme != "水セキュリティ":
        limit_scope = st.toggle("支援範囲を限定する")
    scope = "全Module(気候変動)"
    if limit_scope:
        scope = st.radio("範囲の選択", ["M1-6,13", "M7のみ"])
    
    extra_reviews = 0
    if plan_type == "回数制限プラン":
        st.subheader("オプション")
        
        # テーマに合わせてラベルの表示（h数）を切り替える
        if target_theme == "気候変動":
            opt_label = "追加レビュー回数 (+10h/回)"
        elif target_theme == "水セキュリティ":
            opt_label = "追加レビュー回数 (+5h/回)"
        else: # 気候変動＋水セキュリティ
            opt_label = "追加レビュー回数 (+15h/回)"
            
        extra_reviews = st.number_input(opt_label, min_value=0, value=0, step=1)

    st.divider()
    hourly_rate = st.select_slider("提案単価 (円/h)", options=[10000, 20000, 30000, 40000, 50000, 60000], value=40000)

    st.divider()
    with st.expander("🔍 Module内容の早見表"):
        module_data = [
            ("M1 イントロダクション", "📝", "事業概要、報告境界、およびCDPへの回答姿勢の定義に関して整理します。全ての評価の土台となる基礎情報の提示に関して記載します。"),
            ("M2 依存・リスク・機会", "🔍", "自然資本や気候への依存度・インパクトの特定、および事業に及ぼすリスクと機会の特定・評価・管理プロセスに関して詳述します。"),
            ("M3 リスク・機会の開示", "📢", "特定されたリスクと機会の具体的な内容、および財務状況や事業活動に与える実際的・潜在的な影響の開示に関して記載します。"),
            ("M4 ガバナンス", "🏛️", "環境課題に対する取締役会の監督体制や経営陣の責任、および気候関連課題を考慮した報酬制度等の仕組みの明確化に関して記載します。"),
            ("M5 事業戦略", "📈", "気候変動リスクを考慮した事業計画や財務戦略、および不確実性に備えるためのシナリオ分析の実施状況に関して整理します。"),
            ("M6 環境パフォーマンス - 連結", "🏢", "グループ全体の環境データ収集における連結範囲の策定、および組織全体のパフォーマンスの全体像の定義に関して整理します。"),
            ("M7 環境パフォーマンス - 気候", "⚡", "Scope 1, 2, 3の排出実績値、燃料・電力消費量、および再生可能エネルギーの導入状況といった定量データの記載に関して詳述します。"),
            ("M9 環境パフォーマンス - ウォーター", "💧", "水リスク、水の効率性や原単位、水量や水質などの水関連目標などを記載します。"),
            ("M13 追加情報・承認", "✅", "気候変動以外の環境活動や補足情報の提示、および経営層による最終的な回答内容の承認プロセスの完結に関して記載します。")
        ]
        for title, icon, text in module_data:
            st.markdown(f"""
                <div style="margin-bottom:12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-radius:12px;">
                    <div class="module-card-header"><span style="margin-right:8px;">{icon}</span> {title}</div>
                    <div class="module-card-body">{text}</div>
                </div>
            """, unsafe_allow_html=True)

# --- フィルタリング ---
# 検索用Scope文字列の作成
search_scope = scope.replace('（', '(').replace('）', ')')

if target_theme == "気候変動":
    # 1. 気候変動のみ：選択されたScopeを適用
    df_display = df_master[
        (df_master['theme'] == "気候変動") & 
        (df_master['category'] == category) & 
        (df_master['plan_type'] == plan_type) & 
        (df_master['scope'].str.replace('（', '(').str.replace('）', ')') == search_scope)
    ].reset_index(drop=True)

elif target_theme == "水セキュリティ":
    # 2. 水セキュリティのみ：Scopeを「全Module(気候変動)」に固定して抽出
    df_display = df_master[
        (df_master['theme'] == "水セキュリティ") & 
        (df_master['category'] == category) & 
        (df_master['plan_type'] == plan_type) & 
        (df_master['scope'].str.replace('（', '(').str.replace('）', ')') == "全Module(気候変動)")
    ].reset_index(drop=True)

else:
    # 3. 気候変動＋水セキュリティ：両方のテーマに「現在のScope」を適用して抽出
    df_display = df_master[
        (df_master['theme'].isin(["気候変動", "水セキュリティ"])) & 
        (df_master['category'] == category) & 
        (df_master['plan_type'] == plan_type) & 
        (df_master['scope'].str.replace('（', '(').str.replace('）', ')') == search_scope)
    ].reset_index(drop=True)

# --- メインエリア ---
col_left, col_right = st.columns([1.6, 1], gap="large")

with col_left:
    st.markdown(f"""
        <div class="main-header">
            <h1 class="header-title">CDP回答支援見積ツール</h1>
            <p style="opacity:0.9; margin-top:5px; font-weight:bold; font-size:1.1rem;">{category} / {plan_type}</p>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("📋 支援工程の選択")
    total_h = 0
    selected_items = []

    if df_display.empty:
        st.warning("Excelに該当データがありません。条件を確認してください。")
    else:
        for i, row in df_display.iterrows():
            # 1. チェックボックスとタイトルを表示
            # ** で囲むことで文字を強調し、### で少し大きく表示します
            checked = st.checkbox(f"### **{i+1}. {row['item']}**", value=True, key=f"item_{i}")
            
            # 2. 説明文と工数をひとつのHTML枠に閉じ込める
            desc = row['description'] if pd.notna(row['description']) else "追加の説明はありません。"
            
            st.markdown(f"""
                <div style="
                    background: white; 
                    padding: 24px; 
                    border-radius: 20px; 
                    box-shadow: 0 10px 30px rgba(30, 60, 114, 0.1);
                    border: none;
                    margin-left: 45px;
                    margin-top: -10px;
                    margin-bottom: 20px;
                ">
                    <div style="margin-bottom: 10px;">
                        <span class="hour-tag" style="margin-bottom:0; font-weight:800;">⏱ 想定工数: {row['hours']}h</span>
                    </div>
                    <div style="color: #334155; line-height: 1.7; font-size: 0.95rem;">
                        {desc}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 3. 次の工程へのコネクトライン
            if i < len(df_display) - 1:
                st.markdown('<div class="flow-line" style="margin-left: 60px;"></div>', unsafe_allow_html=True)
            
            # 工数計算
            if checked:
                total_h += row['hours']
                selected_items.append({"工程": row['item'], "工数(h)": row['hours']})

with col_right:
    st.markdown('<div class="sticky-summary">', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f"<h5>💰 御見積サマリー</h5>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:1.1rem;'>{client_name} 御中</p>", unsafe_allow_html=True)
        
        # --- オプション・割引ロジックの定義 ---
        # テーマごとの追加レビュー1回あたりの工数
        if target_theme == "気候変動":
            rate_per_review = 10
        elif target_theme == "水セキュリティ":
            rate_per_review = 5
        else:  # 気候変動＋水セキュリティ
            rate_per_review = 15
        
        option_h = extra_reviews * rate_per_review
        
        # セット割引（気候変動＋水セキュリティ）の適用
        discount_h = 25 if target_theme == "気候変動＋水セキュリティ" else 0
        
        # 合計工数の計算（0以下にならないようにmaxを使用）
        grand_total_h = max(0, total_h + option_h - discount_h)
        grand_total_price = grand_total_h * hourly_rate
        
        # 価格表示
        st.markdown(f'<div class="price-display">¥{int(grand_total_price):,}</div>', unsafe_allow_html=True)
        
        st.divider()
        st.write(f"🔹 基本工数: **{total_h} h**")
        
        if extra_reviews > 0:
            st.write(f"🔸 追加オプション: **+{option_h} h** ({extra_reviews}回)")
            st.caption(f"（レビュー単価: {rate_per_review}h/回）")
            
        if discount_h > 0:
            st.write(f"🎁 セット割引: **-{discount_h} h**")
            
        st.write(f"### 合計: **{grand_total_h} h**")
        st.caption(f"適用単価: ¥{hourly_rate:,} / h")
        
        if grand_total_h > 0:
            import datetime
            # 1. ヘッダー情報（日時・顧客名・条件）の作成
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            header_info = [
                ["見積作成日時", now],
                ["顧客名", client_name],
                ["対象回答項目", target_theme],
                ["支援対象", category],
                ["支援スタイル", plan_type],
                ["適用単価 (円/h)", f"{hourly_rate:,}"],
                ["", ""], # 空行
                ["【選択された工程の内訳】", ""],
                ["工程名", "工数(h)"]
            ]
            
            # 2. 工程内訳の作成
            body_data = [[item["工程"], item["工数(h)"]] for item in selected_items]
            
            # 3. オプション・割引・合計情報の作成
            footer_info = [["", ""]] # 空行
            if extra_reviews > 0:
                footer_info.append([f"追加レビューオプション({extra_reviews}回)", option_h])
            if discount_h > 0:
                footer_info.append(["セット割引", -discount_h])
            
            footer_info.extend([
                ["", ""], # 空行
                ["合計工数", f"{grand_total_h} h"],
                ["合計金額 (税抜)", f"¥{int(grand_total_price):,}"]
            ])

            # 4. すべてを結合してCSV文字列を作成
            all_csv_rows = header_info + body_data + footer_info
            
            # StringIOを使ってCSV形式に書き出し
            output = io.StringIO()
            import csv
            writer = csv.writer(output)
            writer.writerows(all_csv_rows)
            csv_data = output.getvalue()

            # 5. Excelでの文字化けを絶対に防ぐ 'utf-8-sig'
            st.download_button(
                label="📥 見積詳細をCSV保存", 
                data=csv_data.encode('utf-8-sig'), 
                file_name=f"CDP見積書_{client_name}_{datetime.datetime.now().strftime('%Y%m%d')}.csv", 
                mime="text/csv", 
                use_container_width=True
            )
    st.markdown('</div>', unsafe_allow_html=True)