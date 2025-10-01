# /home/irisowner/.local/bin/streamlit run app.py --server.port 8080
#
import streamlit as st
from openai import OpenAI
import tryiris

st.set_page_config(page_title="超簡単AIチャット")
st.title("超簡単AIチャット（Streamlit）")

client = OpenAI()  # 環境変数 OPENAI_API_KEY を利用

# 会話履歴（継続会話の肝）
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role":"system","content":"あなたは親切なアシスタントです。"}
    ]

# 画面に履歴を表示
for m in st.session_state.messages:
    if m["role"] in ("user","assistant"):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# 入力欄
if prompt := st.chat_input("メッセージを入力..."):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 応答生成（モデル名はお好みで）
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages
    )
    answer = resp.choices[0].message.content
    st.session_state.messages.append({"role":"assistant","content":answer})

    with st.chat_message("assistant"):
        st.markdown(answer)

# 履歴の保存/読込/データベース保存（JSONに書く）
import json, os
col1, col2,col3 = st.columns(3)
history="/opt/src/history.json"
with col1:
    if st.button("履歴を保存"):
        with open(history,"w",encoding="utf-8") as f:
            json.dump(st.session_state.messages,f,ensure_ascii=False,indent=2)
        st.success("/opt/src/history.json に保存しました")
with col2:
    if st.button("履歴を読込"):
        if os.path.exists(history):
            with open(history,"r",encoding="utf-8") as f:
                st.session_state.messages = json.load(f)
            st.rerun()
with col3:
    if st.button("データベースの保存"):
        if os.path.exists(history):
            with open(history,"r",encoding="utf-8") as f:
                tryiris.jsonToDB(json.load(f))
                #終わったら消す
                os.remove(history)
            st.rerun()
