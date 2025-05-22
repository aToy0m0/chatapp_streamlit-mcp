
import json
import uuid
import boto3
import streamlit as st
from botocore.exceptions import ClientError
from botocore.eventstream import EventStreamError

agent_id = "XXXXXXXXXX"  # 監督者エージェントのIDで置き換えてね
agent_alias_id = "XXXXXXXXXX"  # 監督者エージェントのエイリアスIDで置き換えてね

def initialize_session():
    """セッションの初期設定を行う"""
    if "client" not in st.session_state:
        st.session_state.client = boto3.client("bedrock-agent-runtime")
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "last_prompt" not in st.session_state:
        st.session_state.last_prompt = None
    
    return st.session_state.client, st.session_state.session_id, st.session_state.messages

def display_chat_history(messages):
    """チャット履歴を表示する"""
    st.title("生成AIユースケース検討くん")
    st.text("社内データとWeb情報をもとに、生成AI活用のアドバイスをするよ！")
    
    for message in messages:
        with st.chat_message(message['role']):
            st.markdown(message['text'])

def invoke_bedrock_agent(client, session_id, prompt):
    """Bedrockエージェントを呼び出す"""
    return client.invoke_agent(
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        sessionId=session_id,
        enableTrace=True,
        inputText=prompt,
    )

def handle_agent_response(response, messages):
    """エージェントのレスポンスを処理する"""
    with st.chat_message("assistant"):
        for event in response.get("completion"):
            if "chunk" in event:
                answer = event["chunk"]["bytes"].decode()
                st.write(answer)
                messages.append({"role": "assistant", "text": answer})

def show_error_popup(exeption):
    """エラーポップアップを表示する"""
    if exeption == "dependencyFailedException":
        error_message = "【エラー】ナレッジベースのAurora Serverlessがスリープしていたようです。1分ほど待ってから、ブラウザをリロードして再度お試しください🙏"
    elif exeption == "throttlingException":
        error_message = "【エラー】Bedrockのモデル負荷が高いようです。1分ほど待ってから、ブラウザをリロードして再度お試しください🙏（改善しない場合は、モデルを変更するか[サービスクォータの引き上げ申請](https://aws.amazon.com/jp/blogs/news/generative-ai-amazon-bedrock-handling-quota-problems/)を実施ください）"
    st.error(error_message)

def main():
    """メインのアプリケーション処理"""
    client, session_id, messages = initialize_session()
    display_chat_history(messages)
    
    if prompt := st.chat_input("例：弊社の営業メンバーの悩みを、生成AIで解決する良いアイディアはある？"):
        messages.append({"role": "human", "text": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        try:
            response = invoke_bedrock_agent(client, session_id, prompt)
            handle_agent_response(response, messages)
        except (EventStreamError, ClientError) as e:
            if "dependencyFailedException" in str(e):
                show_error_popup("dependencyFailedException")
            elif "throttlingException" in str(e):
                show_error_popup("throttlingException")
            else:
                raise e

if __name__ == "__main__":
    main()
    