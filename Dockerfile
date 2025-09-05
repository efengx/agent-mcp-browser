FROM accetto/ubuntu-vnc-xfce-chromium-g3

USER root
WORKDIR /root/app

# 声明
ARG NODE_MAJOR=20
# vnc 密码
ENV VNC_PW=firstx
# vnc 的屏幕进程号
ENV DISPLAY=:1
# 设置操作系统语言默认为中文
ENV LANG=zh_CN.UTF-8
ENV LANGUAGE=zh_CN:zh
ENV LC_ALL=zh_CN.UTF-8

# 构建环境
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list.d/ubuntu.sources  \
    && sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list.d/ubuntu.sources \
    && apt-get update && apt-get install -y curl git supervisor openssh-server ffmpeg lsof bc vim \
    python-is-python3 locales python3-pip \
    # 安装中文字体, 解决ubuntu字体缺失
    fonts-wqy-microhei fonts-wqy-zenhei fonts-arphic-uming fonts-arphic-ukai \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && sed -i -e 's/# zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen \
    && mkdir /var/run/sshd \
    && ssh-keygen -A \
    # <-- 新增：允许 root 用户通过 SSH 登录 (用于调试) -->
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    # <-- 新增：允许密码认证 -->
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    # <-- 新增：为 root 用户设置密码。请务必修改 "headless" 为一个复杂的密码！ -->
    && echo 'root:headless' | chpasswd \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    # 需要强制扫描并加载字体库
    && fc-cache -f -v \
    # 解决 playwright 下的浏览器弹框问题
    # && ln -sf /bin/true /usr/bin/xdg-open \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js using NodeSource PPA
RUN chmod +x /dockerstartup/startup.sh \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install nodejs -y \
    && rm -rf /var/lib/apt/lists/* 

COPY --chown=root:root . .
# 载入下面安装的uv工具和uv tool工具的使用
ENV PATH="/home/headless/.local/bin:${PATH}"

# Install mcp server
RUN mkdir -p /root/Downloads \
    && chmod +x ./script/start-chrome-playwright.sh \
    && npm init -y \
    && npm install @playwright/test @playwright/mcp@latest \
    && npx -y playwright install --with-deps --force chrome \
    # 安装browser-use工具, 进行浏览器代理控制(Agent费用过高, 改为手动控制)
    && uv venv --clear \
    && uv pip install playwright browser-use[cli] fastmcp pytest-playwright \
    # 安装runpod mcp工具
    && cd /root && git clone https://github.com/runpod/runpod-mcp.git \
    && mkdir /root/logs && cd /root/runpod-mcp && npm install && npm run build \
    && npm cache clean --force \
    && rm -rf /root/.cache/uv

CMD ["supervisord","-c","./supervisord.conf"]
