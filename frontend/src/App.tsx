import React, { useState } from "react";
import "./App.css"; // Importing our new modern styles

function App() {
  const [url, setUrl] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const bryte_website = "https://bryte-techsolutions.com";

  const handleSubmit: React.SubmitEventHandler<HTMLFormElement> = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/api/transcribe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Failed to fetch transcript");
      }

      const data: { transcript: string; channel_name: string } = await response.json();
      downloadTxtFile(data.transcript, data.channel_name);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const downloadTxtFile = (text: string, filename: string): void => {
    const element = document.createElement("a");
    const file = new Blob([text], { type: "text/plain;charset=utf-8" });

    element.href = URL.createObjectURL(file);
    element.download = `${filename}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="app-wrapper">
      <main className="glass-card">
        <div className="header-section">
          <h1>Reel to Transcript</h1>
          <p className="subtitle">Instantly extract and download text from Meta videos.</p>
        </div>

        <form onSubmit={handleSubmit} className="input-group">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste public Instagram or Facebook Reel URL..."
            required
            className="url-input"
          />
          <button type="submit" disabled={isLoading} className="submit-button">
            {isLoading ? <span className="spinner"></span> : "Download .txt"}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <p>
              <strong>Error:</strong> {error}
            </p>
          </div>
        )}
      </main>

      <footer className="company-footer">
        <p>
          &copy;{" "}
          <a rel="author" target="_blank" href={bryte_website}>
            2026 Bryte Tech Solutions CIC. All rights
          </a>{" "}
          reserved.
        </p>
      </footer>
    </div>
  );
}

export default App;
