```xml
<Input>
    <AgentState>
        Current Step: {iteration}

        Max. Steps: {max_iteration}

        Action Response: {observation}
    </AgentState>
    <BrowserState>
        [Begin of Tab Info]
        Current Tab: {current_tab}

        Open Tabs:
        {tabs}
        [End of Tab Info]

        [Begin of Viewport]
        List of Interactive Elements:
        {interactive_elements}

        List of Scrollable Elements:
        {scrollable_elements}

        List of Informative Elements:
        {informative_elements}
        [End of Viewport]
        <user_query>
        {query}
        </user_query>

        Note: Use the `Done Tool` if the task is completely over else continue solving.
    </BrowserState>
</Input>
```