function AuthPanel({
  isSignup,
  username,
  password,
  onUsernameChange,
  onPasswordChange,
  onLogin,
  onSignup,
  onToggleMode,
}) {
  return (
    <div style={{ textAlign: "center", marginTop: "20px" }}>
      <h3>{isSignup ? "Signup" : "Login"}</h3>

      <input placeholder="Username" value={username} onChange={onUsernameChange} />

      <br />
      <br />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={onPasswordChange}
      />

      <br />
      <br />

      {isSignup ? (
        <button onClick={onSignup}>Signup</button>
      ) : (
        <button onClick={onLogin}>Login</button>
      )}

      <p style={{ cursor: "pointer", color: "blue", marginTop: "10px" }} onClick={onToggleMode}>
        {isSignup ? "Already have account? Login" : "New user? Signup"}
      </p>
    </div>
  );
}

export default AuthPanel;
