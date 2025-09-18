from src.agent.web.tools.views import Click,Type,Wait,Scroll,GoTo,Back,Key,Download,Scrape,Tab,Upload,Menu,Done,Forward,HumanInput,Script
from src.agent.web.context import Context
from markdownify import markdownify
from typing import Literal,Optional
from termcolor import colored
from src.tool import Tool
from asyncio import sleep
from pathlib import Path
from os import getcwd
import httpx

@Tool('Done Tool',params=Done)
async def done_tool(content:str,context:Context=None):
    '''Indicates that the current task has been completed successfully. Use this to signal completion and provide a summary of what was accomplished.'''
    return content

@Tool('Click Tool',params=Click)
async def click_tool(index:int,context:Context=None):
    '''Clicks on interactive elements like buttons, links, checkboxes, radio buttons, tabs, or any clickable UI component. Automatically scrolls the element into view if needed and handles hidden elements.'''
    page=await context.get_current_page()
    await page.wait_for_load_state('load')
    element=await context.get_element_by_index(index=index)
    handle=await context.get_handle_by_xpath(element.xpath)
    is_hidden=await handle.is_hidden()
    if not is_hidden:
        await handle.scroll_into_view_if_needed()
    await handle.click(force=True)
    return f'Clicked on the element at label {index}'

@Tool('Type Tool',params=Type)
async def type_tool(index:int,text:str,clear:Literal['True','False']='False',press_enter:Literal['True','False']='False',context:Context=None):
    '''Types text into input fields, text areas, search boxes, or any editable element. Can optionally clear existing content before typing. Includes natural typing delay for better compatibility.'''
    page=await context.get_current_page()
    element=await context.get_element_by_index(index=index)
    handle=await context.get_handle_by_xpath(element.xpath)
    await page.wait_for_load_state('load')
    is_hidden=await handle.is_hidden()
    if not is_hidden:
        await handle.scroll_into_view_if_needed()
    await handle.click(force=True)
    if clear=='True':
        await page.keyboard.press('Control+A')
        await page.keyboard.press('Backspace')
    await page.keyboard.type(text,delay=80)
    if press_enter=='True':
        await page.keyboard.press('Enter')
    return f'Typed {text} in element at label {index}'

@Tool('Wait Tool',params=Wait)
async def wait_tool(time:int,context:Context=None):
    '''Pauses execution for a specified number of seconds. Use this to wait for page loading, animations to complete, or content to appear after an action.'''
    await sleep(time)
    return f'Waited for {time}s'

@Tool('Scroll Tool',params=Scroll)
async def scroll_tool(direction:Literal['up','down']='up',index:int=None,amount:int=500,context:Context=None):
    '''Scrolls either the webpage or a specific scrollable container. Can scroll by page increments or by specific pixel amounts. If index is provided, scrolls the specific element container; otherwise scrolls the page. Automatically detects scrollable containers and prevents unnecessary scroll attempts.'''
    page=await context.get_current_page()
    if index is not None:
        element=await context.get_element_by_index(index=index)
        handle=await context.get_handle_by_xpath(xpath=element.xpath)
        if direction=='up':
            await page.evaluate(f'(element)=> element.scrollBy(0,{-amount})', handle)
        elif direction=='down':
            await page.evaluate(f'(element)=> element.scrollBy(0,{amount})', handle)
        else:
            raise ValueError('Invalid direction')
        return f'Scrolled {direction} inside the element at label {index} by {amount}'
    else:
        scroll_y_before = await context.execute_script(page,"() => window.scrollY")
        max_scroll_y = await context.execute_script(page,"() => document.documentElement.scrollHeight - window.innerHeight")
        min_scroll_y = await context.execute_script(page,"() => document.documentElement.scrollHeight")
        # Check if scrolling is possible
        if scroll_y_before >= max_scroll_y and direction == 'down':
            return "Already at the bottom, cannot scroll further."
        elif scroll_y_before == min_scroll_y and direction == 'up':
            return "Already at the top, cannot scroll further."
        if direction=='up':
            if amount is None:
                await page.keyboard.press('PageUp')
            else:
                await page.mouse.wheel(0,-amount)
        elif direction=='down':
            if amount is None:
                await page.keyboard.press('PageDown')
            else:
                await page.mouse.wheel(0,amount)
        else:
            raise ValueError('Invalid direction')
        # Get scroll position after scrolling
        scroll_y_after = await context.execute_script(page,"() => window.scrollY")
        # Verify if scrolling was successful
        if scroll_y_before == scroll_y_after:
            return "Scrolling has no effect, the entire content fits within the viewport."
        amount=amount if amount else 'one page'
        return f'Scrolled {direction} by {amount}'

@Tool('GoTo Tool',params=GoTo)
async def goto_tool(url:str,context:Context=None):
    '''Navigates directly to a specified URL in the current tab. Supports HTTP/HTTPS URLs and waits for the DOM content to load before proceeding.'''
    page=await context.get_current_page()
    await page.goto(url=url,wait_until='domcontentloaded')
    await page.wait_for_timeout(2.5*1000)
    return f'Navigated to {url}'

@Tool('Back Tool',params=Back)
async def back_tool(context:Context=None):
    '''Navigates to the previous page in the browser history, equivalent to clicking the browser's back button. Waits for the page to fully load.'''
    page=await context.get_current_page()
    await page.go_back()
    await page.wait_for_load_state('load')
    return 'Navigated to previous page'

