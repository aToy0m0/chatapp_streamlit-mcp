
# 生成AIチャットアプリ

## はじめに
このアプリは、生成AIを利用して、社内データとWeb情報をもとにアドバイスを提供するツールです。AWSのBedrockエージェントを利用しています。

## セットアップ手順
1. 必要なライブラリをインストールします。
    ```bash
    pip install streamlit boto3
    ```

2. `.env` ファイルにAWSの認証情報を設定します。
    ```bash
    AWS_REGION=us-west-2
    AWS_ACCESS_KEY_ID=your_access_key
    AWS_SECRET_ACCESS_KEY=your_secret_key
    BEDROCK_AGENT_ID=XXXXXXXXXX
    BEDROCK_AGENT_ALIAS_ID=XXXXXXXXXX
    ```

3. Dockerコンテナをビルドして実行します。
    ```bash
    docker-compose up --build
    ```

4. Webブラウザで`http://localhost:8501`にアクセスして、アプリを利用できます。
    