from src.agent.web.tools.views import Click,Type,Wait,Scroll,GoTo,Back,Key,Download,Scrape,Tab,Upload,Menu,Form,Done
from main_content_extractor import MainContentExtractor
from src.agent.web.context import Context
from typing import Literal,Optional
from src.tool import Tool
from pathlib import Path
from os import getcwd
import pyperclip as pc
import httpx
    
@Tool('Done Tool',params=Done)
async def done_tool(answer:str,context:Context=None):
    '''To indicate that the task is completed'''
    return answer

@Tool('Click Tool',params=Click)
async def click_tool(index:int,context:Context=None):
    '''To click on elements such as buttons, links, checkboxes, and radio buttons'''
    page=await context.get_current_page()
    await page.wait_for_load_state('load')
    element=await context.get_element_by_index(index=index)
    handle=await context.get_handle_by_xpath(element.xpath)
    await handle.click()
    return f'Clicked on the element at label {index}'

@Tool('Type Tool',params=Type)
async def type_tool(index:int,text:str,clear:Literal['True','False']='False',context:Context=None):
    '''To type text into input fields, search boxes'''
    page=await context.get_current_page()
    element=await context.get_element_by_index(index=index)
    handle=await context.get_handle_by_xpath(element.xpath)
    await page.wait_for_load_state('load')
    await handle.click()
    if clear=='True':
        await page.keyboard.press('Control+A')
        await page.keyboard.press('Backspace')
    await page.keyboard.type(text,delay=80)
    return f'Typed {text} in element at label {index}'

@Tool('Wait Tool',params=Wait)
async def wait_tool(time:int,context:Context=None):
    '''To wait until the page has fully loaded before proceeding'''
    page=await context.get_current_page()
    await page.wait_for_timeout(time*1000)
    return f'Waited for {time}s'

@Tool('Scroll Tool',params=Scroll)
async def scroll_tool(direction:Literal['up','down']='up',amount:int=None,context:Context=None):
    '''To scroll the page by a certain amount or by a page up or down and on a specific section of the page'''
    page=await context.get_current_page()
    scroll_y_before = await context.execute_script(page,"() => window.scrollY")
    max_scroll_y = await context.execute_script(page,"() => document.documentElement.scrollHeight - window.innerHeight")
     # Check if scrolling is possible
    if scroll_y_before >= max_scroll_y and direction == 'down':
        return "Already at the bottom, cannot scroll further."
    elif scroll_y_before == 0 and direction == 'up':
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
    scroll_y_after = await page.evaluate("() => window.scrollY")
    # Verify if scrolling was successful
    if scroll_y_before == scroll_y_after:
        return "Scrolling had no effect, possibly already at the limit."
    amount=amount if amount else 'one page'
    return f'Scrolled {direction} by {amount}'

@Tool('GoTo Tool',params=GoTo)
async def goto_tool(url:str,context:Context=None):
    '''To navigate directly to a specified URL.'''
    page=await context.get_current_page()
    await page.goto(url=url)
    await page.wait_for_load_state('load')
    return f'Navigated to {url}'

@Tool('Back Tool',params=Back)
async def back_tool(context:Context=None):
    '''Go back to the previous page'''
    page=await context.get_current_page()
    await page.go_back()
    await page.wait_for_load_state('load')
    return 'Navigated to previous page'

@Tool('Key Tool',params=Key)
async def key_tool(keys:str,times:int=1,context:Context=None):
    '''To perform keyboard shorcuts'''
    page=await context.get_current_page()
    await page.wait_for_load_state('domcontentloaded')
    for _ in range(times):
        await page.keyboard.press(keys)
    return f'Pressed {keys}'

@Tool('Download Tool',params=Download)
async def download_tool(url:str=None,filename:str=None,context:Context=None):
    '''To download a file (e.g., pdf, image, video, audio) to the system'''
    folder_path=Path(context.browser.config.downloads_dir)
    async with httpx.AsyncClient() as client:
        response=await client.get(url)
    path=folder_path.joinpath(filename)
    with open(path,'wb') as f:
        f.write(response.content)
    return f'Downloaded {filename} from {url} and saved it to {path}'

@Tool('Scrape Tool',params=Scrape)
async def scrape_tool(format:Literal['markdown','text']='markdown',context:Context=None):
    '''Scrape the contents of the entire webpage'''
    page=await context.get_current_page()
    await page.wait_for_load_state('domcontentloaded')
    html=await page.content()
    content=MainContentExtractor.extract(html=html,include_links=True,output_format=format)
    return f'Extracted Page Content:\n{content}'

@Tool('Tab Tool', params=Tab)
async def tab_tool(mode: Literal['open', 'close', 'switch'], tab_index: Optional[int] = None, context: Context = None):
    '''To open a new tab, close the current tab, and switch from the current tab to the specified tab'''
    session = await context.get_session()
    pages = session.context.pages  # Get all open tabs
    if mode == 'open':
        page = await session.context.new_page()
        session.current_page = page
        await page.wait_for_load_state('load')
        return 'Opened a new tab and switched to it.'
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
        return f'Closed current tab and switched to the previous tab.'
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
    '''To upload files to an element in the webpage'''
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
    '''To interact with an element having dropdown menu and select an option from it'''
    element=await context.get_element_by_index(index=index)
    handle=await context.get_handle_by_xpath(element.xpath)
    labels=labels if len(labels)>1 else labels[0]
    await handle.select_option(label=labels)
    return f'Opened context menu of element at label {index} and selected {', '.join(labels)}'

@Tool('Form Tool',params=Form)
async def form_tool(tool_names:list[Literal['Click Tool','Type Tool','Upload Tool','Menu Tool']],tool_inputs:list[dict],context:Context=None):
    '''To fill input fields of application form'''
    for tool_name,tool_input in zip(tool_names,tool_inputs):
        if tool_name=='Click Tool':
            await click_tool.async_invoke(index=tool_input['index'],context=context)
        elif tool_name=='Type Tool':
            await type_tool.async_invoke(index=tool_input['index'],text=tool_input.get('text'),context=context)
        elif tool_name=='Upload Tool':
            await upload_tool.async_invoke(index=tool_input['index'],filenames=tool_input.get('filenames'),context=context)
        elif tool_name=='Menu Tool':
            await menu_tool.async_invoke(index=tool_input['index'],labels=tool_input.get('labels'),context=context)
    return f'Filled form with inputs {tool_inputs}'