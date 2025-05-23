import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  const [isTyping, setIsTyping] = useState(false);

  // Scroll chat to bottom when messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true); // Start typing indicator

    try {
      const response = await axios.post("http://127.0.0.1:8000/chat", {
        query: input,
        session_id: "default-session",
      });

      const aiMessage = {
        sender: "ai",
        text: response.data.response || "Sorry, no response.",
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        sender: "ai",
        text: "Error: Could not get response from server.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false); // Stop typing indicator
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div style={styles.container}>
      <h2>Weather Agent Chat</h2>
      <div style={styles.chatBox}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              ...styles.message,
              alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
              backgroundColor: msg.sender === "user" ? "#DCF8C6" : "#E8E8E8",
            }}
          >
            {msg.text}
          </div>
        ))}
        {isTyping && (
          <div
            style={{
              ...styles.message,
              alignSelf: "flex-start",
              backgroundColor: "#E8E8E8",
              fontStyle: "italic",
            }}
          >
            Agent is typing...
          </div>
        )}

        <div ref={bottomRef} />
      </div>
      <div style={styles.inputArea}>
        <input
          style={styles.input}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me about the weather..."
        />
        <button onClick={sendMessage} style={styles.button}>
          Send
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 600,
    margin: "20px auto",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  },
  chatBox: {
    border: "1px solid #ccc",
    borderRadius: 8,
    padding: 10,
    height: 400,
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: 10,
    backgroundColor: "#fefefe",
  },
  message: {
    maxWidth: "70%",
    padding: 10,
    borderRadius: 15,
    fontSize: 16,
  },
  inputArea: {
    marginTop: 10,
    display: "flex",
    gap: 10,
  },
  input: {
    flexGrow: 1,
    padding: 10,
    fontSize: 16,
    borderRadius: 20,
    border: "1px solid #ccc",
  },
  button: {
    padding: "10px 20px",
    fontSize: 16,
    borderRadius: 20,
    border: "none",
    backgroundColor: "#4CAF50",
    color: "white",
    cursor: "pointer",
  },
};

export default App;
