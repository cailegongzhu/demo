/* 输入输出示例 · 交互
   前端是独立页面，所以 fetch 要写后端 API 的完整地址（不能用相对路径 /）。 */

// 后端 API 地址：本地开发指向本机 8001 端口。
// 部署到服务器时，把这里改成服务器的地址，例如 https://api.example.com/echo
const API_URL = 'http://127.0.0.1:8001/';

const inputBox = document.getElementById('inputBox');
const outputBox = document.getElementById('outputBox');
const sendBtn = document.getElementById('sendBtn');
const status = document.getElementById('status');

sendBtn.addEventListener('click', async () => {
  const text = inputBox.value;

  if (!text.trim()) {
    status.textContent = '请输入内容再发送。';
    return;
  }

  sendBtn.disabled = true;
  status.textContent = '发送中…';

  try {
    // 跨域 POST：请求体就是输入框的原始文本
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
      body: text,
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    // 后端原样返回的内容，填入输出框
    outputBox.value = await response.text();
    status.textContent = '发送成功，后端已原样返回。';
  } catch (err) {
    status.textContent = '请求失败：' + err.message + '（请确认后端服务已启动）';
  } finally {
    sendBtn.disabled = false;
  }
});
