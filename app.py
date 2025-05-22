import os
import uuid
import boto3
import psycopg2
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_user_id():
    return st.experimental_get_query_params().get("user", ["guest@example.com"])[0]

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def load_history(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT role, message FROM chat_logs WHERE user_id = %s ORDER BY created_at ASC", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [{"role": row[0], "text": row[1]} for row in rows]

def save_message(user_id, role, message):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO chat_logs (user_id, role, message) VALUES (%s, %s, %s)", (user_id, role, message))
    conn.commit()
    conn.close()

def ensure_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING;", (user_id,))
    conn.commit()
    conn.close()

def main():
    st.set_page_config(page_title="生成AIユースケース検討くん", layout="centered")
    st.title("生成AIユースケース検討くん")

    user_id = get_user_id()
    ensure_user(user_id)

    if "messages" not in st.session_state:
        st.session_state.messages = load_history(user_id)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["text"])

    if prompt := st.chat_input("例：弊社の営業メンバーの悩みを、生成AIで解決する良いアイディアはある？"):
        st.session_state.messages.append({"role": "user", "text": prompt})
        save_message(user_id, "user", prompt)

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            client = boto3.client("bedrock-agent-runtime")
            response = client.invoke_agent(
                agentId=os.getenv("BEDROCK_AGENT_ID"),
                agentAliasId=os.getenv("BEDROCK_AGENT_ALIAS_ID"),
                sessionId=str(uuid.uuid4()),
                inputText=prompt,
                enableTrace=True
            )
            answer = ""
            for event in response.get("completion", []):
                if "chunk" in event:
                    chunk_text = event["chunk"]["bytes"].decode()
                    st.write(chunk_text)
                    answer += chunk_text
            save_message(user_id, "assistant", answer)

if __name__ == "__main__":
    main()
