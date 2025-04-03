from src.agent.web.tools.views import Clipboard,Click,Type,Wait,Scroll,GoTo,Back,Key,Download,Scrape,Tab,Upload,Menu,Form
from main_content_extractor import MainContentExtractor
from src.agent.web.context import Context
from typing import Literal,Optional
from src.tool import Tool
from pathlib import Path
from os import getcwd
import pyperclip as pc
import httpx

@Tool('Clipboard Tool', params=Clipboard)
async def clipboard_tool(mode: Literal['copy', 'paste'], text: str = None, context: Context = None):
    '''To copy content to clipboard and retrieve it when needed'''
    if mode == 'copy':
        if text:
            pc.copy(text)  # Copy text to system clipboard
            return f'Copied "{text}" to clipboard'
        else:
            raise ValueError("No text provided to copy")
    elif mode == 'paste':
        clipboard_content = pc.paste()  # Get text from system clipboard
        return f'Clipboard Content: "{clipboard_content}"'
    else:
        raise ValueError('Invalid mode. Use "copy" or "paste".')

@Tool('Click Tool',params=Click)
async def click_tool(index:int,context:Context=None):
    '''To click on elements such as buttons, links, checkboxes, and radio buttons'''
    element=await context.get_element_by_index(index=index)
    handle=await context.get_handle_by_xpath(element.xpath)
    if element.attributes.get('type')in ['checkbox','radio']:
        await handle.check(force=True)
        return f'Checked the element at label {index}'
    await handle.click()
    return f'Clicked on the element at label {index}'

@Tool('Type Tool',params=Type)
async def type_tool(index:int,text:str,clear:Literal['True','False']='False',context:Context=None):
    '''To type text into input fields, search boxes'''
    element=await context.get_element_by_index(index=index)
    handle=await context.get_handle_by_xpath(element.xpath)
    page=await context.get_current_page()
    await page.wait_for_load_state('load')
    if clear=='True':
        await handle.press('Control+A')
        await handle.press('Backspace')
    await handle.type(text,delay=80)
    return f'Typed {text} in element at label {index}'

@Tool('Wait Tool',params=Wait)
async def wait_tool(time:int,context:Context=None):
    '''To wait until the page has fully loaded before proceeding'''
    page=await context.get_current_page()
    await page.wait_for_timeout(time*1000)
    return f'Waited for {time}s'

@Tool('Scroll Tool',params=Scroll)
async def scroll_tool(direction:str,amount:int=None,context:Context=None):
    '''To scroll the page by a certain amount or by a page'''
    page=await context.get_current_page()
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
    amount=amount if amount else 'one page'
    return f'Scrolled {direction} by {amount}'

@Tool('GoTo Tool',params=GoTo)
async def goto_tool(url:str,context:Context=None):
    '''To navigate directly to a specified URL.'''
    page=await context.get_current_page()
    await page.goto(url=url)
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

@Tool('Tab Tool',params=Tab)
async def tab_tool(mode:Literal['open','close','switch'],tab_index:Optional[int]=None,context:Context=None):
    '''To open a new tab, close the current tab and switch from current tab to the specified tab'''
    session=await context.get_session()
    if mode=='open':
        page=await session.context.new_page()
        session.current_page=page
        await page.wait_for_load_state('load')
        return f'Opened new tab and switched to it'
    elif mode=='close':
        page=session.current_page
        await page.close()
        pages=session.context.pages
        if tab_index is not None and tab_index>len(pages):
            raise IndexError('Index out of range')
        page=pages[-1]
        session.current_page=page
        await page.bring_to_front()
        await page.wait_for_load_state('load')
        return f'Closed current tab and switched to previous tab'
    elif mode=='switch':
        pages=session.context.pages
        if tab_index is not None and tab_index>len(pages):
            raise IndexError('Index out of range')
        page=pages[tab_index]
        session.current_page=page
        await page.bring_to_front()
        await page.wait_for_load_state('load')
        return f'Switched to tab {tab_index}'
    else:
        raise ValueError('Invalid mode')
    
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