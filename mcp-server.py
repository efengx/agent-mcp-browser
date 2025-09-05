from typing import Optional, List, Dict, Any
from fastmcp import FastMCP
from browser_use import Agent, BrowserProfile
from browser_use.browser import BrowserSession
from browser_use.llm.openai.chat import ChatOpenAI
from pydantic import BaseModel, Field, PydanticUserError
from browser_use.llm import ChatAnthropic, ChatAzureOpenAI, ChatGoogle, ChatGroq
from enum import Enum
import os
import random
import asyncio
import re
from playwright.async_api import async_playwright, expect
import pathlib
import json
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("browser use")

class Result(BaseModel):
    """
    表示浏览器任务执行结果的模型。
    """
    status: int
    final_output: Optional[str] = None
    error_message: Optional[str] = None

class LLMProvider(str, Enum):
    """支持的语言模型提供商枚举。"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    GEMINI = "gemini"
    GROQ = "groq"

def create_llm_client(
    provider: LLMProvider, 
    model_name: str, 
    model_kwargs: Optional[Dict[str, Any]] = None
) -> Any:
    """
    根据提供商、模型名称和特定参数创建并返回一个LLM客户端实例。

    Args:
        provider (LLMProvider): LLM提供商。
        model_name (str): 要使用的具体模型名称或部署名称。
        model_kwargs (Optional[Dict[str, Any]]): 包含特定于提供商的凭据和配置的字典。
                                                 例如 api_key, azure_endpoint 等。

    Returns:
        Any: 初始化后的LLM客户端实例。

    Raises:
        ValueError: 如果提供了不支持的提供商。
    """
    kwargs = model_kwargs or {}
    
    if provider == LLMProvider.OPENAI:
        return ChatOpenAI(model=model_name, **kwargs)
    elif provider == LLMProvider.ANTHROPIC:
        return ChatAnthropic(model=model_name, **kwargs)
    elif provider == LLMProvider.AZURE_OPENAI:
        return ChatAzureOpenAI(azure_deployment=model_name, **kwargs)
    elif provider == LLMProvider.GEMINI:
        # Gemini 需要 'google_api_key'
        return ChatGoogle(model=model_name, **kwargs)
    elif provider == LLMProvider.GROQ:
        return ChatGroq(model=model_name, **kwargs)
    else:
        raise ValueError(f"不支持的 LLM 提供商: {provider}")

def remove_key_recursively(obj: Any, key_to_remove: str) -> Any:
    """
    递归地从嵌套的字典和列表中移除指定的键。

    Args:
        obj (Any): 要处理的对象（字典、列表或其它类型）。
        key_to_remove (str): 要移除的键的名称。

    Returns:
        Any: 处理后不含指定键的对象。
    """
    if isinstance(obj, dict):
        # 如果是字典，创建一个新字典，并排除要移除的键
        return {
            k: remove_key_recursively(v, key_to_remove)
            for k, v in obj.items()
            if k != key_to_remove
        }
    elif isinstance(obj, list):
        # 如果是列表，对列表中的每个元素进行递归调用
        return [remove_key_recursively(item, key_to_remove) for item in obj]
    else:
        # 如果是其他类型（字符串、数字等），直接返回
        return obj

async def random_wait(min_seconds=1, max_seconds=2, verbose=True, wait_number=1):
    """
    异步地等待一个随机的时间（默认在1到3秒之间）。
    """
    if wait_number <= 0:
        if verbose:
            print("🤖 等待次数为 0，跳过等待。")
        return

    for i in range(wait_number):
        delay = random.uniform(min_seconds, max_seconds)
        if verbose:
            # 更新打印信息，显示当前等待的进度
            print(f"🤖 第 {i + 1}/{wait_number} 次随机等待，时长 {delay:.2f} 秒，模拟人类操作...")
        await asyncio.sleep(delay)

@mcp.tool
async def login_hailuoai(
    iphone: str = Field(
        description="手机号码"
    )
):  
    """登陆海螺, 并发送短信验证码"""


    return {

    }


@mcp.tool
async def enter_code(
    code: str = Field(
        description="验证码"
    )
):
    """输入验证码, 并登陆"""

    return {

    }


@mcp.tool
async def text_to_image(
    text: str = Field(
        description="图片prompt"
    ),
    ratio: str = Field(
        "16:9",
        description="图片的比例, 可用值为: 21:9, 16:9, 9:16, 4:3, 1:1, 3:4, 9:16"
    ),
    wait_number: int = Field(
        1, 
        description="单步动作等待的时长"
    ),
):
    """文生图"""
    async with async_playwright() as p:
        # Connect to the remote Chrome instance via its CDP endpoint
        browser = await p.chromium.connect_over_cdp("http://localhost:9222") # Replace with the remote host and port

        if not browser.contexts:
            raise RuntimeError("No browser contexts found.")
        
        # Access the default browser context
        context = browser.contexts[0] 

        if not context.pages:
            raise RuntimeError("No pages available in context.")
        
        # Access the first page within the default context
        page = context.pages[0] 
        
        # 进入页面
        await page.goto("https://hailuoai.com/create?type=image")
        await random_wait(wait_number=wait_number)

        # 将数量改为1张
        await page.get_by_role("spinbutton").fill("1")

        # 弹出-图片分辨率选择
        # await page.locator("div").filter(has_text=re.compile(r"^\d+:\d+$")).nth(2).click()
        await page.locator(".hover\\:border-hl_bg_00_85").click()
        await random_wait(wait_number=wait_number)

        # 选择指定的比例
        await page.get_by_role("tooltip").locator("div").filter(has_text=re.compile(rf"^{ratio}$")).click()
        await random_wait(wait_number=wait_number)

        # 加载文生图内容
        await page.locator("#video-create-textarea").fill(text)
        await random_wait(wait_number=wait_number)

        # 点击视频生成
        await page.get_by_role("button", name="AI Video create png by Hailuo").click()
        await random_wait(wait_number=wait_number)

        # 清除输入框中的内容
        await page.locator("#video-create-textarea").clear()
        await random_wait(wait_number=wait_number)

        # 点击右边的类型
        await page.get_by_text('类型:').click();
        await random_wait(wait_number=wait_number)
        
        # 选择显示类型
        await page.get_by_role("option", name="图片").click()
        await random_wait(wait_number=wait_number)

        # 验证图片是否在队列中
        is_visible = await page.get_by_text(text[:9]).first.is_visible();
        await random_wait(wait_number=wait_number)

        # 关闭浏览器
        await browser.close()
    return {
        "is_visible": is_visible
    }


@mcp.tool
async def image_to_video(
    text: str = Field(
        description="视频的运镜指令"
    ),
    image_path: str = Field(
        description="图片的上传路径"
    ),
    wait_number: int = Field(
        1, 
        description="单步动作等待的时长"
    ),
):
    """图生视频"""
    async with async_playwright() as p:
        # Connect to the remote Chrome instance via its CDP endpoint
        browser = await p.chromium.connect_over_cdp("http://localhost:9222") # Replace with the remote host and port

        if not browser.contexts:
            raise RuntimeError("No browser contexts found.")
        
        # Access the default browser context
        context = browser.contexts[0] 

        if not context.pages:
            raise RuntimeError("No pages available in context.")
        
        # Access the first page within the default context
        page = context.pages[0] 
        
        # 进入页面
        await page.goto("https://hailuoai.com/create?type=video")
        await expect(page.locator(".common-create-form-container").get_by_text("图生视频")).to_be_visible(timeout=5000)
        await random_wait(wait_number=wait_number)

        # 点击图生视频
        await page.locator(".common-create-form-container").get_by_text("图生视频").click()
        # await page.get_by_text("图生视频").click()
        await random_wait(wait_number=wait_number)

        # 加载视频
        async with page.expect_file_chooser() as fc_info:
            await page.get_by_text("拖拽/粘贴/点击上传新图片").click()
        file_chooser = await fc_info.value
        await file_chooser.set_files(image_path)
        
        # 打开弹出层
        await page.locator(".hover\\:border-hl_bg_00_75 > div > div > svg").first.click()
        await random_wait(wait_number=wait_number)

        # 选择1080p
        await page.get_by_role("tooltip").locator("div").filter(has_text=re.compile(r"^1080p$")).first.click()
        await random_wait(wait_number=wait_number)

        # 关闭弹出层
        await page.locator(".hover\\:border-hl_bg_00_75 > div > div > svg").first.click()
        await random_wait(wait_number=wait_number)

        # 输入运镜指令
        await page.locator("#video-create-textarea").fill(text)
        await random_wait(wait_number=wait_number)

        # 点击视频生成
        await page.get_by_role("button", name="AI Video create png by Hailuo").click()
        await random_wait(wait_number=wait_number)

        # 清除输入框中的内容
        await page.locator("#video-create-textarea").clear()
        await random_wait(wait_number=wait_number)

        # 点击右边的类型
        await page.get_by_text('类型:').click();
        await random_wait(wait_number=wait_number)
        
        # 选择显示类型
        await page.get_by_role("option", name="视频").click()
        await random_wait(wait_number=wait_number)

        # 验证图片是否在队列中
        is_visible = await page.get_by_text(text[:9]).first.is_visible();
        await random_wait(wait_number=wait_number)

        # 关闭浏览器
        await browser.close()
    return {
        "is_visible": is_visible
    }


@mcp.tool
async def text_to_video(
    text: str = Field(
        description="视频的运镜指令"
    ),
    val_text: str = Field(
        description="验证视频是否生成"
    ),
    wait_number: int = Field(
        1, 
        description="单步动作等待的时长"
    ),
):
    """文生视频"""
    async with async_playwright() as p:
        # Connect to the remote Chrome instance via its CDP endpoint
        browser = await p.chromium.connect_over_cdp("http://localhost:9222") # Replace with the remote host and port

        if not browser.contexts:
            raise RuntimeError("No browser contexts found.")
        
        # Access the default browser context
        context = browser.contexts[0] 

        if not context.pages:
            raise RuntimeError("No pages available in context.")
        
        # Access the first page within the default context
        page = context.pages[0] 
        
        # 进入页面
        await page.goto("https://hailuoai.com/create?type=video")
        await expect(page.get_by_text('文生视频')).to_be_visible(timeout=5000)
        await random_wait(wait_number=wait_number)

        # 点击文生视频
        await page.locator(".common-create-form-container").get_by_text('文生视频').click()
        await random_wait(wait_number=wait_number)

        # 打开弹出层
        await page.locator(".hover\\:border-hl_bg_00_75 > div > div > svg").first.click()
        await expect(page.locator("div").filter(has_text=re.compile(r"^1080p$")).first).to_be_visible()
        await random_wait(wait_number=wait_number)

        # 选择1080p
        await page.get_by_role("tooltip").locator("div").filter(has_text=re.compile(r"^1080p$")).first.click()
        await random_wait(wait_number=wait_number)

        # 关闭弹出层
        await page.locator(".hover\\:border-hl_bg_00_75 > div > div > svg").first.click()
        await random_wait(wait_number=wait_number)

        # 加载文生图内容
        await page.locator("#video-create-textarea").fill(text)
        await random_wait(wait_number=wait_number)

        # 点击视频生成
        await page.get_by_role("button", name="AI Video create png by Hailuo").click()
        await random_wait(wait_number=wait_number)

        # 获取页面元素内容
        is_visible = await page.get_by_text(val_text).first.is_visible();
        await random_wait(wait_number=wait_number)

        # 关闭浏览器
        await browser.close()
    return {
        "is_visible": is_visible
    }


@mcp.tool
async def heygen_image_to_video(
    text: str = Field(
        description="视频的运镜指令"
    ),
    image_path: str = Field(
        description="图片的上传路径"
    ),
    audio_path: str = Field(
        description="音频的上传路径"
    ),
    wait_number: int = Field(
        1, 
        description="单步动作等待的时长"
    ),
):
    """heygen图生视频"""
    async with async_playwright() as p:
        # Connect to the remote Chrome instance via its CDP endpoint
        browser = await p.chromium.connect_over_cdp("http://localhost:9222") # Replace with the remote host and port

        if not browser.contexts:
            raise RuntimeError("No browser contexts found.")
        
        # Access the default browser context
        context = browser.contexts[0] 

        if not context.pages:
            raise RuntimeError("No pages available in context.")
        
        # Access the first page within the default context
        page = context.pages[0] 
        
        # 进入页面
        await page.goto("https://app.heygen.com/home")
        await random_wait(wait_number=wait_number)

        # 点击图生视频
        await page.locator("div").filter(has_text=re.compile(r"^Photo to Video with Avatar IVTurn photo and script into talking video$")).first.click()
        await random_wait(wait_number=wait_number)

        # 上传图片
        async with page.expect_file_chooser() as image_info:
            await page.locator(".tw-flex.tw-flex-1.tw-flex-col.tw-items-center").click()
        image_file_chooser = await image_info.value
        await image_file_chooser.set_files(image_path)
        await random_wait(wait_number=wait_number)

        # 设置为竖屏模式
        # await page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(2).click()
        # await page.get_by_role("button", name="Portrait Portrait").click()
        try:
            # await page.locator(".tw-inline-flex.tw-items-center.tw-gap-1.tw-bg-fill-block").first.locator("button").nth(1).click()
            await page.locator('button:has(iconpark-icon[name="portrait-phone"])').click()
            await random_wait(wait_number=wait_number)
        except TimeoutError:
            print("未找到指定的按钮或操作超时，跳过此步骤。")
        
        # 上传音频
        await page.get_by_text("upload or record audio").click()
        async with page.expect_file_chooser() as audio_info:
            await page.get_by_text("Upload a file or drag and drop hereAudio: MP3, WAV up to 100MB").click()
        audio_file_chooser = await audio_info.value
        await audio_file_chooser.set_files(audio_path)
        await page.get_by_role("button", name="Add audio").click()
        await random_wait(wait_number=wait_number)

        # 输入运镜指令
        await page.get_by_role("textbox", name="Describe the gestures and").click()
        await page.get_by_role("textbox", name="Describe the gestures and").fill(text)
        await random_wait(wait_number=wait_number)

        # 选择视频配置
        await page.get_by_role("button", name="Faster").click()
        await random_wait(wait_number=wait_number)

        await page.get_by_role("combobox").click()
        await random_wait(wait_number=wait_number)

        await page.get_by_text("720p", exact=True).click()
        await random_wait(wait_number=wait_number)

        # 点击视频生成
        await page.locator("div").filter(has_text=re.compile(r"^Generate video$")).click()
        await random_wait(wait_number=wait_number)

        # 切换视频列表
        await page.locator('button:has(iconpark-icon[name="list-view"])').click()
        await random_wait(wait_number=wait_number)

        await page.locator(".tw-flex.tw-cursor-pointer.tw-items-center.tw-gap-4.tw-truncate").first.click()
        await random_wait(wait_number=wait_number)

        # 获取当前页面的url连接
        await page.wait_for_url("https://app.heygen.com/videos/**")
        current_url = page.url

        # 打开视频页面
        # await page.locator(".tw-min-w-0.tw-cursor-pointer").first.click()
        # await page.locator(".tw-absolute.tw-inset-0.tw-z-10").first.click()
        # await random_wait(wait_number=wait_number)

        # await page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(1).click()
        # await page.get_by_role("menuitem", name="Get Video ID").click()
        # video_id = await page.evaluate("navigator.clipboard.readText()")

        # 关闭浏览器
        await browser.close()
    return {
        "current_url": current_url
    }


@mcp.tool
async def heygen_download_video(
    download_url: str = Field(
        description="视频下载链接"
    ),
    save_path: str = Field(
        "/root/file/uuid.mp4", 
        description="下载文件保存路径"
    ),
    wait_number: int = Field(
        1, 
        description="单步动作等待的时长"
    ),
):
    """heygen下载视频"""
    async with async_playwright() as p:
        # Connect to the remote Chrome instance via its CDP endpoint
        browser = await p.chromium.connect_over_cdp("http://localhost:9222") # Replace with the remote host and port

        if not browser.contexts:
            raise RuntimeError("No browser contexts found.")
        
        # Access the default browser context
        context = browser.contexts[0] 

        if not context.pages:
            raise RuntimeError("No pages available in context.")
        
        # Access the first page within the default context
        page = context.pages[0] 
        
        # 进入页面
        await page.goto(download_url)
        await random_wait(wait_number=wait_number)

        # 打开下载链接
        await page.get_by_role("button", name="Download").click()
        await random_wait(wait_number=wait_number)
        
        # 下载视频
        async with page.expect_download() as download_info:
            await page.get_by_role("dialog").get_by_role("button", name="Download").click()
        download = await download_info.value

        # 保存下载的文件
        save_directory = os.path.dirname(save_path)
        if save_directory:
            os.makedirs(save_directory, exist_ok=True)
        await download.save_as(save_path)
        await random_wait(wait_number=wait_number)

        # 关闭浏览器
        await browser.close()
    return {
        "filePath": save_path
    }


@mcp.tool
async def download_video(
    text: str = Field(
        description="视频下载的唯一定位描述"
    ),
    type_of_work: str = Field(
        "video",
        description="下载时的作品类型. 值为: 视频, 图片"
    ),
    download_path: str = Field(
        "/root/file", 
        description="下载文件保存路径"
    ),
    wait_number: int = Field(
        1, 
        description="单步动作等待的时长"
    ),
):
    """下载视频"""
    async with async_playwright() as p:
        # Connect to the remote Chrome instance via its CDP endpoint
        browser = await p.chromium.connect_over_cdp("http://localhost:9222") # Replace with the remote host and port

        if not browser.contexts:
            raise RuntimeError("No browser contexts found.")
        
        # Access the default browser context
        context = browser.contexts[0] 

        if not context.pages:
            raise RuntimeError("No pages available in context.")
        
        # Access the first page within the default context
        page = context.pages[0] 
        
        # 进入页面
        await page.goto("https://hailuoai.com/create?type=video")
        await expect(page.get_by_text('文生视频')).to_be_visible(timeout=5000)
        await random_wait(wait_number=wait_number)

        # 点击右边的类型
        await page.get_by_text('类型:').click();
        await random_wait(wait_number=wait_number)
        
        # 选择显示类型
        await page.get_by_role("option", name=type_of_work).click()
        await random_wait(wait_number=wait_number)

        # 定位到指定视频的弹出层
        await page.locator("#preview-video-scroll-container div").filter(has_text=text).nth(2).click()
        await random_wait(wait_number=wait_number)

        # 将鼠标移动到指定位置, 并单击
        if type_of_work == "图片":
            await page.get_by_role("main").filter(has_text=f"创意描述复制{text}").get_by_role("button").nth(1).click()
        elif type_of_work == "视频":
            await page.locator(".mt-auto > .pointer-events-auto > button").first.click()
        await random_wait(wait_number=wait_number)

        # 验证无水印按钮是否存在
        element_to_check = page.get_by_role("menuitem", name="无水印").locator("div")
        await expect(element_to_check).to_be_visible()
        await random_wait(wait_number=wait_number)

        # 下载视频
        async with page.expect_download() as download_info:
            await element_to_check.click()
        download = await download_info.value
        
        # 将下载文件保存到指定路径
        suggested_filename = download.suggested_filename
        save_file_path = os.path.join(download_path, suggested_filename)
        await download.save_as(save_file_path)
        await random_wait(wait_number=wait_number)

        await browser.close()
    return {
        "filePath": download.suggested_filename
    }


@mcp.tool
async def download_tiktok_video(
    video_url: str = Field(
        description="视频下载的唯一定位描述"
    ),
    download_path: str = Field(
        "/root/file", 
        description="下载文件保存路径"
    ),
    save_as_filename: str = Field(
        None, 
        description="为下载的视频指定新的文件名(无需包含扩展名)。如果留空,将使用服务器建议的默认名称。"
    ),
    wait_number: int = Field(
        1, 
        description="单步动作等待的时长"
    ),
):
    """下载tiktok视频"""
    async with async_playwright() as p:
        # Connect to the remote Chrome instance via its CDP endpoint
        browser = await p.chromium.connect_over_cdp("http://localhost:9222") # Replace with the remote host and port

        if not browser.contexts:
            raise RuntimeError("No browser contexts found.")
        
        # Access the default browser context
        context = browser.contexts[0] 

        if not context.pages:
            raise RuntimeError("No pages available in context.")
        
        # Access the first page within the default context
        page = context.pages[0] 
        
        # 进入页面
        await page.goto(video_url)
        await random_wait(wait_number=wait_number)

        # 点击视频暂停播放
        await page.locator("video").click()

        # 点击右键
        await page.locator("video").click(button="right")
        await random_wait(wait_number=wait_number)

        # 下载视频
        async with page.expect_download() as download_info:
            # await page.get_by_text("下载视频").click()
            await page.locator("div").filter(has_text=re.compile(r"^Download video$")).click()
        download = await download_info.value
        
        # 将下载文件保存到指定路径
        suggested_filename = download.suggested_filename

        if save_as_filename:
            extension = pathlib.Path(suggested_filename).suffix
            final_filename = f"{save_as_filename}{extension}"
        else:
            final_filename = suggested_filename

        save_file_path = os.path.join(download_path, final_filename)
        await download.save_as(save_file_path)
        await random_wait(wait_number=wait_number)

        await context.close()
        await browser.close()
    return {
        "filePath": final_filename
    }


@mcp.tool
async def run_task(
    task_id: str = Field(
        description="任务Id"
    ),
    task: str = Field(
        description="文生图的prompt"
    ),
    session_id: str = Field(
        description="会话的ID"
    ),
    model_provider: LLMProvider = Field(
        default=LLMProvider.OPENAI, 
        description="选择要使用的语言模型提供商。"
    ),
    model_name: str = Field(
        default='gpt-4.1-mini', 
        description="指定要使用的模型名称、ID或部署名称。"
    ),
    model_kwargs: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="一个包含模型特定凭据和配置的字典。请根据下面的示例为不同提供商提供所需参数。"
    ),
    max_steps: int = Field(
        default=20, 
        description="Agent最大循环次数, 避免死循环导致的token超量问题"
    )
) -> Result:
    """
    使用可配置的 AI 代理在浏览器中执行一个高层次任务。(需要调试Agent以解决Token消耗过大的问题)

    通过 `model_provider`, `model_name`, 和 `model_kwargs` 来动态切换和配置语言模型。

    --- 调用示例 ---

    1. OpenAI (默认):
       - `model_name`: "gpt-4o", "gpt-4.1-mini", etc.
       - `model_kwargs`: {"api_key": "sk-..."} (如果未设置环境变量)
       {
         "task": "在谷歌上搜索'最好的python框架'",
         "model_provider": "openai",
         "model_name": "gpt-4o"
       }

    2. Anthropic:
       - `model_name`: "claude-3-opus-20240229", "claude-3-sonnet-20240229", etc.
       - `model_kwargs`: {"api_key": "sk-ant-..."} (如果未设置环境变量)
       {
         "task": "在Hacker News上找到关于AI的头条新闻",
         "model_provider": "anthropic",
         "model_name": "claude-3-sonnet-20240229",
         "model_kwargs": {"api_key": "YOUR_ANTHROPIC_KEY"}
       }

    3. Google Gemini:
       - `model_name`: "gemini-1.5-pro-latest", "gemini-pro", etc.
       - `model_kwargs`: {"google_api_key": "AIza..."} (如果未设置环境变量)
       {
         "task": "查找'gemini-1.5-pro'的技术报告摘要",
         "model_provider": "gemini",
         "model_name": "gemini-1.5-pro-latest",
         "model_kwargs": {"google_api_key": "YOUR_GEMINI_KEY"}
       }

    4. Groq:
       - `model_name`: "llama3-8b-8192", "mixtral-8x7b-32768", etc.
       - `model_kwargs`: {"api_key": "gsk_..."} (如果未设置环境变量)
       {
         "task": "在reddit上找到关于Llama3的讨论",
         "model_provider": "groq",
         "model_name": "llama3-8b-8192",
         "model_kwargs": {"api_key": "YOUR_GROQ_KEY"}
       }

    5. Azure OpenAI:
       - `model_name`: 你的Azure部署名称 (e.g., "my-gpt4-deployment")
       - `model_kwargs` (必需): {
           "api_key": "YOUR_AZURE_KEY",
           "azure_endpoint": "https://<your-resource-name>.openai.azure.com/",
           "api_version": "2024-02-01"
         }
       {
         "task": "使用Azure OpenAI完成任务",
         "model_provider": "azure_openai",
         "model_name": "my-gpt4-deployment",
         "model_kwargs": {
           "api_key": "...",
           "azure_endpoint": "...",
           "api_version": "2024-02-01"
         }
       }

    6. AWS Bedrock:
       - 认证: 通常通过环境变量 (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME) 处理。
       - `model_name`: Bedrock模型ID (e.g., "anthropic.claude-3-sonnet-20240229-v1:0")
       - `model_kwargs`: (可选) {"region_name": "us-east-1"} (如果未在环境中设置)
       {
         "task": "使用Bedrock Claude Sonnet完成任务",
         "model_provider": "aws_bedrock",
         "model_name": "anthropic.claude-3-sonnet-20240229-v1:0"
       }

    """
    
    llm = create_llm_client(
        provider=model_provider,
        model_name=model_name,
        model_kwargs=model_kwargs
    )

    async with async_playwright() as p:
        try:
            base_profile = BrowserProfile(
                keep_alive=True,
                highlight_elements=True,
                include_dynamic_attributes=True,
                # wait_for_network_idle_page_load_time=0.2,
                # maximum_wait_page_load_time=2.0,
                # wait_between_actions=0.3
            )
            
            browser_session = BrowserSession(
                cdp_url='http://localhost:9222',
                id=f"session-{session_id}"
            )

            # await browser_session.start()

            # all_pages = browser_session.tabs
            # target_page = all_pages[0]

            # if not target_page:
            #     print("⚠️ 浏览器中没有现有页面，创建了一个新页面。")
            #     target_page = await browser_session.browser_context.new_page()
            #     if browser_session.browser_profile.viewport:
            #         await target_page.set_viewport_size(browser_session.browser_profile.viewport)

            # if target_page != browser_session.agent_current_page:
            #     target_page_index = browser_session.tabs.index(target_page)
            #     await browser_session.switch_tab(target_page_index)
            #     print(f"✅ Agent 切换到 tab 索引 {target_page_index}, URL: {browser_session.agent_current_page.url}")
            # else:
            #     await browser_session.agent_current_page.bring_to_front()
            #     print(f"✅ Agent 已经在目标页面, URL: {browser_session.agent_current_page.url}")

            agent = Agent(
                task_id=task_id,
                task=task, 
                llm=llm,
                # page=page,
                # browser_context=context,
                # browser=browser,
                browser_profile=base_profile,
                browser_session=browser_session,
                use_vision=True,
                max_actions_per_step=3,
                retry_delay=4,
                save_conversation_path="/root/output/history"
            )

            history = await agent.run(max_steps=max_steps)
            final_agent_result = history.final_result()

            final_output_json = json.dumps(final_agent_result, ensure_ascii=False, indent=2) if final_agent_result is not None else None
            
            return Result(
                status=1,
                final_output=final_output_json,
            )
        except Exception as e:
            return Result(
                status=0,
                error_message=f"Error during browser task execution: {e}",
            )


if __name__ == "__main__":
    mcp.run()
