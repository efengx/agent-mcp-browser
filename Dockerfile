FROM accetto/ubuntu-vnc-xfce-chromium-g3:latest

USER root
WORKDIR /home/headless/app

COPY --chown=headless:headless . .
COPY ./dockerstartup/startup.sh /dockerstartup/startup.sh

# 声明
ARG NODE_MAJOR=20
ENV PLAYWRIGHT_BROWSERS_PATH=/home/headless/Downloads

# 构建系统环境
# sed -i 's/cn.archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list.d/ubuntu.sources \

RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list.d/ubuntu.sources \
    && apt-get update && apt-get install -y curl git supervisor \
    python-is-python3 \
    # 安装中文字体, 解决ubuntu字体缺失
    fonts-wqy-microhei fonts-wqy-zenhei fonts-arphic-uming fonts-arphic-ukai \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    # 需要强制扫描并加载字体库
    && fc-cache -f -v \
    # 解决 playwright 下的浏览器弹框问题
    && ln -sf /bin/true /usr/bin/xdg-open \
    && rm -rf /var/lib/apt/lists/*

# 载入下面安装的uv工具和uv tool工具的使用
ENV PATH="/home/headless/.local/bin:${PATH}"

# Install Node.js using NodeSource PPA
RUN  mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install nodejs -y \
    && rm -rf /var/lib/apt/lists/* \
    && npx -y playwright install --with-deps chrome \
    # 更新用户组信息
    && chown -R headless:headless /home/headless \
    && chmod +x /dockerstartup/startup.sh

USER headless
RUN uv tool install mcp-proxy \
    && mkdir -p ./my-browser-profile \
    && npm init -y && npm install @playwright/mcp@latest \
    && npm install @executeautomation/playwright-mcp-server
    # && npx -y playwright install chromium

# COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["supervisord","-c","./supervisord.conf"]
# CMD ["/dockerstartup/startup.sh"]
