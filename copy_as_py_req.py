from burp import IBurpExtender, IContextMenuFactory
from javax.swing import JMenuItem
from java.awt.datatransfer import StringSelection
from java.awt import Toolkit
import base64

class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("Copy as Python requests")
        callbacks.registerContextMenuFactory(self)

    def createMenuItems(self, invocation):
        self._invocation = invocation
        menuItem = JMenuItem("Copy as Python requests", actionPerformed=self.copy_as_python)
        return [menuItem]

    def copy_as_python(self, event):
        http_traffic = self._invocation.getSelectedMessages()
        if not http_traffic:
            return
        
        request_info = self._helpers.analyzeRequest(http_traffic[0])
        headers = request_info.getHeaders()
        body = http_traffic[0].getRequest()[request_info.getBodyOffset():]
        url = request_info.getUrl().toString()
        method = request_info.getMethod()
        
        # Extract headers
        headers_dict = {}
        for header in headers[1:]:  # Skip request line
            key, value = header.split(": ", 1)
            headers_dict[key] = value
        
        # Convert request body if present
        if body:
            encoded_body = base64.b64encode(body).decode('utf-8')
            body_str = 'base64.b64decode("' + encoded_body + '")'
        else:
            body_str = "None"
        
        # Generate Python request
        python_code = (
            'import requests\n'
            'import base64\n\n'
            'url = "' + url + '"\n'
            'headers = ' + str(headers_dict) + '\n'
            'data = ' + body_str + '\n\n'
            'response = requests.' + method.lower() + '(url, headers=headers, data=data)\n'
            'print(response.text)\n'
        )

        # Copy to clipboard
        clipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
        clipboard.setContents(StringSelection(python_code), None)
