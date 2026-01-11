import streamlit as st
import tempfile
import os
from moviepy import VideoFileClip
from pathlib import Path

# ページ設定
st.set_page_config(
    page_title="動画ダイエットくん",
    page_icon="🎬",
    layout="centered"
)

# タイトル
st.title("🎬 動画ダイエットくん（映像→音声変換）")
st.markdown("---")

# ファイルアップロード
uploaded_file = st.file_uploader(
    "動画ファイルをアップロードしてください",
    type=["mp4", "mov", "mkv", "avi", "wmv", "flv", "webm"],
    help="MP4, MOV, MKVなどの動画ファイルに対応しています"
)

if uploaded_file is not None:
    # ファイル情報を表示
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    st.info(f"📁 アップロードされたファイル: **{uploaded_file.name}** ({file_size_mb:.2f} MB)")
    
    # 変換開始ボタン
    if st.button("🚀 変換開始", type="primary", use_container_width=True):
        with st.spinner("変換中... しばらくお待ちください"):
            try:
                # 一時ファイルに保存
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_video:
                    tmp_video.write(uploaded_file.getvalue())
                    tmp_video_path = tmp_video.name
                
                # 動画から音声を抽出
                video = VideoFileClip(tmp_video_path)
                
                # 一時音声ファイルのパス
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                    tmp_audio_path = tmp_audio.name
                
                # 音声をMP3形式で書き出し（ビットレート192k）
                video.audio.write_audiofile(
                    tmp_audio_path,
                    bitrate="192k"
                )
                
                # 動画ファイルを閉じる
                video.close()
                
                # 変換後のファイルサイズを取得
                audio_size_mb = os.path.getsize(tmp_audio_path) / (1024 * 1024)
                reduction_mb = file_size_mb - audio_size_mb
                reduction_percent = (reduction_mb / file_size_mb) * 100
                
                # 結果を表示
                st.success("✅ 変換が完了しました！")
                st.markdown("---")
                
                # サイズ比較を大きく表示
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("元の動画サイズ", f"{file_size_mb:.2f} MB")
                with col2:
                    st.metric("変換後の音声サイズ", f"{audio_size_mb:.2f} MB")
                with col3:
                    st.metric("削減量", f"{reduction_mb:.2f} MB", f"-{reduction_percent:.1f}%")
                
                # 削減量を大きく表示
                st.markdown(f"### 🎉 **{reduction_mb:.2f} MB 削減しました！**")
                st.markdown("---")
                
                # ダウンロードボタン
                with open(tmp_audio_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    audio_name = Path(uploaded_file.name).stem + ".mp3"
                    
                    st.download_button(
                        label="📥 MP3ファイルをダウンロード",
                        data=audio_bytes,
                        file_name=audio_name,
                        mime="audio/mpeg",
                        type="primary",
                        use_container_width=True
                    )
                
                # 一時ファイルを削除
                try:
                    os.unlink(tmp_video_path)
                    os.unlink(tmp_audio_path)
                except:
                    pass
                
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
                # エラー時も一時ファイルを削除
                try:
                    if 'tmp_video_path' in locals():
                        os.unlink(tmp_video_path)
                    if 'tmp_audio_path' in locals():
                        os.unlink(tmp_audio_path)
                except:
                    pass

# フッター
st.markdown("---")
st.caption("💡 ヒント: 動画ファイルから音声だけを抽出して、ファイルサイズを大幅に削減できます。")

