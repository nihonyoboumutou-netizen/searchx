from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os

app = Flask(__name__)

def scrape_top_articles(search_word):
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
        driver.get(f"https://www.google.com/search?q={encoded_query}")
        time.sleep(2)
        
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
                    count += 1
            except Exception:
                continue
    finally:
        driver.quit()
        
    return references

def generate_opinions_from_articles(search_word, references):
    posts = [
        f"{search_word}に関する最近の動向、すごく考えさせられるな…。個人的にはこれからの変化にしっかりついていかないといけないと感じる！ #{search_word.replace(' ', '')}",
        f"「{search_word}」についてのニュースを見かけたけど、みんなはどう思う？これ結構インパクト大きいよね。個人的にはプラスに捉えていきたいところ。",
        f"最近よく見かける{search_word}の話題。表面的なことだけじゃなくて、本質的なメリットを見極める目が大事だなと改めて痛感した。",
        f"{search_word}のトレンド、いよいよ本格化してきた気がする。乗り遅れないように自分なりの意見を持っておきたいよね。#トレンド",
        f"「{search_word}」についての議論が活発ですね。個人的には新しいアプローチとしてかなり期待できると思ってます！"
    ]
    return posts

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.json
    search_word = data.get('search_word')
    timestamp = data.get('timestamp')
    
    if not search_word:
        return jsonify({'status': 'error', 'message': '検索ワードがありません'}), 400
        
    references = scrape_top_articles(search_word)
    if not references:
        return jsonify({'status': 'error', 'message': '有効な検索結果を取得できませんでした'}), 500
        
    posts = generate_opinions_from_articles(search_word, references)
    
    return jsonify({
        'status': 'success',
        'timestamp': timestamp,
        'references': references,
        'posts': posts
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)