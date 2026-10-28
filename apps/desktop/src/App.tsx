
import { useEffect, useState, type FormEvent } from "react";
import "./App.css";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

type HealthResponse = {
  status: string;
  version: string;
};

type ChatResponse = {
  reply?: string;
  conversation_id?: string;
  detail?: string;
};

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [message, setMessage] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [backendStatus, setBackendStatus] = useState<
    "checking" | "online" | "offline"
  >("checking");

  useEffect(() => {
    let active = true;

    async function checkBackend() {
      try {
        const response = await fetch("http://127.0.0.1:8000/health");

        if (!response.ok) {
          throw new Error("Health check failed");
        }

        const data: HealthResponse = await response.json();

        if (data.status !== "ok") {
          throw new Error("Backend is not healthy");
        }

        if (active) setBackendStatus("online");
      } catch {
        if (active) setBackendStatus("offline");
      }
    }

    void checkBackend();

    return () => {
      active = false;
    };
  }, []);

  async function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const text = message.trim();

    if (!text || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", content: text },
    ]);
    setMessage("");
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: text,
          ...(conversationId ? { conversation_id: conversationId } : {}),
        }),
      });

      const data: ChatResponse = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "The JARVIS API returned an error.");
      }

      if (!data.reply) {
        throw new Error("The API returned an empty reply.");
      }

      if (!data.conversation_id) {
        throw new Error("The API did not return a conversation ID.");
      }

      setConversationId(data.conversation_id);
      setMessages((previous) => [
        ...previous,
        { role: "assistant", content: data.reply! },
      ]);
      setBackendStatus("online");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not connect to the JARVIS backend.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <header>
        <h1>JARVIS</h1>
        <p>Your personal AI assistant</p>
        <p
          className={`status backend-status ${backendStatus}`}
          role="status"
        >
          Backend:{" "}
          {backendStatus === "checking"
            ? "Checking connection..."
            : backendStatus === "online"
              ? "Online"
              : "Offline"}
        </p>
      </header>

      <section className="chat" aria-live="polite">
        {messages.length === 0 && (
          <p className="welcome">
            Good day, sir. How may I assist you?
          </p>
        )}

        {messages.map((item, index) => (
          <div
            className={`message ${item.role}`}
            key={`${item.role}-${index}`}
          >
            <strong>
              {item.role === "user" ? "You" : "JARVIS"}
            </strong>
            <p>{item.content}</p>
          </div>
        ))}

        {loading && <p className="status">JARVIS is thinking...</p>}
        {error && <p className="error">{error}</p>}
      </section>

      <form className="chat-form" onSubmit={sendMessage}>
        <input
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Ask JARVIS something..."
          aria-label="Message to JARVIS"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !message.trim()}>
          Send
        </button>
      </form>
    </main>
  );
}

export default App;
