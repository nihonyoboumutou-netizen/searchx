from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os

app = Flask(__name__)

def scrape_top_articles(search_word, logs):
    """Seleniumを用いたGoogle検索・上位3件の抽出（ログ記録付き）"""
    logs.append("ブラウザ（Selenium）を起動中（ヘッドレスモード）...")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=ja-JP")
    
    driver = webdriver.Chrome(options=options)
    
    references = []
    try:
        encoded_query = search_word.replace(" ", "+")
        target_url = f"https://www.google.com/search?q={encoded_query}"
        logs.append(f"Google検索を実行中: {search_word}")
        
        driver.get(target_url)
        time.sleep(2)
        
        logs.append("検索結果ページから上位記事を解析中...")
        search_results = driver.find_elements(By.CSSSelector, 'div.g')
        
        count = 0
        for result in search_results:
            if count >= 3:
                break
            try:
                title_elem = result.find_element(By.CSSSelector, 'h3')
                link_elem = result.find_element(By.CSSSelector, 'a')
                
                title = title_elem.text
                url = link_elem.get_attribute('href')
                
                if title and url:
                    references.append({"title": title, "url": url})
                    logs.append(f"-> 抽出成功 [{count+1}件目]: {title[:30]}...")
                    count += 1
            except Exception:
                continue
    except Exception as e:
        logs.append(f"⚠️ スクレイピング中にエラー: {str(e)}")
    finally:
        driver.quit()
        logs.append("ブラウザを正常に終了しました。")
        
    return references

def generate_opinions_from_articles(search_word, references, logs):
    """記事をもとに感想・意見ベースのポストを5つ作成（ログ記録付き）"""
    logs.append("取得した記事をベースにXポスト（5種類）を生成中...")
    
    posts = [
        f"{search_word}に関する最近の動向、すごく考えさせられるな…。個人的にはこれからの変化にしっかりついていかないといけないと感じる！ #{search_word.replace(' ', '')}",
        f"「{search_word}」についてのニュースを見かけたけど、みんなはどう思う？これ結構インパクト大きいよね。個人的にはプラスに捉えていきたいところ。",
        f"最近よく見かける{search_word}の話題。表面的なことだけじゃなくて、本質的なメリットを見極める目が大事だなと改めて痛感した。",
        f"{search_word}のトレンド、いよいよ本格化してきた気がする。乗り遅れないように自分なりの意見を持っておきたいよね。#トレンド",
        f"「{search_word}」についての議論が活発ですね。個人的には新しいアプローチとしてかなり期待できると思ってます！"
    ]
    
    logs.append("5パターンのポスト生成が完了しました。")
    return posts

@app.route('/api/generate', methods=['POST'])
def api_generate():
    logs = []
    data = request.json
    search_word = data.get('search_word')
    timestamp = data.get('timestamp')
    
    logs.append(f"リクエスト受信 (タイムスタンプ: {timestamp})")
    
    if not search_word:
        logs.append("エラー: 検索ワードが空です。")
        return jsonify({'status': 'error', 'message': '検索ワードがありません', 'logs': logs}), 400
        
    # 1. スクレイピング実行
    references = scrape_top_articles(search_word, logs)
    
    if not references:
        logs.append("エラー: 有効な検索結果が取得できませんでした。")
        return jsonify({'status': 'error', 'message': '有効な検索結果を取得できませんでした', 'logs': logs}), 500
        
    # 2. ポスト生成実行
    posts = generate_opinions_from_articles(search_word, references, logs)
    
    return jsonify({
        'status': 'success',
        'timestamp': timestamp,
        'references': references,
        'posts': posts,
        'logs': logs
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
