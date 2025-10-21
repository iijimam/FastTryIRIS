# はじめてのAI開発 ～ゼロからのIRIS環境構築とOpenAI連携チャットボット作り～

＜10/21 追加した機能＞
- 3回目の質問の後、過去3回分の質問＆回答の要約を作成しています。（その間チャットボットは稼働中なのでユーザ入力できません）
- 会話履歴の消去ができます。この時生成AIへのプロンプトに使っていた情報を消えます。
- データベースへの会話履歴保存ができます。その時に記録している生成Aiへのプロンプトの全ての情報を1レコードで保存します。
- データベースから履歴をロードし、画面に表示します。通常userプロンプトのみを出力しますが、userプロンプトがない状況で過去の要約がある場合は過去の要約を表示します。



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

    - 通勤経路が変わりました。提出書類や手続き順序を教えてください。

    - パワハラを受けている人がいることを人事に伝えようと思いますが密告者を保護する規則はありますか？

    - ペットが亡くなり喪失感があるため有休をとりましたが、ペット死亡による特別休暇はありますか？

    - 住宅手当はありますか？ある場合は申請方法を教えてください。
    

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
    Source VARCHAR(100),
    DocLevel INTEGER,
    Title VARCHAR(100),
    Text VARCHAR(100000),
    NumOfToken INTEGER,
    TextVec VECTOR(Float,1536)
)
go

--- インデックス準備
CREATE INDEX HNSWIndex ON TABLE FS.Document (TextVec)
     AS HNSW(Distance='DotProduct')
go

```

### データ登録

- [mhlw_chapters_vector.jsonl](/data/mhlw_hr_rules_chunk_embeddings.jsonl)：Chunkを設定して分割したデータを利用します。Embeddingも含まれています。

    - INSERT時Embeddingはしません。以下メソッドを実行します。

        [FS.InstallUtils](/src/FS/InstallUtils.cls)クラスのloadvectorjsonl()メソッド

        例）コンテナ開始後は以下で実行できます。
        ```
        do ##class(FS.InstallUtils).loadvectorjsonl("/data/mhlw_hr_rules_chunk_embeddings.jsonl",1)
        ```

    このファイルは、DoclingでPDFを一旦[Markdown](/data/mhlw_full_caption_only.md)にしたあと、作成しています。

    [markdownToChunk.py](/markdownToChunk.py) で作成しています。