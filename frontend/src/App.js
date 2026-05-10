import { useCallback, useEffect, useState } from "react";
import { authHeaders, BASE_URL, formBody, getToken } from "./api";
import AuthPanel from "./components/AuthPanel";
import ConnectModal from "./components/ConnectModal";
import CustomerSupport from "./components/CustomerSupport";
import Dashboard from "./components/Dashboard";
import Generator from "./components/Generator";
import RecentPosts from "./components/RecentPosts";
import "./App.css";

function App() {
  const [topic, setTopic] = useState("");
  const [result, setResult] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isSignup, setIsSignup] = useState(false);

  const [posts, setPosts] = useState([]);
  const [scheduledData, setScheduledData] = useState([]);
  const [connectedAccounts, setConnectedAccounts] = useState([]);

  const fetchScheduled = useCallback(async () => {
    const res = await fetch(`${BASE_URL}/scheduled`, {
      headers: authHeaders(),
    });

    if (res.ok) setScheduledData(await res.json());
  }, []);

  const fetchConnectedAccounts = useCallback(async () => {
    const res = await fetch(`${BASE_URL}/connected-accounts`, {
      headers: authHeaders(),
    });

    if (res.ok) setConnectedAccounts(await res.json());
  }, []);

  useEffect(() => {
    const token = getToken();
    if (token) setIsLoggedIn(true);

    const params = new URLSearchParams(window.location.search);
    const connectStatus = params.get("status");
    const connectMessage = params.get("message");

    if (params.get("connect") === "linkedin" && connectStatus) {
      alert(connectMessage || `LinkedIn ${connectStatus}`);
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    if (params.get("connect") === "youtube" && connectStatus) {
      alert(connectMessage || `YouTube ${connectStatus}`);
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    if (params.get("connect") === "instagram" && connectStatus) {
      alert(connectMessage || `Instagram ${connectStatus}`);
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    if (params.get("connect") === "facebook" && connectStatus) {
      alert(connectMessage || `Facebook ${connectStatus}`);
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  useEffect(() => {
    if (isLoggedIn) {
      fetchScheduled();
      fetchConnectedAccounts();
    }
  }, [isLoggedIn, fetchScheduled, fetchConnectedAccounts]);

  const handleLogin = async () => {
    const res = await fetch(`${BASE_URL}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formBody({ username, password }),
    });

    const data = await res.json();

    if (data.access_token) {
      localStorage.setItem("token", data.access_token);
      setIsLoggedIn(true);
      alert("Login Successful");
    } else {
      alert(data.detail || "Login Failed");
    }
  };

  const handleSignup = async () => {
    const res = await fetch(`${BASE_URL}/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formBody({ username, password }),
    });

    const data = await res.json();
    alert(data.msg || data.detail || "Signup Failed");

    if (data.msg) setIsSignup(false);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    setPosts([]);
    setScheduledData([]);
    setConnectedAccounts([]);
    setResult("");
  };

  const handleAuthError = (data) => {
    if (data.detail === "Invalid token") {
      localStorage.removeItem("token");
      setIsLoggedIn(false);
      setConnectedAccounts([]);
      alert("Session expired. Please login again.");
      return true;
    }

    return false;
  };

  const generateContent = async () => {
    const res = await fetch(`${BASE_URL}/generate?topic=${encodeURIComponent(topic)}`, {
      headers: authHeaders(),
    });

    const data = await res.json();
    setResult(data.result);
  };

  const schedulePost = async () => {
    if (!result || !date || !time) {
      alert("Fill all fields!");
      return;
    }

    const res = await fetch(`${BASE_URL}/schedule`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify({
        content: result,
        date,
        time,
        platforms: ["linkedin"],
      }),
    });

    const data = await res.json();
    alert(data.msg || data.detail || "Post schedule failed");

    if (res.ok) {
      setDate("");
      setTime("");
      setResult("");
      setTopic("");
      setPosts([]);
      fetchScheduled();
    }
  };

  const postNowLinkedIn = async () => {
    if (!result) {
      alert("Generate content first");
      return;
    }

    const res = await fetch(`${BASE_URL}/post-now/linkedin`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify({
        content: result,
      }),
    });

    const data = await res.json();
    alert(data.msg || data.detail || "Post failed");

    if (res.ok) {
      setResult("");
      setTopic("");
      setPosts([]);
      fetchScheduled();
    }
  };

  const connectLinkedIn = async () => {
    if (!isLoggedIn) {
      alert("Please login first");
      return;
    }

    const res = await fetch(`${BASE_URL}/auth/linkedin/start`, {
      headers: authHeaders(),
    });
    const data = await res.json();

    if (handleAuthError(data)) return;

    if (!res.ok) {
      alert(data.detail || "LinkedIn connect failed");
      return;
    }

    window.location.href = data.url;
  };

  const connectInstagram = async () => {
    if (!isLoggedIn) {
      alert("Please login first");
      return;
    }

    const res = await fetch(`${BASE_URL}/auth/instagram/start`, {
      headers: authHeaders(),
    });
    const data = await res.json();

    if (handleAuthError(data)) return;

    if (!res.ok) {
      alert(data.detail || "Instagram connect failed");
      return;
    }

    window.location.href = data.url;
  };

  const disconnectInstagram = async () => {
    const res = await fetch(`${BASE_URL}/connected-accounts/instagram`, {
      method: "DELETE",
      headers: authHeaders(),
    });
    const data = await res.json();
    alert(data.msg || data.detail || "Instagram disconnected");
    fetchConnectedAccounts();
  };

  const connectFacebook = async () => {
    if (!isLoggedIn) {
      alert("Please login first");
      return;
    }

    const res = await fetch(`${BASE_URL}/auth/facebook/start`, {
      headers: authHeaders(),
    });
    const data = await res.json();

    if (handleAuthError(data)) return;

    if (!res.ok) {
      alert(data.detail || "Facebook connect failed");
      return;
    }

    window.location.href = data.url;
  };

  const disconnectFacebook = async () => {
    const res = await fetch(`${BASE_URL}/connected-accounts/facebook`, {
      method: "DELETE",
      headers: authHeaders(),
    });
    const data = await res.json();
    alert(data.msg || data.detail || "Facebook disconnected");
    fetchConnectedAccounts();
  };

  const disconnectLinkedIn = async () => {
    const res = await fetch(`${BASE_URL}/connected-accounts/linkedin`, {
      method: "DELETE",
      headers: authHeaders(),
    });
    const data = await res.json();
    alert(data.msg || data.detail || "LinkedIn disconnected");
    fetchConnectedAccounts();
  };

  const connectYouTube = async () => {
    if (!isLoggedIn) {
      alert("Please login first");
      return;
    }

    const res = await fetch(`${BASE_URL}/auth/youtube/start`, {
      headers: authHeaders(),
    });
    const data = await res.json();

    if (handleAuthError(data)) return;

    if (!res.ok) {
      alert(data.detail || "YouTube connect failed");
      return;
    }

    window.location.href = data.url;
  };

  const disconnectYouTube = async () => {
    const res = await fetch(`${BASE_URL}/connected-accounts/youtube`, {
      method: "DELETE",
      headers: authHeaders(),
    });
    const data = await res.json();
    alert(data.msg || data.detail || "YouTube disconnected");
    fetchConnectedAccounts();
  };

  return (
    <div className="app">
      <header className="hero">
        <h1>AI Social Media Automation</h1>
        <p>Create, Schedule & Grow with AI</p>

        <button onClick={() => setShowModal(true)}>Connect Accounts</button>

        {isLoggedIn && (
          <button onClick={handleLogout} style={{ marginLeft: "10px" }}>
            Logout
          </button>
        )}
      </header>

      {!isLoggedIn && (
        <AuthPanel
          isSignup={isSignup}
          username={username}
          password={password}
          onUsernameChange={(e) => setUsername(e.target.value)}
          onPasswordChange={(e) => setPassword(e.target.value)}
          onLogin={handleLogin}
          onSignup={handleSignup}
          onToggleMode={() => setIsSignup(!isSignup)}
        />
      )}

      {isLoggedIn && (
        <>
          <RecentPosts scheduledData={scheduledData} connectedAccounts={connectedAccounts} />
          <Generator
            topic={topic}
            result={result}
            date={date}
            time={time}
            onTopicChange={(e) => setTopic(e.target.value)}
            onGenerate={generateContent}
            onDateChange={(e) => setDate(e.target.value)}
            onTimeChange={(e) => setTime(e.target.value)}
            onSchedule={schedulePost}
            onPostNow={postNowLinkedIn}
          />
          <Dashboard posts={posts} scheduledData={scheduledData} />
        </>
      )}

      {showModal && (
        <ConnectModal
          connectedAccounts={connectedAccounts}
          onConnectInstagram={connectInstagram}
          onDisconnectInstagram={disconnectInstagram}
          onConnectLinkedIn={connectLinkedIn}
          onDisconnectLinkedIn={disconnectLinkedIn}
          onConnectYouTube={connectYouTube}
          onDisconnectYouTube={disconnectYouTube}
          onConnectFacebook={connectFacebook}
          onDisconnectFacebook={disconnectFacebook}
          onClose={() => setShowModal(false)}
        />
      )}

      <CustomerSupport />
    </div>
  );
}

export default App;
