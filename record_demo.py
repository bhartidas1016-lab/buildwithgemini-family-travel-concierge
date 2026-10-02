import asyncio
import os
import shutil
import time
from playwright.async_api import async_playwright

FRONTEND_URL = "https://family-travel-frontend-816616608855.us-east1.run.app"
ARTIFACT_DIR = "/config/.gemini/antigravity/brain/3c40a083-9eef-4077-bdbf-dedbb7ec8ac0"
OUTPUT_VIDEO_PATH = os.path.join(ARTIFACT_DIR, "demo_video.webm")
TEMP_VIDEO_DIR = "/tmp/playwright_video_temp"

async def record():
    if os.path.exists(TEMP_VIDEO_DIR):
        shutil.rmtree(TEMP_VIDEO_DIR)
    os.makedirs(TEMP_VIDEO_DIR, exist_ok=True)

    async with async_playwright() as p:
        print("Launching Google Chrome...")
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--window-size=1280,800"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=TEMP_VIDEO_DIR,
            record_video_size={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        print(f"Navigating to {FRONTEND_URL}...")
        await page.goto(FRONTEND_URL, wait_until="networkidle")
        await asyncio.sleep(2)

        # 1. Click Category Filter Chip to show interactivity
        print("Clicking Category Filter Chip '🍼 Toddler Friendly'...")
        toddler_chip = page.locator(".filter-chip[data-category='toddler']")
        if await toddler_chip.count() > 0:
            await toddler_chip.click()
            await asyncio.sleep(1.5)

        # 2. Prompt 1: Highlighting core features (database lookup + weather)
        prompt1 = "Find stroller-friendly family activities in San Diego and check the weather for outdoor fun"
        print(f"Submitting Prompt 1: {prompt1}")
        input_box = page.locator("#input")
        await input_box.focus()
        await page.keyboard.type(prompt1, delay=30)
        await asyncio.sleep(0.5)

        send_btn = page.locator(".send-btn")
        await send_btn.click()

        print("Waiting for response to Prompt 1...")
        # Wait until agent message bubble appears and is no longer '…'
        await asyncio.sleep(3)
        for _ in range(30):
            agent_msgs = await page.locator(".msg.agent .bubble").all()
            if agent_msgs:
                last_txt = await agent_msgs[-1].text_content()
                if last_txt and last_txt.strip() != "…":
                    break
            await asyncio.sleep(1)
        await asyncio.sleep(3)

        # 3. Prompt 2: Rich prompt with image tool call (souvenir postcard generation)
        prompt2 = "Generate a family souvenir postcard of our trip to the San Diego Zoo with giraffes and palm trees"
        print(f"Submitting Prompt 2: {prompt2}")
        await input_box.focus()
        await page.keyboard.type(prompt2, delay=30)
        await asyncio.sleep(0.5)
        await send_btn.click()

        print("Waiting for response to Prompt 2 (Image tool call)...")
        await asyncio.sleep(5)
        for _ in range(40):
            agent_msgs = await page.locator(".msg.agent .bubble").all()
            if len(agent_msgs) >= 2:
                last_txt = await agent_msgs[-1].text_content()
                images = await page.locator(".msg.agent img").all()
                if images or (last_txt and last_txt.strip() != "…"):
                    break
            await asyncio.sleep(1)
        
        # Additional pause to showcase final UI state
        await asyncio.sleep(4)

        print("Closing context to save video...")
        await context.close()
        await browser.close()

    # Move recorded video file to artifact directory
    video_files = [f for f in os.listdir(TEMP_VIDEO_DIR) if f.endswith(".webm")]
    if video_files:
        src = os.path.join(TEMP_VIDEO_DIR, video_files[0])
        shutil.copy(src, OUTPUT_VIDEO_PATH)
        print(f"Demo video saved successfully to: {OUTPUT_VIDEO_PATH}")
    else:
        print("Error: No video file was produced by Playwright.")

if __name__ == "__main__":
    asyncio.run(record())
