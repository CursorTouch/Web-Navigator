    const INTERACTIVE_TAGS =new Set([
        'a', 'button', 'details', 'embed', 'input','option','canvas',
        'menu', 'menuitem', 'object', 'select', 'textarea', 'summary',
        'dialog', 'banner'
    ])

    const EXCLUDED_TAGS =new Set([
        'style', 'script', 'noscript','link','meta'
    ])

    const INTERACTIVE_ROLES =new Set([
        'button', 'menu', 'menuitem', 'link', 'checkbox', 'radio',
        'slider', 'tab', 'tabpanel', 'textbox', 'combobox', 'grid',
        'option', 'progressbar', 'scrollbar', 'searchbox','listbox',
        'switch', 'tree', 'treeitem', 'spinbutton', 'tooltip', 'a-button-inner', 
        'a-dropdown-button', 'click','menuitemcheckbox', 'menuitemradio', 
        'a-button-text', 'button-text', 'button-icon', 'button-icon-only',
        'button-text-icon-only', 'dropdown', 'combobox'
    ])

    const CURSOR_TYPES=new Set(["pointer", "move", "text", "grab", "cell"])

    const SAFE_ATTRIBUTES = new Set([
        'name','type','value','placeholder','label','aria-label','aria-labelledby','aria-describedby','role',
        'for','autocomplete','required','readonly','alt','title','src','data-testid','data-id','data-qa',
        'data-cy','href','target','tabindex','class'
    ]);

    const labels = [];

    // Extract visible interactive elements`
    async function getInteractiveElements(node=document.body) {
        const interactiveElements = [];
        // Function to wait for the page to be fully loaded
        function waitForPageToLoad() {
            return new Promise((resolve, reject) => {
                if (document.readyState === 'complete') {
                    resolve();
                } else {
                    window.addEventListener('load', resolve); // Resolves when the load event fires
                }
            });
        }  
        await waitForPageToLoad();

        function isVisible(element) {
            let type = element.getAttribute('type');
            // The radio and checkbox elements are all ready invisible so we can skip them
            if(new Set(['radio', 'checkbox']).has(type)) return true;
            const style = window.getComputedStyle(element);
            const onScreen = element.offsetWidth > 0 && element.offsetHeight > 0;
            return style.display !== 'none' &&
            style.visibility !== 'hidden' &&
            style.opacity !== '0' && 
            !element.hasAttribute('hidden') &&
            onScreen;
        }

        function isElementInViewport(element) {
            if (!element || element.offsetParent === null) {
                return false; // Hidden elements (display: none)
            }

            const rect = element.getBoundingClientRect();
            const style = window.getComputedStyle(element);
            const windowHeight = window.innerHeight || document.documentElement.clientHeight;
            const windowWidth = window.innerWidth || document.documentElement.clientWidth;
        
            // Always consider fixed elements in the viewport if they have dimensions
            if (style.position === "fixed") {
                return rect.width > 0 && rect.height > 0;
            }
            // Sticky elements: Check if they are visible inside their parent
            if (style.position === "sticky") {
                const parent = element.offsetParent;
                if (parent) {
                    const parentRect = parent.getBoundingClientRect();
                    if (rect.bottom < parentRect.top || rect.top > parentRect.bottom) {
                        return false; // Sticky element is outside its parent's view
                    }
                }
            }
            // Check if any part of the element is inside the viewport
            return (
                rect.bottom >= 0 &&
                rect.right >= 0 &&
                rect.top <= windowHeight &&
                rect.left <= windowWidth
            );
        }

        function isElementClickable(element) {
            const style = window.getComputedStyle(element);
            return CURSOR_TYPES.has(style.cursor)||element.hasAttribute('onclick') || element.hasAttribute('v-on:click') ||
            element.hasAttribute('@click') || element.hasAttribute("ng-click")
        }

        function isElementCovered(element) {
            let type = element.getAttribute('type');
            // The radio and checkbox elements are all ready covered so we can skip them
            if(new Set(['radio', 'checkbox']).has(type)) return false;
            // Get the bounding box of the element to find its center point
            const boundingBox = element.getBoundingClientRect();
            const x = boundingBox.left + boundingBox.width / 2;
            const y = boundingBox.top + boundingBox.height / 2;
            // Get the top element under the center of the current element
            const topElement = document.elementFromPoint(x, y);
            // If no element is found at the point, return false (no element is covering it)
            if (!topElement) return false;
            // Compare if topElement is inside the current element
            const isInside = element.contains(topElement);
            // If topElement is inside the current element, it means it's not covered by it
            if (isInside) return false;        
            return true;  // If no coverage, return true
        }

        function traverseDom(currentNode) {
            if (!currentNode) return;
            if (currentNode.nodeType !== Node.ELEMENT_NODE) return;

            const tagName = currentNode.tagName.toLowerCase();
            if (EXCLUDED_TAGS.has(tagName)) return;
            const role = currentNode.getAttribute('role');

            const hasInteractiveTag = INTERACTIVE_TAGS.has(tagName);
            const hasInteractiveRole = role && INTERACTIVE_ROLES.has(role);

            if ((hasInteractiveTag || hasInteractiveRole || isElementClickable(currentNode)) && isVisible(currentNode) && isElementInViewport(currentNode)) {
                // Check if the element is covered by another element
                const isCovered = !isElementCovered(currentNode);
                if (isCovered) {
                    const rect = currentNode.getBoundingClientRect();
                    let left = rect.left;
                    let top = rect.top;
                    let width = rect.width;
                    let height = rect.height;
                    let frame = window.frameElement;
                    // If the element is in an iframe, adjust the coordinates
                    while (frame) {
                        let frameRect = frame.getBoundingClientRect();
                        left += frameRect.left;
                        top += frameRect.top;
                        frame = frame.ownerDocument.defaultView?.frameElement;
                    }
                    const boundingBox = { left, top, width, height };
                    const x = Math.floor(boundingBox.left + boundingBox.width / 2);
                    const y = Math.floor(boundingBox.top + boundingBox.height / 2);
                    
                    interactiveElements.push({
                        tag: currentNode.tagName.toLowerCase(),
                        role: currentNode.getAttribute('role') || 'none',  // Default to 'none' if no role is found
                        name: currentNode.getAttribute('aria-label') ||
                              currentNode.getAttribute('name') ||
                              currentNode.getAttribute('aria-labelledby') ||
                              currentNode.getAttribute('aria-describedby') ||
                              currentNode.textContent?.replace(/\s+/g, ' ').trim().split('.')[0] || 'none', // Trim textContent if it exists
                        attributes: Object.fromEntries(
                            Array.from(currentNode.attributes)
                                .filter(attr => SAFE_ATTRIBUTES.has(attr.name))
                                .map(attr => [attr.name, attr.value])),
                        box: boundingBox || null,  // Avoid undefined errors
                        center: { x, y },
                        root: frame?'iframe':'document'
                    });
                }
            }
            // Handle shadow DOM
            const shadowRoot=currentNode.shadowRoot
            if(shadowRoot){
                Array.from(shadowRoot.children).forEach(child => traverseDom(child));
            }
            if(!isElementClickable(currentNode)) {
                Array.from(currentNode.children).forEach(child => traverseDom(child));
            }
        }
        traverseDom(node);
        return interactiveElements;
    }

    // Mark page by placing bounding boxes and labels
    function mark_page(elements) {
        // Function to generate a random color
        function getRandomColor() {
            const letters = '0123456789ABCDEF';
            let color = '#';
            for (let i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        }

        elements.forEach((element,index) => {
            const { box } = element;
            if (!box) return;

            const { left, top, width, height } = box;
            const color = getRandomColor();

            // Create bounding box
            const boundingBox = document.createElement('div');
            boundingBox.style.position = 'fixed';
            boundingBox.style.left = `${left}px`;
            boundingBox.style.top = `${top}px`;
            boundingBox.style.width = `${width}px`;
            boundingBox.style.height = `${height}px`;
            boundingBox.style.outline = `2px dashed ${color}`;
            boundingBox.style.pointerEvents = 'none';
            boundingBox.style.zIndex = '9999';

            // Create a label for numbering
            const label = document.createElement('span');
            label.textContent = index;
            label.style.position = 'absolute';
            label.style.top = '-19px';
            label.style.right = '0px';
            label.style.backgroundColor = color;
            label.style.color = 'white';
            label.style.padding = '2px 4px';
            label.style.fontSize = '12px';
            label.style.borderRadius = '2px';

            // Append label and bounding box
            boundingBox.appendChild(label);
            labels.push(boundingBox);
            document.body.appendChild(boundingBox);
        });
    }

    // Remove all bounding boxes and labels
    function unmark_page() {
        for (const label of labels) {
            document.body.removeChild(label);
        }
        labels.length = 0;
    }