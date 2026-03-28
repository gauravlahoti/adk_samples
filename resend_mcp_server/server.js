const http = require('http');
const { spawn } = require('child_process');

const PORT = process.env.PORT || 8080;
const MCP_PORT = 3001;

console.log(`Starting Resend MCP proxy server...`);
console.log(`External port: ${PORT}, Internal MCP port: ${MCP_PORT}`);

// Start the resend-mcp server internally
const mcpProcess = spawn('npx', ['-y', 'resend-mcp', '--http', '--port', MCP_PORT.toString()], {
  stdio: 'inherit',
  env: process.env
});

mcpProcess.on('error', (err) => {
  console.error('Failed to start MCP server:', err);
  process.exit(1);
});

// Wait for MCP server to start, then create proxy
setTimeout(() => {
  const server = http.createServer((req, res) => {
    const options = {
      hostname: '127.0.0.1',
      port: MCP_PORT,
      path: req.url,
      method: req.method,
      headers: {
        ...req.headers,
        host: `127.0.0.1:${MCP_PORT}`  // Override host to localhost
      }
    };

    const proxyReq = http.request(options, (proxyRes) => {
      res.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(res);
    });

    proxyReq.on('error', (err) => {
      console.error('Proxy error:', err.message);
      res.writeHead(502);
      res.end(JSON.stringify({ error: 'Bad Gateway', message: err.message }));
    });

    req.pipe(proxyReq);
  });

  server.listen(PORT, '0.0.0.0', () => {
    console.log(`Proxy server listening on port ${PORT}`);
    console.log(`Forwarding to internal MCP server on port ${MCP_PORT}`);
  });
}, 3000);

process.on('SIGTERM', () => {
  console.log('Shutting down...');
  mcpProcess.kill();
  process.exit(0);
});
