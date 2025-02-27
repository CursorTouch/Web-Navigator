from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    args=[
        '--remote-debugging-port=9222',
        '--disable-gpu'
    ]
    ignore_default_args=['--enable-automation']
    context = p.chromium.launch_persistent_context(executable_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',headless=False,
    user_data_dir="C:\\Users\\jeoge\\AppData\\Local\\Google\\Chrome\\User Data", args=args,ignore_default_args=ignore_default_args
    )
    page = context.new_page()
    page.goto('http://www.google.com')
    page.wait_for_timeout(5000)
    context.close()