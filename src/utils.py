import requests
import json

def getEmbed(input):
    # APIキーの設定
    api_key = ""

    # リクエストURL
    url = "https://api.openai.com/v1/embeddings"
    # ヘッダー
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # リクエストボディ
    data = {
        "model": "text-embedding-3-small",  # または "text-embedding-3-large", "text-embedding-ada-002"
        "input": input, 
        "encoding_format": "float"
    }

    # HTTPリクエスト送信
    response = requests.post(url, headers=headers, json=data)
    embeddingstr=None
    # レスポンス確認
    if response.status_code == 200:
        result = response.json()
        embedding = result['data'][0]['embedding']
        #print(f"成功: ベクトル次元数 = {len(embedding)}")
        embeddingstr=str(embedding)[1:-1]
    else:
        print(f"エラー: {response.status_code}")
        print(response.text)
    
    return embeddingstr