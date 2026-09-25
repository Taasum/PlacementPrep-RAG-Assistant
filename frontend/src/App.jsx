import { useState } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [subject, setSubject] = useState("All Subjects");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  const suggestions = [
    "What is deadlock in operating systems?",
    "Explain normalization in DBMS.",
    "What is the difference between TCP and UDP?",
    "Explain BFS and DFS.",
  ];

  const askQuestion = async (customQuestion = null) => {
    const currentQuestion = customQuestion || question.trim();

    if (!currentQuestion || loading) return;

    const userMessage = {
      role: "user",
      content: currentQuestion,
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: currentQuestion,
          subject: subject,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error("Failed to get answer");
      }

      const assistantMessage = {
        role: "assistant",
        content: data.answer,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, something went wrong while generating the answer.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const uploadPDF = async (event) => {
    const file = event.target.files[0];

    if (!file) return;

    if (file.type !== "application/pdf") {
      alert("Please select a PDF file.");
      event.target.value = "";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);

    try {
      const response = await fetch("/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      if (data.error) {
        alert(`Upload failed: ${data.error}`);
      } else {
        alert(`${data.filename} uploaded and indexed successfully.`);
      }
    } catch (error) {
      console.error(error);
      alert("Failed to upload PDF.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  const newChat = () => {
    setMessages([]);
    setQuestion("");
  };

  return (
    <div className="app">

      {/* ================= SIDEBAR ================= */}
      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">✦</div>

          <div>
            <h2>PlacementPrep</h2>
            <p>AI Study Assistant</p>
          </div>
        </div>

        {/* Upload + New Chat */}
        <div className="sidebar-actions">

          <label className="upload-button">
            <span>↑</span>
            {uploading ? "Uploading..." : "Upload PDF"}

            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={uploadPDF}
              disabled={uploading}
              hidden
            />
          </label>

          <button className="new-chat-button" onClick={newChat}>
            <span>＋</span>
            New Chat
          </button>

        </div>

        {/* Study Material */}
        <div className="study-material">

          <div className="section-title">
            STUDY MATERIAL
          </div>

          <button
            className={`subject-button ${
              subject === "All Subjects" ? "active" : ""
            }`}
            onClick={() => setSubject("All Subjects")}
          >
            <span>⌘</span>
            All Subjects
          </button>

          <button
            className={`subject-button ${
              subject === "Operating Systems" ? "active" : ""
            }`}
            onClick={() => setSubject("Operating Systems")}
          >
            <span>◇</span>
            Operating Systems
          </button>

          <button
            className={`subject-button ${
              subject === "DBMS" ? "active" : ""
            }`}
            onClick={() => setSubject("DBMS")}
          >
            <span>▣</span>
            DBMS
          </button>

          <button
            className={`subject-button ${
              subject === "Computer Networks" ? "active" : ""
            }`}
            onClick={() => setSubject("Computer Networks")}
          >
            <span>◇</span>
            Computer Networks
          </button>

          <button
            className={`subject-button ${
              subject === "DSA" ? "active" : ""
            }`}
            onClick={() => setSubject("DSA")}
          >
            <span>λ</span>
            DSA
          </button>

        </div>

        {/* Bottom Status */}
        <div className="sidebar-footer">

          <div className="status">
            <span className="status-dot"></span>
            RAG System Online
          </div>

          <div className="powered-by">
            Powered by FAISS + Groq
          </div>

        </div>

      </aside>

      {/* ================= MAIN CONTENT ================= */}
      <main className="main-content">

        {/* Top Bar */}
        <header className="topbar">

          <div>
            <h1>PlacementPrep AI</h1>
            <p>Ask questions from your study material</p>
          </div>

          <div className="ai-status">
            <span className="status-dot"></span>
            AI Assistant
          </div>

        </header>

        {/* Chat Area */}
        <div className="chat-container">

          {messages.length === 0 ? (

            /* ================= EMPTY STATE ================= */
            <div className="empty-state">

              <div className="empty-icon">
                ✦
              </div>

              <h2>
                Prepare smarter with your study material
              </h2>

              <p>
                Upload your placement preparation PDFs and ask
                questions directly from them.
              </p>

              <div className="suggestions">

                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    className="suggestion"
                    onClick={() => askQuestion(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}

              </div>

            </div>

          ) : (

            /* ================= CHAT MESSAGES ================= */
            <div className="messages">

              {messages.map((message, index) => (

                <div
                  key={index}
                  className={`message ${
                    message.role === "user"
                      ? "user-message"
                      : "assistant-message"
                  }`}
                >

                  <div className="message-content">

                    <div className="message-label">
                      {message.role === "user"
                        ? "You"
                        : "PlacementPrep AI"}
                    </div>

                    <div className="message-text">
                      {message.content}
                    </div>

                  </div>

                </div>

              ))}

              {/* Loading */}
              {loading && (
                <div className="message assistant-message">

                  <div className="message-content">

                    <div className="message-label">
                      PlacementPrep AI
                    </div>

                    <div className="typing">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>

                  </div>

                </div>
              )}

            </div>

          )}

        </div>

        {/* ================= INPUT AREA ================= */}
        <div className="input-area">

          <div className="input-wrapper">

            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about OS, DBMS, CN, DSA..."
              rows="1"
              disabled={loading}
            />

            <button
              className="send-button"
              onClick={() => askQuestion()}
              disabled={!question.trim() || loading}
            >
              ↑
            </button>

          </div>

          <div className="input-hint">
            Press Enter to send · Answers are generated from your
            uploaded study material
          </div>

        </div>

      </main>

    </div>
  );
}

export default App;