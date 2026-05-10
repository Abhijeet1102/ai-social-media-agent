import { useState } from "react";

function ConnectModal({
  connectedAccounts,
  onClose,
  onConnectInstagram,
  onDisconnectInstagram,
  onConnectLinkedIn,
  onDisconnectLinkedIn,
  onConnectYouTube,
  onDisconnectYouTube,
  onConnectFacebook,
  onDisconnectFacebook,
}) {
  const [openPlatform, setOpenPlatform] = useState("");
  const instagramAccount = connectedAccounts.find(
    (account) => account.platform === "instagram" && account.status === "connected"
  );
  const linkedinAccount = connectedAccounts.find(
    (account) => account.platform === "linkedin" && account.status === "connected"
  );
  const youtubeAccount = connectedAccounts.find(
    (account) => account.platform === "youtube" && account.status === "connected"
  );
  const facebookAccount = connectedAccounts.find(
    (account) => account.platform === "facebook" && account.status === "connected"
  );
  const platforms = [
    { id: "instagram", label: "Instagram", available: true },
    { id: "linkedin", label: "LinkedIn", available: true },
    { id: "youtube", label: "YouTube", available: true },
    { id: "facebook", label: "Facebook", available: true },
  ];

  const togglePlatform = (platform) => {
    setOpenPlatform(openPlatform === platform ? "" : platform);
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <h2>Connect Your Accounts</h2>

        <div className="account-list">
          {platforms.map((platform) => (
            <div className="account-dropdown" key={platform.id}>
              <button className="account-trigger" onClick={() => togglePlatform(platform.id)}>
                <span>{platform.label}</span>
                <span>{openPlatform === platform.id ? "Hide" : "Show"}</span>
              </button>

              {openPlatform === platform.id && (
                <div className="account-panel">
                  {platform.id === "instagram" && instagramAccount && (
                    <>
                      <strong>Instagram Connected</strong>
                      <span>{instagramAccount.profile?.name || "Instagram account"}</span>
                      <small>Type: {instagramAccount.profile?.account_type || "Not available"}</small>
                      <small>Scopes: {instagramAccount.scope || "Not available"}</small>

                      <button onClick={() => window.open("https://www.instagram.com/", "_blank")}>
                        Open Instagram Account
                      </button>
                      <button className="danger-button" onClick={onDisconnectInstagram}>
                        Logout Instagram
                      </button>
                    </>
                  )}

                  {platform.id === "instagram" && !instagramAccount && (
                    <>
                      <span>Instagram is not connected.</span>
                      <button onClick={onConnectInstagram}>Connect Instagram</button>
                    </>
                  )}

                  {platform.id === "linkedin" && linkedinAccount && (
                    <>
                      <strong>LinkedIn Connected</strong>
                      <span>{linkedinAccount.profile?.name || "LinkedIn account"}</span>
                      <span>{linkedinAccount.profile?.email || "Email not available"}</span>
                      <small>Scopes: {linkedinAccount.scope || "Not available"}</small>

                      <button onClick={() => window.open("https://www.linkedin.com/feed/", "_blank")}>
                        Open LinkedIn Account
                      </button>
                      <button className="danger-button" onClick={onDisconnectLinkedIn}>
                        Logout LinkedIn
                      </button>
                    </>
                  )}

                  {platform.id === "linkedin" && !linkedinAccount && (
                    <>
                      <span>LinkedIn is not connected.</span>
                      <button onClick={onConnectLinkedIn}>Connect LinkedIn</button>
                    </>
                  )}

                  {platform.id === "youtube" && youtubeAccount && (
                    <>
                      <strong>YouTube Connected</strong>
                      <span>{youtubeAccount.profile?.name || "YouTube channel"}</span>
                      <small>Scopes: {youtubeAccount.scope || "Not available"}</small>

                      <button onClick={() => window.open("https://www.youtube.com/channel_switcher", "_blank")}>
                        Open YouTube Account
                      </button>
                      <button className="danger-button" onClick={onDisconnectYouTube}>
                        Logout YouTube
                      </button>
                    </>
                  )}

                  {platform.id === "youtube" && !youtubeAccount && (
                    <>
                      <span>YouTube is not connected.</span>
                      <button onClick={onConnectYouTube}>Connect YouTube</button>
                    </>
                  )}

                  {platform.id === "facebook" && facebookAccount && (
                    <>
                      <strong>Facebook Connected</strong>
                      <span>{facebookAccount.profile?.name || "Facebook account"}</span>
                      <span>{facebookAccount.profile?.email || "Email not available"}</span>
                      <small>Pages: {facebookAccount.pages?.length || 0}</small>
                      <small>Scopes: {facebookAccount.scope || "Not available"}</small>

                      <button onClick={() => window.open("https://www.facebook.com/pages/?category=your_pages", "_blank")}>
                        Open Facebook Pages
                      </button>
                      <button className="danger-button" onClick={onDisconnectFacebook}>
                        Logout Facebook
                      </button>
                    </>
                  )}

                  {platform.id === "facebook" && !facebookAccount && (
                    <>
                      <span>Facebook is not connected.</span>
                      <button onClick={onConnectFacebook}>Connect Facebook</button>
                    </>
                  )}

                  {!platform.available && (
                    <>
                      <span>{platform.label} integration is coming next.</span>
                      <button disabled>Not available yet</button>
                    </>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        <button className="close-btn" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
}

export default ConnectModal;
