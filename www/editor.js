const highlight = document.getElementById('highlight');


// Ensure that "tab" in the text area causes a tab character to be inserted instead of moving focus
editor.addEventListener('keydown', function (e) {

    const textarea = e.target;

    // Code editor style tab handling - indentation
    if (e.key === 'Tab') {
         // Prevent default tab behavior (moving focus)
         
        var isBackward = e.getModifierState('Shift');  
        e.preventDefault(); 

        // Get the current position of the cursor
        const cursorPos = textarea.selectionStart;

        if (isBackward) {
            // If Shift is pressed, remove a tab character (4 spaces)
            const textBefore = textarea.value.substring(0, cursorPos);
            const textAfter = textarea.value.substring(cursorPos);

            // If the last newline in textBefore has four spaces after it, remove those spaces
            const lastNewlineIndex = textBefore.lastIndexOf('\n');
            const textBeforeLastNewline = textBefore.substring(0, lastNewlineIndex + 1);
            const textAfterLastNewline = textBefore.substring(lastNewlineIndex + 1);
           
            //count number of leading spaces on textAfterLastNewline
            var numLeadingSpaces = textAfterLastNewline.match(/^\s*/)[0].length;
            //Limit to four spaces (one tab)
            if(numLeadingSpaces > 4) {
                numLeadingSpaces = 4;
            }

            // remove the leading spaces and reassemble text
            if (numLeadingSpaces >= 0) {
                textarea.value = textBeforeLastNewline + textAfterLastNewline.slice(numLeadingSpaces) + textAfter;
                textarea.selectionStart = textarea.selectionEnd = cursorPos - numLeadingSpaces;
            }

        } else {
            // Get the text before and after the cursor
            const textBefore = textarea.value.substring(0, cursorPos);
            const textAfter = textarea.value.substring(cursorPos);

            // Insert a tab character
            textarea.value = textBefore + '    ' + textAfter;

            // Move the cursor position after the inserted tab
            textarea.selectionStart = textarea.selectionEnd = cursorPos + 4;
        }
    }

    // Get total height and width of textarea in pixels
    var totalHeight = parseInt(window.getComputedStyle(textarea).getPropertyValue('height'));
    var totalWidth = parseInt(window.getComputedStyle(textarea).getPropertyValue('width'));
    // get number of rows and columns in textarea
    var rows = textarea.rows;
    var cols = textarea.cols;
    
    var curRow = 0;
    var curCol = 0;


});


function escapeHtml(str) {
  return str.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
}


//regex for all python keywords
var keywords = ["def", "class", "if", "elif", "else", "while", "for", "in", "try", "except", "finally", "with", "as", "import", "from", "return", "break", "continue"];
var keywordRegex = new RegExp("\\b(" + keywords.join("|") + ")\\b", "g");

//regex for all python language components
var commentRegex = new RegExp(/(#.*)$/gm);
var stringRegex = new RegExp(/((['"])(?:(?=(\\?))\2.)*?\1)/g); // Matches both single and double quoted strings
var numberRegex = new RegExp(/(\b\d+(\.\d+)?\b)/g); // Matches integers and floats
var semicolonRegex = new RegExp(/(;)/g); // Matches semicolons
//match python operators
var operatorRegex = new RegExp(/([+\-*/%&|^!~<>]=?|[=<>]=?|[+\-*/%&|^!~])/g); // Matches operators
//match python flow and grouping
var punctuationRegex = new RegExp(/([(){}\[\],.:])/g); // Matches punctuation


function updateHighlight() {
    const text = escapeHtml(editor.value);
    const tokens = [];

    function addMatches(regex, type) {
        let match;
        while ((match = regex.exec(text)) !== null) {
            tokens.push({ start: match.index, end: match.index + match[0].length, text: match[0], type });
        }
    }

    addMatches(commentRegex, 'comment');
    addMatches(stringRegex, 'string');
    addMatches(numberRegex, 'number');
    addMatches(keywordRegex, 'keyword');
    addMatches(punctuationRegex, 'punctuation');
    addMatches(semicolonRegex, 'error');
    // addMatches(operatorRegex, 'operator'); // You can enable this if needed

    // Sort by start index
    tokens.sort((a, b) => a.start - b.start);

    // Merge into output
    let result = '';
    let lastIndex = 0;

    for (const token of tokens) {
        if (token.start < lastIndex) continue; // skip overlaps
        result += text.slice(lastIndex, token.start);
        result += `<span class="${token.type}">${token.text}</span>`;
        lastIndex = token.end;
    }

    result += text.slice(lastIndex);
    highlight.innerHTML = result;
}


editor.addEventListener('input', updateHighlight);
editor.addEventListener('scroll', () => {
  highlight.scrollTop = editor.scrollTop;
  highlight.scrollLeft = editor.scrollLeft;
});

// make sure we do an initial highlight
updateHighlight();