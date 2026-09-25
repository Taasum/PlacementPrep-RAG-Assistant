import { useState } from "react";
import "./App.css";

const suggestions = [
  "What is deadlock in Operating Systems?",
  "Explain normalization in DBMS",
  "What is the difference between TCP and UDP?",
  "Explain BFS and DFS",
];

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState("All Subjects");
  const [uploading, setUploading] = useState(false);

  const uploadPDF = async (event) => {
  const file = event.target.files[0];

  if (!file) return;

  if (file.type !== "application/pdf") {
    alert("Please select a PDF file.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  setUploading(true);

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/upload",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error("Upload failed");
    }

    alert(
      `${data.filename} uploaded and indexed successfully.`
    );
  } catch (error) {
    console.error(error);
    alert("Failed to upload PDF.");
  } finally {
    setUploading(false);
    event.target.value = "";
  }
};
  const askQuestion = async (text = question) => {
    if (!text.trim() || loading) return;

    const userQuestion = text.trim();

    setMessages((prev) => [
      ...prev,
      {
        type: "user",
        text: userQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userQuestion,
          subject: selectedSubject,
        }),
      });

      if (!response.ok) {
        throw new Error("API request failed");
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          text: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          text: "I couldn't connect to the backend. Please make sure FastAPI is running on port 8000.",
          sources: [],
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="app">

      {/* Sidebar */}
      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">✦</div>

          <div>
            <h2>PlacementPrep</h2>
            <span>AI Study Assistant</span>
          </div>
        </div>

        <button
          className="new-chat"
          onClick={clearChat}
          
        >
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
          <span>＋</span>
          New Chat
        </button>

        <div className="sidebar-section">
          <p className="section-title">STUDY MATERIAL</p>

          <div
  className={`subject ${
    selectedSubject === "All Subjects" ? "active" : ""
  }`}
  onClick={() => setSelectedSubject("All Subjects")}
>
  <span className="subject-icon">⌘</span>
  <span>All Subjects</span>
</div>

          <div
  className={`subject ${
    selectedSubject === "Operating Systems" ? "active" : ""
  }`}
  onClick={() => setSelectedSubject("Operating Systems")}
>
  <span className="subject-icon">◈</span>
  <span>Operating Systems</span>
</div>

          <div
  className={`subject ${
    selectedSubject === "DBMS" ? "active" : ""
  }`}
  onClick={() => setSelectedSubject("DBMS")}
>
  <span className="subject-icon">▣</span>
  <span>DBMS</span>
</div>

          <div
  className={`subject ${
    selectedSubject === "Computer Networks" ? "active" : ""
  }`}
  onClick={() => setSelectedSubject("Computer Networks")}
>
  <span className="subject-icon">◇</span>
  <span>Computer Networks</span>
</div>

         <div
  className={`subject ${
    selectedSubject === "DSA" ? "active" : ""
  }`}
  onClick={() => setSelectedSubject("DSA")}
>
  <span className="subject-icon">λ</span>
  <span>DSA</span>
</div>
        </div>

        <div className="sidebar-bottom">
          <div className="status">
            <span className="status-dot"></span>
            RAG System Online
          </div>

          <p>Powered by FAISS + Gemini</p>
        </div>

      </aside>

      {/* Main */}
      <main className="main">

        {/* Header */}
        <header className="topbar">

          <div>
            <h3>PlacementPrep AI</h3>
            <p>Ask questions from your study material</p>
          </div>

          <div className="topbar-badge">
            <span>●</span> AI Assistant
          </div>

        </header>

        {/* Chat */}
        <section className="chat-area">

          {messages.length === 0 ? (

            <div className="welcome">

              <div className="welcome-icon">
                ✦
              </div>

              <h1>
                Prepare smarter.
                <br />
                <span>Ask anything.</span>
              </h1>

              <p className="welcome-text">
                Your personal RAG-powered assistant for
                placement preparation.
              </p>

              <div className="suggestions">

                {suggestions.map((item, index) => (
                  <button
                    key={index}
                    onClick={() => askQuestion(item)}
                  >
                    <span>→</span>
                    {item}
                  </button>
                ))}

              </div>

            </div>

          ) : (

            <div className="conversation">

              {messages.map((message, index) => (

                <div
                  key={index}
                  className={`message-row ${message.type}`}
                >

                  {message.type === "bot" && (
                    <div className="avatar ai-avatar">
                      ✦
                    </div>
                  )}

                  <div className="message-content">

                    <div className="message-label">
                      {message.type === "user"
                        ? "You"
                        : "PlacementPrep AI"}
                    </div>

                    <div
                      className={`message-bubble ${
                        message.error ? "error" : ""
                      }`}
                    >
                      {message.text}
                    </div>

                    {message.sources &&
                      message.sources.length > 0 && (

                      <div className="sources">

                        <div className="sources-title">
                          <span>⌕</span>
                          Retrieved Sources
                        </div>

                        <div className="source-list">

                          {message.sources.map(
                            (source, sourceIndex) => (

                            <div
                              className="source"
                              key={sourceIndex}
                            >
                              <span className="file-icon">
                                ▤
                              </span>

                              <span>{message.sources && message.sources.length > 0 && (
  <div className="sources">
    <h4>Sources</h4>

    <div className="source-list">
      {message.sources.map((source, sourceIndex) => (
        <div className="source" key={sourceIndex}>
          <div className="source-header">
            <span className="file-icon">▤</span>

            <span className="source-file">
              {source.file}
            </span>

            <span className="source-distance">
              {Number(source.distance).toFixed(2)}
            </span>
          </div>

          <p className="source-snippet">
            {source.snippet}
          </p>
        </div>
      ))}
    </div>
  </div>
)}</span>
                            </div>

                          ))}

                        </div>

                      </div>
                    )}

                  </div>

                  {message.type === "user" && (
                    <div className="avatar user-avatar">
                      U
                    </div>
                  )}

                </div>

              ))}

              {loading && (

                <div className="message-row bot">

                  <div className="avatar ai-avatar">
                    ✦
                  </div>

                  <div className="message-content">

                    <div className="message-label">
                      PlacementPrep AI
                    </div>

                    <div className="message-bubble loading">

                      <span></span>
                      <span></span>
                      <span></span>

                    </div>

                  </div>

                </div>
              )}

            </div>
          )}

        </section>

        {/* Input */}
        <div className="input-wrapper">

          <div className="input-box">

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

          <p className="input-hint">
            Press <strong>Enter</strong> to send ·
            Answers are generated from your uploaded study material
          </p>

        </div>

      </main>

    </div>
  );
}

export default App;