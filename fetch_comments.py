import requests
import json
import sys

# 从浏览器网络请求中找到的评论API
API_URL = "https://edith.xiaohongshu.com/api/sns/web/v2/comment/page"
NOTE_ID = "69a2de780000000028020abc"
XSEC_TOKEN = "CBrIDxCIif4wZA1xdKrhfkuaUNwK3ltqkGvjHUu2lvwzs%3D"

# 模拟浏览器的headers
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.xiaohongshu.com/",
    "Accept": "application/json, text/plain, */*",
}

params = {
    "note_id": NOTE_ID,
    "cursor": "",
    "top_comment_id": "",
    "image_formats": "jpg,webp,avif",
    "xsec_token": XSEC_TOKEN
}

try:
    print("正在获取评论数据...")
    response = requests.get(API_URL, headers=headers, params=params, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        
        # 保存原始响应
        with open("raw_comments.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("原始数据已保存到 raw_comments.json")
        
        # 解析评论
        comments = []
        if "data" in data and "comments" in data["data"]:
            for item in data["data"]["comments"]:
                comment_info = {
                    "id": item.get("id", ""),
                    "username": item.get("user", {}).get("nickname", "匿名用户"),
                    "avatar": item.get("user", {}).get("avatar", ""),
                    "content": item.get("content", ""),
                    "likes": item.get("like_count", 0),
                    "time": item.get("create_time", ""),
                }
                comments.append(comment_info)
        
        # 保存解析后的评论
        with open("comments.json", "w", encoding="utf-8") as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)
        
        print(f"成功获取 {len(comments)} 条评论！")
        print(f"已保存到 comments.json")
        
        # 打印一些示例评论
        print("\n=== 示例评论 ===")
        for i, c in enumerate(comments[:5]):
            print(f"{i+1}. {c['username']}: {c['content'][:50]}...")
            
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}")
        
except Exception as e:
    print(f"发生错误: {e}")
    import traceback
    traceback.print_exc()