@Tool('Forward Tool',params=Forward)
async def forward_tool(context:Context=None):
    '''Navigates to the next page in the browser history, equivalent to clicking the browser's forward button. Waits for the page to fully load.'''
    page=await context.get_current_page()
    await page.go_forward()
    await page.wait_for_load_state('load')
    return 'Navigated to next page'

@Tool('Key Tool',params=Key)
async def key_tool(keys:str,times:int=1,context:Context=None):
    '''Performs keyboard shortcuts and key combinations (e.g., "Control+C", "Enter", "Escape", "Tab"). Can repeat the key press multiple times. Supports all standard keyboard keys and modifiers.'''
    page=await context.get_current_page()
    await page.wait_for_load_state('domcontentloaded')
    for _ in range(times):
        await page.keyboard.press(keys)
    return f'Pressed {keys}'

@Tool('Download Tool',params=Download)
async def download_tool(url:str=None,filename:str=None,context:Context=None):
    '''Downloads files from the internet (PDFs, images, videos, audio, documents) and saves them to the system's downloads directory. Handles various file types and formats.'''
    folder_path=Path(context.browser.config.downloads_dir)
    async with httpx.AsyncClient() as client:
        response=await client.get(url)
    path=folder_path.joinpath(filename)
    with open(path,'wb') as f:
        async for chunk in response.aiter_bytes():
            f.write(chunk)
    return f'Downloaded {filename} from {url} and saved it to {path}'

@Tool('Scrape Tool',params=Scrape)
async def scrape_tool(context:Context=None):
    '''Extracts and returns the main content from the current webpage. Can output in markdown format (preserving links and structure). Filters out navigation, ads, and other non-essential content.'''
    page=await context.get_current_page()
    await page.wait_for_load_state('domcontentloaded')
    html=await page.content()
    content= markdownify(html)
    return f'Scraped the contents of the entire webpage:\n{content}'

@Tool('Tab Tool', params=Tab)
async def tab_tool(mode: Literal['open', 'close', 'switch'], tab_index: Optional[int] = None, context: Context = None):
    '''Manages browser tabs: opens new blank tabs, closes the current tab (if not the last one), or switches between existing tabs by index. Automatically handles focus and loading states.'''
    session = await context.get_session()
    pages = session.context.pages  # Get all open tabs
    if mode == 'open':
        page = await session.context.new_page()
        session.current_page = page
        await page.wait_for_load_state('load')
        return 'Opened a new blank tab and switched to it.'
    elif mode == 'close':
        if len(pages) == 1:
            return 'Cannot close the last remaining tab.'
        page = session.current_page
        await page.close()
        # Get remaining pages after closing
        pages = session.context.pages
        session.current_page = pages[-1]  # Switch to last remaining tab
        await session.current_page.bring_to_front()
        await session.current_page.wait_for_load_state('load')
        return 'Closed current tab and switched to the next last tab.'
    elif mode == 'switch':
        if tab_index is None or tab_index < 0 or tab_index >= len(pages):
            raise IndexError(f'Tab index {tab_index} is out of range. Available tabs: {len(pages)}')
        session.current_page = pages[tab_index]
        await session.current_page.bring_to_front()
        await session.current_page.wait_for_load_state('load')
        return f'Switched to tab {tab_index} (Total tabs: {len(pages)}).'
    else:
        raise ValueError("Invalid mode. Use 'open', 'close', or 'switch'.")

@Tool('Upload Tool',params=Upload)
async def upload_tool(index:int,filenames:list[str],context:Context=None):
    '''Uploads one or more files to file input elements on webpages. Handles both single and multiple file uploads. Files should be placed in the ./uploads directory before using this tool.'''
    element=await context.get_element_by_index(index=index)
    handle=await context.get_handle_by_xpath(element.xpath)
    files=[Path(getcwd()).joinpath('./uploads',filename) for filename in filenames]
    page=await context.get_current_page()
    async with page.expect_file_chooser() as file_chooser_info:
        await handle.click()
    file_chooser=await file_chooser_info.value
    handle=file_chooser.element
    if file_chooser.is_multiple():
        await handle.set_input_files(files=files)
    else:
        await handle.set_input_files(files=files[0])
    await page.wait_for_load_state('load')
    return f'Uploaded {filenames} to element at label {index}'

@Tool('Menu Tool',params=Menu)
async def menu_tool(index:int,labels:list[str],context:Context=None):
    '''Interacts with dropdown menus, select elements, and multi-select lists. Can select single or multiple options by their visible labels. Handles both simple dropdowns and complex multi-selection interfaces.'''
    element=await context.get_element_by_index(index=index)
    handle=await context.get_handle_by_xpath(element.xpath)
    labels=labels if len(labels)>1 else labels[0]
    await handle.select_option(label=labels)
    return f'Opened context menu of element at label {index} and selected {", ".join(labels)}'

@Tool("Script Tool",params=Script)
async def script_tool(script:str,context:Context=None):
    '''Executes arbitrary JavaScript code on the page. Can be used to manipulate the DOM or trigger events or scrape data. Returns the result of the executed script.'''
    page=await context.get_current_page()
    result=await context.execute_script(page,script)
    return f"Result of the executed script: {result}"

@Tool('Human Tool',params=HumanInput)
async def human_tool(prompt:str,context:Context=None):
    '''Requests human assistance when encountering challenges that require human intervention such as CAPTCHAs, OTP codes, complex decisions, or when explicitly asked to involve a human user.'''
    print(colored(f"Agent: {prompt}", color='cyan', attrs=['bold']))
    human_response = input("User: ")
    return f"User provided the following input: '{human_response}'"