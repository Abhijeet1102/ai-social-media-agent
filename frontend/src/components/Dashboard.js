function Dashboard({ posts, scheduledData }) {
  return (
    <>
      <section>
        <h2>Dashboard</h2>

        {posts.map((post, index) => (
          <div key={index} className="result-card">
            <p>{post.result}</p>
            <small>Topic: {post.topic}</small>
          </div>
        ))}
      </section>

      <section>
        <h2>Scheduled Posts</h2>

        {scheduledData.map((post, index) => (
          <div key={index} className="result-card">
            <p>{post.content}</p>
            <small>
              {post.date} {post.time} | Status: {post.status}
            </small>
          </div>
        ))}
      </section>
    </>
  );
}

export default Dashboard;
