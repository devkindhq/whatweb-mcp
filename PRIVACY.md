# Privacy policy: WhatWeb MCP server

Effective date: 11 November 2026

This policy covers the WhatWeb MCP server (`devkind/whatweb-mcp` Docker image) and its Claude plugin, published by Devkind. The server runs in a Docker container on your own machine. Devkind does not run a hosted copy and does not receive any of your data.

## What the server handles

- **The website you ask it to scan.** The server needs no account and no API key.
- **Scan results**: the site's HTTP status and the technologies it detects, with versions and the matched text. Results can include contact details that the site publishes, such as email addresses in `mailto:` links.

## Where the data goes

- Each scan sends HTTP requests from your machine to the website you name, with the user agent `WhatWeb/0.6.4`. WhatWeb follows up to 10 redirects, also to other hosts. The `aggressive` level sends many more requests than `stealthy`.
- Scan results return to your MCP client, such as Claude. The client handles them under its own privacy terms.
- On first use, Docker downloads the server image from Docker Hub.

## How the data is used

The server uses this data only to make the request you ask for. Devkind does not receive, use or sell it.

## What is stored

- The server keeps the most recent scan results, about 100, in memory for the session.
- WhatWeb writes each scan log inside the container. With `--rm`, which the plugin uses, Docker deletes the container and its logs when the session ends.
- The server sends no telemetry or analytics to Devkind or anyone else. It writes logs to stderr on your machine only.

## Third parties

Each scan sends your IP address and the scan requests to the website you name. That site's own policy covers what it logs. Docker Hub serves the image download under Docker's policy.

## Children

The server is a technical research tool. It is not intended for people under 18.

## Changes and contact

Devkind updates this file when the server's data handling changes. The repository history records each change. Send questions to hello@devkind.com.au.
