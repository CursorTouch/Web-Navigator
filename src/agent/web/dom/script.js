const INTERACTIVE_TAGS = [
    'a', 'button', 'details', 'embed', 'input','option','canvas',
    'menu', 'menuitem', 'object', 'select', 'textarea', 'summary'
]

const INTERACTIVE_ROLES = [
    'button', 'menu', 'menuitem', 'link', 'checkbox', 'radio',
    'slider', 'tab', 'tabpanel', 'textbox', 'combobox', 'grid',
    'option', 'progressbar', 'scrollbar', 'searchbox','listbox','listbox',
    'switch', 'tree', 'treeitem', 'spinbutton', 'tooltip', 'a-button-inner', 'a-dropdown-button', 'click',
    'menuitemcheckbox', 'menuitemradio', 'a-button-text', 'button-text', 'button-icon', 'button-icon-only', 
    'button-text-icon-only', 'dropdown', 'combobox'
]

const SAFE_ATTRIBUTES = [
	'name',
	'type',
	'value',
	'placeholder',
    'label',
	'aria-label',
	'aria-labelledby',
	'aria-describedby',
	'role',
	'for',
	'autocomplete',
	'required',
	'readonly',
	'alt',
	'title',
	'src',
	'data-testid',
	'data-id',
	'data-qa',
	'data-cy',
	'href',
	'target',
    'id',
    'class'
];

    const labels = [];
    const selectorMap = {};

    // Function to get a random color
    function getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

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

    // Extract visible interactive elements
    async function getInteractiveElements(node=document.body) {

        const interactiveElements = [];  
        await waitForPageToLoad()
        function isVisible(element) {
            let type = element.getAttribute('type');
            // The radio and checkbox elements are all ready invisible so we can skip them
            if(['radio', 'checkbox'].includes(type)) return true;
            const style = window.getComputedStyle(element);
            const hasBoundingBox = element.offsetWidth > 0 && element.offsetHeight > 0;
            const visible =
                style.display !== 'none' &&
                style.visibility !== 'hidden' &&
                style.opacity !== '0' &&
                hasBoundingBox;

            return visible;
        }

        function isClickable(element) {
            return element.hasAttribute('onclick') || element.hasAttribute('@click')||
            element.getAttribute('role') === 'button' || window.getComputedStyle(element).cursor === 'pointer'
        }

        function isElementCovered(element) {
            let type = element.getAttribute('type');
            // The radio and checkbox elements are all ready covered so we can skip them
            if(['radio', 'checkbox'].includes(type)) return false;
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
            const role = currentNode.getAttribute('role');

            const hasInteractiveTag = INTERACTIVE_TAGS.includes(tagName);
            const hasInteractiveRole = role && INTERACTIVE_ROLES.includes(role);

            if ((hasInteractiveTag || hasInteractiveRole || isClickable(currentNode)) && isVisible(currentNode)) {
                // Check if the element is covered by another element
                const isCovered = isElementCovered(currentNode);
                if (!isCovered) {
                    const boundingBox = currentNode.getBoundingClientRect();
                    const xCenter = boundingBox.left + boundingBox.width / 2;
                    const yCenter = boundingBox.top + boundingBox.height / 2;
                    interactiveElements.push({
                        tag: currentNode.tagName.toLowerCase(),
                        role: currentNode.getAttribute('role'),
                        name: currentNode.getAttribute('name')||currentNode.getAttribute('aria-label')||currentNode.getAttribute('aria-labelledby')||currentNode.getAttribute('aria-describedby')||currentNode?.textContent,
                        attributes: Object.fromEntries(
                            Array.from(currentNode.attributes).filter(attr => SAFE_ATTRIBUTES.includes(attr.name)).map(attr => [attr.name, attr.value])
                        ),
                        box: boundingBox,
                        center: {'x': xCenter, 'y': yCenter},
                        handle: currentNode
                    });
                }
            }
            const shadowRoot=currentNode.shadowRoot
            if(shadowRoot){
                shadowRoot.childNodes.forEach(child => traverseDom(child));
            }
            if(tagName === 'iframe') {
                try{
                    const iframeDocument = currentNode.contentDocument || currentNode.contentWindow.document;
                    traverseDom(iframeDocument.body);
                }
                catch (e) {
                    console.log('The iframe is not accessable');
                }
            }
            if(!isClickable(currentNode)) {
                currentNode.childNodes.forEach(child => traverseDom(child)); // Go deeper if the current node is not interactive
            }
        }

        traverseDom(node);
        selectorMapping(interactiveElements);
        return interactiveElements;
    }

    // Mark page by placing bounding boxes and labels
    function mark_page(elements) {
        let index = 0; // Start numbering from 1

        elements.forEach(element => {
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
            index++;
        });
    }

    // Remove all bounding boxes and labels
    function unmark_page() {
        for (const label of labels) {
            document.body.removeChild(label);
        }
        labels.length = 0;
    }


    // Function to populate the registry with interactive elements
    function selectorMapping(elements) {
        elements.forEach((element, index) => {
            selectorMap[index] = element.handle;  // Store the element object directly
        });
    }

    // Function to get element by index
    function getElementByIndex(index) {
        return selectorMap[index] || null;
    }