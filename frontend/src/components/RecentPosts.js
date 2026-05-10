import { useState } from "react";

const platforms = [
  { id: "instagram", label: "Instagram" },
  { id: "linkedin", label: "LinkedIn" },
  { id: "youtube", label: "YouTube" },
  { id: "facebook", label: "Facebook" },
];

function RecentPosts({ scheduledData, connectedAccounts }) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState("");

  const isConnected = (platform) =>
    connectedAccounts.some((account) => account.platform === platform && account.status === "connected");

  const recentPosts = scheduledData.filter((post) => {
    const postPlatforms = post.platforms || [];
    return selectedPlatform && postPlatforms.includes(selectedPlatform);
  });

  return (
    <section className="top-section">
      <button className="section-trigger" onClick={() => setIsOpen(!isOpen)}>
        <span>Recent Posts</span>
        <span>{isOpen ? "Hide" : "Show"}</span>
      </button>

      {isOpen && (
        <div className="recent-panel">
          <div className="platform-grid">
            {platforms.map((platform) => (
              <button
                key={platform.id}
                className={selectedPlatform === platform.id ? "platform-button active" : "platform-button"}
                onClick={() => setSelectedPlatform(platform.id)}
              >
                <span>{platform.label}</span>
                <small>{isConnected(platform.id) ? "Connected" : "Not connected"}</small>
              </button>
            ))}
          </div>

          {selectedPlatform && (
            <div className="recent-list">
              <h3>{platforms.find((platform) => platform.id === selectedPlatform)?.label} Recent Posts</h3>

              {recentPosts.length === 0 && <p>No recent posts for this account yet.</p>}

              {recentPosts.map((post, index) => (
                <div className="recent-item" key={`${post.date}-${post.time}-${index}`}>
                  <p>{post.content}</p>
                  <small>
                    {post.date} {post.time} | Status: {post.status}
                  </small>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}

export default RecentPosts;
