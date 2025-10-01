# 仮：はじめてのAI開発 ～ゼロからのIRIS環境構築とOpenAI連携チャットボット作り～

## 動かし方

1. [.env](.env)にOpenAI の APIキーを設定する

    環境変数に設定します。（二重引用符いりません）

2. コンテナビルド＆開始

    ```
    docker compose up -d
    docker exec -it fasttryiris bash
    ```

3. Stremalit開始

    ```
    /home/irisowner/.local/bin/streamlit run /src/app.py --server.port 8080
    ```

4. Webページ起動

    http://localhost:9090/