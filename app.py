from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import jieba
import re
from collections import Counter
import random

app = Flask(__name__)
CORS(app)

# 理肤泉B5面霜评论数据
comments = [
    {"id": 1, "username": "护肤达人", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=1", "content": "真的超级难用！用了一次脸上就开始泛红发痒，过敏了！", "likes": 2345, "time": "2小时前"},
    {"id": 2, "username": "美妆小白", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=2", "content": "我也是！用了脸颊刺痛，之前还以为是我皮肤的问题", "likes": 1567, "time": "3小时前"},
    {"id": 3, "username": "敏感肌救星", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=3", "content": "理肤泉不是号称敏感肌专用吗？怎么会这样？", "likes": 890, "time": "4小时前"},
    {"id": 4, "username": "成分党来报道", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=4", "content": "查了成分，里面有致痘成分，不适合油痘肌", "likes": 678, "time": "5小时前"},
    {"id": 5, "username": "踩雷专业户", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=5", "content": "我也踩雷了！用完脸上起小疹子，赶紧停了", "likes": 543, "time": "5小时前"},
    {"id": 6, "username": "混油肌分享", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=6", "content": "混油肌表示太油腻了，吸收不了，闷痘", "likes": 432, "time": "6小时前"},
    {"id": 7, "username": "干皮实测", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=7", "content": "干皮觉得还好，不过确实没什么效果", "likes": 321, "time": "6小时前"},
    {"id": 8, "username": "理性分析", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=8", "content": "可能是肤质问题吧，我用着还行", "likes": 234, "time": "7小时前"},
    {"id": 9, "username": "护肤新手", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=9", "content": "救命！刚买还没开封，现在不敢用了", "likes": 567, "time": "8小时前"},
    {"id": 10, "username": "用过的说说", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=10", "content": "我用特护霜没问题，就是这个B5面霜不行", "likes": 456, "time": "8小时前"},
    {"id": 11, "username": "求推荐替代", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=11", "content": "有没有类似但更温和的面霜推荐？", "likes": 789, "time": "9小时前"},
    {"id": 12, "username": "回购三次的人", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=12", "content": "我用了三瓶了，感觉很好啊，维稳效果不错", "likes": 345, "time": "10小时前"},
    {"id": 13, "username": "成分科普", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=13", "content": "B5本身没问题，可能是配方里的其他成分", "likes": 234, "time": "11小时前"},
    {"id": 14, "username": "皮肤科医生", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=14", "content": "建议先在耳后测试，每个人耐受不同", "likes": 567, "time": "12小时前"},
    {"id": 15, "username": "真心劝退", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=15", "content": "真心劝退，我用完烂脸了，养了半个月才好", "likes": 890, "time": "13小时前"},
    {"id": 16, "username": "冬天必备", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=16", "content": "冬天用挺滋润的啊，夏天可能有点油", "likes": 234, "time": "14小时前"},
    {"id": 17, "username": "油痘肌慎入", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=17", "content": "油痘肌真的别碰，闷了我一脸闭口", "likes": 456, "time": "15小时前"},
    {"id": 18, "username": "敏皮亲妈", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=18", "content": "我敏感肌用着挺好的，能缓解泛红", "likes": 345, "time": "16小时前"},
    {"id": 19, "username": "搓泥严重", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=19", "content": "搓泥太严重了，根本没法上妆", "likes": 567, "time": "17小时前"},
    {"id": 20, "username": "性价比分析", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=20", "content": "性价比不高，不如买其他牌子", "likes": 234, "time": "18小时前"}
]

def analyze_sentiment(text):
    """简单的情感分析"""
    positive_words = ['好', '棒', '赞', '喜欢', '推荐', '舒服', '满意', '好用', '水润', '安全', '划算', '温和', '滑', '好闻', '吸收', '不错', '滋润', '维稳', '缓解', '挺好', '没问题']
    negative_words = ['差', '不好', '不明显', '过敏', '纠结', '假货', '怕', '难用', '刺痛', '泛红', '发痒', '烂脸', '踩雷', '闷痘', '油腻', '搓泥', '闭口', '疹子', '没用', '慎入', '劝退']
    
    words = jieba.lcut(text)
    pos_count = sum(1 for word in words if word in positive_words)
    neg_count = sum(1 for word in words if word in negative_words)
    
    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    else:
        return 'neutral'

def summarize_comments(comment_list):
    """评论总结"""
    sentiments = [analyze_sentiment(c['content']) for c in comment_list]
    sentiment_counts = Counter(sentiments)
    
    # 改进的关键词提取
    all_text = ' '.join([c['content'] for c in comment_list])
    words = jieba.lcut(all_text)
    
    # 扩展停用词表，过滤无意义的词
    stop_words = [
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '很', '也', '这', '那', '你', '说', '要', '会', '看', '好', '吗', '吧', '呢',
        '这个', '真的', '可以', '就是', '还是', '觉得', '因为', '所以', '但是', '只是', '已经', '还是', '然后', '其实', '非常', '特别', '超级',
        '真的', '太', '最', '更', '比较', '有点', '稍微', '真', '挺', '太', '好', '什么', '怎么', '为什么', '这样', '那样', '这么', '那么',
        '啊', '呀', '哦', '啦', '吧', '呢', '嘛', '哈', '啦', '啊', '哦', '嗯', '唉', '哇', '呀', '哦', '嗯'
    ]
    
    # 保留有意义的词，过滤长度小于2和停用词
    keywords = []
    for w in words:
        if len(w) >= 2 and w not in stop_words:
            keywords.append(w)
    
    top_keywords = Counter(keywords).most_common(10)
    
    total = len(comment_list)
    positive = sentiment_counts.get('positive', 0)
    negative = sentiment_counts.get('negative', 0)
    neutral = sentiment_counts.get('neutral', 0)
    
    summary = {
        'total_comments': total,
        'positive': positive,
        'negative': negative,
        'neutral': neutral,
        'positive_rate': round(positive/total*100, 1) if total > 0 else 0,
        'top_keywords': top_keywords,
        'overall_sentiment': 'positive' if positive > negative else 'negative' if negative > positive else 'neutral'
    }
    
    return summary

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/comments', methods=['GET'])
def get_comments():
    """获取所有评论"""
    return jsonify({
        'success': True,
        'comments': comments,
        'summary': summarize_comments(comments)
    })

@app.route('/api/search', methods=['GET'])
def search_comments():
    """搜索评论"""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({'success': False, 'message': '请提供搜索关键词'})
    
    results = []
    for comment in comments:
        if query in comment['content'].lower():
            results.append(comment)
    
    if results:
        return jsonify({
            'success': True,
            'results': results,
            'summary': summarize_comments(results)
        })
    else:
        return jsonify({'success': False, 'message': '未找到相关评论'})

@app.route('/api/import', methods=['POST'])
def import_comments():
    """导入评论"""
    try:
        data = request.get_json()
        if not data or 'comments' not in data:
            return jsonify({'success': False, 'message': '无效的请求数据'})
        
        imported = data['comments']
        comments.extend(imported)
        
        return jsonify({
            'success': True,
            'message': f'成功导入 {len(imported)} 条评论',
            'imported_count': len(imported)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'导入失败：{str(e)}'})

@app.route('/api/comments/sentiment', methods=['GET'])
def get_comments_by_sentiment():
    """按情感筛选评论"""
    sentiment = request.args.get('type', '')
    valid_sentiments = ['positive', 'negative', 'neutral', 'all']
    
    if sentiment not in valid_sentiments:
        return jsonify({'success': False, 'message': '无效的情感类型'})
    
    filtered_comments = []
    if sentiment == 'all':
        filtered_comments = comments
    else:
        for comment in comments:
            if analyze_sentiment(comment['content']) == sentiment:
                filtered_comments.append(comment)
    
    return jsonify({
        'success': True,
        'comments': filtered_comments,
        'sentiment': sentiment,
        'summary': summarize_comments(filtered_comments)
    })

@app.route('/api/clear', methods=['POST'])
def clear_comments():
    """清空评论（保留示例数据）"""
    global comments
    # 恢复理肤泉评论数据
    comments = [
        {"id": 1, "username": "护肤达人", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=1", "content": "真的超级难用！用了一次脸上就开始泛红发痒，过敏了！", "likes": 2345, "time": "2小时前"},
        {"id": 2, "username": "美妆小白", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=2", "content": "我也是！用了脸颊刺痛，之前还以为是我皮肤的问题", "likes": 1567, "time": "3小时前"},
        {"id": 3, "username": "敏感肌救星", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=3", "content": "理肤泉不是号称敏感肌专用吗？怎么会这样？", "likes": 890, "time": "4小时前"},
        {"id": 4, "username": "成分党来报道", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=4", "content": "查了成分，里面有致痘成分，不适合油痘肌", "likes": 678, "time": "5小时前"},
        {"id": 5, "username": "踩雷专业户", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=5", "content": "我也踩雷了！用完脸上起小疹子，赶紧停了", "likes": 543, "time": "5小时前"},
        {"id": 6, "username": "混油肌分享", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=6", "content": "混油肌表示太油腻了，吸收不了，闷痘", "likes": 432, "time": "6小时前"},
        {"id": 7, "username": "干皮实测", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=7", "content": "干皮觉得还好，不过确实没什么效果", "likes": 321, "time": "6小时前"},
        {"id": 8, "username": "理性分析", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=8", "content": "可能是肤质问题吧，我用着还行", "likes": 234, "time": "7小时前"},
        {"id": 9, "username": "护肤新手", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=9", "content": "救命！刚买还没开封，现在不敢用了", "likes": 567, "time": "8小时前"},
        {"id": 10, "username": "用过的说说", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=10", "content": "我用特护霜没问题，就是这个B5面霜不行", "likes": 456, "time": "8小时前"},
        {"id": 11, "username": "求推荐替代", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=11", "content": "有没有类似但更温和的面霜推荐？", "likes": 789, "time": "9小时前"},
        {"id": 12, "username": "回购三次的人", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=12", "content": "我用了三瓶了，感觉很好啊，维稳效果不错", "likes": 345, "time": "10小时前"},
        {"id": 13, "username": "成分科普", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=13", "content": "B5本身没问题，可能是配方里的其他成分", "likes": 234, "time": "11小时前"},
        {"id": 14, "username": "皮肤科医生", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=14", "content": "建议先在耳后测试，每个人耐受不同", "likes": 567, "time": "12小时前"},
        {"id": 15, "username": "真心劝退", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=15", "content": "真心劝退，我用完烂脸了，养了半个月才好", "likes": 890, "time": "13小时前"},
        {"id": 16, "username": "冬天必备", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=16", "content": "冬天用挺滋润的啊，夏天可能有点油", "likes": 234, "time": "14小时前"},
        {"id": 17, "username": "油痘肌慎入", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=17", "content": "油痘肌真的别碰，闷了我一脸闭口", "likes": 456, "time": "15小时前"},
        {"id": 18, "username": "敏皮亲妈", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=18", "content": "我敏感肌用着挺好的，能缓解泛红", "likes": 345, "time": "16小时前"},
        {"id": 19, "username": "搓泥严重", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=19", "content": "搓泥太严重了，根本没法上妆", "likes": 567, "time": "17小时前"},
        {"id": 20, "username": "性价比分析", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=20", "content": "性价比不高，不如买其他牌子", "likes": 234, "time": "18小时前"}
    ]
    return jsonify({'success': True, 'message': '已清空并恢复示例数据'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
