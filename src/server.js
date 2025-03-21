import { createServer } from "net";
import { handleClient } from "./handlers/handleClient.js";
import { PORT, HOST } from "./config.js";

function startServer() {
    const server = createServer(handleClient);
    server.listen(PORT, HOST, () => {
        console.log(`Listening on ${HOST}:${PORT}...`);
    });

    server.on("error", (err) => {
        console.log("Server error:", err);
    });
}

export { startServer };
