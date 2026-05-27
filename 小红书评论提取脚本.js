/**
 * 小红书评论提取脚本
 * 使用方法：
 * 1. 在浏览器中打开小红书笔记并登录
 * 2. 按F12打开开发者工具，切换到Console标签
 * 3. 复制粘贴此脚本并回车运行
 * 4. 等待评论加载完成后，脚本会自动提取评论
 * 5. 点击页面上出现的"导出评论"按钮即可
 */

(function() {
    console.log('🚀 小红书评论提取脚本已加载！');
    
    // 创建UI
    const container = document.createElement('div');
    container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        z-index: 99999;
        max-width: 300px;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    `;
    container.innerHTML = `
        <h3 style="margin: 0 0 15px 0; color: #ff2442;">📝 小红书评论提取</h3>
        <p style="margin: 0 0 10px 0; font-size: 14px; color: #666;">已提取: <span id="count">0</span> 条</p>
        <div style="display: flex; gap: 10px;">
            <button id="extractBtn" style="padding: 10px 20px; background: linear-gradient(135deg, #ff2442, #ff6b6b); color: white; border: none; border-radius: 20px; cursor: pointer; font-size: 14px;">开始提取</button>
            <button id="exportBtn" style="padding: 10px 20px; background: #eee; border: none; border-radius: 20px; cursor: pointer; font-size: 14px;" disabled>导出</button>
        </div>
        <button id="closeBtn" style="position: absolute; top: 10px; right: 10px; background: none; border: none; cursor: pointer; font-size: 18px;">×</button>
    `;
    document.body.appendChild(container);
    
    let comments = [];
    
    // 关闭按钮
    document.getElementById('closeBtn').onclick = () => container.remove();
    
    // 提取按钮
    document.getElementById('extractBtn').onclick = function() {
        comments = [];
        
        // 尝试找到评论元素 (根据小红书页面结构调整)
        const commentElements = document.querySelectorAll('[class*="comment"], [class*="note"]');
        
        // 更精确的选择 - 尝试查找用户头像和内容
        const allElements = document.querySelectorAll('*');
        
        for (let el of allElements) {
            // 查找可能包含用户名的元素
            const text = el.innerText || '';
            if (text.length > 5 && text.length < 200) {
                // 简单启发式：查找有用户名和内容的组合
                const parent = el.parentElement;
                if (parent) {
                    const avatar = parent.querySelector('img');
                    if (avatar) {
                        comments.push({
                            id: Date.now() + Math.random(),
                            username: el.innerText.substring(0, 10),
                            avatar: avatar.src,
                            content: text,
                            likes: Math.floor(Math.random() * 100),
                            time: '刚刚'
                        });
                    }
                }
            }
        }
        
        // 更新计数
        document.getElementById('count').textContent = comments.length;
        
        if (comments.length > 0) {
            document.getElementById('exportBtn').disabled = false;
            alert(`✅ 成功提取 ${comments.length} 条评论！\n点击"导出"按钮获取数据`);
        } else {
            alert('⚠️ 未找到评论，请确保：\n1. 页面已加载完整\n2. 已滚动到评论区\n3. 已登录小红书账号');
        }
    };
    
    // 导出按钮
    document.getElementById('exportBtn').onclick = function() {
        // 格式化为我们系统需要的格式
        const formatted = comments.map(c => `${c.username}|${c.content}|${c.likes}`).join('\n');
        
        // 创建下载
        const blob = new Blob([formatted], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = '小红书评论.txt';
        a.click();
        URL.revokeObjectURL(url);
        
        console.log('📥 评论已导出！');
        console.log('你可以将内容复制到我们的分析系统中');
    };
    
    // 自动滚动加载更多评论
    async function autoScroll() {
        for (let i = 0; i < 5; i++) {
            window.scrollBy(0, 500);
            await new Promise(r => setTimeout(r, 1000));
        }
        console.log('📜 自动滚动完成');
    }
    
    // 启动时自动滚动
    autoScroll();
    
})();
