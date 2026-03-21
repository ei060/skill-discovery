Skip to content
Navigation Menu
Appearance settings
Platform
Solutions
Resources
Open Source
Enterprise
Pricing
Search or jump to...
Sign in
Sign up
Appearance settings
Dismiss alert
ChromeDevTools
/
chrome-devtools-mcp
Public
Notifications You must be signed in to change notification settings
Fork 1.6k
Star 27.1k
You must be signed in to change notification settings
Code
Issues
55
Pull requests
14
Discussions
Actions
Security
Insights
Additional navigation options
ChromeDevTools/chrome-devtools-mcp
 main
22 Branches
37 Tags
Code
Folders and files
Name Last commit message Last commit date
Latest commit
nroscino
chore: evaluate script on service workers (#1052)
2 days ago
505089c
 · 2 days ago
Feb 27, 2026
History
594 Commits
.agent/rules
chore: move gemini to agents (#776)
2 months agoJan 15, 2026
.claude-plugin
fix: use relative path for plugin source in marketplace (#724)
2 months agoJan 9, 2026
.github
chore: update pre-release workflow name (#1050)
3 days agoFeb 26, 2026
docs
feat: integrate Lighthouse audits (#831)
3 days agoFeb 26, 2026
scripts
feat: integrate Lighthouse audits (#831)
3 days agoFeb 26, 2026
skills
docs: Adapt a11y skill to utilize Lighthouse (#1054)
2 days agoFeb 27, 2026
src
chore: evaluate script on service workers (#1052)
2 days agoFeb 27, 2026
tests
chore: evaluate script on service workers (#1052)
2 days agoFeb 27, 2026
.gitattributes
chore: make eval scripts cross-platform compatible (Windows) (
5 days agoFeb 24, 2026
.gitignore
chore: add basic eval (#766)
2 months agoJan 14, 2026
.mcp.json
docs: add MCP config for Claude plugin + docs (#944)
2 weeks agoFeb 13, 2026
.nvmrc
ci: re-configure ci (#1)
6 months agoSep 11, 2025
.prettierignore
feat: integrate Lighthouse audits (#831)
3 days agoFeb 26, 2026
.prettierrc.cjs
docs: improve Cursor install instructions (#58)
6 months agoSep 22, 2025
.release-please-manifest.json
chore(main): release chrome-devtools-mcp 0.18.1 (#1042)
4 days agoFeb 25, 2026
CHANGELOG.md
chore(main): release chrome-devtools-mcp 0.18.1 (#1042)
4 days agoFeb 25, 2026
CONTRIBUTING.md
docs: add a mention of evals into contributing.md (#773)
2 months agoJan 16, 2026
LICENSE
feat: initial version
6 months agoSep 11, 2025
README.md
feat: integrate Lighthouse audits (#831)
3 days agoFeb 26, 2026
SECURITY.md
feat: initial version
6 months agoSep 11, 2025
eslint.config.mjs
feat: integrate Lighthouse audits (#831)
3 days agoFeb 26, 2026
gemini-extension.json
chore: latest gemini extension (#142)
6 months agoSep 25, 2025
package-lock.json
feat: integrate Lighthouse audits (#831)
3 days agoFeb 26, 2026
package.json
feat: integrate Lighthouse audits (#831)
3 days agoFeb 26, 2026
puppeteer.config.cjs
test: add Puppeteer config (#479)
5 months agoOct 27, 2025
release-please-config.json
refactor: extract version in a seprate file (#1032)
5 days agoFeb 24, 2026
rollup.config.mjs
feat: integrate Lighthouse audits (#831)
3 days agoFeb 26, 2026
server.json
chore(main): release chrome-devtools-mcp 0.18.1 (#1042)
4 days agoFeb 25, 2026
tsconfig.json
chore(build): add devtools-formatter-worker.ts bundle (#792)
2 months agoJan 19, 2026
Repository files navigation
README
Contributing
Apache-2.0 license
Security
Chrome DevTools MCP
chrome-devtools-mcp lets your coding agent (such as Gemini, Claude, Cursor or Copilot) control and inspect a live Chrome browser. It acts as a Model-Context-Protocol (MCP) server, giving your AI coding assistant access to the full power of Chrome DevTools for reliable automation, in-depth debugging, and performance analysis.
Tool reference | Changelog | Contributing | Troubleshooting | Design Principles
Key features
Get performance insights: Uses Chrome DevTools to record traces and extract actionable performance insights.
Advanced browser debugging: Analyze network requests, take screenshots and check browser console messages (with source-mapped stack traces).
Reliable automation. Uses puppeteer to automate actions in Chrome and automatically wait for action results.
Disclaimers
chrome-devtools-mcp exposes content of the browser instance to the MCP clients allowing them to inspect, debug, and modify any data in the browser or DevTools. Avoid sharing sensitive or personal information that you don't want to share with MCP clients.
Performance tools may send trace URLs to the Google CrUX API to fetch real-user experience data. This helps provide a holistic performance picture by presenting field data alongside lab data. This data is collected by the Chrome User Experience Report (CrUX). To disable this, run with the --no-performance-crux flag.
Usage statistics
Google collects usage statistics (such as tool invocation success rates, latency, and environment information) to improve the reliability and performance of Chrome DevTools MCP.
Data collection is enabled by default. You can opt-out by passing the --no-usage-statistics flag when starting the server:
"args": ["-y", "chrome-devtools-mcp@latest", "--no-usage-statistics"]
Google handles this data in accordance with the Google Privacy Policy.
Google's collection of usage statistics for Chrome DevTools MCP is independent from the Chrome browser's usage statistics. Opting out of Chrome metrics does not automatically opt you out of this tool, and vice-versa.
Collection is disabled if CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS or CI env variables are set.
Requirements
Node.js v20.19 or a newer latest maintenance LTS version.
Chrome current stable version or newer.
npm.
Getting started
Add the following config to your MCP client:
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
Note
Using chrome-devtools-mcp@latest ensures that your MCP client will always use the latest version of the Chrome DevTools MCP server.
If you are intersted in doing only basic browser tasks, use the --slim mode:
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--slim", "--headless"]
    }
  }
}
See Slim tool reference.
MCP Client configuration
Amp
Follow and use the config provided above. You can also install the Chrome DevTools MCP server using the CLI:
Antigravity
Claude Code

Cline
Follow and use the config provided above.
Codex
Follow the using the standard config from above. You can also install the Chrome DevTools MCP server using the Codex CLI:
Copilot CLI
Copilot / VS Code
Cursor
Factory CLI
Use the Factory CLI to add the Chrome DevTools MCP server ():
Gemini CLI
Install the Chrome DevTools MCP server using the Gemini CLI.
Gemini Code Assist
Follow the using the standard config from above.
JetBrains AI Assistant & Junie
Kiro
Katalon Studio
OpenCode
Qoder
Qoder CLI
Visual Studio
Warp
Windsurf
Follow the using the standard config from above.
Your first prompt
Enter the following prompt in your MCP Client to check if everything is working:
Check the performance of https://developers.chrome.com
Your MCP client should open the browser and record a performance trace.
Note
The MCP server will start the browser automatically once the MCP client uses a tool that requires a running browser instance. Connecting to the Chrome DevTools MCP server on its own will not automatically start the browser.
Tools
If you run into any issues, checkout our troubleshooting guide.
Input automation (9 tools)
click
drag
fill
fill_form
handle_dialog
hover
press_key
type_text
upload_file
Navigation automation (6 tools)
close_page
list_pages
navigate_page
new_page
select_page
wait_for
Emulation (2 tools)
emulate
resize_page
Performance (4 tools)
performance_analyze_insight
performance_start_trace
performance_stop_trace
take_memory_snapshot
Network (2 tools)
get_network_request
list_network_requests
Debugging (6 tools)
evaluate_script
get_console_message
lighthouse_audit
list_console_messages
take_screenshot
take_snapshot
Configuration
The Chrome DevTools MCP server supports the following configuration option:
--autoConnect/ --auto-connect If specified, automatically connects to a browser (Chrome 144+) running in the user data directory identified by the channel param. Requires the remoted debugging server to be started in the Chrome instance via chrome://inspect/#remote-debugging.
Type: boolean
Default: false
--browserUrl/ --browser-url, -u Connect to a running, debuggable Chrome instance (e.g. http://127.0.0.1:9222). For more details see: https://github.com/ChromeDevTools/chrome-devtools-mcp#connecting-to-a-running-chrome-instance.
Type: string
--wsEndpoint/ --ws-endpoint, -w WebSocket endpoint to connect to a running Chrome instance (e.g., ws://127.0.0.1:9222/devtools/browser/). Alternative to --browserUrl.
Type: string
--wsHeaders/ --ws-headers Custom headers for WebSocket connection in JSON format (e.g., '{"Authorization":"Bearer token"}'). Only works with --wsEndpoint.
Type: string
--headless Whether to run in headless (no UI) mode.
Type: boolean
Default: false
--executablePath/ --executable-path, -e Path to custom Chrome executable.
Type: string
--isolated If specified, creates a temporary user-data-dir that is automatically cleaned up after the browser is closed. Defaults to false.
Type: boolean
--userDataDir/ --user-data-dir Path to the user data directory for Chrome. Default is $HOME/.cache/chrome-devtools-mcp/chrome-profile$CHANNEL_SUFFIX_IF_NON_STABLE
Type: string
--channel Specify a different Chrome channel that should be used. The default is the stable channel version.
Type: string
Choices: stable, canary, beta, dev
--logFile/ --log-file Path to a file to write debug logs to. Set the env variable DEBUG to * to enable verbose logs. Useful for submitting bug reports.
Type: string
--viewport Initial viewport size for the Chrome instances started by the server. For example, 1280x720. In headless mode, max size is 3840x2160px.
Type: string
--proxyServer/ --proxy-server Proxy server configuration for Chrome passed as --proxy-server when launching the browser. See https://www.chromium.org/developers/design-documents/network-settings/ for details.
Type: string
--acceptInsecureCerts/ --accept-insecure-certs If enabled, ignores errors relative to self-signed and expired certificates. Use with caution.
Type: boolean
--experimentalScreencast/ --experimental-screencast Exposes experimental screencast tools (requires ffmpeg). Install ffmpeg https://www.ffmpeg.org/download.html and ensure it is available in the MCP server PATH.
Type: boolean
--chromeArg/ --chrome-arg Additional arguments for Chrome. Only applies when Chrome is launched by chrome-devtools-mcp.
Type: array
--ignoreDefaultChromeArg/ --ignore-default-chrome-arg Explicitly disable default arguments for Chrome. Only applies when Chrome is launched by chrome-devtools-mcp.
Type: array
--categoryEmulation/ --category-emulation Set to false to exclude tools related to emulation.
Type: boolean
Default: true
--categoryPerformance/ --category-performance Set to false to exclude tools related to performance.
Type: boolean
Default: true
--categoryNetwork/ --category-network Set to false to exclude tools related to network.
Type: boolean
Default: true
--performanceCrux/ --performance-crux Set to false to disable sending URLs from performance traces to CrUX API to get field performance data.
Type: boolean
Default: true
--usageStatistics/ --usage-statistics Set to false to opt-out of usage statistics collection. Google collects usage data to improve the tool, handled under the Google Privacy Policy (https://policies.google.com/privacy). This is independent from Chrome browser metrics. Disabled if CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS or CI env variables are set.
Type: boolean
Default: true
--slim Exposes a "slim" set of 3 tools covering navigation, script execution and screenshots only. Useful for basic browser tasks.
Type: boolean
Pass them via the args property in the JSON configuration. For example:
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--channel=canary",
        "--headless=true",
        "--isolated=true"
      ]
    }
  }
}
Connecting via WebSocket with custom headers
You can connect directly to a Chrome WebSocket endpoint and include custom headers (e.g., for authentication):
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--wsEndpoint=ws://127.0.0.1:9222/devtools/browser/<id>",
        "--wsHeaders={\"Authorization\":\"Bearer YOUR_TOKEN\"}"
      ]
    }
  }
}
To get the WebSocket endpoint from a running Chrome instance, visit http://127.0.0.1:9222/json/version and look for the webSocketDebuggerUrl field.
You can also run npx chrome-devtools-mcp@latest --help to see all available configuration options.
Concepts
User data directory
chrome-devtools-mcp starts a Chrome's stable channel instance using the following user data directory:
Linux / macOS: $HOME/.cache/chrome-devtools-mcp/chrome-profile-$CHANNEL
Windows: %HOMEPATH%/.cache/chrome-devtools-mcp/chrome-profile-$CHANNEL
The user data directory is not cleared between runs and shared across all instances of chrome-devtools-mcp. Set the isolated option to true to use a temporary user data dir instead which will be cleared automatically after the browser is closed.
Connecting to a running Chrome instance
By default, the Chrome DevTools MCP server will start a new Chrome instance with a dedicated profile. This might not be ideal in all situations:
If you would like to maintain the same application state when alternating between manual site testing and agent-driven testing.
When the MCP needs to sign into a website. Some accounts may prevent sign-in when the browser is controlled via WebDriver (the default launch mechanism for the Chrome DevTools MCP server).
If you're running your LLM inside a sandboxed environment, but you would like to connect to a Chrome instance that runs outside the sandbox.
In these cases, start Chrome first and let the Chrome DevTools MCP server connect to it. There are two ways to do so:
Automatic connection (available in Chrome 144): best for sharing state between manual and agent-driven testing.
Manual connection via remote debugging port: best when running inside a sandboxed environment.
Automatically connecting to a running Chrome instance
Step 1: Set up remote debugging in Chrome
In Chrome (>= M144), do the following to set up remote debugging:
Navigate to chrome://inspect/#remote-debugging to enable remote debugging.
Follow the dialog UI to allow or disallow incoming debugging connections.
Step 2: Configure Chrome DevTools MCP server to automatically connect to a running Chrome Instance
To connect the chrome-devtools-mcp server to the running Chrome instance, use --autoConnect command line argument for the MCP server.
The following code snippet is an example configuration for gemini-cli:
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest", "--autoConnect"]
    }
  }
}
Step 3: Test your setup
Make sure your browser is running. Open gemini-cli and run the following prompt:
Check the performance of https://developers.chrome.com
Note
The autoConnect option requires the user to start Chrome. If the user has multiple active profiles, the MCP server will connect to the default profile (as determined by Chrome). The MCP server has access to all open windows for the selected profile.
The Chrome DevTools MCP server will try to connect to your running Chrome instance. It shows a dialog asking for user permission.
Clicking Allow results in the Chrome DevTools MCP server opening developers.chrome.com and taking a performance trace.
Manual connection using port forwarding
You can connect to a running Chrome instance by using the --browser-url option. This is useful if you are running the MCP server in a sandboxed environment that does not allow starting a new Chrome instance.
Here is a step-by-step guide on how to connect to a running Chrome instance:
Step 1: Configure the MCP client
Add the --browser-url option to your MCP client configuration. The value of this option should be the URL of the running Chrome instance. http://127.0.0.1:9222 is a common default.
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--browser-url=http://127.0.0.1:9222"
      ]
    }
  }
}
Step 2: Start the Chrome browser
Warning
Enabling the remote debugging port opens up a debugging port on the running browser instance. Any application on your machine can connect to this port and control the browser. Make sure that you are not browsing any sensitive websites while the debugging port is open.
Start the Chrome browser with the remote debugging port enabled. Make sure to close any running Chrome instances before starting a new one with the debugging port enabled. The port number you choose must be the same as the one you specified in the --browser-url option in your MCP client configuration.
For security reasons, Chrome requires you to use a non-default user data directory when enabling the remote debugging port. You can specify a custom directory using the --user-data-dir flag. This ensures that your regular browsing profile and data are not exposed to the debugging session.
macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-profile-stable
Linux
/usr/bin/google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-profile-stable
Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%TEMP%\chrome-profile-stable"
Step 3: Test your setup
After configuring the MCP client and starting the Chrome browser, you can test your setup by running a simple prompt in your MCP client:
Check the performance of https://developers.chrome.com
Your MCP client should connect to the running Chrome instance and receive a performance report.
If you hit VM-to-host port forwarding issues, see the “Remote debugging between virtual machine (VM) and host fails” section in docs/troubleshooting.md.
For more details on remote debugging, see the Chrome DevTools documentation.
Debugging Chrome on Android
Please consult these instructions.
Known limitations
See Troubleshooting.
About
Chrome DevTools for coding agents
npmjs.org/package/chrome-devtools-mcp
Topics
debugging chrome browser chrome-devtools mcp devtools puppeteer mcp-server
Resources
Readme
License
Apache-2.0 license
Contributing
Contributing
Security policy
Security policy
Activity
Custom properties
Stars
27.1k stars
Watchers
99 watching
Forks
1.6k forks
Report repository
Releases 37
chrome-devtools-mcp: v0.18.1
Latest
4 days agoFeb 25, 2026
+ 36 releases
Contributors
61
+ 47 contributors
Languages
TypeScript
96.3%
JavaScript
3.7%
Footer
© 2026 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Community
Docs
Contact
Manage cookies
Do not share my personal information