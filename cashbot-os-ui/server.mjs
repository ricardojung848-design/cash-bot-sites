import { createServer } from "node:http";
import { parse } from "node:url";
import next from "next";
import { WebSocketServer } from "ws";

const prod = process.argv.includes("--prod");
const dev = !prod;
const host = "localhost";
const port = Number(process.env.PORT || 3000);

const app = next({ dev, hostname: host, port });
const handle = app.getRequestHandler();

const eventTypes = ["idea.created", "task.assigned", "task.completed", "audit.logged"];

app.prepare().then(() => {
  const server = createServer((req, res) => {
    const parsedUrl = parse(req.url, true);
    handle(req, res, parsedUrl);
  });

  const wss = new WebSocketServer({ noServer: true });

  const sendEvent = () => {
    const type = eventTypes[Math.floor(Math.random() * eventTypes.length)];
    const payload = JSON.stringify({
      type,
      timestamp: new Date().toISOString(),
      message: `Test-Event ${type}`,
    });
    wss.clients.forEach((client) => {
      if (client.readyState === 1) {
        client.send(payload);
      }
    });
  };

  const interval = setInterval(sendEvent, 9000);

  wss.on("connection", (socket) => {
    socket.send(
      JSON.stringify({
        type: "system.connected",
        timestamp: new Date().toISOString(),
        message: "WebSocket-Verbindung aktiv.",
      }),
    );
  });

  server.on("upgrade", (req, socket, head) => {
    if (req.url === "/api/v1/events/ws") {
      wss.handleUpgrade(req, socket, head, (ws) => {
        wss.emit("connection", ws, req);
      });
      return;
    }
    socket.destroy();
  });

  server.listen(port, () => {
    const mode = dev ? "Entwicklung" : "Produktion";
    console.log(`[CashBot OS UI] Server läuft (${mode}) auf http://${host}:${port}`);
  });

  server.on("close", () => clearInterval(interval));
});
