import streamlit as st
import tempfile
import os
from moviepy import VideoFileClip
from pathlib import Path

# ページ設定
st.set_page_config(
    page_title="動画ダイエットくん（映像→音声変換）",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# カスタムCSS
st.markdown("""
<style>
    /* メインコンテナ */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #333;
    }
    
    /* ヘッダースタイル */
    .main-header {
        text-align: center;
        padding: 2.5rem 1rem;
        background: #ffffff;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    .main-header .subtitle {
        color: #7f8c8d;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    /* ステップインジケーター */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
        padding: 0 2rem;
        position: relative;
    }
    
    .step-item {
        text-align: center;
        z-index: 1;
        position: relative;
        flex: 1;
    }
    
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #ddd;
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .step-active .step-circle {
        background-color: #6c5ce7;
        box-shadow: 0 0 0 5px rgba(108, 92, 231, 0.2);
    }
    
    .step-completed .step-circle {
        background-color: #2ecc71;
    }
    
    .step-label {
        font-size: 0.9rem;
        color: #999;
        font-weight: 600;
    }
    
    .step-active .step-label {
        color: #6c5ce7;
    }
    
    .step-line {
        position: absolute;
        top: 20px;
        left: 0;
        right: 0;
        height: 2px;
        background-color: #ddd;
        z-index: 0;
        margin: 0 15%;
    }
    
    /* カードスタイル */
    .card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease;
    }
    
    .card:hover {
        transform: translateY(-2px);
    }
    
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* アップロードエリアのカスタマイズ */
    .stFileUploader {
        padding: 2rem;
        border: 2px dashed #a29bfe;
        border-radius: 15px;
        background-color: #f8f9fa;
        text-align: center;
        transition: all 0.3s;
    }
    
    .stFileUploader:hover {
        border-color: #6c5ce7;
        background-color: #f0f3ff;
    }

    /* ボタンスタイル */
    .stButton > button {
        background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.8rem 2.5rem !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(108, 92, 231, 0.3) !important;
        transition: all 0.3s !important;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(108, 92, 231, 0.4) !important;
    }
    
    /* メトリクス表示 */
    .metric-container {
        display: flex;
        justify-content: space-around;
        text-align: center;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .metric-item strong {
        display: block;
        font-size: 1.5rem;
        color: #2d3436;
    }
    
    .metric-item span {
        font-size: 0.9rem;
        color: #636e72;
    }
    
    /* 成功メッセージ */
    .stSuccess {
        background-color: #d4edda !important;
        color: #155724 !important;
        border-color: #c3e6cb !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    /* フッター */
    .footer {
        text-align: center;
        color: #b2bec3;
        margin-top: 3rem;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ヘッダーエリア
st.markdown("""
<div class="main-header">
    <div style="font-size: 3rem; margin-bottom: 0.5rem;">🎬</div>
    <h1>動画ダイエットくん</h1>
    <p class="subtitle">映像ファイルから音声を抽出して軽量化（MP4 → MP3）</p>
</div>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'step' not in st.session_state:
    st.session_state['step'] = 1

# ステップインジケーター表示関数
def render_steps(current_step):
    step1_class = "step-active" if current_step == 1 else ("step-completed" if current_step > 1 else "")
    step2_class = "step-active" if current_step == 2 else ("step-completed" if current_step > 2 else "")
    step3_class = "step-active" if current_step == 3 else ("step-completed" if current_step > 3 else "")
    
    st.markdown(f"""
    <div class="step-indicator">
        <div class="step-line"></div>
        <div class="step-item {step1_class}">
            <div class="step-circle">1</div>
            <div class="step-label">アップロード</div>
        </div>
        <div class="step-item {step2_class}">
            <div class="step-circle">2</div>
            <div class="step-label">変換実行</div>
        </div>
        <div class="step-item {step3_class}">
            <div class="step-circle">3</div>
            <div class="step-label">完了・DL</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# メイン処理
uploaded_file = st.file_uploader(
    "ここに動画ファイルをドラッグ＆ドロップしてください",
    type=["mp4", "mov", "mkv", "avi", "wmv", "flv", "webm", "mpeg4"],
    help="最大2GBまで対応しています",
    key="file_uploader"
)

# アップロード状態に応じたステップ判定
if uploaded_file is None:
    st.session_state['step'] = 1
    render_steps(1)
    
    # イントロダクションカード
    st.markdown("""
    <div class="card">
        <div class="section-title">✨ なぜ使うの？</div>
        <p style="color: #666; line-height: 1.6;">
            議事録の作成やメンバーとの共有がスムーズに！！
            会議の録画ファイルや講義動画など、映像が不要な場合に音声だけを抽出することで、
            ファイルサイズを劇的に（最大90%以上）削減できます。<br>
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    # ファイルがアップロードされている場合
    
    # 変換が完了していない場合はステップ2
    if 'converted_file' not in st.session_state or st.session_state.get('last_uploaded') != uploaded_file.name:
        st.session_state['step'] = 2
        st.session_state['converted_file'] = None
        st.session_state['last_uploaded'] = uploaded_file.name
    
    render_steps(st.session_state['step'])
    
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    file_size_display = f"{file_size_mb:.1f} MB" if file_size_mb < 1024 else f"{file_size_mb/1024:.2f} GB"

    # ファイル情報カード
    st.markdown(f"""
    <div class="card">
        <div class="section-title">📂 選択されたファイル</div>
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="background: #eee; padding: 0.8rem; border-radius: 10px; font-size: 1.5rem;">🎥</div>
                <div>
                    <div style="font-weight: bold; font-size: 1.1rem; color: #2d3436;">{uploaded_file.name}</div>
                    <div style="color: #636e72; font-size: 0.9rem;">{file_size_display}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 変換ボタンエリア (未完了の場合のみ表示)
    if st.session_state['step'] == 2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 音声を抽出して変換する", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("⏳ 準備中...")
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_video:
                        tmp_video.write(uploaded_file.getvalue())
                        tmp_video_path = tmp_video.name
                    
                    progress_bar.progress(30)
                    status_text.text("🎬 映像を解析中...")
                    
                    video = VideoFileClip(tmp_video_path)
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                        tmp_audio_path = tmp_audio.name
                    
                    progress_bar.progress(50)
                    status_text.text("🎵 音声データを抽出・変換中...")
                    
                    video.audio.write_audiofile(
                        tmp_audio_path,
                        bitrate="192k",
                        logger=None
                    )
                    
                    video.close()
                    
                    progress_bar.progress(100)
                    status_text.text("✅ 完了しました！")
                    
                    # 結果をsession_stateに保存
                    st.session_state['audio_path'] = tmp_audio_path
                    st.session_state['original_size'] = file_size_mb
                    st.session_state['audio_size'] = os.path.getsize(tmp_audio_path) / (1024 * 1024)
                    st.session_state['tmp_video_path'] = tmp_video_path
                    st.session_state['step'] = 3
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
                    # クリーンアップ
                    if 'tmp_video_path' in locals(): os.unlink(tmp_video_path)
                    if 'tmp_audio_path' in locals(): os.unlink(tmp_audio_path)

    # 完了画面 (ステップ3)
    if st.session_state['step'] == 3:
        audio_size_mb = st.session_state['audio_size']
        original_size_mb = st.session_state['original_size']
        reduction_mb = original_size_mb - audio_size_mb
        reduction_percent = (reduction_mb / original_size_mb) * 100
        
        st.markdown(f"""
        <div class="card" style="border-left: 5px solid #2ecc71;">
            <div class="section-title">🎉 変換完了！</div>
            <p>ファイルサイズが大幅に削減されました。</p>
            
            <div class="metric-container">
                <div class="metric-item">
                    <span>元のサイズ</span>
                    <strong>{original_size_mb:.1f} MB</strong>
                </div>
                <div style="font-size: 1.5rem; color: #b2bec3; padding-top: 0.5rem;">➡</div>
                <div class="metric-item">
                    <span>変換後</span>
                    <strong>{audio_size_mb:.1f} MB</strong>
                </div>
                <div class="metric-item">
                    <span style="color: #e17055;">削減率</span>
                    <strong style="color: #e17055;">-{reduction_percent:.1f}%</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ダウンロードボタン
        with open(st.session_state['audio_path'], "rb") as f:
            audio_bytes = f.read()
            st.download_button(
                label="📥 MP3ファイルをダウンロード",
                data=audio_bytes,
                file_name=Path(uploaded_file.name).stem + ".mp3",
                mime="audio/mpeg"
            )
        
        # リセットボタン
        if st.button("🔄 別のファイルを変換する"):
            # ファイル削除
            try:
                os.unlink(st.session_state['audio_path'])
                os.unlink(st.session_state['tmp_video_path'])
            except:
                pass
            # 状態リセット
            st.session_state['step'] = 1
            st.session_state['converted_file'] = None
            st.rerun()

# フッター
st.markdown("""
<div class="footer">
    Video Diet Tool © 2026<br>
    Simple, Fast, and Secure.
</div>
""", unsafe_allow_html=True)
