import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    print("Starting e2e browser test...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating to frontend...")
        await page.goto("http://localhost:5173/")
        
        # Click login
        print("Logging in...")
        await page.click("text=Login")
        await page.fill("input[type='email']", "test@test.com")
        await page.fill("input[type='password']", "password")
        await page.click("button[type='submit']")
        
        print("Waiting for dashboard...")
        await page.wait_for_selector("text=Welcome back")
        
        # Check health status
        print("Checking health status...")
        await page.wait_for_selector("text=API")
        
        # Create Project
        print("Creating project...")
        await page.click("text=+ New Project")
        await page.fill("input[placeholder='my-awesome-website']", "My Test Project")
        
        # Upload files
        print("Uploading files...")
        file_input = await page.wait_for_selector("input[type='file']")
        
        test_site_dir = r"d:\GitHub_desktop\WebChain\test-site"
        files_to_upload = [
            os.path.join(test_site_dir, "index.html"),
            os.path.join(test_site_dir, "style.css"),
            os.path.join(test_site_dir, "script.js"),
            os.path.join(test_site_dir, "assets", "logo.svg")
        ]
        await file_input.set_input_files(files_to_upload)
        
        await page.click("text=Create Project →")
        
        print("Deploying project...")
        await page.click("text=Deploy")
        
        # Wait for deployment to finish
        print("Waiting for deployment to finish...")
        await page.wait_for_selector("text=Redeploy", timeout=60000)
        
        print("Opening project details...")
        await page.click("text=Details")
        
        print("Verifying details...")
        await page.wait_for_selector("text=Website ID")
        await page.wait_for_selector("text=IPFS CID")
        
        print("Verifying CID...")
        await page.click("text=Use Current CID")
        await page.click("button:has-text('Verify CID')")
        await page.wait_for_selector("text=Verified! CID matches the blockchain record.", timeout=15000)
        
        print("Update website...")
        update_input = await page.wait_for_selector("input[type='file']")
        await update_input.set_input_files(files_to_upload[:1]) # Just upload index.html
        await page.click("button:has-text('Deploy Update')")
        
        await page.wait_for_selector("text=Update complete! ✓", timeout=60000)
        
        print("E2E Test Passed Successfully!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
