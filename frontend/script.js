/* ============================================
   Git 学习手册 · 交互脚本
   只负责"行为"，不含 HTML 结构，也不写死样式
   ============================================ */

// 命令数据：实际项目中这类数据通常来自接口，这里先用数组模拟
const commands = [
  { cat: 'init',  cmd: 'git init', desc: '在当前目录初始化一个空的 Git 仓库' },
  { cat: 'init',  cmd: 'git config --global user.name "你的名字"', desc: '设置全局用户名（提交时会用到）' },
  { cat: 'init',  cmd: 'git config --global user.email "you@example.com"', desc: '设置全局邮箱' },
  { cat: 'init',  cmd: 'git clone <仓库地址>', desc: '把远程仓库完整下载到本地' },
  { cat: 'daily', cmd: 'git status', desc: '查看工作区与暂存区的状态' },
  { cat: 'daily', cmd: 'git add <文件>', desc: '把指定文件加入暂存区' },
  { cat: 'daily', cmd: 'git add .', desc: '把当前目录所有改动加入暂存区' },
  { cat: 'daily', cmd: 'git commit -m "提交说明"', desc: '把暂存区内容提交为一个版本快照' },
  { cat: 'branch',cmd: 'git branch', desc: '列出所有本地分支' },
  { cat: 'branch',cmd: 'git checkout -b <分支名>', desc: '新建并切换到新分支' },
  { cat: 'branch',cmd: 'git switch <分支名>', desc: '切换到已有分支（新写法）' },
  { cat: 'branch',cmd: 'git merge <分支名>', desc: '把指定分支合并到当前分支' },
  { cat: 'branch',cmd: 'git branch -d <分支名>', desc: '删除已合并的本地分支' },
  { cat: 'remote',cmd: 'git remote -v', desc: '查看已配置的远程仓库地址' },
  { cat: 'remote',cmd: 'git remote add origin <地址>', desc: '关联一个远程仓库' },
  { cat: 'remote',cmd: 'git push origin <分支名>', desc: '把本地提交推送到远程仓库' },
  { cat: 'remote',cmd: 'git pull', desc: '拉取远程改动并合并到当前分支' },
  { cat: 'remote',cmd: 'git fetch', desc: '只下载远程改动，不自动合并' },
  { cat: 'undo',  cmd: 'git log --oneline', desc: '用单行简洁格式查看提交历史' },
  { cat: 'undo',  cmd: 'git diff', desc: '查看工作区相对暂存区的改动' },
  { cat: 'undo',  cmd: 'git restore --staged <文件>', desc: '把文件从暂存区移回工作区' },
  { cat: 'undo',  cmd: 'git restore <文件>', desc: '丢弃工作区对该文件的修改（谨慎）' },
  { cat: 'undo',  cmd: 'git reset --hard HEAD~1', desc: '回退最近一次提交（危险，会丢弃改动）' },
  { cat: 'undo',  cmd: 'git stash', desc: '临时保存当前改动，稍后用 stash pop 恢复' },
];

const list = document.getElementById('cmdList');

// 根据分类渲染命令列表
function render(cat) {
  list.innerHTML = '';
  commands.filter(c => cat === 'all' || c.cat === cat).forEach(c => {
    const el = document.createElement('div');
    el.className = 'cmd';
    el.innerHTML = '<code></code><div class="desc"></div><button class="copy">复制</button>';
    el.querySelector('code').textContent = c.cmd;
    el.querySelector('.desc').textContent = c.desc;

    const btn = el.querySelector('.copy');
    btn.addEventListener('click', () => {
      navigator.clipboard?.writeText(c.cmd).then(() => {
        btn.textContent = '已复制';
        btn.classList.add('done');
        setTimeout(() => {
          btn.textContent = '复制';
          btn.classList.remove('done');
        }, 1500);
      }).catch(() => { btn.textContent = '请手动复制'; });
    });

    list.appendChild(el);
  });
}

// 初始化：显示全部命令
render('all');

// 标签切换
document.getElementById('tabs').addEventListener('click', e => {
  const tab = e.target.closest('.tab');
  if (!tab) return;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  tab.classList.add('active');
  render(tab.dataset.cat);
});
