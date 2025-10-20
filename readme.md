# はじめてのAI開発 ～ゼロからのIRIS環境構築とOpenAI連携チャットボット作り～

## 動かし方

1. [.env](.env)にOpenAI の APIキーを設定する

    環境変数に設定します。（二重引用符いりません）
    
    ```
    OPENAI_API_KEY=s*-abc***
    ```

2. コンテナビルド＆開始

    ```
    docker compose up -d
    docker exec -it fasttryiris bash
    ```

3. Stremalit開始

    ```
    /home/irisowner/.local/bin/streamlit run /src/app.py --server.port 8080
    ```
    デバッグモード
    ```
    /home/irisowner/.local/bin/streamlit run /src/app.py --server.port 8080 --logger.level=debug
    ```


    【質問例】
    - 産休・育休を取得する場合の申請手順を教えてください。社内への報告の仕方も教えてください。

    - 介護休暇を取得する場合の申請手順を教えてください。一般的な社内の報告順も教えてください。

    - パワハラを受けている人がいることを人事に伝えようと思いますが密告者を保護する規則はありますか？

4. Webページ起動

    http://localhost:9090/

## ベクトル検索の元など

厚生省が出してる[モデル就業規則](https://www.mhlw.go.jp/content/001018385.pdf)を利用しています。

### Diclingを使ってマークダウン→ベクトル用のJsonl作成

[pdfmarkdown.py](/pdfmarkdown.py)を使ってマークダウン用ファイルとベクトル検索用に章立を１行にしたファイルを作成

※Windowsで試してます

### ベクトル化

ベクトルが入るテーブルの作成は、[sample.sql](/src/sample.sql)の4行目以降にあります。

%Embedding.Configを使ってEmbeddingをした際、＋や÷、×の文字が含まれているとエラーが出てしまうため、使用していません。

VECTOR型でカラムを設定しています。
```
--- ベクトル検索用テーブル
CREATE TABLE FS.Document (
    FileName VARCHAR(100),
    DocLevel INTEGER,
    Title VARCHAR(100),
    Text VARCHAR(100000),
    TextVec VECTOR(Float,1536)
)
go

--- インデックス準備
CREATE INDEX HNSWIndex ON TABLE FS.Document (TextVec)
     AS HNSW(Distance='DotProduct')
go

```

### データ登録

- [mhlw_chapters.jsonl](/data/mhlw_chapters.jsonl)章立てごとに１行にしたファイルを使う場合（ベクトルはINSERT時に実行）

    - INSERTしながらOpenAIのEmbeddingを呼ぶ出します。以下メソッドを実行します。

        [FS.InstallUtils](/src/FS/InstallUtils.cls)クラスのloadjsonl()メソッド

        ```
        do ##class(FS.InstallUtils).loadjsonl("/data/mhlw_chapters.jsonl")
        ```

- [mhlw_chapters_vector.jsonl](/data/mhlw_chapters_vector.jsonl)章立てごと１行にしたファイル＋テキストのベクトル化も含まれるファイル

    - INSERT時Embeddingはしません。以下メソッドを実行します。

        [FS.InstallUtils](/src/FS/InstallUtils.cls)クラスのloadvectorjsonl()メソッド

        例）
        ```
        USER>d ##class(FS.InstallUtils).loadvectorjsonl("/data/mhlw_chapters_vector.jsonl")
        処理時間：0.505584716796875
        ```

